# subset-b-004169 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-v4l2.c

Purpose: implements the ST HVA V4L2 memory-to-memory encoder device. It exposes `/dev/video*` for raw NV12/NV21 input frames and H.264 capture streams, registers the available `hva_enc` codec backends, owns per-open encoder contexts, validates formats and controls, and bridges videobuf2/V4L2 m2m jobs to the hardware-specific encoder callbacks in `hva-hw` and codec files.

Important APIs and functions: the platform entry points are `hva_probe`, `hva_remove`, `hva_register_device`, and `hva_unregister_device`. File lifecycle is `hva_open`/`hva_release`; ioctl handlers include query/enum/get/try/set format, `hva_qbuf`, and stream parameter access. Control setup is in `hva_ctrls_setup` and `hva_s_ctrl`, covering bitrate, GOP, H.264 profile/level/entropy/CPB/QP/VUI/SEI controls. Queue and job callbacks are `hva_queue_init`, `hva_queue_setup`, `hva_buf_prepare`, `hva_start_streaming`, `hva_stop_streaming`, `hva_device_run`, `hva_job_ready`, `hva_job_abort`, and `hva_run_work`.

Control flow: probe allocates `struct hva_dev`, coerces a 32-bit DMA mask, probes hardware, registers encoders/formats, registers a V4L2 device, creates a workqueue, and registers the mem2mem video node. Open allocates `struct hva_ctx`, initializes controls and two vb2 queues, assigns defaults, and optionally creates debugfs context state. Streaming opens an encoder only after both output and capture queues have started, stores the context in the device instance table, and then mem2mem scheduling queues `hva_run_work`. The worker removes one source and destination buffer, calls `enc->encode(ctx, frame, stream)`, propagates timestamp/sequence/payload, completes both buffers, and finishes the m2m job. Stop returns pending buffers, closes the encoder once both queues are stopped, and clears abort state.

State and persistence: all state is volatile kernel/V4L2 state: `hva_dev` device resources, registered encoders and formats, per-file `hva_ctx` controls, stream/frame format flags, frame/stream sequence numbers, vb2 DMA-contig buffer addresses, active encoder private data, error counters, and optional debugfs performance data. There is no disk persistence. Runtime PM delegates to `hva_hw_runtime_suspend` and `hva_hw_runtime_resume`.

Dependencies and integration points: depends on V4L2 mem2mem, vb2 DMA-contig, V4L2 controls/events/ioctls, platform device/OF matching, HVA hardware helpers, encoder backends `nv12h264enc` and `nv21h264enc`, and optional HVA debugfs. It is the public V4L2 frontend for codec and hardware modules.

Risks and test signals: key risks are format negotiation asymmetry between output and capture queues, estimated stream size under-allocation, qbuf header `bytesused` handling for capture buffers, instance-table lifetime when release races with streaming teardown, workqueue reentrancy, control values accepted before encoder open, and error paths that must return buffers in correct vb2 states. Test with v4l2-compliance, TRY/S_FMT before and during streaming, MMAP/DMABUF queues, H.264 encode smoke tests for NV12 and NV21, abort/streamoff during active jobs, runtime PM suspend/resume, module remove after active opens, and debug/error counter inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva.h

Purpose: defines the shared object model for the ST HVA encoder driver. It describes uncompressed frame metadata, compressed stream metadata, V4L2/H.264 control storage, vb2 buffer wrappers, per-instance context state, device-wide resources, and the encoder backend interface consumed by `hva-v4l2.c` and codec/hardware files.

Important types and APIs: `struct hva_frameinfo` and `struct hva_streaminfo` store negotiated raw and compressed formats. `struct hva_controls` mirrors V4L2 MPEG/H.264 controls. `struct hva_frame` and `struct hva_stream` wrap `vb2_v4l2_buffer` with list nodes, DMA physical addresses, kernel virtual addresses, prepared flags, and size/payload data. `struct hva_ctx` holds one open encoder instance, including `v4l2_fh`, control handler, format validity flags, sequence counters, encoder pointer, private codec data, and error counters. `struct hva_dev` holds V4L2/video/m2m objects, platform resources, registers, clock/IRQ/workqueue/hardware lock, encoder registries, supported format tables, hardware error registers, and optional debugfs state. `struct hva_enc` is the backend ABI with `open`, `close`, and `encode` callbacks.

Control flow and integration: the V4L2 layer populates `hva_ctx` and uses `to_hva_frame`/`to_hva_stream` to convert vb2 buffers. Encoder backends are selected by `(pixelformat, streamformat)` and operate through `hva_enc`. Hardware support fills `struct hva_dev` registers, clocks, IRQs, ESRAM, and PM hooks. Optional debugfs functions are declared only when configured.

