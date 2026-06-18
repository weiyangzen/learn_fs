# subset-b-004129 grouped research

This grouped report covers the requested Linux media PCI driver files and preserves each source path in its file-level section title. Each section is bounded by the reconciliation markers required by the worker contract.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-core.c

## Purpose
This is the common SAA7146 "budget" DVB support layer used by board-specific TT/Hauppauge/Siemens budget drivers. It allocates the transport-stream DMA buffer, registers the DVB adapter/demux/dmxdev/network frontend plumbing, drives SAA7146 DMA3 capture, dispatches received MPEG-TS packets into the software demux, and exports helper APIs for DEBI access and video-port switching.

## Important APIs, Types, And Functions
The file operates on `struct budget` from `budget.h` and exports `budget_debug`, `ttpci_budget_init`, `ttpci_budget_init_hooks`, `ttpci_budget_deinit`, `ttpci_budget_irq10_handler`, `ttpci_budget_set_video_port`, `ttpci_budget_debiread`, and `ttpci_budget_debiwrite`. Internal capture functions are `start_ts_capture` and `stop_ts_capture`; DVB feed callbacks are `budget_start_feed` and `budget_stop_feed`; registration helpers are `budget_register` and `budget_unregister`. `budget_read_fe_status` wraps the frontend `read_status` callback to gate DMA on frontend lock.

## Control Flow
Probe-side callers allocate `struct budget`, set `dev->ext_priv`, and call `ttpci_budget_init`. Initialization selects DMA width/height from board type, clamps the `bufsize` module parameter, registers the DVB adapter, sets SAA7146 DD1/GPIO/I2C state, parses EEPROM MAC, allocates a vmalloc DMA buffer with an SAA7146 page table, initializes VPE bottom-half work, powers the frontend, and registers DVB demux devices. `ttpci_budget_init_hooks` replaces the frontend `read_status` with `budget_read_fe_status`. When demux feeds start, `budget_start_feed` increments `feeding`; capture starts only when a feed exists and `fe_synced` is true. IRQ10 queues `vpeirq`, which syncs the SG buffer for CPU, computes the DMA write pointer from `PCI_VDP3`, slices complete 188-byte packets, and sends them to `dvb_dmx_swfilter_packets`. Feed stop, frontend unlock, deinit, or video-port changes stop/restart DMA as needed.

## State And Persistence
All state is runtime-only kernel driver state: buffer geometry, `feeding`, `fe_synced`, circular DMA pointer `ttbp`, warning counters, DVB adapter/demux objects, I2C adapter, and page table. No persistent storage is written. `feedlock` serializes feed/capture transitions and `debilock` serializes DEBI register transactions. The DMA buffer is explicitly zeroed before capture starts and freed during deinit.

## Dependencies And Integration Points
The file depends on the SAA7146 media bridge API, Linux DVB core (`dvb_register_adapter`, `dvb_dmx_init`, `dvb_dmxdev_init`, `dvb_net_init`), I2C core, `ttpci-eeprom` MAC parsing, workqueues, DMA sync APIs, and board-specific modules that attach a frontend. Its exported symbols are shared by sibling `budget*.c` drivers.

## Risks
Capture correctness depends on frontend lock transitions; a frontend driver whose `read_status` behavior changes can leave DMA stopped or running at the wrong time. Buffer sizing and SAA7146 register programming vary by board type and video port, so regressions are hardware-specific. `vpeirq` silently returns if the DMA pointer is outside the buffer. Overrun detection is only a warning based on the consumed span. DEBI helpers return `0` for invalid counts, which can be ambiguous with a valid read value.

## Test Signals
Useful signals are successful DVB adapter registration, I2C frontend detection by board-specific drivers, valid MPEG-TS demux output under `dvb_dmx_swfilter_packets`, absence of repeated ">80% of buffer" warnings, correct DMA stop on frontend unlock/feed stop, and successful unload without workqueue or DMA mapping leaks. Hardware tests should exercise Activy, DVB-C, and default TS-width paths plus video-port switching while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget.c

## Purpose
This is the board-specific driver for SAA7146 budget DVB PCI cards without analog input or CI. It binds PCI subsystem IDs to `budget_info`, attaches demodulator/tuner/LNB helper drivers over the I2C adapter created by `budget-core.c`, implements GPIO-driven DiSEqC/tone/voltage helpers for selected boards, and registers the SAA7146 extension.

## Important APIs, Types, And Functions
The attach/detach entry points are `budget_attach` and `budget_detach`, wired into `struct saa7146_extension budget_extension`. Frontend setup is centralized in `frontend_init`, which switches on `pci->subsystem_device`. Tuner programming helpers include `alps_bsrv2_tuner_set_params`, `alps_tdbe2_tuner_set_params`, `grundig_29504_401_tuner_set_params`, `grundig_29504_451_tuner_set_params`, and `s5h1420_tuner_set_params`. Satellite control helpers include `Set22K`, `SendDiSEqCMsg`, `budget_set_tone`, `budget_diseqc_send_master_cmd`, `budget_diseqc_send_burst`, and `SetVoltage_Activy`. The file defines many frontend config structures for VES, STV, L64781, TDA, S5H, LNBP/ISL/LNBH companion chips.

## Control Flow
Module load registers the SAA7146 extension. On PCI match, `budget_attach` allocates `struct budget`, stores it in `dev->ext_priv`, calls `ttpci_budget_init`, then calls `frontend_init`. `frontend_init` tries the appropriate demod/tuner chain for the subsystem ID, often probing alternate demods in order, mutating frontend ops for tuner `set_params`, tone, DiSEqC, voltage, and firmware callbacks. If a chain succeeds, it registers the frontend on the DVB adapter; otherwise it logs the vendor/device/subsystem tuple. Detach unregisters and detaches the frontend, calls `ttpci_budget_deinit`, frees the budget object, and clears `ext_priv`.

