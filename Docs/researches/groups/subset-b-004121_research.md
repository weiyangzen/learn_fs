# Research: subset-b-004121

Grouped source research for subset B work item `subset-b-004121`. Each section preserves the source path and can be split into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-ioctl.c

## Purpose
This file implements the V4L2 ioctl surface for the ivtv Conexant CX2341x MPEG encoder/decoder driver. It translates userspace controls for video/audio routing, TV standards, tuner frequency, capture/output formats, encoder and decoder commands, OSD overlay/framebuffer attributes, sliced/raw VBI, passthrough, and private YUV DMA into ivtv internal state and firmware mailbox calls.

## Important APIs, Types, and Functions
Externally visible helpers include `ivtv_service2vbi`, `ivtv_expand_service_set`, `ivtv_get_service_set`, `ivtv_set_osd_alpha`, `ivtv_set_speed`, `ivtv_set_funcs`, `ivtv_s_std_enc`, `ivtv_s_std_dec`, `ivtv_do_s_frequency`, and `ivtv_do_s_input`. The file defines the `v4l2_ioctl_ops` table and many per-ioctl handlers for format get/try/set, standard/frequency/input/output, encoder/decoder command, framebuffer, selection, event subscription, and default private ioctls.

## Control Flow
Most calls enter through `video_ioctl2` and dispatch through `ivtv_ioctl_ops`. Format handlers normalize V4L2 structures, clamp geometry to hardware limits, and reject changes while capture or decode is active. Decoder commands route through `ivtv_video_command`, which validates speed, output mode, pause/resume state, and calls stream start/stop helpers. Encoder commands call capture start/stop or pause/resume firmware APIs. Standard changes split into encoder and decoder paths: encoder state updates capture dimensions/VBI layout and calls video subdevices, while decoder standard changes wait for a safe vsync window before programming firmware and display rectangles.

## State and Persistence Behavior
The file mutates persistent per-card state in `struct ivtv`: active input/output, audio input, tuner standard, `std`/`std_out`, 50/60 Hz booleans, capture dimensions, VBI formats, `main_rect`, YUV playback settings, OSD alpha/chroma key flags, output mode, playback speed, program index read cursor, and stream/device capabilities. It also sets or clears internal flags for paused decode/encode and updates firmware state through cached mailbox commands.

## Dependencies and Integration Points
It depends on V4L2 ioctl, event, control, and subdev APIs; ivtv stream lifecycle, fileops, queue, VBI, routing, YUV, GPIO, controls, cards, and mailbox layers; cx2341x MPEG control helpers; tuner/video/audio subdevices; SAA7127 OSD/video output routing; and private ivtv UAPI commands such as `IVTV_IOC_DMA_FRAME` and `IVTV_IOC_PASSTHROUGH_MODE`.

## Risks
The high-risk areas are lock ordering around `serialize_lock` when waiting on DMA or vsync, rejecting mutable settings while streams are active, speed conversion edge cases, private ioctl output-mode ownership, and VBI service-line normalization across PAL/NTSC. Firmware calls can fail or hang if issued outside expected decoder timing. OSD framebuffer state must remain coherent with `ivtvfb` and YUV tracking state.

## Test Signals
Useful signals include V4L2 compliance for all node types, format clamp tests for MPEG/YUV/raw VBI/sliced VBI, input/frequency/standard switching while idle and busy, decoder speed/pause/resume/stop tests, EOS and vsync event delivery, private YUV DMA frame tests, OSD overlay flag/alpha/chroma-key checks, and log-status output under active streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-ioctl.h

## Purpose
This header exposes the ivtv ioctl helper interface shared by stream setup, VBI handling, routing, controls, and other ivtv modules.

## Important APIs, Types, and Functions
It forward-declares `struct ivtv` and declares helpers for VBI service conversion and expansion, OSD alpha programming, decoder speed changes, installation of V4L2 ioctl ops, encoder/decoder standard programming, tuner frequency changes, and input selection.

## Control Flow
There is no executable flow in the header. It allows callers to invoke the implementation in `ivtv-ioctl.c` without pulling in that file's private ioctl dispatch table.

## State and Persistence Behavior
The header stores no state. The declared functions mutate `struct ivtv` state, V4L2 video-device ioctl hooks, firmware OSD state, tuner routing, standard flags, and stream dimensions in the implementation.

## Dependencies and Integration Points
It depends on V4L2 types such as `struct v4l2_sliced_vbi_format`, `struct video_device`, `v4l2_std_id`, `struct v4l2_frequency`, and `struct ivtv_stream`. Consumers include stream registration, VBI conversion, and driver init code.

## Risks
Signature drift would break cross-file ivtv integration. Callers must respect the implementation's locking and active-stream restrictions because the prototypes do not encode those requirements.

## Test Signals
Build coverage catches declaration mismatches. Runtime signals come from ioctl paths that call the declared helpers: stream registration, standard switching, input/frequency switching, speed control, and VBI format expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-irq.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-irq.c

## Purpose
This file handles ivtv hardware interrupts, DMA/PIO scheduling, completion processing, VBI/YUV/PCM deferred work, and DMA timeout recovery. It converts firmware mailbox interrupt data into buffer queue movement and stream wakeups.

## Important APIs, Types, and Functions
Public entry points are `ivtv_irq_handler`, `ivtv_irq_work_handler`, `ivtv_dma_stream_dec_prepare`, and `ivtv_unfinished_dma`. Key internals include `stream_enc_dma_append`, `dma_post`, encoder/decoder DMA start helpers, IRQ-specific handlers for DMA read/write completion/errors, encoder start capture, VBI capture/reinsert, decoder data requests, and vsync processing.

## Control Flow
The top-half IRQ handler reads and masks interrupt status, clears handled bits, dispatches DMA, capture, decoder, EOS, and vsync events, then round-robins pending DMA or PIO streams when the engine is idle. DMA preparation builds `sg_pending`, moves buffers through `q_predma`/`q_dma`, starts the hardware transfer, and arms a timeout. Completion handlers sync DMA memory, retry failed segments up to a small limit, post buffers to `q_full` or `q_free`, wake stream waitqueues, and queue kthread work for PIO, VBI, YUV, or PCM handling.