State and persistence: the header defines only in-memory state. The most persistent state is kernel object lifetime across open files and active streams; there is no filesystem persistence. Error counters and debug metrics are diagnostic and reset with context/device lifetime.

Dependencies and risks: depends on V4L2 controls, V4L2 device, vb2-v4l2, and V4L2 mem2mem. Risks are ABI coupling between the generic V4L2 frontend and codec backends, assumptions that all supported raw formats are one-plane DMA-contig frames, fixed `HVA_MAX_INSTANCES`/encoder/format limits, direct exposure of DMA addresses, and keeping format flags consistent with negotiated `frameinfo`/`streaminfo`. Test signals are compile coverage with and without debugfs, concurrent instance limit tests, backend open/close/encode paths, and validation that every registered encoder contributes expected format tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/Kconfig

Purpose: declares STM32 media platform driver configuration symbols for CSI, DCMI, DCMIPP, and DMA2D. It controls which drivers are built and which media/V4L2 helper subsystems are selected.

Important symbols: `VIDEO_STM32_CSI` builds the STM32 Camera Serial Interface bridge and selects media controller plus V4L2 fwnode support. `VIDEO_STM32_DCMI` builds the Digital Camera Memory Interface capture driver and selects vb2 DMA-contig, media controller, and V4L2 fwnode. `VIDEO_STM32_DCMIPP` builds the Digital Camera Memory Interface Pixel Processor pipeline and selects media controller, vb2 DMA-contig, V4L2 subdev API, and V4L2 fwnode. `VIDEO_STM32_DMA2D` builds the Chrom-Art Accelerator mem2mem driver and selects vb2 DMA-contig and V4L2 mem2mem.

Control flow and integration: each symbol depends on the appropriate media driver class (`V4L_PLATFORM_DRIVERS` or `V4L_MEM2MEM_DRIVERS`), `VIDEO_DEV`, and either `ARCH_STM32` or `COMPILE_TEST`. These options feed the adjacent Makefile and govern module names such as `stm32-csi`, `stm32-dcmi`, `stm32-dcmipp`, and `stm32-dma2d`.

State and risks: Kconfig has no runtime state but shapes build-time dependency availability. Risks are missing selected helpers for vb2, fwnode graph parsing, media-controller links, or mem2mem scheduling, and compile-test paths masking runtime-only clock/reset/DMA/DT requirements. Test signals are `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and targeted builds with each symbol disabled, modular, and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/Makefile

Purpose: maps STM32 media Kconfig symbols to build artifacts.

Important build rules: `CONFIG_VIDEO_STM32_CSI` builds `stm32-csi.o`; `CONFIG_VIDEO_STM32_DCMI` builds `stm32-dcmi.o`; `CONFIG_VIDEO_STM32_DCMIPP` descends into `stm32-dcmipp/`; and `CONFIG_VIDEO_STM32_DMA2D` builds the composite `stm32-dma2d.o` from `dma2d/dma2d.o` plus `dma2d/dma2d-hw.o`.

Control flow and integration: the file is consumed by kbuild after Kconfig selection. The DMA2D object composition separates V4L2/mem2mem policy from register programming, while DCMIPP has its own subdirectory Makefile for multi-entity composition.

State and risks: no runtime state. Risks are object-list drift when adding new source files, missing subdirectory traversal for DCMIPP, or mismatched module names expected by Kconfig help and userspace. Test signals are clean modular and built-in builds for each STM32 media symbol and link checks for `stm32-dma2d-objs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d-hw.c

Purpose: contains the low-level register programming helpers for the STM32 DMA2D/Chrom-Art V4L2 mem2mem driver. It translates `struct dma2d_frame` and operation mode state into DMA2D hardware register writes.

Important APIs: `dma2d_start` sets `CR_START`; `dma2d_get_int` reads interrupt status; `dma2d_clear_int` acknowledges all currently set interrupt flags; `dma2d_config_common` programs operation mode and output dimensions; `dma2d_config_out` enables interrupts, programs output pixel format, destination address, output color, and output line offset; `dma2d_config_fg` and `dma2d_config_bg` program foreground/background memory addresses, offsets, input pixel formats, alpha modes, alpha values, and default colors.

Control flow: `dma2d.c` calls these helpers from `device_run` after selecting source and destination vb2 buffers. Foreground is configured from the output/source queue buffer, destination is configured from the capture buffer, common mode/size is written, and `dma2d_start` launches the transfer. Completion is handled by the parent driver's IRQ path.