## State And Persistence
The persistent board identity is the PCI subsystem ID table; runtime state lives in `struct budget` and in frontend private data such as `tuner_priv`. Module parameters are `diseqc_method` and `adapter_nr`. GPIO lines are used as hardware state for tone, DiSEqC, voltage, and reset sequencing, but nothing is persisted outside hardware registers.

## Dependencies And Integration Points
This file is a hub for many DVB frontend modules: `stv0299`, `ves1x93`, `ves1820`, `l64781`, `tda8083`, `s5h1420`, `tda10086`, `tda826x`, `lnbp21`, `stv6110x`, `stv090x`, `isl6423`, and `lnbh24`. It depends on the common exported APIs from `budget-core.c`, SAA7146 PCI extension registration, Linux I2C transfers, firmware loading for TDHD1, and DVB frontend registration.

## Risks
The switch table encodes many historical boards and fallback probes; incorrect ordering can attach the wrong frontend. GPIO timing for DiSEqC and reset uses busy waits and sleeps and is hardware-revision sensitive. Some configs, notably `tt1600_stv090x_config`, are mutated after tuner attach, so shared static config state can be surprising across devices. Error paths detach partially constructed frontends, but companion attach failures must be checked carefully to avoid dangling frontend ops.

## Test Signals
Test by loading the module on each supported subsystem ID and checking frontend registration, tuner lock, DiSEqC/tone/voltage behavior, and MPEG-TS streaming through the core demux. Logs should show expected tuner-detection messages and no "Frontend registration failed" or missing LNB/tuner errors. For TT S2/Omicom paths, validate STV090x/STV6110x plus LNB controller attachment and repeated tune cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget.h

## Purpose
This header defines the shared object model and exported interface for SAA7146 budget DVB drivers. It gives board-specific modules a common `struct budget`, board type constants, debug macro, helper macro for PCI extension data, and prototypes for initialization, teardown, IRQ, video-port, and DEBI access.

## Important APIs, Types, And Functions
`struct budget_info` stores the human-readable board name and board type. `struct budget` aggregates DVB adapter/device/network/demux/dmxdev frontends, SAA7146 device pointer, I2C adapter, DMA buffer and page table, bottom-half work items, feed/capture state, locks, frontend hooks, and a `priv` pointer. `MAKE_BUDGET_INFO` constructs a `budget_info` plus `saa7146_pci_extension_data` linked to the external `budget_extension`. Public functions include `ttpci_budget_init`, `ttpci_budget_init_hooks`, `ttpci_budget_deinit`, `ttpci_budget_irq10_handler`, `ttpci_budget_set_video_port`, `ttpci_budget_debiread`, and `ttpci_budget_debiwrite`.

## Control Flow
The header itself has no runtime flow, but it defines the contract used by board modules: allocate/own `struct budget`, call the common init, attach a frontend, call hook initialization, then deinitialize through the common teardown. IRQ and DEBI helpers are called from SAA7146 extension callbacks and board-specific hardware helpers.

## State And Persistence
All fields are volatile driver state. Important state fields include `feeding`, `fe_synced`, `video_port`, buffer size/geometry, `ttbp`, warning counters, frontend pointer, original `read_fe_status`, and lock objects. No persistent data format is defined.

## Dependencies And Integration Points
The header includes Linux module/mutex/workqueue APIs, DVB core headers, and `media/drv-intf/saa7146.h`. It is included by common and board-specific budget sources and exports `budget_debug` for the `dprintk` macro.

## Risks
Because `struct budget` is shared across multiple modules, field layout and semantics are cross-file ABI within the kernel build. The macro assumes an in-scope `budget_extension` symbol, which is convenient but implicit. Feed and frontend state fields require callers to respect the locking discipline established in `budget-core.c`.

## Test Signals
Compile coverage is the primary signal for this header: all budget variants should build with the same struct and prototypes. Runtime signals include successful sharing of `dev->ext_priv`, frontend hook replacement through `dvb_adapter.priv`, and absence of lockdep issues around `feedlock`/`debilock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/Kconfig

## Purpose
This Kconfig entry exposes the Techwell TW5864 V4L2 capture/encoder driver as `CONFIG_VIDEO_TW5864`. The help text describes support for TW5864-based multichannel video/audio grabbing and encoding boards, though the listed object set implements H.264 video capture paths in this subset.

## Important APIs, Types, And Functions
The config symbol is `VIDEO_TW5864`, a tristate. It depends on `VIDEO_DEV` and `PCI`, and selects `VIDEOBUF2_DMA_CONTIG`, matching `tw5864-video.c` use of `vb2_dma_contig_memops` and coherent encoder DMA buffers.

## Control Flow
When enabled as built-in or module, the Makefile links `tw5864.o`, whose PCI driver is registered by `module_pci_driver` in `tw5864-core.c`.

## State And Persistence
Kconfig state persists in the kernel build configuration only. It does not create runtime state.

## Dependencies And Integration Points
The entry integrates with the media PCI Kconfig tree and ensures V4L2, PCI, and contiguous videobuf2 support are available before compilation.

## Risks
The help text mentions audio/MJPEG/ADPCM capabilities that are not represented by the current object list, which can overstate runtime functionality. Missing selections for V4L2 controls/events are normally covered by `VIDEO_DEV`, but build changes should be checked if dependencies are refactored.

## Test Signals
Configuration tests should verify `m`, `y`, and disabled builds, and confirm `tw5864.ko` links with `tw5864-core.o`, `tw5864-video.o`, `tw5864-h264.o`, and `tw5864-util.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/Makefile

## Purpose
This Makefile declares the TW5864 module composition. It builds a single `tw5864` driver object when `CONFIG_VIDEO_TW5864` is enabled.

## Important APIs, Types, And Functions
`tw5864-objs` is composed from `tw5864-core.o`, `tw5864-video.o`, `tw5864-h264.o`, and `tw5864-util.o`. `obj-$(CONFIG_VIDEO_TW5864) += tw5864.o` connects the composite object to Kbuild.