## State and Persistence Behavior
The file mutates `itv->i_flags`, `cur_dma_stream`, `cur_pio_stream`, `dma_retries`, `irq_rr_idx`, `dma_data_req_size`, `dma_data_req_offset`, `last_vsync_field`, and stream scatter-gather state such as `sg_pending`, `sg_processing`, offsets, PTS, and transfer counters. It also maintains buffer queue membership and updates YUV frame scheduling state during vsync.

## Dependencies and Integration Points
It integrates with the queue layer, mailbox data extraction, UDMA, VBI conversion/output, YUV work, ALSA PCM callbacks, kthread work, timers, waitqueues, V4L2 event queues, hardware register accessors, and firmware interrupt mailbox conventions.

## Risks
The file is concurrency-sensitive: hard IRQs, timers, kthread work, DMA callbacks, and userspace waits all share flags and queue state. DMA error handling can race the hardware status register, and the code deliberately avoids clearing certain busy states. Magic-cookie offset correction, VBI piggybacking on MPEG DMA, and PIO fallback are fragile. Missed vsync detection can report `IRQ_NONE` even after doing local work.

## Test Signals
Test with sustained MPEG/YUV/VBI/PCM capture, decoder feed under backpressure, DMA timeout injection, DMA error retry behavior, PIO-only streams, ALSA and V4L2 PCM contention, VBI reinsertion, vsync event delivery, YUV register updates on field changes, and stream stop while DMA is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-irq.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-irq.h

## Purpose
This header defines ivtv interrupt bit values, standard interrupt masks, and the public IRQ/DMA helper entry points.

## Important APIs, Types, and Functions
It exports bit definitions for encoder capture/EOS/VBI/DMA/PIO events, decoder audio/data/DMA/VBI/vsync events, and DMA error/read/write status. It defines `IVTV_IRQ_MASK_INIT`, `IVTV_IRQ_MASK_CAPTURE`, and `IVTV_IRQ_MASK_DECODE`, and declares `ivtv_irq_handler`, `ivtv_irq_work_handler`, `ivtv_dma_stream_dec_prepare`, and `ivtv_unfinished_dma`.

## Control Flow
There is no executable flow. The masks are consumed by driver init, capture/decode start/stop paths, and the IRQ implementation to enable or disable groups of hardware events.

## State and Persistence Behavior
The header stores no state. Its constants control persistent hardware interrupt mask state in `itv->irqmask` and transient DMA scheduling state in the implementation.

## Dependencies and Integration Points
It integrates with stream lifecycle code, UDMA/YUV decode preparation, the kernel IRQ API, timer callbacks, and hardware register definitions from the core driver.

## Risks
Incorrect bit definitions or mask composition can lose DMA completions, flood IRQs, or leave capture/decode paths stalled. Callers must use the capture and decode masks in the right lifecycle phase.

## Test Signals
Build coverage catches signature drift. Runtime signals include clean IRQ enable/disable transitions during init, start/stop capture, start/stop decode, YUV playback, and DMA timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-mailbox.c

## Purpose
This file implements the mailbox transport used to send CX2341x encoder, decoder, and OSD firmware API commands. It handles mailbox claiming, command argument/result marshalling, caching idempotent commands, timeouts, special DMA mailbox behavior, and variadic helper wrappers.

## Important APIs, Types, and Functions
Public functions are `ivtv_api`, `ivtv_api_func`, `ivtv_vapi_result`, `ivtv_vapi`, `ivtv_api_get_data`, and `ivtv_mailbox_cache_invalidate`. Internals include `struct ivtv_api_info`, the `api_info` command metadata table, `try_mailbox`, `get_mailbox`, `write_mailbox`, `clear_all_mailboxes`, and `ivtv_api_call`.

## Control Flow
Callers submit a command and arguments. `ivtv_api_call` validates the command, clears unused data words, optionally skips cached commands issued with identical data, chooses the encoder or decoder mailbox region, then either claims a DMA mailbox or searches non-DMA mailboxes. For result commands it polls briefly, then sleeps or delays until firmware marks the mailbox done or a timeout expires, copies result words back, clears flags, and releases the busy bit. `ivtv_api` retries once on busy.

## State and Persistence Behavior
The file mutates firmware mailbox MMIO/shared memory, `mbdata->busy` bits, and `itv->api_cache[cmd]` data and timestamps. Cached commands persist for up to 30 minutes unless invalidated. It can clear all mailbox flags after failure, which resets driver/firmware mailbox ownership state.

## Dependencies and Integration Points
It depends on CX2341x command IDs, ivtv mailbox memory mappings, jiffies/timeouts, MMIO read/write helpers, sleep/delay helpers, and the many ivtv modules that control firmware through `ivtv_vapi` or `ivtv_vapi_result`.

## Risks
Mailbox ownership is central to device liveness. Busy-bit leaks, bad timeout choices, over-aggressive mailbox clearing, or incorrect cache eligibility can desynchronize driver and firmware. DMA commands intentionally do not wait for normal results, so completion is validated by IRQ paths instead.

## Test Signals
Signals include firmware ping/version calls, repeated cached OSD/control calls, high-volume DMA scheduling under load, timeout injection, mailbox busy recovery, invalid command validation, and firmware restart followed by cache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-mailbox.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-mailbox.h

## Purpose
This header declares the ivtv firmware mailbox API and names the DMA mailbox slots.

## Important APIs, Types, and Functions
It defines `IVTV_MBOX_DMA_END` and `IVTV_MBOX_DMA`, and declares the command helpers `ivtv_api`, `ivtv_vapi_result`, `ivtv_vapi`, `ivtv_api_func`, `ivtv_api_get_data`, and `ivtv_mailbox_cache_invalidate`.