State and persistence: state is hardware MMIO register state only, plus the caller-owned `dma2d_dev` and frame structures. There is no persistent storage. Register access uses relaxed reads/writes, so ordering expectations rely on device semantics and caller locking.

Dependencies and risks: depends on `dma2d.h`, `dma2d-regs.h`, Linux IO accessors, and valid DMA addresses from vb2 DMA-contig. Risks include incorrect bitfield masking for alpha mode (`(a_mode << 16) & 0x03` appears narrower than the shifted field), unsupported color mode values being silently ignored, interrupt enable policy being embedded in output config, and no explicit memory barriers around start. Test signals are register traces, RGB format conversion tests, R2M fill color tests, interrupt status/clear behavior, and comparing output pixels for every advertised format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d-regs.h

Purpose: defines the STM32 DMA2D register map, bitfields, color mode constants, hardware limits, and default dimensions used by the DMA2D V4L2 mem2mem driver.

Important constants: control register fields include operation modes `CR_M2M`, `CR_M2M_PFC`, `CR_M2M_BLEND`, `CR_R2M`, interrupt enables, abort/suspend/start bits, and mode masks. Status/clear flags cover configuration, transfer complete, access, watermark, transfer complete, and transfer error conditions. Address/offset/pixel-format registers are defined for foreground, background, and output layers. `MAX_WIDTH`/`MAX_HEIGHT` are 2592, defaults are 240x320 with `DEFAULT_SIZE` 307200, and color mode constants include ARGB8888, ARGB4444, and A4.

Control flow and integration: `dma2d-hw.c` uses these definitions to program MMIO registers; `dma2d.c` uses size limits and defaults for V4L2 format negotiation. The constants are a hardware ABI and must match STM32 DMA2D documentation.

State and risks: no runtime state. Risks are stale or incorrect bit definitions causing silent register misprogramming, partial color-mode coverage relative to `enum dma2d_cmode`, and default size assumptions that must match default pixel format/depth. Test signals are compile-time use across both DMA2D source files, hardware register dumps, interrupt flag clear tests, and format conversion validation across all advertised formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d.c

Purpose: implements the STM32 DMA2D/Chrom-Art Accelerator as a V4L2 memory-to-memory video device. It supports one-plane RGB-style buffers for memory copy, pixel format conversion, and register-to-memory color fill selected through V4L2 controls.

Important APIs and functions: file lifecycle is `dma2d_open`/`dma2d_release`; queue callbacks are `queue_init`, `dma2d_queue_setup`, `dma2d_buf_out_validate`, `dma2d_buf_prepare`, `dma2d_buf_queue`, `dma2d_start_streaming`, and `dma2d_stop_streaming`; ioctl handlers are querycap, enum/g/try/s format, and standard m2m vb2 ioctls. `dma2d_s_ctrl` handles `V4L2_CID_COLORFX` and `V4L2_CID_COLORFX_RGB`. `device_run` programs hardware for the next src/dst pair, and `dma2d_isr` completes buffers. Platform setup is in `dma2d_probe`/`dma2d_remove`.

Control flow: probe maps registers, obtains/prepares the `dma2d` clock, requests the IRQ, registers a V4L2 device, initializes the mem2mem scheduler, and registers the video node. Open allocates a context with default capture/output/background frames and controls. Users negotiate formats on output and capture queues; the output colorspace is propagated to capture. During a mem2mem job, `device_run` records the current context, gets next source and destination buffers, copies metadata, enables the clock, configures foreground/output/common registers, chooses M2M or M2M_PFC unless R2M was selected, and starts DMA2D. The IRQ clears status, disables the clock, removes the src/dst buffers, marks both done, finishes the m2m job, and clears `dev->curr`.

State and persistence: runtime state lives in `struct dma2d_dev` (V4L2/m2m/video objects, mutex, control spinlock, clock, register base, current context) and `struct dma2d_ctx` (per-open frame formats, operation mode, controls, colorspace). No persistent storage is used.

Dependencies and integration points: depends on V4L2 mem2mem, vb2 DMA-contig, platform devices, IRQs, clocks, OF matching `"st,stm32-dma2d"`, and low-level helpers from `dma2d-hw.c`. Userspace integration is the standard V4L2 mem2mem API.