## Control Flow
There is no runtime control flow. At build time, Kbuild compiles the listed objects and links them into either a built-in object or `tw5864.ko`.

## State And Persistence
The file contributes only build metadata. It does not define runtime state.

## Dependencies And Integration Points
The object list corresponds to the PCI probe/IRQ implementation, V4L2/vb2 video implementation, H.264 header generation, and indirect register helpers. Any new source file with referenced symbols must be added here.

## Risks
The linked objects must stay consistent with exported prototypes in `tw5864.h`. Adding audio or MJPEG support without updating this list would create unresolved symbols or missing functionality.

## Test Signals
Build `CONFIG_VIDEO_TW5864=m` and confirm the resulting module contains the PCI driver and all helper symbols referenced across the four objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-core.c

## Purpose
This file is the PCI core for the Techwell TW5864 driver. It registers the PCI driver, maps MMIO, initializes V4L2 device state and video subdevices, handles top-level interrupts, schedules H.264 frame bottom halves, and coordinates the single hardware encoder among four inputs.

## Important APIs, Types, And Functions
Key functions are `tw5864_initdev`, `tw5864_finidev`, `tw5864_isr`, `tw5864_h264_isr`, `tw5864_timer_isr`, `tw5864_irqmask_apply`, and `tw5864_interrupts_disable`. The `video_nr` module parameter assigns V4L2 node numbers. The PCI ID table matches vendor Techwell and device `0x5864`. `tw5864_h264_isr` fills `struct tw5864_h264_frame` ring entries; `tw5864_timer_isr` scans inputs for new raw frames and starts an encode request.

## Control Flow
Probe allocates `struct tw5864_dev` with devm, registers a V4L2 device, enables PCI, sets 32-bit DMA, maps BAR0, initializes the spinlock, logs hardware revisions, calls `tw5864_video_init`, and requests a shared IRQ. The ISR reads low/high interrupt status, clears both halves, then dispatches VLC-done and timer interrupts. VLC-done records encoded frame metadata, advances the four-entry H.264 ring if space is available, queues `bh_work`, updates per-input sequence/GOP state, clears `encoder_busy`, programs the next DMA buffer addresses, and acknowledges the PCI/VLC interrupt. Timer interrupts avoid starting a new encode if the encoder is busy, otherwise round-robin over enabled inputs, compare raw frame buffer pointers, and call `tw5864_request_encoded_frame`.

## State And Persistence
Runtime state includes MMIO base, IRQ mask, global spinlock, `encoder_busy`, `next_input`, H.264 DMA ring read/write indices, and per-input sequence/deadline state. Nothing is persisted outside device registers and allocated kernel memory.

## Dependencies And Integration Points
The core depends on PCI, DMA mask setup, V4L2 device registration, `tw5864_video_init/fini`, register macros from `tw5864-reg.h`, workqueues, and bottom-half handling in `tw5864-video.c`.

## Risks
The hardware has one encoder for four channels, so bugs in `encoder_busy` or ring index handling can drop frames or stall all channels. The timer stuck-channel recovery writes `ENC_BUF_PTR_REC1` based on `buf_id + 3`, a hardware-specific workaround. The driver comments document known H.264 quality issues; GOP size 1 is the practical workaround. Interrupt clearing acknowledges all bits, so future interrupt sources need careful dispatch.

## Test Signals
Expected logs include hardware and H.264 core versions plus video node registration. Streaming tests should show round-robin service across four inputs, no repeated "all buffers busy" messages, frame sequence increments, and correct unload after `tw5864_interrupts_disable` and `tw5864_video_fini`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-h264.c

## Purpose
This file generates the software-written H.264 NAL headers that are prepended to encoded payloads produced by the TW5864 hardware encoder. It emits SPS, PPS, and slice headers for baseline-profile D1-style streams and returns tail-bit alignment information needed to join software headers with hardware VLC output.

## Important APIs, Types, And Functions
The public APIs are `tw5864_h264_put_stream_header` and `tw5864_h264_put_slice_header`. Internal helpers implement a simple bitstream writer: `struct bs`, `bs_init`, `bs_len`, `bs_write`, `bs_write1`, `bs_write_ue`, `bs_write_se`, and `bs_rbsp_trailing`. RBSP generators are `tw5864_h264_gen_sps_rbsp`, `tw5864_h264_gen_pps_rbsp`, and `tw5864_h264_gen_slice_head`.

## Control Flow
`tw5864_prepare_frame_headers` in `tw5864-video.c` calls `tw5864_h264_put_stream_header` at the start of each GOP and `tw5864_h264_put_slice_header` for every frame. Header functions write the Annex B start code, NAL type byte, and RBSP-coded fields. SPS fields derive macroblock dimensions from `width` and `height`; PPS encodes QP offsets; slice headers choose I versus P slice based on `frame_gop_seqno`, write frame number and POC, and return any partial byte as `tail`/`tail_nb_bits`.

## State And Persistence
The file is stateless apart from a static four-byte start-code marker. All state is passed in the destination pointer, available space, QP, dimensions, GOP sequence, and tail output parameters.

## Dependencies And Integration Points
It depends on `linux/log2.h` for `ilog2`/`fls`, constants from `tw5864.h` such as `MAX_GOP_SIZE`, and the video path that merges headers with hardware VLC data.

## Risks
The low-level bit writer mostly drops writes when close to the end of the buffer instead of returning detailed errors. Width and height are assumed macroblock-aligned. The SPS/PPS are narrowly tailored to the TW5864 baseline stream parameters; changing resolution modes, GOP limits, profile, or entropy mode would require updating header fields and downstream tail alignment.

## Test Signals
Validate generated H.264 with userspace decoders and bitstream analyzers, especially first-frame SPS/PPS presence, I/P slice NAL types, frame number wrap at `MAX_GOP_SIZE`, QP-dependent PPS values, and clean decode after start-code emulation prevention in the video handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-reg.h