## Control Flow
There is no executable logic. Callers use fixed mailbox slots for IRQ-side DMA data extraction and use the helper functions for sleepable firmware commands.

## State and Persistence Behavior
The header stores no state. The declared functions manipulate firmware mailbox memory, command cache timestamps, and mailbox busy bits.

## Dependencies and Integration Points
It depends on `struct ivtv`, `struct ivtv_mailbox_data`, CX2341x mailbox data sizing, and `u32`. It is included by ioctl, stream lifecycle, IRQ, framebuffer, and other firmware-control modules.

## Risks
The DMA slot constants must match firmware layout. `ivtv_api_get_data` is intended for non-sleeping contexts, so callers must not replace it with the sleepable API in IRQ paths.

## Test Signals
Build coverage for all users and runtime testing of DMA interrupt data, OSD calls, encoder/decoder start/stop, and firmware cache invalidation cover this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-mailbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-queue.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-queue.c

## Purpose
This file implements ivtv stream buffer queue management and stream buffer allocation/freeing. It provides byte-counted list queues used by file I/O, DMA preparation, IRQ completion, and stream teardown.

## Important APIs, Types, and Functions
Public functions are `ivtv_buf_copy_from_user`, `ivtv_buf_swap`, `ivtv_queue_init`, `ivtv_enqueue`, `ivtv_dequeue`, `ivtv_queue_move`, `ivtv_flush_queues`, `ivtv_stream_alloc`, and `ivtv_stream_free`. The internal `ivtv_queue_move_buf` performs locked list/accounting transitions.

## Control Flow
Buffers start in `q_free`. Writers fill buffers from userspace, capture DMA moves free buffers into `q_predma`, active DMA moves them to `q_dma`, and completion moves them to `q_full` or back to `q_free`. `ivtv_queue_move` can move a byte target or all buffers and can steal complete transfer groups from another queue when free buffers are exhausted. Allocation creates host SG arrays, a hardware SG element, DMA mappings, and per-stream data buffers.

## State and Persistence Behavior
The file mutates queue list membership and counters (`buffers`, `length`, `bytesused`), buffer fields (`bytesused`, `readpos`, flags, DMA handles, transfer counters), and stream SG pointers/handles. `ivtv_stream_free` unmaps DMA and frees all allocated buffers and SG arrays.

## Dependencies and Integration Points
It depends on Linux list/spinlock APIs, DMA mapping/sync APIs through header helpers, userspace copy helpers, and `struct ivtv_stream` queue fields. It is a core dependency for fileops, IRQ, stream lifecycle, VBI, and decode/encode DMA.

## Risks
Queue counters must stay synchronized with list operations under `qlock`. Stealing buffers from full queues can drop application data; the transfer-counter grouping avoids partial-frame drops but depends on correct `dma_xfer_cnt`. DMA mappings must be unmapped exactly once and SG handles must respect `IVTV_DMA_UNMAPPED`.

## Test Signals
Stress read/write under backpressure, queue stealing during slow readers, stream allocation failure unwinding, DMA and PIO streams, repeated open/close, buffer byteswap for MPEG/VBI, and leak checks for DMA mappings and allocated buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-queue.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-queue.h

## Purpose
This header declares ivtv queue and stream-buffer helpers and defines inline policy for DMA vs PIO use and DMA cache synchronization.

## Important APIs, Types, and Functions
It defines `IVTV_DMA_UNMAPPED` and `SLICED_VBI_PIO`, inline helpers `ivtv_might_use_pio`, `ivtv_use_pio`, `ivtv_might_use_dma`, `ivtv_use_dma`, buffer/stream DMA sync helpers, and prototypes for buffer copy/swap, queue operations, and stream allocation/freeing.

## Control Flow
The inline helpers decide whether a stream can or should use PIO based on stream DMA direction and sliced-VBI policy. Sync helpers gate DMA cache operations so PIO streams skip DMA API calls.

## State and Persistence Behavior
The header stores no state. Its helpers affect DMA synchronization of stream buffers and SG descriptors; implementation functions mutate queues and allocations.

## Dependencies and Integration Points
It depends on `struct ivtv_stream`, `struct ivtv_buffer`, `struct ivtv_queue`, PCI device DMA APIs, and stream type constants. IRQ, fileops, stream setup, VBI, UDMA, and YUV paths rely on its policy helpers.

## Risks
Changing PIO/DMA policy changes interrupt and buffer-flow behavior globally. Sync helpers must be used consistently around CPU and device access or stale/corrupt data can appear.

## Test Signals
Build coverage plus DMA and PIO capture/decode tests, sliced VBI behavior with policy toggled, cache-coherency checks on non-coherent platforms, and allocation/free leak checks validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-routing.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-routing.c

## Purpose
This file centralizes audio and video input/output routing for ivtv cards. It programs board-specific subdevices and GPIO/mux chips based on the current active input, audio input, radio mode, and card wiring tables.

## Important APIs, Types, and Functions
The exported functions are `ivtv_audio_set_io` and `ivtv_video_set_io`. They consume card description structures for audio inputs, radio input, video inputs, muxer hardware, video processors, GPIO, and optional UPD64031A/UPD6408X chips.

## Control Flow
Audio routing chooses the radio input when radio mode is active, otherwise the current audio input, then routes through an optional M52790 muxer and the card's audio decoder. Video routing sends the active video input to the main video subdevice, classifies tuner/S-Video/composite, programs GPIO routing when present, and configures optional UPD64031A/UPD6408X processing paths for tuner, composite, and S-Video variants.

## State and Persistence Behavior
The file does not own long-lived software state, but it applies persistent hardware routing state in subdevices and GPIO chips. It reads `itv->active_input`, `itv->audio_input`, radio flags, and card configuration to decide the routing.

## Dependencies and Integration Points
It depends on V4L2 subdev routing calls, ivtv card tables, GPIO support, MSP3400, M52790, UPD64031A, UPD64083, tuner/video/audio hardware masks, and ioctl input/audio selection paths.