Risks and test signals: risks include `get_frame()` mapping output types to `ctx->cap` and capture to `ctx->out` names that are easy to misuse, only partial operation support despite a blend enum, weak error handling in `device_run` when no buffers or clock enable fails, interrupt logic treating zero status as completion, no explicit failed-buffer completion on hardware error flags, and color-fill mode still expecting both src and dst buffers. Test with v4l2-compliance, every advertised RGB format pair, COLORFX fill/no-fill toggles, IRQ error injection, streamoff while a job is active, clock failure paths, and module unload after open contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d.h

Purpose: declares shared data structures and hardware helper prototypes for the STM32 DMA2D V4L2 mem2mem driver.

Important types and APIs: `enum dma2d_op_mode` models M2M, M2M with pixel format conversion, M2M blend, and register-to-memory modes. `enum dma2d_cmode` and `enum dma2d_alpha_mode` describe hardware color and alpha handling. `struct dma2d_fmt` maps V4L2 fourcc to depth and color mode. `struct dma2d_frame` stores dimensions, crop/offset fields, line offset, format, ARGB color, alpha mode, buffer size, and sequence. `struct dma2d_ctx` stores one file handle, source/capture/background frame configs, operation mode, controls, and colorimetry. `struct dma2d_dev` stores V4L2/video/m2m objects, locks, instance count, registers, clock, current context, and IRQ. The header declares `dma2d_start`, interrupt accessors, and foreground/background/output/common configuration helpers.

Control flow and integration: `dma2d.c` owns V4L2 policy and calls the prototypes implemented in `dma2d-hw.c`. Context and device structs are shared across queue callbacks, control callbacks, IRQ handling, and platform lifecycle.

State and risks: no standalone persistence. Risks are naming ambiguity between `cap` and `out`, unimplemented crop/background/blend fields becoming misleading API surface, and tight coupling between enum numeric values and hardware register encodings. Test signals are compile coverage for both source files, format negotiation tests that validate `size`, `line_offset`, and color mode, and IRQ/job scheduling tests that verify `dev->curr` lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/dma2d/dma2d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-csi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-csi.c

Purpose: implements the STM32 Camera Serial Interface as a V4L2 subdevice/media bridge. It configures a MIPI CSI-2 D-PHY receiver, lane merger, virtual channel/data type filtering, error interrupts, and forwards stream control to the remote source subdevice.

Important APIs and functions: resource/probe lifecycle is `stm32_csi_probe`, `stm32_csi_remove`, `stm32_csi_get_resources`, `stm32_csi_parse_dt`, runtime PM suspend/resume, and reset handling. Subdevice operations include `stm32_csi_init_state`, mbus code enumeration, `stm32_csi_set_pad_format`, `stm32_csi_enable_streams`, `stm32_csi_disable_streams`, and `stm32_csi_log_status`. Hardware setup is split between `stm32_csi_start`, `stm32_csi_stop`, `stm32_csi_start_vc`, `stm32_csi_stop_vc`, `stm32_csi_setup_lane_merger`, and `stm32_csi_phy_reg_write`. Interrupt handling is in `stm32_csi_irq_thread`.

Control flow: probe maps registers, gets three clocks and two regulators, requests a threaded IRQ, parses endpoint lane configuration, initializes a two-pad subdevice, resets hardware, enables runtime PM, and registers the subdevice. Async binding creates an immutable link from the remote sensor/bridge source pad to the CSI sink. Enabling streams computes link frequency from the remote pad and selected bpp/lanes, selects D-PHY timing from the Synopsys table, resumes power, programs lane merger, enables CSI/global and lane error interrupts, programs PHY test registers, enables lanes and PHY, starts VC0 filtering, and then enables the remote stream. Disable reverses remote streaming, VC0, core, interrupts, and runtime PM.

State and persistence: state is volatile: lane IDs/count, register base, clocks/regulators, error counters for SR0/SR1 events, subdevice state formats, remote subdevice pointer/pad, and media pads. Error counters persist only for the driver instance and are reported via log_status.

Dependencies and integration points: depends on V4L2 subdev state API, media controller, V4L2 fwnode parsing, MIPI CSI-2 data type constants, runtime PM, regulators, clocks, resets, threaded IRQs, and compatible `"st,stm32mp25-csi"`. It can feed a downstream capture/processor entity in the media graph.

Risks and test signals: risks include PHY timing table bounds, link-frequency assumptions (`2 * lanes`), duplicated Bayer table entries, JPEG/all-data filtering, lane numbering validation, incomplete cleanup of notifier state on remove, and error counters racing with interrupts if locking is wrong. Test with media graph enumeration, one-lane and two-lane sensors, RAW/YUV/RGB/JPEG formats, bad link-frequency controls, D-PHY error injection, log_status counter changes, runtime suspend/resume, and stream enable/disable ordering with the remote sensor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmi.c

