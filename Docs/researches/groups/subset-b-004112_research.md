# subset-b-004112 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-queue.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-queue.c

Purpose: implements the cx18 stream buffer and memory descriptor list queue machinery used to move capture buffers between driver ownership and CX23418 firmware ownership. It manages four queue states on each `struct cx18_stream`: idle MDLs not configured for firmware, free MDLs ready to submit, busy MDLs owned by firmware, and full MDLs returned with data.

Important APIs: `cx18_queue_init`, `_cx18_enqueue`, `cx18_dequeue`, `cx18_queue_get_mdl`, `cx18_flush_queues`, `cx18_unload_queues`, `cx18_load_queues`, `_cx18_mdl_sync_for_device`, `cx18_stream_alloc`, and `cx18_stream_free`. `cx18_buf_swap` and `_cx18_mdl_swap` correct 32-bit byte ordering for non-TS data. Queue depth is tracked with atomics, while list mutation uses per-queue spinlocks.

Control flow: allocation creates one MDL and one DMA-mapped buffer per configured stream buffer, places MDLs on `q_idle`, and records a firmware SCB base index. `cx18_load_queues` binds buffers from `buf_pool` into MDLs, writes physical address and length entries into `cx->scb->cpu_mdl`, and moves complete MDLs to `q_free`. Firmware completion calls use `cx18_queue_get_mdl` to find the returned MDL in `q_busy`, update per-buffer `bytesused`, sync DMA for CPU, and mark byte-swapping as needed. Missed completions are detected by repeated skips and swept back to `q_free`.

State and persistence: state is volatile kernel memory plus DMA mappings and firmware-visible SCB MDL entries. There is no disk persistence. Cleanup unloads queues, unmaps DMA buffers, and frees MDLs and buffer memory. Risks include lock ordering in `cx18_queue_flush`, firmware/driver MDL desynchronization, DMA coherency errors, SCB reserved area exhaustion, and the unlocked `buf_pool` requirement that callers stop stream activity before unload/reconfiguration. Test signals are capture start/stop stress, queue depth invariants, DMA mapping failures, VBI/YUV partial MDL sizing, and warnings about skipped MDLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-queue.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-queue.h

Purpose: declares the cx18 queue API and fast inline helpers for DMA cache synchronization, MDL byte swapping, FIFO enqueue, and LIFO push behavior. It is the interface consumed by stream startup, interrupt completion handling, VBI post-processing, and file read paths.

Important APIs/types: `CX18_DMA_UNMAPPED`, `cx18_buf_sync_for_cpu`, `cx18_buf_sync_for_device`, `cx18_mdl_sync_for_device`, `cx18_mdl_swap`, `cx18_enqueue`, `cx18_push`, `cx18_dequeue`, `cx18_queue_get_mdl`, `cx18_unload_queues`, `cx18_load_queues`, `cx18_stream_alloc`, and `cx18_stream_free`. The header depends on `struct cx18_stream`, `struct cx18_buffer`, `struct cx18_mdl`, Linux list helpers, and the PCI DMA API.

Control flow and integration: callers use `cx18_enqueue` for normal FIFO queueing and `cx18_push` when an incomplete MDL should be restored to the front, such as in `cx18_load_queues`. Inline single-buffer fast paths avoid iterating MDL buffer lists for the common one-buffer-per-MDL case. The header intentionally delegates multi-buffer work to the `.c` file.

State and risks: the header directly exposes low-level DMA synchronization semantics, so misuse can corrupt capture data or leak stale cache contents. Test signals are architecture-sensitive DMA coherency tests, non-TS byte-swap validation, and multi-buffer YUV/VBI MDL paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-scb.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-scb.c

Purpose: initializes the CX23418 System Control Block in encoder memory. The SCB tells firmware processors where IPC mailboxes, interrupt values, processor state fields, MDL acknowledgements, and MDL arrays live.

Important API: `cx18_init_scb(struct cx18 *cx)`. It uses `cx18_setup_page`, `cx18_memset_io`, and `cx18_writel` to zero the 64 KiB reserved SCB area, then populate interrupt masks and mailbox offsets for CPU, APU, HPU, PPU, and EPU pairs.