## Risks
Board tables must match physical wiring. Wrong input classification can select the wrong ADC, disable needed 3D Y/C separation, or route audio incorrectly. Radio mode overrides normal audio input and must be cleared by caller lifecycle code.

## Test Signals
Switch all card inputs, verify tuner/composite/S-Video capture, radio audio routing, GPIO routing on affected boards, UPD filter behavior, and input changes while capture is blocked by ioctl busy checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-routing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-routing.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-routing.h

## Purpose
This header declares the ivtv audio/video routing helpers.

## Important APIs, Types, and Functions
It declares `ivtv_audio_set_io(struct ivtv *itv)` and `ivtv_video_set_io(struct ivtv *itv)`.

## Control Flow
There is no executable logic. Input and audio ioctl handlers call these functions after updating `struct ivtv` selection state.

## State and Persistence Behavior
The header stores no state. The implementation programs persistent hardware routing in V4L2 subdevices and board-specific GPIO/mux chips.

## Dependencies and Integration Points
It depends on `struct ivtv` and is included by ioctl and other modules that need to reapply routing after state changes.

## Risks
The function signatures provide no locking contract; callers must serialize routing changes with active-stream restrictions in the ioctl layer.

## Test Signals
Build coverage and runtime input/audio switching across supported board profiles validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-routing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-streams.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-streams.c

## Purpose
This file sets up, registers, starts, stops, and tears down all ivtv V4L2 stream nodes. It maps ivtv stream types to video/radio/VBI devices, buffer/DMA policy, capture/decode firmware setup, VBI setup, passthrough mode, and shared capture/decode counters.

## Important APIs, Types, and Functions
Public functions are `ivtv_streams_setup`, `ivtv_streams_register`, `ivtv_streams_cleanup`, `ivtv_start_v4l2_encode_stream`, `ivtv_stop_v4l2_encode_stream`, `ivtv_start_v4l2_decode_stream`, `ivtv_stop_v4l2_decode_stream`, `ivtv_stop_all_captures`, and `ivtv_passthrough_mode`. Important internals include the V4L2 fops tables, `ivtv_stream_info`, `ivtv_stream_init`, `ivtv_prep_dev`, `ivtv_reg_dev`, `ivtv_vbi_setup`, and `ivtv_setup_v4l2_decode_stream`.

## Control Flow
Setup prepares each stream device according to capability flags and user buffer sizing, allocates queue/DMA buffers, and later registers V4L2 minors. Encoder start initializes firmware DMA block size, digitizer quirks, VBI config, program index memory, MPEG controls, subdevice streaming, interrupt masks, and starts the requested firmware capture subtype. Decode start initializes audio/display/prebuffer/VBI extraction/source settings, starts playback, and unmasks decoder interrupts. Stop paths issue firmware stop commands, optionally wait for EOS or decoder drain, mask interrupts, flush queues, update counters, and queue events.

## State and Persistence Behavior
The file mutates stream `video_device` fields, buffer allocations, stream flags, `capturing` and `decoding` atomics, firmware busy state, VBI encoder/decoder offsets, program index state, output mode, passthrough flags, IRQ masks, and subdevice streaming state. Registered device nodes persist until cleanup.

## Dependencies and Integration Points
It depends on V4L2 video-device registration, ivtv fileops/ioctl/queue/mailbox/IRQ/YUV/VBI/firmware/card layers, cx2341x control setup, subdevice audio/video streaming, and V4L2 EOS events.

## Risks
Start/stop ordering is firmware-sensitive. Shared counters mean one stream can keep capture hardware active while another stops. GOP-end stop waits can time out. Passthrough manipulates both encoder and decoder state and must balance atomics. Device minor calculation depends on MPEG stream registration.

## Test Signals
Open/read/write/poll all nodes, register/unregister with and without OSD, start multiple capture substreams, stop MPEG at GOP end, VBI-only capture, decode drain and immediate stop, passthrough enable/disable, firmware check failures, and cleanup after partial allocation/registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-streams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-streams.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-streams.h

## Purpose
This header declares the ivtv stream lifecycle API for setup, registration, cleanup, capture/decode control, and passthrough mode.

## Important APIs, Types, and Functions
It declares `ivtv_streams_setup`, `ivtv_streams_register`, `ivtv_streams_cleanup`, encoder and decoder start/stop functions, `ivtv_stop_all_captures`, and `ivtv_passthrough_mode`.

## Control Flow
There is no executable flow. Driver probe and remove paths use setup/register/cleanup, while fileops and ioctl paths use the start/stop and passthrough declarations.

## State and Persistence Behavior
The header stores no state. Implementations allocate stream buffers, register V4L2 devices, mutate stream flags and atomics, issue firmware commands, and update IRQ masks.

## Dependencies and Integration Points
It depends on `struct ivtv_stream`, `struct ivtv`, V4L2 stream semantics, and the broader ivtv fileops/ioctl code.

## Risks
Callers must pass stream types appropriate to encode/decode helpers and must hold expected serialization locks where required by implementation paths.

## Test Signals
Build coverage plus stream setup/register/unregister and V4L2 capture/decode/passthrough tests cover the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-streams.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-udma.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-udma.c

## Purpose
This file implements user-memory DMA support for sending userspace buffers to the decoder/OSD side of the ivtv hardware. It pins user pages, handles highmem bounce pages, builds Linux and hardware scatter-gather lists, starts decoder DMA, and unmaps resources.

## Important APIs, Types, and Functions
Public functions are `ivtv_udma_get_page_info`, `ivtv_udma_fill_sg_list`, `ivtv_udma_fill_sg_array`, `ivtv_udma_alloc`, `ivtv_udma_setup`, `ivtv_udma_unmap`, `ivtv_udma_free`, `ivtv_udma_start`, and `ivtv_udma_prepare`.