## Purpose
This header is the TW5864 hardware register contract. It maps direct MMIO offsets, indirect decoder/audio/motion-detection registers, and bit fields for the H.264 encoder, sensor interface, DDR, VLC/MV buffers, PCI interrupt bridge, video input decoder, and motion detection blocks.

## Important APIs, Types, And Functions
It is a macro-only file. Major symbol families include `TW5864_EMU`, `TW5864_DSP*`, `TW5864_SLICE`, `TW5864_ENC_BUF_PTR_REC*`, `TW5864_SENIF_ORG_FRM_PTR*`, `TW5864_INTERLACING`, `TW5864_MOTION_SEARCH_ETC`, `TW5864_QUAN_TAB`, `TW5864_FRAME_*`, `TW5864_VLC*`, `TW5864_INTR_*`, `TW5864_H264EN_*`, `TW5864_DDR_*`, `TW5864_PCI_*`, `TW5864_MV*`, and `TW5864_INDIR_*`. Function-like macros compute per-channel register addresses for frame buses, rate controls, video input decoder bytes, picture size, and detection controls.

## Control Flow
There is no executable control flow, but the macros drive all register programming in `tw5864-core.c`, `tw5864-video.c`, and `tw5864-util.c`. Direct registers are accessed through `tw_readl`/`tw_writel`; indirect registers are accessed through `TW5864_IND_CTL`/`TW5864_IND_DATA` helper functions.

## State And Persistence
The file describes hardware state rather than owning state. Persistent effects are writes into TW5864 registers: encoder configuration, DMA base addresses, interrupt masks/status, input standard selection, crop/size settings, DDR behavior, and motion-detection thresholds/masks.

## Dependencies And Integration Points
The header assumes Linux `BIT()` is visible through includers. It is included by `tw5864.h` and directly by implementation files. Its constants are tightly coupled to datasheet behavior and to inferred/undocumented bits noted in comments, such as `TW5864_DSP_INTER_ST`.

## Risks
Many definitions represent reverse-engineered or poorly documented hardware behavior. A wrong shift/mask can corrupt unrelated channels because registers pack per-channel fields. Some address ranges are large and sparse, making debug-register bounds important. Maintaining this file requires checking every user of a field before renaming or changing bit semantics.

## Test Signals
Signals are indirect: successful hardware initialization, valid H.264 output, correct interrupt delivery, stable frame-rate controls, accurate input status reporting, and no register-debug access outside documented direct/indirect ranges. Hardware regression tests should cover all four channel indices to catch packed-field errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-util.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-util.c

## Purpose
This file implements byte-wide indirect register access for TW5864 sub-blocks. The indirect bus is used for video decoder, audio, reset, clock, crop, and motion-detection registers that are not exposed as ordinary direct MMIO offsets.

## Important APIs, Types, And Functions
The public APIs are `tw5864_indir_writeb(struct tw5864_dev *dev, u16 addr, u8 data)` and `tw5864_indir_readb(struct tw5864_dev *dev, u16 addr)`. Callers normally use the `tw_indir_writeb` and `tw_indir_readb` convenience macros from `tw5864.h`.

## Control Flow
Both functions poll `TW5864_IND_CTL` bit 31 until the indirect controller is idle or a retry counter expires. Writes then store the byte in `TW5864_IND_DATA` and issue an indirect write command with address, `TW5864_RW`, and `TW5864_ENABLE`. Reads issue an indirect read command, poll again for completion, and return `TW5864_IND_DATA`.

## State And Persistence
The functions mutate hardware indirect registers and report only timeout errors via `dev_err`. They do not maintain software state or return explicit error codes.

## Dependencies And Integration Points
The implementation depends on `tw5864.h` for `struct tw5864_dev`, direct MMIO helpers, and register constants from `tw5864-reg.h`. It is used by video initialization, controls, standard detection, debug register access, reset, and clock setup.

## Risks
Timeouts are logged but not propagated, so callers may proceed after failed indirect transactions. The polling loop is a tight busy loop with a fixed retry count and no delay. Read returns the full `readl` value truncated to `u8`, which is intended but assumes the data byte is in the low bits.

## Test Signals
Hardware tests should watch for "retries exhausted" logs during probe, control changes, standard detection, and streaming. Successful setting of brightness/contrast/hue/saturation and input standard probing is a practical validation of indirect read/write behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-video.c

## Purpose
This is the TW5864 V4L2 video/H.264 implementation. It initializes encoder tables and DMA buffers, registers one V4L2 capture device per input, configures analog decoder and H.264 encoder registers, manages vb2 queues, assembles software H.264 headers with hardware VLC output, and reports motion-detection events.

## Important APIs, Types, And Functions
Externally used functions are `tw5864_video_init`, `tw5864_video_fini`, `tw5864_prepare_frame_headers`, and `tw5864_request_encoded_frame`. Core vb2 callbacks are `tw5864_queue_setup`, `tw5864_buf_queue`, `tw5864_start_streaming`, and `tw5864_stop_streaming`. Control/ioctl handlers include `tw5864_s_ctrl`, format/std/input/parm handlers, `tw5864_subscribe_event`, and optional advanced debug register access. Frame completion is handled by `tw5864_handle_frame_work` and `tw5864_handle_frame`.

## Control Flow
`tw5864_video_init` allocates four coherent VLC/MV DMA frame buffers, uploads VLC and quantization tables, resets and clocks video input hardware, initializes encoder DMA base addresses, enables sensor/H.264 channels, sets bus maps, starts timer/VLC interrupts, initializes bottom-half work, and registers four video inputs. Streaming starts by enabling an input, choosing D1 geometry, programming indirect picture/crop registers and direct encoder/scaler/rate registers, then setting `enabled`. Timer ISR in the core calls `tw5864_request_encoded_frame`, which writes per-frame encoder state, prepares headers in the next user buffer, programs VLC bit alignment, selects raw/reconstructed buffers, and toggles `START_NSLICE`. VLC-done IRQ queues bottom-half work; the worker syncs coherent buffers, calls `tw5864_handle_frame`, inserts emulation-prevention bytes, sets payload/timestamp/sequence, optionally queues `V4L2_EVENT_MOTION_DET`, and completes the vb2 buffer.