Control flow: the function selects the SCB encoder memory page at `SCB_OFFSET`, clears it, writes non-ACK and ACK interrupt bit values into each processor communication slot, writes absolute SCB offsets for every mailbox pair, writes `ipc_offset`, and finally marks the EPU state ready. It must run before mailbox/API or MDL exchange starts.

State and risks: all state is firmware-visible MMIO memory, not persistent storage. A wrong offset or bit mask breaks inter-processor firmware IPC and can prevent firmware boot or DMA completion. Test signals are firmware boot readiness, mailbox command success, interrupt acknowledgement behavior, and capture start after cold reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-scb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-scb.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-scb.h

Purpose: defines the CX23418 System Control Block layout and IPC interrupt constants shared by the host driver and firmware. It maps the reserved encoder-memory region used for processor state, mailbox exchange, semaphore state, MDL acknowledgements, and firmware DMA descriptors.

Important types/constants: `IRQ_*` constants encode SW1/SW2 interrupt and ack bits; `SCB_OFFSET` is `0xDC0000`; `SCB_RESERVED_SIZE` is 64 KiB; `struct cx18_mdl_ent` holds firmware-visible physical address and length pairs; `struct cx18_scb` contains processor state blocks, all mailbox structures, `cpu_mdl_ack`, and flexible-array `cpu_mdl`.

Control flow/integration: stream allocation checks `SCB_RESERVED_SIZE` before assigning MDL slots; stream loading writes `cpu_mdl[]`; stream startup gives firmware offsets to `cpu_mdl_ack` and individual MDLs. Mailbox code relies on the offsets initialized by `cx18_init_scb`.

State and risks: this is a hardware ABI structure, so packing, ordering, and offset changes are high risk. Test signals include compile-time structure consistency, boot firmware IPC, mailbox ping, DMA done notifications, and high-buffer-count SCB exhaustion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-scb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-streams.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-streams.c

Purpose: owns cx18 stream lifecycle for MPEG, transport stream, YUV, VBI, PCM, IDX, and radio devices. It prepares V4L2/DVB devices, initializes videobuf2 for YUV capture, allocates DMA queues, registers device nodes, starts/stops firmware capture tasks, and refills firmware MDLs through a workqueue.

Important APIs: `cx18_streams_setup`, `cx18_streams_register`, `cx18_streams_cleanup`, `cx18_start_v4l2_encode_stream`, `cx18_stop_v4l2_encode_stream`, `cx18_stop_all_captures`, `cx18_stream_rotate_idx_mdls`, `cx18_out_work_handler`, `cx18_find_handle`, and `cx18_handle_to_stream`. Internal helpers include stream metadata tables, vb2 queue callbacks, `cx18_vbi_setup`, `cx18_stream_configure_mdls`, and `_cx18_stream_load_fw_queue`.

Control flow: setup iterates stream types, prepares devices based on card capabilities and buffer settings, allocates DVB state for TS streams, initializes vb2 only for YUV, and allocates queue buffers. Registration exposes V4L2 nodes and DVB adapters. Capture startup creates a firmware task, sets channel type, configures shared encoder parameters, sets VBI and index options, applies cx2341x controls, sets MDL ack offsets, configures stream MDL size, loads MDLs to firmware, and issues `CX18_CPU_CAPTURE_START`. Stop sets stopping flags, issues firmware stop/release/destroy commands, decrements capture counters, disables busy state, and wakes waiters.

State and dependencies: stream flags, handles, queue depths, vb2 capture lists, timers, atomic `ana_capturing` and `tot_capturing`, firmware task handles, and SCB MDLs are all volatile. Dependencies include cx18 queue, mailbox/API, V4L2 core, vb2, cx2341x controls, cx25840 subdev VBI configuration, and cx18 DVB support. Risks center on shared firmware parameters between capture channels, correct capture counter balancing, failure unwinding, timer/list locking, and YUV/VBI MDL sizing. Test signals include device node registration, concurrent analog stream starts, VBI mode changes, IDX recycling under load, vb2 streamon/streamoff, DVB TS registration, and firmware error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-streams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-streams.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-streams.h