Purpose: implements the STM32 Digital Camera Memory Interface as a V4L2 video capture driver. It exposes a capture node, discovers and links to a parallel/BT.656 camera subdevice, negotiates formats and crop, manages a vb2 DMA-contig queue, and captures frames through DMA with optional MDMA chaining via SRAM.

Important APIs and functions: capture lifecycle centers on `dcmi_start_streaming`, `dcmi_stop_streaming`, `dcmi_start_capture`, `dcmi_restart_capture`, `dcmi_process_frame`, `dcmi_irq_callback`, and `dcmi_irq_thread`. Buffer handling includes `dcmi_queue_setup`, `dcmi_buf_init`, `dcmi_buf_prepare`, `dcmi_buf_cleanup`, `dcmi_buf_queue`, and `dcmi_buffer_done`. Format/crop APIs include `dcmi_try_fmt`, `dcmi_set_fmt`, `dcmi_pipeline_s_fmt`, enum/g/s format, selection handlers, frame size/interval enumeration, and sensor parm forwarding. Probe/graph logic includes `dcmi_probe`, `dcmi_graph_init`, async bound/complete/unbind callbacks, format/frame-size initialization, and PM callbacks.

Control flow: probe parses the endpoint, rejects CSI input, validates BT.656 width, maps registers, obtains `mclk`, requests DMA and optional MDMA, configures channels, optionally allocates SRAM for DMA-MDMA chaining, initializes media/V4L2/video/vb2 objects, registers the video node, starts async graph binding, resets hardware, and enables runtime PM. Graph completion finds the upstream source, enumerates supported mbus formats and framesizes, gets crop bounds, sets the default format, and requests the DCMI IRQ. Streaming resumes PM, starts the media pipeline and source subdev, configures bus width/polarity/BT.656 sync/crop, enables DCMI, starts DMA on the first queued buffer or waits for one, and enables frame/overrun/error interrupts. Frame IRQ processing computes bytes used from DMA residue, completes the active buffer, terminates DMA, and restarts capture on the next queued buffer.

State and persistence: state is volatile: queued buffer list, active buffer, state machine `STOPPED/WAIT_FOR_BUFFER/RUNNING`, format/crop/sensor bounds, supported format/frame-size caches, DMA descriptors/scatterlists per buffer, optional SRAM/MDMA state, media pipeline, counters for errors/overruns/buffers, and runtime PM clock state. No disk persistence exists.

Dependencies and integration points: depends on media controller, V4L2 async/fwnode/subdev APIs, vb2 DMA-contig, DMAengine, optional MDMA, genalloc SRAM pool, runtime/system PM, reset/clock/pinctrl, and OF graph endpoints. It integrates directly with camera sensors or bridges over parallel or BT.656 media bus.

Risks and test signals: risks include complex DMA/MDMA residue accounting, sg-table cleanup on partial prepare failures, overrun restart behavior, crop disabling rules for JPEG/BT.656, source format propagation through multi-entity pipelines, async graph lifetime, returning queued buffers with correct states on start failure, and removing while the video node was unregistered by async unbind. Test with v4l2-compliance, MMAP/DMABUF/read paths, parallel and BT.656 sensors, JPEG and raw/YUV/RGB formats, crop selection edge cases, sensor framesize enumeration fallbacks, DMA max burst splitting, MDMA SRAM chaining, overrun/error IRQ injection, streamoff during active capture, suspend/resume, and media pipeline validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/Makefile

Purpose: declares the object composition for the STM32 DCMIPP driver module.

Important build rule: `stm32-dcmipp-y` links `dcmipp-core.o`, `dcmipp-common.o`, `dcmipp-input.o`, `dcmipp-byteproc.o`, and `dcmipp-bytecap.o` into one `stm32-dcmipp.o` module when `CONFIG_VIDEO_STM32_DCMIPP` is enabled.

Control flow and integration: kbuild uses this file after the parent STM32 Makefile descends into the directory. The composition mirrors the runtime pipeline: core platform/media orchestration, common entity helpers, input bridge, byte processor, and byte capture node.

State and risks: no runtime state. Risks are missing new DCMIPP entity objects from the aggregate list or breaking link order assumptions for init/release symbols. Test signals are modular and built-in builds of `CONFIG_VIDEO_STM32_DCMIPP`, plus symbol resolution for all `dcmipp_*_ent_init` and release functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-bytecap.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-bytecap.c