## State And Persistence
Per-input state includes active vb2 list, current buffer, enabled flag, standard, dimensions, sequence counters, GOP/QP/frame interval, H.264 tail bits, register shadow values, current raw-buffer ID, and motion threshold grid. Device state includes the shared H.264 ring and work item. State is runtime-only; hardware registers hold active configuration until reset/unload.

## Dependencies And Integration Points
The file integrates V4L2 ioctls, controls, events, and `videobuf2-dma-contig`; TW5864 core IRQ scheduling; H.264 header helpers; indirect register helpers; and register definitions. Userspace sees H.264 capture devices supporting read, mmap, DMABUF, streaming, controls, frame intervals, and motion events.

## Risks
Only D1 resolution is effectively selected despite enum support for HD1/CIF/QCIF. `tw5864_video_input_init` writes indirect standard registers using `video_nr` rather than `input->nr`, which is notable if requested video node numbers differ from channel numbers. The encoder table upload writes forward then inverse quantization tables to the same base range, which should be verified against hardware expectations. Buffer handling depends on `tw5864_prepare_frame_headers` having reserved a vb2 buffer before VLC completion. Motion detection is heuristic and based on MV data from P-frames only.

## Test Signals
Exercise `v4l2-ctl --stream-mmap`, `--stream-user` is not supported here, read I/O, QP/GOP controls, standard query/set, frame interval changes, motion event subscription, and all four channels simultaneously. Decode output with FFmpeg/GStreamer, check SPS/PPS at GOP starts, verify no "vb is empty" or buffer-space drop logs, and test GOP size 1 for the documented quality workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864.h

## Purpose
This is the shared TW5864 driver header. It defines core device/input/buffer structures, constants for channel count and H.264 buffer sizes, video-standard and resolution enums, MMIO helper macros, indirect-register helper prototypes, and cross-file function prototypes.

## Important APIs, Types, And Functions
Important types are `struct tw5864_buf`, `struct tw5864_dma_buf`, `enum tw5864_vid_std`, `struct tw5864_input`, `struct tw5864_h264_frame`, and `struct tw5864_dev`. Helper macros include `tw_readl`, `tw_writel`, `tw_mask_shift_readl`, `tw_mask_shift_writel`, `tw_setl`, and `tw_clearl`. Function prototypes expose IRQ-mask application, video init/fini, H.264 header generation, frame header preparation, indirect byte access, and encode requests.

## Control Flow
The header has no executable flow. It establishes the structure used by probe in `tw5864-core.c`, streaming and controls in `tw5864-video.c`, H.264 header generation in `tw5864-h264.c`, and indirect register access in `tw5864-util.c`.

## State And Persistence
`struct tw5864_input` stores per-channel runtime state: locks, V4L2 objects, vb2 queue, active buffers, resolution/standard, frame counters, H.264 header tail data, shadow register values, current vb2 buffer, controls, QP/GOP, frame interval, and stuck-frame deadline. `struct tw5864_dev` stores global V4L2/PCI/MMIO state, a four-entry H.264 DMA ring, bottom-half work, encoder arbitration, and IRQ mask. No persistent disk state is represented.

## Dependencies And Integration Points
The header includes Linux PCI, interrupt, workqueue, mutex, MMIO, V4L2, control, and vb2 DMA-SG/contig headers plus `tw5864-reg.h`. It is the integration contract between all TW5864 objects.

## Risks
The MMIO macros depend on a local variable named `dev`, making call sites concise but context-sensitive. Shared structures are accessed from IRQ, workqueue, and userspace ioctl contexts, so lock ownership must remain clear. Constants such as `H264_VLC_BUF_SIZE`, `H264_MV_BUF_SIZE`, `MAX_GOP_SIZE`, and `TW5864_INPUTS` are baked into queue sizes, header generation, and ring logic.

## Test Signals
Build and sparse-style checks should catch prototype drift. Runtime validation should focus on lockdep, all four input structures being initialized and freed, correct DMA address programming from `struct tw5864_h264_frame`, and V4L2 controls mapping into the fields defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/Kconfig

## Purpose
This Kconfig entry exposes the Techwell TW68xx V4L2 frame grabber driver as `CONFIG_VIDEO_TW68`.

## Important APIs, Types, And Functions
`VIDEO_TW68` is a tristate depending on `VIDEO_DEV` and `PCI`. It selects `VIDEOBUF2_DMA_SG`, which matches the driver's scatter-gather vb2 memory model and RISC DMA program generation.

## Control Flow
When enabled, Kbuild links the objects listed in the directory Makefile and `tw68-core.c` registers the PCI driver through `module_pci_driver`.

## State And Persistence
The file contributes build configuration state only.

## Dependencies And Integration Points
It integrates with the media PCI build system and ensures V4L2 and PCI support are available. The selected vb2 SG dependency is consumed by `tw68-video.c`.

## Risks
If the video path's memory model changes, the selected vb2 helper must be updated. The help text is intentionally broad and does not enumerate specific supported PCI IDs, so runtime support is determined by `tw68-core.c`.

## Test Signals
Validate compile coverage for disabled, built-in, and module configurations, and confirm `tw68.ko` links against videobuf2 DMA-SG support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/Makefile

## Purpose
This Makefile defines the TW68 composite module.

## Important APIs, Types, And Functions
`tw68-objs` links `tw68-core.o`, `tw68-video.o`, and `tw68-risc.o`. `obj-$(CONFIG_VIDEO_TW68) += tw68.o` connects the module to the selected config symbol.

## Control Flow
There is no runtime flow; Kbuild uses the object list to construct the driver.

## State And Persistence
The file contains only build metadata.