Purpose: exposes cx18 stream lifecycle, firmware queue submission, and handle lookup helpers to the rest of the driver. It is the compact public contract for stream setup/teardown and capture start/stop.

Important APIs: `cx18_find_handle`, `cx18_handle_to_stream`, `cx18_streams_setup`, `cx18_streams_register`, `cx18_streams_cleanup`, `cx18_stream_rotate_idx_mdls`, `cx18_stream_enabled`, `cx18_stream_load_fw_queue`, `cx18_stream_put_mdl_fw`, `cx18_out_work_handler`, `cx18_start_v4l2_encode_stream`, `cx18_stop_v4l2_encode_stream`, and `cx18_stop_all_captures`.

Control flow/integration: callers return completed MDLs with `cx18_stream_put_mdl_fw`, which places them on `q_free` and schedules work to hand them back to firmware. `cx18_stream_enabled` unifies V4L2, DVB, and IDX enablement checks. Capture users call start/stop through these declarations.

State and risks: inline helpers hide asynchronous workqueue behavior, so callers must not assume immediate firmware ownership after queueing. Test signals are correct queue refilling, handle lookup after task creation/destruction, and disabled stream short-circuit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-streams.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-vbi.c

Purpose: post-processes CX23418 Vertical Blank Interval buffers returned from firmware. It converts raw byte-swapped VBI frames into user-facing raw VBI data, decodes sliced VBI through the AV subdevice, and optionally prepares MPEG private stream payloads for insertion.

Important functions: `cx18_process_vbi_data`, `_cx18_process_vbi_data`, `compress_raw_buf`, `compress_sliced_buf`, and `copy_vbi_data`. It uses `cx18_buf_swap`, `cx18_raw_vbi`, `v4l2_subdev_call(... decode_vbi_line ...)`, and `cx18_service2vbi`.

Control flow: firmware returns a VBI buffer with a 12-byte header and 32-bit swapped data. Raw mode strips SAV bytes, trims the frame, appends a frame counter, and updates `bytesused`. Sliced mode locates EAV reference codes, asks the AV decoder to decode line services, copies `v4l2_sliced_vbi_data` back into the buffer, ensures at least one empty line, and may build an MPEG private stream packet with line masks and PTS.

State and risks: state lives in `cx->vbi`, including frame counters, decoded line storage, sliced MPEG ring buffers, sizes, and insertion flags. Risks include reliance on one complete VBI frame per buffer, the FIXME that raw compression ignores input size, endian assumptions, malformed headers, and line-count constants differing between 50 Hz and 60 Hz standards. Test signals are raw and sliced VBI captures, closed-caption/teletext decoding, MPEG insertion PTS correctness, and buffer-size fuzzing around short/invalid VBI frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-vbi.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-vbi.h

Purpose: declares the cx18 VBI post-processing interface. `cx18_process_vbi_data` is used when a firmware MDL is returned so VBI stream buffers can be transformed before userspace consumes them. `cx18_used_line` is declared for VBI line filtering support elsewhere in the driver.

Dependencies and integration: the declarations depend on `struct cx18`, `struct cx18_mdl`, and cx18 stream type IDs. The implementation integrates with the queue layer for buffer swapping and with the AV subdevice for sliced VBI decoding.

Risks and tests: correctness depends on stream type filtering and callers only passing complete VBI-frame buffers. Test signals are both raw and sliced VBI capture paths and builds that verify all declared symbols are defined by the wider cx18 driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-vbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-version.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-version.h

Purpose: centralizes the cx18 driver name and version macros. `CX18_DRIVER_NAME` is `"cx18"` and `CX18_VERSION` is `"1.5.1"`.

Integration: these macros are consumed by module metadata, logging, or user-visible driver identification in the cx18 subsystem. The header has a simple include guard and no runtime state.

Risks and tests: the main risk is stale user-visible version reporting if code changes are not reflected here. Test signals are compile coverage and module/device information that reports the expected driver name and version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-video.c

Purpose: routes the active cx18 analog video input through the AV decoder subdevice. It is intentionally narrow and provides one operation, `cx18_video_set_io`.