## Control Flow
Setup computes page span and offsets for the user buffer, pins pages with `pin_user_pages_unlocked`, fills a software scatterlist, allocates/copies bounce pages for highmem pages, maps the SG list for DMA-to-device, converts it into the CX2341x SG array, marks the last element with the interrupt bit, and syncs the SG array for the device. Prepare either starts DMA immediately under `dma_reg_lock` or marks UDMA pending. IRQ completion or callers later unmap SG mappings and unpin pages.

## State and Persistence Behavior
The file mutates `itv->udma` fields: pinned page array, bounce pages, `page_count`, `SG_length`, SG array, SG DMA handle, and UDMA pending/in-progress flags. Bounce pages and the SG array mapping persist across individual transfers until module/card cleanup.

## Dependencies and Integration Points
It depends on Linux GUP, scatterlist, DMA mapping/sync APIs, highmem mapping, ivtv IRQ DMA arbitration, framebuffer writes, and YUV frame DMA paths.

## Risks
Pinned user pages must be released on every error path. Highmem bounce handling copies data before DMA and assumes write-only device direction. SG array bounds depend on caller-provided maximum page capacity. Starting UDMA shares the decoder DMA engine with normal stream DMA, so flag arbitration must be correct.

## Test Signals
Exercise aligned and unaligned userspace buffers, multi-page and single-page transfers, highmem bounce paths where possible, signal interruption while pending, DMA mapping failures, repeated OSD/YUV transfers, and cleanup with active or failed UDMA setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-udma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-udma.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-udma.h

## Purpose
This header declares ivtv user-DMA helpers and inline DMA sync operations for the shared UDMA SG array.

## Important APIs, Types, and Functions
It declares page-info, SG-list, SG-array, setup, unmap, free, alloc, prepare, and start functions. Inline helpers `ivtv_udma_sync_for_device` and `ivtv_udma_sync_for_cpu` synchronize `itv->udma.SGarray` through `itv->udma.SG_handle`.

## Control Flow
There is no standalone flow. Callers allocate the shared SG array, set up a transfer, prepare/start it through the IRQ-arbitrated DMA engine, then unmap after completion.

## State and Persistence Behavior
The header stores no state. The declared implementation mutates pinned pages, SG mappings, DMA handles, and UDMA flags in `struct ivtv`.

## Dependencies and Integration Points
It depends on `struct ivtv`, `struct ivtv_user_dma`, `struct ivtv_dma_page_info`, V4L2/user buffers, DMA APIs, and decoder DMA registers.

## Risks
The sync helpers assume `SG_handle` is valid. Callers must serialize with `itv->udma.lock` and respect UDMA setup/unmap pairing.

## Test Signals
Build coverage, framebuffer DMA writes, YUV frame DMA, pending DMA interruption, and cleanup after mapping errors validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-udma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-vbi.c

## Purpose
This file implements ivtv Vertical Blanking Interval support. It converts raw and sliced VBI capture data, packages sliced VBI for MPEG insertion, decodes reinsertion data from MPEG streams, accepts sliced VBI output data from userspace, and schedules WSS/VPS/closed-caption updates to the video encoder.

## Important APIs, Types, and Functions
Public functions are `ivtv_write_vbi_from_user`, `ivtv_process_vbi_data`, `ivtv_disable_cc`, and `ivtv_vbi_work_handler`. Internal helpers handle VPS/CC/WSS output, parity checks, sliced-line ingestion, MPEG private-stream packaging, ivtv VBI private-format conversion, raw/sliced buffer compression, and passthrough VBI polling.

## Control Flow
Capture-side processing byteswaps hardware buffers, compresses raw SAV-framed lines or decodes sliced VBI lines through the video subdevice, stores at least one sliced record, and optionally builds MPEG insertion packets. Decoder VBI reinsertion byteswaps and converts ivtv private VBI blocks into V4L2 sliced data, then writes the data to output state. The work handler runs outside hard IRQ to push pending WSS, CC, or VPS changes, or in passthrough mode to poll input VBI and mirror it to SAA7127 output.

## State and Persistence Behavior
The file mutates `itv->vbi` payload buffers, frame counters, sliced MPEG ring entries, WSS/VPS/CC payloads and missing counters, and update bits in `itv->i_flags`. Output VBI state persists in the SAA7127 subdevice until changed or disabled.

## Dependencies and Integration Points
It depends on V4L2 sliced VBI formats, video-subdevice `decode_vbi_line` and `g_vbi_data`, SAA7127 VBI output calls, ivtv queue buffer swapping, ioctl service conversion helpers, IRQ deferred work, and stream VBI setup.

## Risks
VBI line numbering differs by standard and field; off-by-one errors break captions/WSS/VPS. The MPEG private format has alignment and linemask special cases. Passthrough missing counters can intentionally keep or clear stale VBI. Buffer byteswapping assumes 4-byte alignment except for the handled decoder offset case.

## Test Signals
Test raw VBI capture, sliced VBI capture in PAL and NTSC, closed caption parity, MPEG VBI insertion/extraction round trips, sliced VBI output from userspace, passthrough WSS/CC mirroring, CC disable, and VBI behavior during stream start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-vbi.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-vbi.h

## Purpose
This header declares ivtv VBI input, conversion, output, and deferred-work helpers.

## Important APIs, Types, and Functions
It declares `ivtv_write_vbi_from_user`, `ivtv_process_vbi_data`, `ivtv_used_line`, `ivtv_disable_cc`, `ivtv_set_vbi`, and `ivtv_vbi_work_handler`.

## Control Flow
There is no executable logic. File write paths, IRQ completion, stream setup, and deferred IRQ work call these helpers to process or emit VBI data.

## State and Persistence Behavior
The header stores no state. The implementation mutates VBI buffers, payload queues, frame counters, update flags, and video-output subdevice state.

## Dependencies and Integration Points
It depends on `struct ivtv`, `struct ivtv_buffer`, V4L2 sliced VBI data, and stream type IDs. It bridges fileops, IRQ, ioctl, and stream lifecycle modules.