## Dependencies And Integration Points
The object split mirrors core PCI/IRQ/probe logic, V4L2/vb2 video handling, and RISC DMA program generation.

## Risks
Any new cross-file symbol implementation must be added here or link failures will occur. Removing `tw68-risc.o` would break buffer preparation.

## Test Signals
Build with `CONFIG_VIDEO_TW68=m` and check that all three object files are included in the linked module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-core.c

## Purpose
This file is the PCI core for Techwell TW6800/TW6801/TW6804/TW6816-family capture devices. It registers the PCI driver, initializes hardware registers, maps MMIO, configures DMA/interrupt masks, registers the V4L2 device, and handles suspend/resume.

## Important APIs, Types, And Functions
Key functions are `tw68_initdev`, `tw68_finidev`, `tw68_hw_init1`, `tw68_irq`, `tw68_suspend`, and `tw68_resume`. Module parameters are `latency`, `video_nr`, and `card`. The PCI ID table matches several Techwell devices. It calls video-layer functions `tw68_video_init1`, `tw68_video_init2`, `tw68_irq_video_done`, `tw68_video_start_dma`, and `tw68_set_tvnorm_hw`.

## Control Flow
Probe allocates `struct tw68_dev`, assigns a V4L2 device instance name, registers it, enables PCI, optionally sets the latency timer, logs PCI info, sets bus mastering and 32-bit DMA, determines decoder type and interrupt mask from PCI ID, reserves and maps BAR0, runs `tw68_hw_init1`, requests a shared IRQ, initializes/registers the video device, and enables interrupts. IRQ handling reads `TW68_INTSTAT & pci_irqmask`, loops up to ten times dispatching video interrupt bits to `tw68_irq_video_done`, and disables the interrupt mask if status cannot be drained. Remove stops DMA/FIFO and interrupts, unregisters V4L2 controls/video device, unmaps MMIO, releases the region, and unregisters V4L2. Suspend stops DMA/IRQs and discards done buffers; resume reapplies TV norm and restarts DMA on the active buffer.

## State And Persistence
State is held in `struct tw68_dev`: V4L2 device, decoder type, video device, controls, PCI/MMIO resources, IRQ masks, capture format/size/field, active buffer list, and selected input. Hardware registers hold current decoder/DMA state but are reinitialized on probe.

## Dependencies And Integration Points
The file depends on Linux PCI, PM, DMA mask setup, V4L2 device registration, videobuf2 state through the video layer, and TW68 register macros. It is the lifecycle owner for the video layer.

## Risks
`tw68_resume` assumes `dev->active.next` is a valid buffer and can be unsafe if no buffers are active during resume. Interrupt storms disable the mask after ten loops, which protects the system but can leave capture stopped. Register initialization is manually coded from hardware defaults and comments, so board variants may need tuning. The `card` module parameter is declared but not used in this file.

## Test Signals
Probe logs should show device, revision, IRQ, latency, and registered video node. Streaming should survive interrupt load without "INTERRUPT NOT HANDLED" messages. PM tests should suspend/resume during active and idle capture. Remove/unload should leave no mapped region, IRQ, or V4L2 device leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-reg.h

## Purpose
This header defines TW68xx register offsets, interrupt bits, I2C/SBUS bits, decoder/scaler/control registers, RISC DMA instruction opcodes, video standard IDs, and pixel format encodings.

## Important APIs, Types, And Functions
It is macro-only. Important groups include DMA/interrupt registers (`TW68_DMAC`, `TW68_DMAP_SA`, `TW68_INTSTAT`, `TW68_INTMASK`), video decoder/scaler registers (`TW68_INFORM`, `TW68_OPFORM`, `TW68_CROP_HI`, `TW68_VDELAY_LO`, `TW68_HACTIVE_LO`, `TW68_*SCALE*`), controls (`TW68_BRIGHT`, `TW68_CONTRAST`, `TW68_SAT_U`, `TW68_HUE`), RISC opcodes (`RISC_SYNCO`, `RISC_SYNCE`, `RISC_JUMP`, `RISC_LINESTART`, `RISC_INLINE`), video standards, and `ColorFormat*` encodings.

## Control Flow
The header has no executable flow. Its constants are consumed by `tw68-core.c`, `tw68-video.c`, and `tw68-risc.c` to program reset defaults, construct DMA programs, configure scaling/cropping, handle interrupts, and map V4L2 formats to hardware output formats.

## State And Persistence
The header describes hardware state locations. Writes through these constants persist in device registers until reset or reprogramming.

## Dependencies And Integration Points
It is included by `tw68.h`, making the register map available through the driver's common MMIO helper macros. The RISC instruction constants are shared with the buffer-program generator and queue chaining logic.

## Risks
The direct register space mixes byte and long accesses; using the wrong helper can target wrong byte lanes. RISC instruction bit fields are encoded manually, so changes require matching `tw68-risc.c`. Interrupt bit definitions are used in masks that differ by chip generation.

## Test Signals
Validation is indirect through successful register initialization, correct V4L2 control effects, stable DMA interrupts, and readable debug register dumps. Format tests should verify all `ColorFormat*` mappings produce expected byte order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-risc.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-risc.c

## Purpose
This file builds TW68 DMA RISC programs for scatter-gather vb2 capture buffers. The programs synchronize odd/even fields, issue line DMA instructions across SG boundaries, and chain buffers by jump instructions.

## Important APIs, Types, And Functions
The exported implementation is `tw68_risc_buffer`. The internal generator is `tw68_risc_field`, which emits optional initial jumps, field sync instructions, `RISC_LINESTART`, and `RISC_INLINE` fragments. Disabled debug helpers `tw68_risc_decode` and `tw68_risc_program_dump` document instruction decoding.