Control flow: the function reads `cx->active_input`, indexes `cx->card->video_inputs`, and calls `v4l2_subdev_call(cx->sd_av, video, s_routing, video_input, 0, 0)`. It does not change audio routing or persist settings itself.

Dependencies and risks: depends on card input tables from `cx18-cards.h` and a valid `cx->sd_av` subdevice. Invalid `active_input`, missing subdevice, or incorrect board routing tables cause wrong video source selection. Test signals are switching tuner/composite/S-video inputs and verifying the AV decoder receives the expected routing values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-video.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-video.h

Purpose: declares `cx18_video_set_io(struct cx18 *cx)` for analog video input routing. It is included by cx18 code that needs to reapply input routing after device setup or input changes.

Integration and risks: the function contract assumes initialized card input metadata and an AV subdevice. Because the header has no include guard, duplicate inclusion is only safe because it contains a single compatible prototype. Test signals are compile coverage and analog input switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx23418.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx23418.h

Purpose: defines CX23418 firmware command IDs, capture channel IDs, data-exchange commands, audio processor commands, manager task commands, and firmware error codes used by cx18 mailbox/API code and stream startup/stop code.

Important constants: task manager commands `CX18_CREATE_TASK` and `CX18_DESTROY_TASK`; CPU capture commands such as `CX18_CPU_CAPTURE_START`, `CX18_CPU_CAPTURE_STOP`, `CX18_CPU_SET_CHANNEL_TYPE`, `CX18_CPU_SET_RAW_VBI_PARAM`, `CX18_CPU_SET_INDEXTABLE`, `CX18_CPU_SET_VFC_PARAM`; data-exchange commands `CX18_CPU_DE_SET_MDL_ACK`, `CX18_CPU_DE_SET_MDL`, `CX18_CPU_DE_RELEASE_MDL`; channel types for MPEG, IDX, YUV, PCM, VBI, sliced VBI, and TS; and `CXERR_*` return codes.

Control flow/integration: `cx18_start_v4l2_encode_stream` creates CPU capture tasks, sets channel type, configures VBI/index/control state, submits MDL ack offsets and MDLs, starts capture, then stops and destroys tasks through this command namespace. VBI setup and queue loading rely on the documented parameter shapes.

State and risks: this header is a firmware ABI. Any numeric change breaks mailbox communication. Comments document expected input/output argument positions and are essential for call-site correctness. Test signals are mailbox ping/command success, all capture stream types, error-code logging, VBI setup, and firmware data-exchange completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx23418.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/Kconfig

Purpose: defines the kernel configuration entries for the cx23885 PCIe media driver and the optional Altera FPGA CI module.

Important symbols: `VIDEO_CX23885` is a tristate gated by DVB core, V4L2, PCI, I2C, input, sound, and RC core support. It selects audio PCM, I2C bit-banging, tuner/eeprom helpers, videobuf2 DVB and DMA-SG, cx25840, cx2341x, cs3308, and many optional frontend/tuner drivers under `MEDIA_SUBDRV_AUTOSELECT`. `MEDIA_ALTERA_CI` depends on `VIDEO_CX23885` and `DVB_CORE` and selects `ALTERA_STAPL`.

Integration: these symbols control whether `cx23885.o` and `altera-ci.o` are built by the Makefile and whether board support paths can call into optional CI helpers. Risks are missing selected dependencies causing probe/runtime failures or over-selecting frontends. Test signals are allyesconfig/modular builds and probe tests for boards requiring optional demods, tuners, ALSA, RC, or CI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/Makefile

Purpose: declares the build composition for the cx23885 driver and optional Altera CI module.

Important build outputs: `cx23885-objs` links board setup, video, VBI, core, I2C, DVB, CX23417 encoder support, ioctl, IR/input, NetUP init/eeprom, CIMax2, f300, and ALSA support into `cx23885.o`. `obj-$(CONFIG_VIDEO_CX23885)` builds the main module and `obj-$(CONFIG_MEDIA_ALTERA_CI)` builds `altera-ci.o`.