## Risks
Declared functions are used across sleepable and deferred contexts; callers must choose the right context and locking because the header does not enforce it.

## Test Signals
Build coverage and end-to-end raw/sliced VBI capture, MPEG insertion/reinsertion, VBI output, and passthrough tests validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-vbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-version.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-version.h

## Purpose
This header centralizes the ivtv driver name and version string.

## Important APIs, Types, and Functions
It defines `IVTV_DRIVER_NAME` as `"ivtv"` and `IVTV_VERSION` as `"1.4.3"`.

## Control Flow
There is no executable flow. The constants are used by capability reporting, logging, module/device naming, and status output.

## State and Persistence Behavior
The header stores no runtime state. The version value is compile-time metadata.

## Dependencies and Integration Points
It is included by ioctl/status and core ivtv code that needs stable driver identity strings.

## Risks
Stale version strings can mislead diagnostics. Driver name changes affect userspace-visible capability data and log parsing.

## Test Signals
Build coverage and `VIDIOC_QUERYCAP`/log-status output confirm the constants are wired into userspace-visible metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-yuv.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-yuv.c

## Purpose
This file implements YUV playback support for cx23415 output. It manages firmware YUV buffer slots, userspace DMA into decoder memory, frame geometry/lacing decisions, cropping/scaling calculations, hardware register programming, vsync-driven display advancement, and cleanup/restoration.

## Important APIs, Types, and Functions
Public symbols are `yuv_offset`, `ivtv_yuv_filter_check`, `ivtv_yuv_work_handler`, `ivtv_yuv_frame_complete`, `ivtv_yuv_setup_stream_frame`, `ivtv_yuv_udma_stream_frame`, `ivtv_yuv_prep_frame`, and `ivtv_yuv_close`. Important internals include `ivtv_yuv_prep_user_dma`, `ivtv_yuv_filter`, horizontal/vertical register handlers, window setup, initialization, next-free frame selection, frame setup, and per-frame UDMA.

## Control Flow
Frame setup chooses a buffer slot, snapshots source/destination geometry, decides progressive/interlaced treatment, and marks whether register updates are needed. UDMA pins Y and UV user planes, builds an SG list targeting the selected decoder YUV buffer and optional blanking region, starts UDMA, waits for completion, unmaps, and advances fill state. Vsync IRQ code advances displayed frame and queues `ivtv_yuv_work_handler`, which clamps/crops against the OSD-visible window and writes horizontal/vertical scaler registers and filters.

## State and Persistence Behavior
The file mutates `itv->yuv_info`: frame indices, frame info rings, old register snapshots, filter selections, OSD tracking geometry, blanking buffer mapping, lacing thresholds/modes, forced-update flags, and running state. It also changes decoder MMIO registers and restores snapshots on close.

## Dependencies and Integration Points
It depends on UDMA helpers, IRQ vsync/decode data request paths, ioctl/private YUV DMA commands, stream decode setup, OSD/framebuffer geometry, decoder memory offsets, and firmware filter tables.

## Risks
The register programming is hardware-specific and full of rounding/fudge factors. Geometry can become invalid after crop/scale and must blank output safely. Y/UV split and blanking offsets must match firmware buffer layout. Cleanup must restore registers so MPEG playback works afterward. UDMA wait logic must handle signals without leaking pinned pages.

## Test Signals
Test private DMA frames, streaming YUV writes, PAL/NTSC output, progressive/interlaced/auto lacing, OSD tracking and panning, extreme crop/scale ratios, invalid tiny windows, repeated start/close register restoration, filter-table validation, and signal interruption during UDMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-yuv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-yuv.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-yuv.h

## Purpose
This header declares YUV playback helpers and hardware constants for cx23415 decoder memory and scaler filter tables.

## Important APIs, Types, and Functions
It defines `IVTV_YUV_BUFFER_UV_OFFSET`, filter-table offsets, update flags, exports `yuv_offset`, and declares YUV filter check, stream frame setup, userspace DMA frame transfer, frame completion, private DMA frame preparation, close, and deferred work handler functions.

## Control Flow
There is no standalone flow. Decode IRQ paths, ioctl handlers, stream fileops, and cleanup code call these functions to feed and display YUV frames.

## State and Persistence Behavior
The header stores no state. The implementation mutates `itv->yuv_info`, decoder registers, UDMA state, and YUV output flags.

## Dependencies and Integration Points
It depends on `struct ivtv`, `struct ivtv_dma_frame`, userspace pointers, and shared constants such as `IVTV_YUV_BUFFERS`. It integrates with IRQ, UDMA, ioctl, and framebuffer OSD tracking.

## Risks
Offset constants and update flags must stay synchronized with hardware and implementation assumptions. Callers must not use YUV helpers without decoder/output support.

## Test Signals
Build coverage, YUV DMA frame tests, vsync-driven display, OSD panning/tracking, filter checks, and cleanup after YUV playback validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-yuv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtvfb.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtvfb.c

## Purpose
This file implements the `ivtvfb` fbdev driver for cx23415 on-screen display memory. It exposes decoder OSD memory as a Linux framebuffer, manages display modes, color maps, panning, blanking, vsync ioctls, large DMA writes, write-combining setup, and restore after firmware restart.

## Important APIs, Types, and Functions
Important structures are `struct osd_info` and `struct ivtv_osd_coords`. Key functions include framebuffer API wrappers for OSD coordinates and framebuffer memory, `ivtvfb_write`, `ivtvfb_ioctl`, `ivtvfb_set_var`, `_ivtvfb_check_var`, `ivtvfb_pan_display`, `ivtvfb_set_par`, `ivtvfb_setcolreg`, `ivtvfb_blank`, `ivtvfb_restore`, `ivtvfb_init_vidmode`, `ivtvfb_init_io`, `ivtvfb_init_card`, callback init/cleanup, and module init/exit.