Purpose: implements the DCMIPP byte capture entity as the actual V4L2 video capture node. It maps media-bus formats from the upstream byte processor to V4L2 pixel formats, manages a vb2 DMA-contig queue, starts/stops the media pipeline, programs capture buffer addresses and limits, and handles frame/vsync/overrun interrupts.

Important APIs and functions: ioctl handlers include querycap, g/try/s/enum format, and enum framesizes. Queue callbacks are `dcmipp_bytecap_start_streaming`, `dcmipp_bytecap_stop_streaming`, `dcmipp_bytecap_queue_setup`, `dcmipp_bytecap_buf_init`, `dcmipp_bytecap_buf_prepare`, and `dcmipp_bytecap_buf_queue`. Capture and IRQ helpers are `dcmipp_start_capture`, `dcmipp_bytecap_set_next_frame_or_stop`, `dcmipp_bytecap_process_frame`, `dcmipp_bytecap_irq_callback`, `dcmipp_bytecap_irq_thread`, and `dcmipp_buffer_done`. Entity registration is `dcmipp_bytecap_ent_init` and release is `dcmipp_bytecap_ent_release`.

Control flow: init allocates the video entity, one sink pad, vb2 queue, DMA mask, buffer list/lock, default format, shared IRQ callbacks, and registers a video device. On stream start it caches the immutable upstream subdev, resumes runtime PM, starts the media pipeline, enables upstream streaming, enables the DCMIPP pipe, writes the first buffer address/limit, enables interrupts, and enters running state. VSYNC swaps `active` and `next` because the address register is shadowed for the next frame; frame-end reads captured byte count and completes `active`; overrun increments counters and may recycle state. Stop disables upstream stream, pipeline, interrupts, capture request, waits for inactive status, disables pipe, clears pending IRQs, returns queued buffers as errors, dumps debug registers, and releases PM.

State and persistence: state is volatile: current V4L2 format, vb2 queue, queued buffers, `active`/`next` pointers, capture state, media pipeline, cached upstream subdev/pad, interrupt status, and counters for errors, limits, overruns, buffers, vsync, frame, interrupts, underrun, and missing active buffers. Buffers store DMA addresses and prepared state. There is no persistent storage.

Dependencies and integration points: depends on DCMIPP common helpers, V4L2 ioctl/file APIs, media controller link validation, vb2 DMA-contig, runtime PM, and the upstream DCMIPP byteproc/input subdevices. Link validation requires width/height and mbus-code/pixelformat agreement.

Risks and test signals: risks include subtle `active`/`next` shadow-register sequencing, underrun behavior with only one queued buffer, frame count larger than buffer limit, format duplicate filtering, JPEG size assumptions, `video_set_drvdata(vdev, &vcap->ved)` requiring callers to container back correctly, and IRQ fan-out ordering from core. Test with media-ctl format propagation, v4l2-compliance, all mapped formats, min/max sizes, one-buffer and multi-buffer streaming, overrun and frame-limit IRQ cases, streamoff while active, runtime suspend/resume, and link validation failures for mismatched upstream formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-bytecap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-byteproc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-byteproc.c

Purpose: implements the DCMIPP byte processor subdevice. It is a two-pad media entity that propagates mbus formats, exposes compose/crop selections, and programs hardware decimation and crop registers before forwarding stream enable to the upstream input entity.

Important APIs and functions: format helpers include `dcmipp_byteproc_pix_map_by_code`, `dcmipp_byteproc_adjust_fmt`, `dcmipp_byteproc_adjust_compose`, and `dcmipp_byteproc_adjust_crop`. Subdevice operations include init state, enum mbus code, enum frame size, set/get format, get/set selection, enable/disable streams, and s_stream helper integration. Hardware programming is `dcmipp_byteproc_configure_scale_crop`. Entity lifecycle is `dcmipp_byteproc_ent_init`, release callback, and `dcmipp_byteproc_ent_release`.

Control flow: init registers a scaler-function subdevice with sink and source pads. Format setting on the sink validates mbus code, clamps dimensions/colorimetry, resets compose/crop to full frame, and mirrors the format to the source. Source format is derived from sink format and current source crop dimensions. Compose on the sink represents decimation before crop; crop on the source represents the crop after decimation. Stream enable finds the upstream subdev connected to the sink, programs decimation and crop registers based on sink format, compose, crop, and bytes-per-pixel, then enables upstream streaming. Disable forwards stream disable upstream.

State and persistence: state is held in V4L2 subdev state for pad formats, compose, and crop, plus hardware registers programmed on stream enable. The entity has no persistent storage.