Integration and risks: include paths expose tuner and DVB frontend headers. Object ordering matters for symbol resolution only through the linker, while Kconfig controls optional module presence. Test signals are modular and built-in builds with and without `MEDIA_ALTERA_CI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/altera-ci.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/altera-ci.c

Purpose: supports the Altera FPGA Common Interface module used with NetUP Dual DVB-T/C RF CI cards and provides hardware PID filtering by interposing on DVB demux feed callbacks.

Important types/functions: `struct fpga_internal` shares FPGA state across two CI slots and two PID filters; `struct altera_ci_state` wraps `dvb_ca_en50221`; `struct netup_hw_pid_filter` stores old demux callbacks and filter state. Public exports are `altera_ci_init`, `altera_ci_release`, `altera_ci_irq`, and `altera_ci_tuner_reset`. Internal helpers manage a global `fpga_inode` list keyed by device or demux, CAM memory/control access, slot reset/status/TS control, PID bit programming, and full-TS toggling.

Control flow: init finds or creates shared FPGA state, registers a DVB CA slot, installs PID-filter feed callbacks, enables TS output and interrupts in FPGA registers, and schedules status work. CAM operations serialize on `fpga_mutex`, select address/control registers through the caller-provided `fpga_rw`, and read/write data. IRQ scheduling updates slot present/ready state. Feed start/stop updates PID filter bits, calls original demux callbacks, and treats PID `0x2000` as full transport stream mode.

State and risks: global linked-list lifetime, shared mutex, CI state arrays, overridden demux function pointers, work_struct scheduling, and FPGA register state are volatile. Risks include no explicit global-list lock, release ordering between CI and PID filters, callback restoration, NULL paths in demux lookup, and hardware-specific PID semantics. Test signals are dual-slot CAM insertion/removal, feed start/stop for individual PIDs and full TS, unload/reload, IRQ status updates, tuner reset, and Kconfig disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/altera-ci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/altera-ci.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/altera-ci.h

Purpose: exposes the Altera CI integration contract and MC417/FPGA bit definitions used by cx23885 board setup and DVB code.

Important APIs/types: `ALT_DATA`, `ALT_TDI`, `ALT_TDO`, `ALT_TCK`, `ALT_RDY`, `ALT_RD`, `ALT_WR`, `ALT_AD_RG`, and `ALT_CS` describe bus bits. `struct altera_ci_config` carries main device pointer, DVB adapter, demux, and `fpga_rw` callback. When `CONFIG_MEDIA_ALTERA_CI` is reachable, `altera_ci_init`, `altera_ci_release`, `altera_ci_irq`, and `altera_ci_tuner_reset` are externs; otherwise inline stubs warn and return success-like values.

Integration and risks: board code can compile regardless of optional module availability, but disabled stubs mean CI hardware will not work. The `void *` contract puts type safety on callers. Test signals include builds with CI as built-in, module, and disabled, plus NetUP board CAM/tuner reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/altera-ci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cimax2.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cimax2.c

Purpose: supports CIMax2 SP2 Common Interface hardware on NetUP-style cx23885 DVB-S2 CI boards. It bridges DVB CA EN50221 operations to I2C configuration registers and MC417 GPIO data/address cycles.

Important APIs: exported CI accessors `netup_ci_read_attribute_mem`, `netup_ci_write_attribute_mem`, `netup_ci_read_cam_ctl`, `netup_ci_write_cam_ctl`, `netup_ci_slot_reset`, `netup_ci_slot_shutdown`, `netup_ci_slot_ts_ctl`, `netup_ci_slot_status`, `netup_poll_ci_slot_status`, `netup_ci_init`, and `netup_ci_exit`. Internal helpers wrap bounded I2C read/write, MC417 ACK polling, CAM bus cycles, IRQ mode programming, and workqueue status updates.

Control flow: init allocates `netup_ci_state`, selects I2C address by transport port, writes a 34-byte CIMax init table, locks/powers slots, registers one DVB CA slot, initializes work, and schedules status. CAM access switches memory/control mode over I2C when needed, writes address bytes through MC417 GPIO under `dev->gpio_lock`, selects the chip, toggles RD/WR, and reads data after ACK. IRQ handling schedules work for GPIO0/GPIO1; work handles FR/DA IRQs and polls insertion/removal at most once per second.

State and risks: state includes current CI flag, current IRQ mode, cached slot status, next poll time, and `port->port_priv`. Risks include I2C transfer errors, 1 ms MC417 ACK timeout, missing work cancellation in exit, mutex-less `ca_mutex` unused, and hardware timing sensitivity. Test signals are CAM attribute/control IO, slot reset, TS enable, insertion/removal IRQs, poll-open IRQ mode changes, and unload after active CA use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cimax2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cimax2.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cimax2.h

Purpose: declares the CIMax2/NetUP CI functions used by cx23885 DVB and interrupt code.

Important APIs: CAM attribute/control memory accessors, slot reset/shutdown/TS control, IRQ status handler, poll status helper, `netup_ci_init`, and `netup_ci_exit`. The header includes DVB CA EN50221 definitions and relies on `struct cx23885_dev` and `struct cx23885_tsport` from the main driver.

Integration and risks: this is the public boundary between the main cx23885 transport-port logic and CIMax2 hardware support. Missing initialization leaves `port_priv` unset and IRQ paths unsafe. Test signals are compile coverage and CI init/exit plus slot-status interrupt paths on NetUP/DVBSky CI boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cimax2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-417.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-417.c

Purpose: supports CX23417 MPEG encoder chips connected through the cx23885 MC417 host port. It implements low-level MC417 register/memory cycles, firmware loading and mailbox commands, cx2341x control integration, and a V4L2 MPEG capture device backed by vb2 DMA-SG buffers.

Important APIs: `cx23885_mc417_init`, `mc417_register_write/read`, `mc417_memory_write/read`, `mc417_gpio_set/clear/enable`, `cx23885_417_check_encoder`, `cx23885_417_register`, and `cx23885_417_unregister`. Internal pieces include firmware mailbox access (`cx23885_mbox_func`, `cx23885_api_cmd`), mailbox discovery, firmware upload verification, codec setup, vb2 queue callbacks, V4L2 ioctl handlers, and the MPEG video-device template.

Control flow: registration only proceeds when board port B is `CX23885_MPEG_ENCODER`. It initializes cx2341x controls, allocates a V4L2 device, initializes vb2 queue parameters, registers the node, and pre-initializes firmware. Streaming start initializes or pings firmware, loads firmware if needed, finds the mailbox, programs video size/rate/VBI/audio/input settings, starts encoder capture, then starts cx23885 DMA on the TS port. Streaming stop sends `CX2341X_ENC_STOP_CAPTURE`, checks sequence-end status, and cancels buffers.

State and risks: state includes module buffer parameters, `dev->cx23417_mailbox`, firmware memory, GPIO state restored around firmware load, `dev->cxhdl`, `dev->v4l_device`, and `dev->vb2_mpegq`. Risks include strict firmware size/magic requirements, slow bytewise MC417 firmware transfer, mailbox timeout/signature corruption, hardcoded port assumptions, limited VBI configuration, and error unwinding after vb2/video registration. Test signals include firmware request failure, checksum validation, first stream stability, V4L2 MPEG ioctls, streamon/streamoff, tuner/input/std controls, and suspend/unload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-417.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-alsa.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-alsa.c

Purpose: implements ALSA PCM capture for cx23885 analog audio. It allocates vmalloc-backed audio buffers, maps them as scatter-gather DMA, builds a RISC program, controls the audio SRAM DMA channel, handles audio IRQs, and registers an ALSA capture card.

Important APIs: `cx23885_audio_register`, `cx23885_audio_unregister`, and `cx23885_audio_irq`. Internal callbacks include DMA init/map/unmap/free, `cx23885_start_audio_dma`, `cx23885_stop_audio_dma`, `dsp_buffer_free`, PCM open/hw_params/hw_free/trigger/pointer/page, and PCM device creation.

Control flow: registration creates an ALSA card unless disabled or SRAM channel config is missing. PCM open constrains period count to powers of two and fixes hardware parameters to 48 kHz, stereo, S16_LE with period size tied to FIFO lines. `hw_params` allocates a buffer, maps pages, creates a RISC databuffer, and exposes `dma_area`. Trigger start programs SRAM channel, audio length/mode/counter, interrupt masks, PCI interrupt mask, and RISC/FIFO enable bits. IRQs acknowledge status, handle opcode/sync errors, update period count from hardware, and call `snd_pcm_period_elapsed`.

State and risks: state lives in `cx23885_audio_dev`, `cx23885_audio_buffer`, SG mappings, RISC DMA memory, atomic count, ALSA runtime DMA pointers, and hardware interrupt masks. Risks include vmalloc_to_page failures, SG mapping failures, exact FIFO/period-size assumptions, no NULL guard in unregister, and IRQ status races during trigger stop. Test signals are ALSA open/close, mmap/read capture, xrun/period timing, sync/opcode error paths, module parameter disabling, and unload after active PCM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-alsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-av.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-av.c

Purpose: handles deferred AV-core interrupt work for cx23885 devices. It is used when the PCI interrupt path schedules work for cx25840/flatiron audio-video subdevice handling.

Important API: `cx23885_av_work_handler(struct work_struct *work)`. It obtains `struct cx23885_dev` from `cx25840_work`, calls the cx25840 subdevice `interrupt_service_routine` with `PCI_MSK_AV_CORE`, falls back to clearing flatiron left/right ADC interrupt flags when unhandled, and re-enables the AV core PCI interrupt.

State and risks: state is hardware interrupt state plus the subdevice `handled` result. Risks include interrupt storms if neither cx25840 nor flatiron status is cleared, NULL subdevice assumptions, and re-enabling interrupts too early. Test signals are AV-core interrupt handling on analog boards, flatiron ADC interrupt fallback, and IR-over-AV-core boards that share this mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-av.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-av.h

Purpose: declares `cx23885_av_work_handler` and guards the AV support interface for cx23885. The handler is wired into `struct cx23885_dev` workqueue setup elsewhere.

Integration and risks: consumers need `struct work_struct` visible before inclusion. The declaration is small but important for interrupt work compilation. Test signals are build coverage and AV interrupt work scheduling on boards using cx25840 or integrated IR through the AV core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-av.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-cards.c

Purpose: is the main board database and board-specific setup layer for cx23885. It maps PCI subsystem IDs to board models, declares per-board port/input/tuner/CI capabilities, interprets EEPROMs, performs reset and GPIO sequencing, configures transport port defaults, loads AV and auxiliary subdevices, initializes NetUP/Altera firmware, and sets up IR support.

Important data/functions: `cx23885_boards`, `cx23885_bcount`, `cx23885_subids`, `cx23885_idcount`, `cx23885_card_list`, `hauppauge_eeprom`, `viewcast_eeprom`, `tbs_card_init`, `cx23885_tuner_callback`, `cx23885_gpio_setup`, `cx23885_ir_init`, `cx23885_ir_fini`, `cx23885_ir_pci_int_enable`, `netup_jtag_io`, and `cx23885_card_setup`.

Control flow: probe code chooses a board from subids or module option, then setup reads EEPROM when available, logs validated Hauppauge/ViewCast model data, configures TS port mode/register defaults by board, optionally bit-bangs TBS SPI init, resets demods/tuners/CAM chips through GP0 or MC417 GPIOs, loads cx25840 AV core firmware for analog or IR-dependent boards, creates cs3308 audio subdevices for ViewCast boards, initializes NetUP hardware, and for NetUP DVB-T/C RF requests Altera firmware and configures the FPGA through JTAG. IR init chooses between cx23888 IR, AV-core IR pins, or external `ir-kbd-i2c`, gated by `enable_885_ir` for risky integrated IR paths.

State and risks: this file mutates `dev->board`, port settings, tuner metadata, `sd_cx25840`, `sd_ir`, EEPROM-derived logging, GPIO registers, MC417 registers, interrupt masks, and firmware-loaded FPGA state. Risks are high because board-specific GPIO mistakes can hold tuners/demods in reset, cause interrupt storms, or damage unsupported IR wiring. Other risks include stale board tables, incomplete EEPROM model handling, firmware absence, missing release of requested firmware on error paths, and hardcoded module parameters such as `netup_card_rev`. Test signals are per-board probe, EEPROM parsing, analog input routing, DVB frontend attach success, CI CAM operation, IR receive/transmit, GPIO reset sequencing, and unknown-board fallback list output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-cards.c -->