## Control Flow
`tw68_buf_prepare` calls `tw68_risc_buffer` with field-specific offsets, bytes per line, padding, and line count. `tw68_risc_buffer` computes a conservative instruction count, allocates coherent DMA memory for the RISC program, emits top and/or bottom field programs, records `buf->jmp`, initializes the leading jump target to `buf->dma + 8`, and asserts that the generated program fits. `tw68_risc_field` walks the SG list, subtracting offsets until it reaches the target segment, then emits either a single line instruction or a fragmented line split across SG entries.

## State And Persistence
The generated program is stored in per-buffer coherent memory tracked by `struct tw68_buf` (`cpu`, `dma`, `jmp`, `size`). It persists for the lifetime of the vb2 buffer and is freed in `tw68_buf_finish`.

## Dependencies And Integration Points
The file depends on `tw68.h`, DMA coherent allocation, SG DMA addresses/lengths, and RISC opcodes from `tw68-reg.h`. `tw68-video.c` mutates `buf->jmp` and the first instruction to chain queued buffers and generate completion interrupts.

## Risks
SG traversal assumes valid SG entries for the requested offsets and line sizes. Instruction sizing is conservative but protected by `BUG_ON`, which is harsh if violated. Fragmented-line emission updates `offset = todo` after the final fragment, which should be reviewed carefully for padding behavior. The debug dump references a disabled `struct tw68_core` type, so it is not build-active.

## Test Signals
Stress capture with small, non-contiguous SG buffers, all supported field modes, and format/size changes that force program regeneration. Watch for DMA errors, PABORT/DMAPERR interrupts, buffer sequence continuity, and absence of coherent allocation leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-risc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-video.c

## Purpose
This file implements the TW68 V4L2 capture device. It defines supported pixel formats and TV norms, programs decoder/scaler/crop registers, manages vb2 DMA-SG queues, chains RISC DMA buffers, handles video controls and ioctls, and completes buffers from video interrupts.

## Important APIs, Types, And Functions
Public functions used by the core are `tw68_set_tvnorm_hw`, `tw68_video_init1`, `tw68_video_init2`, `tw68_irq_video_done`, and `tw68_video_start_dma`. Internal functions include `format_by_fourcc`, `set_tvnorm`, `tw68_set_scale`, queue callbacks (`tw68_queue_setup`, `tw68_buf_queue`, `tw68_buf_prepare`, `tw68_buf_finish`, `tw68_start_streaming`, `tw68_stop_streaming`), control handler `tw68_s_ctrl`, format/std/input handlers, and optional advanced debug register access.

## Control Flow
Initialization first creates V4L2 controls, then `tw68_video_init2` selects PAL defaults, BGR24 720x576 interlaced format, initializes the vb2 DMA-SG queue, and registers the video device. Format ioctls validate pixel format, clamp width/height, choose field mode, and update device capture state. Buffer prepare allocates a RISC program based on field layout. Queueing appends a looping jump to each buffer and, when a previous buffer exists, patches the previous buffer's final jump to the new program and enables an interrupt on the new buffer's first instruction. Streaming starts DMA from the first active buffer. Video interrupts reset handled bits, complete the current buffer on `TW68_DMAPI`, stamp timestamp/field/sequence, and log/reset exceptional FIFO or DMA conditions.

## State And Persistence
Runtime state is held in `struct tw68_dev`: current format, width, height, field, selected norm, input, sequence number, vb2 queue, active buffer list, and IRQ mask. Per-buffer RISC state lives in `struct tw68_buf`. Hardware scaler, decoder, DMA, and control registers hold current capture configuration.

## Dependencies And Integration Points
The file integrates V4L2 ioctls/controls/events, videobuf2 DMA-SG, RISC program generation from `tw68-risc.c`, register macros from `tw68-reg.h`, and lifecycle/IRQ management in `tw68-core.c`.

## Risks
`tw68_start_streaming` assumes the active list contains a buffer, relying on `min_queued_buffers`. `tw68_stop_streaming` walks the active list without taking `slock`, while queueing/IRQ paths use it. Format changes can leave already-active buffers using the previous RISC program until drained, as noted in comments. Debug register access lacks bounds checks. Input switching while active may trigger FDMIS on some chips.

## Test Signals
Exercise all advertised formats and byte orders, norm switching while idle, input switching, mmap/userptr/read/DMABUF paths, single-field and interlaced modes, and stop/start while buffers are queued. Logs should avoid PABORT/DMAPERR and persistent FIFO overflow. Captured frame sizes and colorspace should match V4L2 format ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68.h

## Purpose
This common header defines the TW68 driver's shared data structures, board constants, supported norm mask, interrupt masks, MMIO helper macros, and cross-file function prototypes.

## Important APIs, Types, And Functions
Important types are `enum tw68_decoder_type`, `struct tw68_tvnorm`, `struct tw68_format`, `struct tw68_buf`, `struct tw68_fmt`, and `struct tw68_dev`. Macros include `TW68_NORMS`, video and I2C interrupt masks, board/input limits, `BUFFER_TIMEOUT`, and register access helpers `tw_readl`, `tw_readb`, `tw_writel`, `tw_writeb`, `tw_andorl`, `tw_andorb`, `tw_setl`, `tw_setb`, `tw_clearl`, and `tw_clearb`. Prototypes expose video setup/IRQ/DMA and RISC buffer generation.

## Control Flow
The header has no runtime flow. It binds the core, video, and RISC files around a shared `struct tw68_dev` and helper macro convention where functions operate with a local `dev` pointer.

## State And Persistence
`struct tw68_dev` contains all runtime driver state: mutex/spinlock, instance number, V4L2 objects, decoder type, PCI/MMIO resources, IRQ masks, current capture format/dimensions/field, vb2 queue, active buffer list, controls, and selected input. Per-buffer state includes DMA program memory and jump pointer.

## Dependencies And Integration Points
It includes Linux PCI/MMIO/mutex/delay and V4L2/vb2 headers plus `tw68-reg.h`. It is the shared compile-time contract among `tw68-core.c`, `tw68-video.c`, and `tw68-risc.c`.