Dependencies and integration points: depends on DCMIPP common registration and register helpers, V4L2 subdev selection/state APIs, media pad links, and the DCMIPP input and bytecap entities. It does not convert pixel format; output mbus code remains the input code.

Risks and test signals: risks include restricted decimation ratios, bytes-per-pixel assumptions for crop register units, no compose for JPEG/Bayer or non-1/2-byte formats, source pad selection validity, format changes blocked only while streaming, and needing upstream/downstream formats to remain synchronized. Test via media-ctl selection operations, crop/compose boundary cases, JPEG and Bayer no-scale behavior, Y8 1/4 width decimation, YUV/RGB 1/2 decimation, stream enable register programming, and link validation through bytecap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-byteproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-common.c

Purpose: provides common media-entity helpers for DCMIPP subdevices. It centralizes pad allocation, standard subdevice initialization/registration, link validation wiring, and subdevice cleanup.

Important APIs: `dcmipp_pads_init` allocates and initializes an array of `media_pad` entries from caller-supplied flags. `dcmipp_ent_sd_register` initializes a `dcmipp_ent_device` plus `v4l2_subdev`, assigns entity function/ops/name/owner/internal ops/subdev ops, exposes a devnode, initializes media pads, finalizes subdev state, registers the subdev, and stores optional IRQ callbacks. `dcmipp_ent_sd_unregister` cleans the entity and unregisters the subdevice. `dcmipp_entity_ops` uses `v4l2_subdev_link_validate`.

Control flow: DCMIPP input and byteproc entities call `dcmipp_ent_sd_register` during core topology creation. On failures, pads and media entity state are unwound. Release paths call `dcmipp_ent_sd_unregister` and rely on subdev internal release callbacks for private allocation cleanup.

State and persistence: state is allocated kernel memory for pads and subdevice/media entity registrations. No disk persistence exists. The helper stores IRQ handler pointers in the shared `dcmipp_ent_device`, later consumed by `dcmipp-core.c` IRQ fan-out.

Dependencies and risks: depends on media controller, V4L2 subdev registration, and the shared `dcmipp_ent_device` contract in `dcmipp-common.h`. Risks include cleanup ordering (`media_entity_cleanup` before/after subdev unregister), pad leaks if caller release paths miss `dcmipp_pads_cleanup`, and all subdevices using the same generic link validator even when entity-specific validation might be needed. Test signals are probe failure injection at pad init/entity init/finalize/register, remove/unbind leak checks, media graph validation, and IRQ callback registration visibility in core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-common.h

Purpose: defines the shared constants, entity wrapper, registration helpers, register accessors, colorimetry clamp macro, and entity init/release prototypes for the STM32 DCMIPP driver.

Important types and APIs: constants define the platform driver name, min/max/default frame sizes, and default colorimetry. `dcmipp_colorimetry_clamp` normalizes invalid V4L2 colorimetry fields for both pixel and mbus formats. `struct dcmipp_ent_device` wraps a media entity, pads, input bus description/type, and optional hard/threaded IRQ callbacks with last handler return. `dcmipp_pads_init`, `dcmipp_pads_cleanup`, `dcmipp_ent_sd_register`, and `dcmipp_ent_sd_unregister` form the common entity lifecycle API. `reg_read`, `reg_write`, `reg_set`, and `reg_clear` macros add device-scoped debug logging around relaxed MMIO access. Prototypes expose input, byteproc, and bytecap entity init/release functions.

Control flow and integration: `dcmipp-core.c` builds the topology from the entity init/release prototypes and dispatches shared IRQs using the callback fields. Entity files use the register macros and colorimetry clamp to keep behavior consistent.

State and persistence: the header defines in-memory state only. `dcmipp_ent_device` is the shared runtime handle that lets core traverse subdevices and video nodes uniformly.

Dependencies and risks: depends on Linux IRQ/slab and media/V4L2/fwnode headers. Risks include macro side effects from evaluating `device` multiple times, relaxed MMIO ordering assumptions, broad colorimetry validity thresholds, and the shared entity wrapper needing to work for both subdev and video_device containers. Test signals are compile coverage for all DCMIPP entities, runtime media graph creation, invalid colorimetry TRY/S_FMT tests, and dynamic debug traces of register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-core.c

Purpose: is the platform and media-graph core for the STM32 DCMIPP driver. It selects SoC-specific topology configuration, creates DCMIPP entities and immutable internal links, binds the external camera/CSI source, fans out the shared IRQ, registers the media device/subdev nodes, and owns clocks, reset, runtime PM, and system PM.