## Control Flow
Module init finds the ivtv PCI driver and initializes eligible decoder-output cards. Card init checks PAT/write-combining policy, allocates `osd_info`, initializes ivtv firmware, obtains OSD framebuffer base, maps the framebuffer region, sets a default mode, registers fbdev, enables OSD output, allocates UDMA resources, and advertises V4L2 overlay capability. Writes use CPU copy for small/unaligned data and UDMA for large aligned transfers. Mode changes validate fb var settings, program pixel format/flicker/coordinates/window registers, and force YUV register updates.

## State and Persistence Behavior
It stores per-card OSD state in `itv->osd_info`, including physical/virtual framebuffer addresses, write-combining cookie, current mode, palette, blank state, pan offset, fb_info/fix/var data, and display geometry. It updates shared ivtv state such as `osd_video_pbase`, `osd_rect`, V4L2 overlay caps, `ivtvfb_restore`, and `yuv_info` OSD tracking fields.

## Dependencies and Integration Points
It depends on fbdev APIs, ivtv firmware/mailbox/UDMA/card infrastructure, SAA7127 video output, decoder memory mappings, arch write-combining helpers, V4L2 device iteration through the ivtv driver, and YUV overlay state.

## Risks
Mode validation must match hardware limits and TV standard timing. UDMA writes pin userspace pages and share the decoder DMA engine. Cleanup assumes `osd_info` exists for output-capable cards. PAT/write-combining policy can block initialization on x86_64. Framebuffer size is hardcoded to avoid overlap, so firmware/layout changes could invalidate assumptions.

## Test Signals
Test module load/unload with multiple ivtv cards, fbcon/fbset mode changes, 8/16/32 bpp color maps, panning, blank/unblank/powerdown, `FBIOGET_VBLANK`, `FBIO_WAITFORVSYNC`, large aligned and small unaligned writes, firmware restart restore, PAT policy, and V4L2 overlay capability toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtvfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/Kconfig

## Purpose
This Kconfig file defines build-time options for the Mantis/Hopper PCI bridge DVB drivers.

## Important APIs, Types, and Functions
It defines `MANTIS_CORE`, `DVB_MANTIS`, and `DVB_HOPPER`. The card options select frontend/tuner dependencies such as MB86A16, ZL10353, STV0299, LNBP21, STB0899, STB6100, TDA665x, TDA10021, TDA10023, and DVB_PLL when media subdriver autoselection is enabled.

## Control Flow
There is no runtime control flow. Kconfig dependency resolution controls which modules can be built and which helper frontend drivers are selected.

## State and Persistence Behavior
No runtime state is stored. The selected symbols persist in the kernel build configuration and determine object inclusion.

## Dependencies and Integration Points
All options require PCI, I2C, DVB core support, and the core bridge. `MANTIS_CORE` also depends on INPUT and RC_CORE. The symbols feed the local Makefile's `obj-$(CONFIG_...)` rules.

## Risks
Missing `select` dependencies can produce a driver that probes but lacks its frontend. Over-selection can pull unnecessary modules into builds. The help text and dependencies must match actual card support.

## Test Signals
Build matrix coverage for disabled core, core-only, DVB_MANTIS, DVB_HOPPER, built-in vs module, and MEDIA_SUBDRV_AUTOSELECT on/off catches configuration issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/Makefile

## Purpose
This Makefile composes the Mantis/Hopper media PCI bridge objects and maps Kconfig symbols to kernel modules.

## Important APIs, Types, and Functions
It defines object lists for `mantis_core`, `mantis`, and `hopper`, including PCI, DMA, I2C, DVB, HIF/CA/PCMCIA/input, card tables, and per-board frontend files. It adds the DVB frontend include path through `ccflags-y`.

## Control Flow
There is no runtime flow. Kbuild links `mantis_core.o`, `mantis.o`, and `hopper.o` when their configuration symbols are enabled.

## State and Persistence Behavior
No runtime state is stored. Build composition determines which code is present in the kernel or modules.

## Dependencies and Integration Points
It integrates with the media PCI build, local Kconfig symbols, shared Mantis core modules, card-specific implementations, and headers under `drivers/media/dvb-frontends`.

## Risks
Object-list drift can omit required code or link unused/incompatible board files. Shared CA/HIF code lives in core, so card drivers depend on correct module ordering and symbol exports.

## Test Signals
Build tests for each Kconfig combination, module link checks, `modpost` symbol validation, and include-path validation for frontend headers are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_cards.c

## Purpose
This file is the PCI driver for Hopper bridge based DVB cards, currently wiring the Twinhan VP-3028 DVB-T board to the shared Mantis core.

## Important APIs, Types, and Functions
Key elements are module parameter `verbose`, `hopper_irq_handler`, `hopper_pci_probe`, `hopper_pci_remove`, the `hopper_pci_table`, and `hopper_pci_driver`. The probe path uses `struct mantis_pci`, `struct mantis_pci_drvdata`, and `struct mantis_hwconfig`.

## Control Flow
Probe allocates `mantis_pci`, copies PCI/config data, installs the Hopper IRQ handler into the hardware config, initializes core PCI resources, sets stream routing to HIF, initializes I2C, reads the MAC, initializes DMA, and registers DVB. Error paths unwind in reverse. The IRQ handler reads interrupt status/mask, handles GPIF/CA events, UART, RISC DMA blocks, I2C completion, error bits, clears status, and schedules bottom halves or wakes waitqueues.

## State and Persistence Behavior
The driver stores per-device state in `struct mantis_pci`, including interrupt status/mask, GPIF status, busy DMA block, adapter state, RC map, and core subsystem allocations. The global `devs` count assigns device numbers and `verbose` controls logging.

## Dependencies and Integration Points
It depends on PCI module infrastructure, shared Mantis PCI/I2C/DMA/DVB/UART/IOC code, Hopper VP-3028 config, Mantis register access macros, CA/HIF waitqueues/work items, and DVB demux/frontend registration.