## Risks
MMIO helper macros depend on pointer arithmetic with `lmmio` as `u32 __iomem *` for long registers and `bmmio` for byte registers. Incorrect helper use can corrupt registers. Shared active-list and capture-state fields are touched from ioctl, vb2, IRQ, suspend, and resume paths, making locking discipline important.

## Test Signals
Compile checks catch prototype and struct field drift. Runtime lockdep, suspend/resume, streaming, and format-change tests validate that the shared state model is coherent across files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/Kconfig

## Purpose
This Kconfig entry exposes the Intersil/Techwell TW686x video capture driver as `CONFIG_VIDEO_TW686X`, covering TW6864/TW6865/TW6868/TW6869-class boards.

## Important APIs, Types, And Functions
`VIDEO_TW686X` is a tristate depending on `PCI`, `VIDEO_DEV`, and `SND`. It selects `VIDEOBUF2_VMALLOC`, `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_DMA_SG`, and `SND_PCM`, reflecting multiple video DMA modes and ALSA capture support.

## Control Flow
When enabled, Kbuild links `tw686x.o`; `tw686x-core.c` owns PCI registration while this work item covers the audio object linked into that module.

## State And Persistence
The entry persists only in kernel build configuration.

## Dependencies And Integration Points
It integrates media and ALSA dependencies. Audio support in `tw686x-audio.c` requires `SND` and `SND_PCM`; video support requires the selected vb2 allocators.

## Risks
The help text notes some chip variants and channels are untested or partially supported, so enabling the symbol does not guarantee all hardware channels work. Dependency selections are broad because the driver supports configurable DMA modes.

## Test Signals
Build tests should cover module and built-in configurations with ALSA enabled. Runtime tests should verify both `/dev/video*` and ALSA PCM capture devices appear on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/Makefile

## Purpose
This Makefile defines the TW686x composite driver module.

## Important APIs, Types, And Functions
`tw686x-objs` links `tw686x-core.o`, `tw686x-video.o`, and `tw686x-audio.o`. `obj-$(CONFIG_VIDEO_TW686X) += tw686x.o` attaches the module to the Kconfig symbol.

## Control Flow
There is no runtime control flow. Kbuild uses the object list to produce the TW686x module or built-in object.

## State And Persistence
Only build metadata is represented.

## Dependencies And Integration Points
The file ensures the audio implementation researched here is linked with core PCI/IRQ code and the video implementation.

## Risks
If audio or video is made optional inside the driver, this fixed object list would need adjustment. Missing objects cause unresolved references from the shared header prototypes.

## Test Signals
Build `CONFIG_VIDEO_TW686X=m` and confirm `tw686x-audio.o` is present in the resulting module along with core and video objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-audio.c

## Purpose
This file implements ALSA PCM capture support for TW686x devices. It initializes an ALSA card/PCM capture device, manages per-channel audio DMA buffers, applies global audio sample-rate and period-size settings, services audio DMA interrupts, and starts/stops hardware audio channels.

## Important APIs, Types, And Functions
Externally used functions are `tw686x_audio_init`, `tw686x_audio_free`, and `tw686x_audio_irq`. ALSA callbacks are `tw686x_pcm_open`, `tw686x_pcm_close`, `tw686x_pcm_prepare`, `tw686x_pcm_trigger`, and `tw686x_pcm_pointer`, collected in `tw686x_pcm_ops`. Helpers are `tw686x_snd_pcm_init`, `tw686x_audio_dma_alloc`, and `tw686x_audio_dma_free`. The hardware contract is described by `tw686x_capture_hw`.

## Control Flow
Audio init enables external audio, creates an ALSA card, initializes each `tw686x_audio_channel`, optionally allocates coherent ping-pong DMA buffers for memcpy mode, creates capture substreams for `max_channels(dev)`, assigns managed ALSA buffers, and registers the card. PCM open stores the substream and hardware caps. Prepare rejects changes to global rate/period while any audio channel is enabled, disables the channel, updates audio clock divider and DMA size registers when needed, builds a list of runtime periods, selects initial P/B buffers, and programs DMA addresses in non-memcpy modes. Trigger start enables the channel and arms the DMA delay timer; trigger stop disables it and clears current buffers. IRQ handling rotates completed/current buffers based on P/B status, copies from coherent staging buffers in memcpy mode or programs the next DMA address otherwise, updates the ALSA pointer, and calls `snd_pcm_period_elapsed`.

## State And Persistence
Device-level runtime state includes `audio_rate`, `period_size`, `audio_enabled`, DMA mode, sound card pointer, and timer. Each channel stores lock, substream, channel number, buffer list, current ping-pong buffers, pointer, and optional coherent DMA descriptors. No data is persisted beyond hardware registers and ALSA runtime buffers.

## Dependencies And Integration Points
The file depends on ALSA core/PCM APIs, `tw686x.h` structures and channel helpers, `tw686x-regs.h` register definitions, PCI DMA allocation, timers owned by core code, and interrupt dispatch from `tw686x-core.c`.

## Risks
`dev->audio_enabled` is a single boolean, so stopping one channel clears it even if other channels remain active; this can weaken the global-parameter guard. In `tw686x_audio_irq`, `next` is only assigned when `buf_list` is non-empty, but non-memcpy mode writes `next->dma` after a done buffer is selected, so empty-list handling depends on queue invariants. `tw686x_audio_free` disables all audio DMA bits and frees the card but does not call `tw686x_audio_dma_free` for normal teardown in the shown path unless ALSA card cleanup indirectly covers only managed buffers, leaving coherent memcpy descriptors as a point to audit.

## Test Signals
Use ALSA capture on every channel at 8 kHz through 48 kHz, period sizes from 512 to 4096 bytes, and all supported period counts. Test simultaneous channels, attempts to change rate/period while another channel captures, memcpy and direct DMA modes, IRQ period cadence, pointer monotonicity, and unload/reload under active and idle audio capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-audio.c -->