Important APIs and functions: topology data is stored in `dcmipp_pipeline_config`, `dcmipp_ent_config`, and `dcmipp_ent_link`. `dcmipp_create_subdevs` calls entity init functions, `dcmipp_create_links` builds internal links, and `dcmipp_graph_init` registers the async remote source notifier. IRQ dispatch is `dcmipp_irq_callback` and `dcmipp_irq_thread`. Async notifier callbacks are bound/unbind/complete. Platform lifecycle is `dcmipp_probe`, `dcmipp_remove`, runtime suspend/resume, and system suspend/resume.

Control flow: probe gets match data for MP13 or MP25, resets hardware, maps registers, requests the shared threaded IRQ, gets `kclk` and optional `mclk`, registers V4L2 and media devices, creates input/byteproc/bytecap entities, links input -> byteproc -> bytecap, registers the remote endpoint notifier, and enables runtime PM. When the remote subdev binds, the core parses endpoint bus type, validates CSI support and BT.656 width, stores bus settings in the input entity, and creates an immutable external link. Completion registers the media device and subdev nodes. The top-half IRQ calls each entity handler and records its return; the thread calls each entity thread function that requested `IRQ_WAKE_THREAD`.

State and persistence: state is volatile platform state: device resources, register base, clocks, selected topology config, media/V4L2 devices, entity array, and async notifier. No disk persistence exists.

Dependencies and integration points: depends on platform/OF match data (`st,stm32mp13-dcmipp`, `st,stm32mp25-dcmipp`), media controller, V4L2 async/fwnode APIs, reset/clock/pinctrl/runtime PM, and the common/entity modules. It integrates external sensors or CSI bridges with internal DCMIPP processing/capture nodes.

Risks and test signals: risks include optional `mclk` handling where runtime PM unconditionally disables/enables `mclk`, cleanup if entity creation fails after graph init, shared IRQ fan-out return semantics, endpoint parsing across parallel/BT.656/CSI, and media device registration only after async completion. Test with MP13 and MP25 device-tree variants, CSI unsupported on MP13, invalid bus width, probe failure injection at each entity, shared IRQ activity during streaming, media graph enumeration, runtime/system suspend-resume, and remove after async bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-input.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-input.c

Purpose: implements the DCMIPP input bridge subdevice. It accepts an external parallel, BT.656, or CSI-2 source on its sink pad, maps incoming mbus codes to DCMIPP internal formats on its source pad, programs input interface registers, and forwards stream enable/disable to the upstream source.

Important APIs and functions: format lookup helpers are `dcmipp_inp_pix_map_by_index` and `dcmipp_inp_pix_map_by_code`. Subdevice operations include init state, enum mbus code, enum frame size, set/get format, enable/disable streams, and s_stream helper integration. Hardware paths are `dcmipp_inp_configure_parallel` and `dcmipp_inp_configure_csi`. Entity lifecycle is `dcmipp_inp_ent_init`, internal release, and `dcmipp_inp_ent_release`.

Control flow: init registers a two-pad video-interface bridge subdevice. Format setting clamps dimensions and colorimetry, rejects unsupported mbus codes, excludes JPEG on BT.656, and when the sink format changes mirrors an adjusted source format. Stream enable locates the upstream subdev linked to the sink pad, configures parallel/BT.656 bus polarity, embedded sync, PRCR format and byte swap, or configures CSI data-type filtering through P0FSCR and CMCR, then enables the upstream stream. Disable stops the upstream stream and disables the parallel interface when applicable.

State and persistence: state is V4L2 subdev pad format state plus bus flags/type stored by the core in `dcmipp_ent_device`. Hardware register state is programmed only for active streams. There is no persistent storage.

Dependencies and integration points: depends on DCMIPP common helpers/register macros, media/V4L2 subdev APIs, MIPI CSI-2 data type constants, and endpoint bus settings parsed by `dcmipp-core.c`. It feeds byteproc through an immutable internal link.

Risks and test signals: risks include many mbus mapping aliases, sink/source code pair validation, JPEG/all-data CSI behavior, BT.656 exclusion rules, byte swap configuration for 2x8 formats, no local IRQ handling, and disabling only the parallel interface while CSI input selection remains register state. Test with all supported mbus codes, parallel polarity variants, BT.656 sync, CSI RAW/YUV/RGB/JPEG data-type filtering, media-ctl format propagation, stream enable failure unwinding, and upstream subdev missing/unbound cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-input.c -->