## Risks
IRQ handling assumes `mantis->mantis_ca` is valid when IRQ0 fires. Probe error labels must match initialization order; early failures after `mantis_stream_control` jump to PCI teardown without a separate stream undo. Interrupt mask manipulation must be protected by `intmask_lock` for IRQ1. Device count is not decremented on remove.

## Test Signals
PCI probe/remove, IRQ storm handling, I2C completion waits, DMA RISC block delivery, CA IRQ0 events, UART IRQ1 work scheduling, frontend attach through VP-3028 config, and failure injection at each probe stage are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_vp3028.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_vp3028.c

## Purpose
This file provides the board configuration and frontend initialization for the Hopper VP-3028 DVB-T card.

## Important APIs, Types, and Functions
It defines `hopper_vp3028_config` for the ZL10353 demodulator, `vp3028_frontend_init`, and exported `struct mantis_hwconfig vp3028_config` with model/type, TS size, UART parameters, frontend callback, power GPIO, and reset GPIO.

## Control Flow
Frontend init toggles reset low, powers the frontend, waits, deasserts reset, powers on again, waits for hardware stabilization, then calls `dvb_attach(zl10353_attach, ...)` on the Mantis I2C adapter. It returns failure if power-on or frontend attach fails.

## State and Persistence Behavior
The file stores static board configuration only. Runtime state changes are hardware GPIO/power/reset lines and the DVB frontend object attached by the core.

## Dependencies and Integration Points
It depends on the ZL10353 frontend driver, Mantis GPIO/power helpers, Mantis DVB attach flow, and the Hopper PCI table that references `vp3028_config`.

## Risks
The local `fe` parameter is assigned but not stored by this function, so correctness depends on the broader Mantis attach convention. Timing delays and reset/power GPIO definitions are board-specific. Returning `-1` instead of a conventional errno on attach failure can affect diagnostics.

## Test Signals
Probe VP-3028 hardware, validate frontend I2C detection at address 0x0f, tune DVB-T channels, suspend/resume or reset cycles, and inject power/attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_vp3028.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_vp3028.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_vp3028.h

## Purpose
This header declares the VP-3028 board ID and hardware configuration used by the Hopper PCI driver.

## Important APIs, Types, and Functions
It defines `MANTIS_VP_3028_DVB_T` as the board/device ID and declares `extern struct mantis_hwconfig vp3028_config`.

## Control Flow
There is no executable flow. The PCI ID table references the exported config to bind VP-3028 hardware to the frontend initialization data.

## State and Persistence Behavior
The header stores no runtime state. The implementation's static config is shared through this declaration.

## Dependencies and Integration Points
It includes `mantis_common.h` for `struct mantis_hwconfig` and is included by `hopper_cards.c` and `hopper_vp3028.c`.

## Risks
The ID constant and external declaration must match the implementation and PCI table. Wrong IDs prevent board matching or attach the wrong frontend config.

## Test Signals
Build/link coverage and PCI probe of VP-3028 devices validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_vp3028.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ca.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ca.c

## Purpose
This file implements the DVB EN50221 Common Interface adapter for Mantis CAM/CA hardware. It bridges DVB CA callbacks to Mantis host-interface memory/I/O operations, slot reset/status handling, and event-manager lifecycle.

## Important APIs, Types, and Functions
Public functions are `mantis_ca_init` and `mantis_ca_exit`. Internal DVB CA callbacks include attribute memory read/write, CAM control read/write, slot reset, slot shutdown, transport stream control, and slot status polling.

## Control Flow
Initialization allocates `struct mantis_ca`, links it to `struct mantis_pci`, fills the `dvb_ca_en50221` callback table, initializes locks and waitqueues, registers one EN50221 slot with IRQ CAM-change support, and starts the Mantis event manager. Callback reads/writes validate slot 0 and delegate to HIF memory or I/O helpers. Slot reset toggles the PCMCIA reset register, waits, and signals CAM ready. Exit stops the event manager, releases the EN50221 device, and frees state.

## State and Persistence Behavior
The file owns `mantis->mantis_ca`, `ca->en50221`, `ca->ca_lock`, HIF waitqueues, and slot state observed by `mantis_slot_status`. It programs persistent reset state through `MANTIS_PCMCIA_RESET` during slot reset.

## Dependencies and Integration Points
It depends on DVB CA EN50221 core, Mantis HIF/link/register helpers, Mantis event manager, waitqueues, mutexes, and shared `struct mantis_pci` state. Hopper/Mantis IRQ handlers wake CA waitqueues and schedule CA event work.

## Risks
Only slot 0 is supported; callers with other slots receive `-EINVAL`. Error cleanup in init frees `ca` but does not clear `mantis->mantis_ca`, which can leave a stale pointer if later code observes it. Reset timing is fixed and hardware-specific. `mantis_slot_status` trusts event-manager-maintained `slot_state`.

## Test Signals
Insert/remove CAM modules, EN50221 userspace access to attribute and control spaces, slot reset readiness, IRQ CAM-change events, encrypted transport stream enablement, init failure injection, and module unload with active CA users are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ca.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ca.h

## Purpose
This header declares the Mantis Common Interface lifecycle API.

## Important APIs, Types, and Functions
It declares `mantis_ca_init(struct mantis_pci *mantis)` and `mantis_ca_exit(struct mantis_pci *mantis)`.

## Control Flow
There is no executable flow. Mantis core/card initialization calls `mantis_ca_init` when CA support is needed and calls `mantis_ca_exit` during teardown.

## State and Persistence Behavior
The header stores no state. The implementation allocates and frees `mantis->mantis_ca`, EN50221 state, waitqueues, and event-manager resources.

## Dependencies and Integration Points
It depends on `struct mantis_pci` being visible to includers through surrounding Mantis headers. It is part of the core object list and used by card drivers and HIF/CA integration.

## Risks
Callers must pair init and exit and must tolerate init failures. The header does not expose whether CA is optional for a given board.

## Test Signals
Build coverage, CA init/exit during probe/remove, and CAM insertion/removal tests validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ca.h -->
