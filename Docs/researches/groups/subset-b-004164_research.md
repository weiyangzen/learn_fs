# subset-b-004164 research

This grouped report covers Samsung camera media drivers from the Exynos FIMC/FIMC-LITE/FIMC-IS/MIPI-CSIS area plus the adjacent S3C CAMIF build metadata. Each section preserves the source path for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp-video.c

## Purpose
Implements the optional V4L2 multi-planar capture video node for the FIMC-IS ISP DMA2 output path, bridging vb2 buffers to the firmware parameter block used by the imaging subsystem.

## Important APIs, Types, and Functions
The public entry points are `fimc_isp_video_device_register()`, `fimc_isp_video_device_unregister()`, and `fimc_isp_video_irq_handler()`. Internal APIs are the vb2 queue callbacks, V4L2 file/ioctl operations, `__isp_video_try_fmt()`, and `isp_video_pipeline_validate()`.

## Control Flow
Registration initializes one capture video device, a sink media pad, and a `vb2_queue` using `vb2_dma_contig_memops`. Open powers the ISP runtime PM domain and opens the media pipeline; stream-on starts the pipeline, validates media-bus formats upstream, and delegates buffer start to vb2. Queued buffers first populate the firmware shared address table, then `isp_video_capture_start_streaming()` enables DMA2 output, pushes ISP parameters to firmware, and starts upstream streaming. Interrupt completion maps the firmware frame index to a stored vb2 buffer, timestamps it, completes it, clears the bit from `buf_mask`, and updates the hardware mask.

## State and Persistence
Runtime state lives in `fimc_is_video`: requested count, prepared buffer count, DMA buffer table, buffer mask, current format, and `streaming`. `ST_ISP_VID_CAP_BUF_PREP` and `ST_ISP_VID_CAP_STREAMING` gate first-time address programming and active DMA. The only persistence is volatile firmware shared memory and ISP parameter state.

## Dependencies and Integration Points
Depends on V4L2/vb2, media-controller graph state, DMA-contiguous memory, FIMC-IS firmware parameter helpers, and `fimc_pipeline_call()` from the Exynos media pipeline. It relies on formats exported by `fimc-isp.c` and structures in `fimc-isp.h`.

## Risks and Edge Cases
`FIMC_ISP_REQ_BUFS_MAX` is 32 while `struct fimc_is_video::buffers` has `FIMC_ISP_MAX_BUFS` entries, so large `REQBUFS` counts can exceed the software buffer table. Buffer re-prepare only accepts previously known DMA addresses after `ST_ISP_VID_CAP_BUF_PREP`, making late replacement buffers fail with `-ENXIO`. Stop-streaming returns early if pipeline stop fails, leaving local DMA state uncleared.

## Test Signals
Exercise `REQBUFS` at minimum, maximum, and above four buffers; verify DMA address table programming in firmware memory; stream through a full media graph; confirm frame-done IRQs complete the expected vb2 indices; and test stream-off/pipeline-failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp-video.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp-video.h

## Purpose
Declares the ISP DMA capture video-node API and supplies no-op stubs when `CONFIG_VIDEO_EXYNOS4_ISP_DMA_CAPTURE` is disabled.

## Important APIs, Types, and Functions
Exports `fimc_isp_video_device_register()`, `fimc_isp_video_device_unregister()`, and `fimc_isp_video_irq_handler()` for the ISP subdev and interrupt paths. It includes `fimc-isp.h` for `struct fimc_isp` and `struct fimc_is`.

## Control Flow
When DMA capture support is enabled, callers register/unregister the ISP capture node during subdev registration lifecycle and forward ISP frame-done interrupts to the video queue. When disabled, registration succeeds as a no-op and IRQ handling is empty, allowing the ISP subdev to build without the capture node.

## State and Persistence
The header has no state; it controls whether the `fimc_isp` object's `video_capture` member becomes externally visible as a registered video node.

## Dependencies and Integration Points
Integrates `fimc-isp.c` with `fimc-isp-video.c` under a Kconfig feature boundary. It also includes videobuf2 definitions because the enabled implementation stores vb2 buffers in the associated structures.

## Risks and Edge Cases
The stub `fimc_isp_video_device_register()` returns success, so callers must tolerate a missing media link/video entity when DMA capture is not built. Any code assuming the capture node has pads must check entity pad count, as `media-dev.c` does.

## Test Signals
Build with the option enabled and disabled; verify ISP subdev registration succeeds in both cases; and verify media graph creation skips the ISP DMA video link when the video node is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp.c

## Purpose
Implements the FIMC-IS ISP V4L2 subdevice: media pads, raw Bayer format negotiation, streaming/power sequencing through FIMC-IS firmware, ISP controls, and registration of the optional DMA capture video node.

## Important APIs, Types, and Functions
Exports `fimc_isp_find_format()`, `fimc_isp_irq_handler()`, `fimc_isp_subdev_create()`, and `fimc_isp_subdev_destroy()`. Important callbacks are pad `get_fmt`/`set_fmt`, `fimc_isp_subdev_s_stream()`, `fimc_isp_subdev_s_power()`, internal registered/unregistered hooks, and `fimc_is_s_ctrl()`.

## Control Flow
Creation initializes a three-pad subdev: sink, FIFO source, and DMA source. Sink format changes propagate source formats while subtracting CAC margins, and active format changes are blocked during streaming. Power-on resumes runtime PM, boots firmware, powers sub-IP blocks, and initializes hardware. Stream-on sends pending parameters, changes firmware mode, issues hardware stream-on, and waits for firmware state bits; stream-off waits for stream-off and resets setfile sub-index. ISP interrupt handling reads firmware interrupt arguments, clears the ISP frame-done interrupt, forwards video DMA completion, and wakes waiters.

## State and Persistence
`struct fimc_isp` stores active sink/source media-bus formats, control handler state, locks, and video capture state. `struct fimc_is` firmware state bits are persistent runtime state across operations, but are reset on power-off along with parameter-region indices.

## Dependencies and Integration Points
Depends on V4L2 subdev/media-controller APIs, the FIMC-IS command and parameter interfaces, runtime PM, and `fimc-isp-video.h`. It participates in `media-dev.c` pipeline power/stream ordering and provides raw Bayer formats for the ISP DMA node.

## Risks and Edge Cases
Power-off tests `!IS_ST_PWR_ON` before closing the sensor, which is suspicious because close usually belongs to the powered state. `__ctrl_set_aewb_lock()` sets `ISP_AA_TARGET_AE` for both AE and AWB lock operations, likely failing to target AWB. Controls only push parameters immediately while streaming, so pre-stream control state depends on later pending-parameter flush.

## Test Signals
Validate power-on firmware boot, active/try format propagation across all pads, stream-on/off timeouts, control writes before and during streaming, DMA capture registration, and ISP IRQ-driven buffer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp.h

## Purpose
Defines the FIMC-IS ISP driver's shared data model, pad layout, format limits, video-buffer structures, state bits, and exported ISP helper prototypes.

## Important APIs, Types, and Functions
Key definitions include `struct fimc_isp`, `struct fimc_is_video`, `struct isp_video_buf`, `struct fimc_isp_ctrls`, pad constants `FIMC_ISP_SD_PAD_*`, and buffer/format constants such as `FIMC_ISP_NUM_FORMATS` and `FIMC_ISP_REQ_BUFS_*`.

## Control Flow
The header shapes control flow by separating subdev state from capture-node state: subdev operations take `subdev_lock`, video operations take `video_lock`, and ISR paths use `struct fimc_is_video::buffers` and state bits to complete frames.

## State and Persistence
`struct fimc_isp` aggregates platform device identity, media pads, active formats, V4L2 controls, locks, state bits, and capture video state. `struct fimc_is_video` holds volatile vb2 queue state, requested buffers, current buffer mask, and active format; none is persistent beyond the device lifetime.

## Dependencies and Integration Points
Includes kernel I/O/platform primitives, media entity/subdev/vb2 headers, and Exynos FIMC common format types. It is consumed by ISP subdev, ISP video, FIMC-IS core, and media graph code.

## Risks and Edge Cases
`FIMC_ISP_MAX_BUFS` is 4 while public request limits allow up to 32, creating a contract mismatch for capture-buffer storage. The `ctrl_to_fimc_isp()` macro ignores its `_ctrl` parameter and references `ctrl`, which works only in callers using that exact local variable name.

## Test Signals
Compile-test with sparse and different local variable names around `ctrl_to_fimc_isp()`, stream with more than four ISP DMA buffers, and verify lockdep behavior around concurrent video and subdev calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite-reg.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite-reg.c

## Purpose
Provides the low-level MMIO programming helpers for the Exynos FIMC-LITE camera host interface.

## Important APIs, Types, and Functions
Exports reset, IRQ, capture, test-pattern, input format, crop/window, camera bus, DMA output, DMA buffer, buffer mask, and register-dump helpers such as `flite_hw_reset()`, `flite_hw_set_source_format()`, `flite_hw_set_camera_bus()`, `flite_hw_set_output_dma()`, and `flite_hw_set_dma_buffer()`.

## Control Flow
The main driver calls these helpers while holding `fimc_lite::slock` for register programming. Hardware init sets camera bus/mux, source format, crop offset, DMA mask, DMA output mode, interrupt masks, and optional test pattern. IRQ paths read and clear status, while queue paths program or mask DMA start-address slots.

## State and Persistence
All state is hardware-register state under `dev->regs`; the file keeps only static media-bus-to-register mapping tables. No save/restore cache exists, so callers must reprogram after reset or power transitions.

## Dependencies and Integration Points
Depends on `fimc-lite.h`, `fimc-lite-reg.h`, common Exynos FIMC format descriptors, media-bus codes, and MMIO accessors. It is tightly integrated with `fimc-lite.c` queue, stream, suspend, and register-dump paths.

## Risks and Edge Cases
The format-map lookup falls back to table entry zero on unsupported input codes, which can silently program YUYV ordering after logging. `flite_hw_set_out_order()` assumes a matching YUV code and can fall through to index zero for non-YUV formats. Reset waits for ready but proceeds even if timeout expires.

## Test Signals
Validate each supported YUV/raw/JPEG media-bus code, parallel versus MIPI bus polarity, one-buffer and 32-buffer variants, crop/compose offset programming, reset timeout behavior, and register dumps before/after stream start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite-reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite-reg.h

## Purpose
Defines FIMC-LITE register offsets, bit fields, and the MMIO helper API implemented by `fimc-lite-reg.c`.

## Important APIs, Types, and Functions
Key definitions cover `CISRCSIZE`, `CIGCTRL`, `CIIMGCPT`, crop offsets, DMA format/address registers, interrupt status bits, and `CIFCNTSEQ`. The helper prototypes expose reset, IRQ, bus, format, window, DMA, test-pattern, dump, and buffer-mask operations.

## Control Flow
The main driver uses these constants to program source geometry, interrupt enables, capture enable, output DMA mode, and per-buffer sequence masks. The inline `flite_hw_set_dma_buf_mask()` writes the active DMA-buffer mask directly.

## State and Persistence
The header has no software state. It documents volatile register layout and bit semantics used to reconstruct hardware state after each reset or resume.

## Dependencies and Integration Points
Includes `linux/bitops.h` and `fimc-lite.h`, binding the register API to `struct fimc_lite`, `struct flite_frame`, `struct flite_buffer`, and `struct fimc_source_info`.

## Risks and Edge Cases
Several masks assume 13- or 14-bit geometry fields; callers must clamp dimensions before register writes. `FLITE_REG_CIGCTRL_IRQ_*` bits are disable-mask bits, so inverted semantics can easily enable the wrong interrupt set.

## Test Signals
Compile-test all helper declarations against `fimc-lite.c`, confirm register constants match hardware manuals for Exynos4/5 variants, and inspect IRQ-mask programming for DMA versus ISP output modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite.c

## Purpose
Implements the Exynos FIMC-LITE camera host interface as both a V4L2 capture video node and a media subdevice that can feed FIMC-IS directly.

## Important APIs, Types, and Functions
Important units are the platform driver, vb2 callbacks, video ioctls, media link setup, subdev pad/selection/stream callbacks, IRQ handler, runtime/system PM callbacks, and capture subdev registration. Core functions include `fimc_lite_hw_init()`, `fimc_lite_reinit()`, `flite_irq_handler()`, `start_streaming()`, `buffer_queue()`, `fimc_lite_streamon()`, and `fimc_lite_subdev_s_stream()`.

## Control Flow
Probe maps registers, obtains the clock and IRQ, creates a media subdev, enables runtime PM, sets DMA segment limits, and initializes default formats. The subdev registered callback creates the video node and vb2 queue. Link setup chooses `FIMC_IO_DMA` for video capture or `FIMC_IO_ISP` for internal ISP feed. DMA streaming validates the media pipeline, finds the remote sensor, initializes hardware, starts capture when active buffers exist, and completes frames from IRQs. ISP-feed streaming resets and starts hardware through the subdev `.s_stream` path without vb2 capture.

## State and Persistence
`struct fimc_lite` stores active input/output frames, payload, queue lists, buffer index, frame counter, output path, source group id, sensor pointer, event counters, and state bits. Suspend can move active buffers back to pending and resume requeues them; hardware registers are reinitialized rather than persistently saved.

## Dependencies and Integration Points
Depends on V4L2/vb2/media-controller APIs, DMA-contiguous memory, runtime PM, device tree match data, FIMC-LITE register helpers, and Exynos media pipeline callbacks. It links sensors or CSIS receivers to either its video node or the FIMC-IS ISP.

## Risks and Edge Cases
`fimc_lite_streamon()` returns 0 after a failed `vb2_ioctl_streamon()` because the error path drops through with `return 0`, masking stream-on failures. Buffer indices wrap at `reqbufs_count`; if no `REQBUFS` has set it, modulo-like behavior is unsafe. IRQ handler sets `ST_FLITE_RUN` even after some non-running paths, so state transitions need hardware validation.

## Test Signals
Test DMA capture stream-on error propagation, stream-on/off with no queued buffers and with pending requeue, MIPI and parallel sensors, crop/compose changes during streaming, suspend/resume with owned buffers, overflow event counting, and both Exynos4 one-DMA-buffer and Exynos5 32-buffer variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite.h

## Purpose
Defines shared data structures, constants, state bits, queue helpers, and variant data for the FIMC-LITE driver.

## Important APIs, Types, and Functions
Key types are `struct flite_drvdata`, `struct flite_frame`, `struct flite_buffer`, `struct fimc_lite_events`, and `struct fimc_lite`. Inline helpers check activity and push/pop active or pending buffer queues.

## Control Flow
The header establishes a two-queue model: buffers move from pending to active when programmed into DMA registers, then active to vb2 completion on frame-end IRQ. State bits distinguish low power, pending, run, stream, suspended, off, in-use, config-update, and sensor-stream conditions.

## State and Persistence
`struct fimc_lite` owns all runtime state for a device instance, including media/video entities, sensor pointer, clocks/registers, frame formats, output path, vb2 queue, buffer lists, event counters, and locks. No fields are intended for persistence beyond the driver instance.

## Dependencies and Integration Points
Includes kernel platform/IRQ/clock primitives, V4L2 subdev/control/vb2 headers, media entities, and Exynos FIMC format definitions. It is shared by the main FIMC-LITE driver and register helper layer.

## Risks and Edge Cases
The enum defines `ST_FLITE_LPM`, while `fimc-lite.c` uses `ST_LPM` from `fimc-core.h`, making state-bit ownership easy to confuse. Queue pop helpers assume the list is non-empty; all callers must check before popping.

## Test Signals
Run lockdep around queue operations, compile with state-bit warnings enabled, exercise suspend/resume bit transitions, and verify queue helpers are never invoked on empty lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-lite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-m2m.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-m2m.c

## Purpose
Implements the V4L2 memory-to-memory interface for the Samsung FIMC video postprocessor, covering format conversion, scaling, crop/compose, rotation, and DMA-to-DMA jobs.

## Important APIs, Types, and Functions
Exports `fimc_register_m2m_device()`, `fimc_unregister_m2m_device()`, and `fimc_m2m_job_finish()`. Important internals are `fimc_device_run()`, `fimc_m2m_shutdown()`, vb2 queue callbacks, format/selection ioctls, `queue_init()`, `fimc_m2m_open()`, and `fimc_m2m_release()`.

## Control Flow
Open allocates a per-file `fimc_ctx`, creates controls, initializes a v4l2-m2m context with source and destination vb2 queues, marks M2M running, and installs default RGB32 formats. Streaming resumes runtime PM. The scheduler calls `fimc_device_run()`, which prepares DMA offsets and addresses, copies timestamps, reprograms FIMC hardware when parameters changed or context switched, and activates input DMA/capture. Stop streaming waits for pending hardware shutdown, completes queued buffers with error, and drops runtime PM.

## State and Persistence
Per-file state lives in `struct fimc_ctx`: source/destination frames, controls, paths, scaler, rotation/effects, and parameter-dirty bits. Device-level `fimc->m2m` tracks the current hardware context, v4l2-m2m device, video node, and reference count. All state is volatile.

## Dependencies and Integration Points
Depends on FIMC core helpers, register helpers in `fimc-reg.c`, vb2 DMA-contig, V4L2 mem2mem framework, runtime PM, and common format/scaler validation code.

## Risks and Edge Cases
`fimc_buf_prepare()` sets payloads without checking actual plane sizes, relying on vb2/core allocation correctness. `fimc_device_run()` exits after DMA address or scaler errors without explicitly finishing the job, so error handling depends on later abort/stop paths. Selection type checks use single-planar buffer types while the queues are multi-planar, reflecting the driver's inverted-crop compatibility quirk and needing regression coverage.

## Test Signals
Exercise source/destination format negotiation, crop/compose scaler-ratio limits, rotation and flips, tiled formats, DMABUF/MMAP/USERPTR queues, runtime PM reference balance, job abort, and hardware IRQ completion through `fimc_m2m_job_finish()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-m2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-reg.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-reg.c

## Purpose
Provides the low-level register-programming implementation for Samsung FIMC capture/postprocessor hardware.

## Important APIs, Types, and Functions
Exports reset, rotation, target/input/output DMA setup, scaler setup, effect/alpha programming, input/output path selection, camera source/type/polarity/offset setup, IRQ clearing, capture activation/deactivation, frame-index reads, DMA sequence writes, and SYSREG writeback routing.

## Control Flow
M2M and capture code call these helpers while holding the device spinlock during hardware reconfiguration. A typical M2M job programs input path, input DMA geometry/order, scaler ratios, target format, rotation/effects, output DMA geometry/order, buffer addresses, then enables scaler/capture and input DMA. Capture paths additionally configure camera bus/source/type and offsets. Writeback configuration uses regmap updates to reset and enable ISP/CAM block FIFO routing.

## State and Persistence
The file stores no per-device software state; it transforms `struct fimc_ctx`, `struct fimc_frame`, and `struct fimc_source_info` into volatile MMIO and SYSREG state. Caller-owned frame/scaler fields are the source of truth for reprogramming after reset.

## Dependencies and Integration Points
Depends on `fimc-core.h`, `media-dev.h`, common Exynos media-bus definitions, MMIO accessors, and optional sysreg `regmap`. It is used by FIMC capture and M2M paths.

## Risks and Edge Cases
`fimc_hw_enable_capture()` uses `cfg &= FIMC_REG_CIIMGCPT_IMGCPTEN_SC` when disabling scaler capture, which preserves only that bit rather than clearing it from the existing register value. Camera type setup supports only a narrow subset of MIPI formats, returning `-EINVAL` for many valid CSI-2 media-bus codes. Register writes assume earlier format/geometry clamping.

## Test Signals
Validate register traces for each input/output color family, scaler enabled/bypass modes, 90/270 rotation paths, tiled DMA, camera MIPI/parallel/writeback inputs, frame index reporting on variants with and without `CISTATUS2`, and SYSREG writeback setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-reg.h

## Purpose
Defines Samsung FIMC register offsets, bit fields, SYSREG writeback bits, and register helper prototypes.

## Important APIs, Types, and Functions
Key definitions cover source format, crop offsets, global control, output/input DMA addresses and offsets, target format, scaler, status, capture control, effects, tiled DMA parameters, CSI image format, and output DMA sequence mask. The inline `fimc_hw_set_dma_seq()` writes `FIMC_REG_CIFCNTSEQ`.

## Control Flow
The header supplies the constants used by `fimc-reg.c` and higher-level capture/M2M code to reset hardware, select camera sources, configure scaler/DMA paths, activate capture, and query active frame indices.

## State and Persistence
No software state is defined here; all constants describe volatile hardware register state. Register state must be rebuilt by callers when hardware is reset or resumed.

## Dependencies and Integration Points
Includes `fimc-core.h` for core device/context types and is consumed by FIMC capture, M2M, and media writeback integration.

## Risks and Edge Cases
Many masks encode limited 11- to 12-bit width/height fields, so out-of-range geometry corrupts adjacent bits if not bounded earlier. Some declarations, such as `fimc_hw_en_irq()`, are present without an implementation in this file, so link coverage depends on other compilation units or dead code.

## Test Signals
Compile all FIMC configurations, compare register constants with SoC manuals, validate sequence masks for four versus 32 output buffers, and trace capture enable/disable bit transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/media-dev.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/media-dev.c

## Purpose
Implements the top-level Samsung S5P/Exynos FIMC media device, responsible for discovering sensors and platform subdevices, constructing media links, managing pipeline power/stream order, exposing camera clocks, and registering the media device.

## Important APIs, Types, and Functions
Important functions include `fimc_pipeline_prepare()`, `fimc_pipeline_s_power()`, `__fimc_pipeline_open()`, `__fimc_pipeline_s_stream()`, platform entity registration helpers, sensor DT parsing, link creation helpers, link-notify pipeline modification, clock-provider registration, async notifier callbacks, `fimc_md_probe()`, and module init/exit.

## Control Flow
Probe populates child platform devices, initializes media/v4l2 devices, obtains clocks, registers FIMC/FIMC-LITE/CSIS/FIMC-IS entities, parses sensor endpoints, exposes the subdev API mode sysfs attribute, registers camera-clock providers, and waits for async sensor binding. Completion creates sensor-to-CSIS/FIMC/FIMC-LITE/ISP links, registers subdev nodes, and registers the media device. Opening a video node prepares the active graph, powers subdevs in ordered sequences, and streaming calls `.s_stream` in a separate order with rollback on failure.

## State and Persistence
`struct fimc_md` stores arrays of registered platform entities and sensors, async connections, camera/writeback clocks, pipeline objects, media/v4l2 devices, user-subdev API mode, and graph walk state. State is runtime-only; sysfs toggles affect current in-memory pipeline configuration behavior.

## Dependencies and Integration Points
Depends on OF graph parsing, v4l2-async, media-controller graph/link APIs, clk provider APIs, runtime PM, FIMC/FIMC-LITE/FIMC-IS/CSIS subdrivers, and Exynos pipeline operations.

## Risks and Edge Cases
`fimc_md_create_links()` calls `__fimc_md_create_flite_source_links()` unconditionally, but that helper dereferences `fmd->fimc_is` when FIMC-LITE instances exist; non-ISP configurations with FIMC-LITE need coverage. `subdev_notifier_bound()` increments `num_sensors` even though the same field was used as a parse count and reset before notifier registration, making count semantics phase-dependent. Link-notify rollback is complex and can leave power use-counts wrong if subdev callbacks return mixed errors.

## Test Signals
Validate DTs with parallel sensors, CSI sensors, FIMC-IS sensors, no sensors, no ISP, and multiple FIMC/FIMC-LITE entities; toggle `subdev_conf_mode`; exercise link changes while video nodes are open; and verify power/stream order and clock-provider PM balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/media-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/media-dev.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/media-dev.h

## Purpose
Defines the top-level FIMC media-device data structures, entity names, limits, pipeline indices, clock-provider structures, and helper accessors used across the Samsung camera media graph.

## Important APIs, Types, and Functions
Key types are `struct fimc_pipeline`, `struct fimc_sensor_info`, `struct cam_clk`, and `struct fimc_md`. Helper functions/macros include `to_fimc_pipeline()`, `source_to_sensor_info()`, `entity_to_fimc_mdev()`, `notifier_to_fimc_md()`, graph lock/unlock helpers, `fimc_md_is_isp_available()`, and `__fimc_md_get_subdev()`.

## Control Flow
The pipeline index enum defines ordered positions for sensor, CSIS, FIMC-LITE, FIMC-IS ISP, and FIMC capture subdevices. Media-device code fills these slots during graph walks and then uses them for power and stream sequencing.

## State and Persistence
`struct fimc_md` is the persistent runtime container for one media-device instance: registered entities, sensor descriptors, clocks, notifier, media/v4l2 devices, mode flags, spinlock, pipelines, and graph walk object. It is allocated at probe and released at remove.

## Dependencies and Integration Points
Includes media controller, V4L2 subdev/device, clk provider, OF, and all local entity headers. It is the shared contract between the top-level media device and subdrivers.

## Risks and Edge Cases
The helper `entity_to_fimc_mdev()` assumes any associated media device is embedded in `struct fimc_md`; using it on foreign media entities would miscast. `fimc_md_is_isp_available()` only checks for an available child node named `fimc-is`, so unusual DT layouts are invisible.

## Test Signals
Compile with and without OF, test graph helpers on all registered entity types, validate pipeline slot population from several graph shapes, and verify clock arrays are initialized before cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/media-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/mipi-csis.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/mipi-csis.c

## Purpose
Implements the Samsung S5P/Exynos MIPI CSI-2 receiver subdevice, including D-PHY/control register programming, format negotiation, packet-buffer capture, interrupt/error counters, runtime PM, and DT probing.

## Important APIs, Types, and Functions
Important types are `struct csis_state`, `struct csis_pix_format`, `struct csis_drvdata`, and event/pktbuf structures. Key functions include `s5pcsis_parse_dt()`, `s5pcsis_start_stream()`, `s5pcsis_stop_stream()`, pad format callbacks, `s5pcsis_s_rx_buffer()`, `s5pcsis_irq_handler()`, PM resume/suspend helpers, `s5pcsis_probe()`, and `s5pcsis_remove()`.

## Control Flow
Probe parses DT lane and clock configuration, obtains PHY/regulators/clocks/MMIO/IRQ, initializes a two-pad subdev, sets a default format, and enables runtime PM. Stream-on clears counters, resumes PM, resets hardware, programs lane count, format, resolution, settle time, alignment, wrapper clock source, enables the D-PHY/system, and unmasks interrupts. IRQ handling copies non-image packet data into a caller-supplied buffer, updates event counters, and clears interrupt sources. PM suspend stops streaming, powers off PHY/regulators, disables the gate clock, and marks suspend state.

## State and Persistence
`struct csis_state` stores active media-bus format, selected hardware format, lane/clock/settle settings, flags for powered/streaming/suspended, packet buffer pointer/length, and event counters. Hardware state is volatile and reprogrammed on stream start or resume.

## Dependencies and Integration Points
Depends on V4L2 subdev/media pads, OF graph/fwnode endpoint parsing, PHY, regulators, runtime PM, clocks, platform IRQs, and Exynos media graph registration through `media-dev.c`.

## Risks and Edge Cases
`s5pcsis_s_stream()` calls runtime resume before taking the lock; if streaming is rejected due to `ST_SUSPENDED`, it exits without a matching runtime PM put. `s5pcsis_parse_dt()` uses the first graph endpoint and derives index from port number, so malformed DT ports can misidentify receiver instances. Packet-buffer copying happens in IRQ context into an external pointer that must remain valid until completion.

## Test Signals
Validate Exynos4/5 interrupt masks, 1/2/4 lane DTs, default and explicit clock rates, all supported media-bus formats, runtime PM balance on failed stream-on, non-image packet buffer delivery, event counters under CRC/ECC/overflow injection, and suspend/resume while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/mipi-csis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/mipi-csis.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/mipi-csis.h

## Purpose
Defines public constants for the Samsung MIPI-CSIS receiver driver.

## Important APIs, Types, and Functions
Constants include driver/subdev names, maximum receiver entities, lane limits for CSIS0 and CSIS1, sink/source pad indices, pad count, and default pixel dimensions.

## Control Flow
The header determines media pad layout and naming used by probe, media-device registration, and link creation. `CSIS_MAX_ENTITIES` bounds media-device arrays and DT mux-id validation.

## State and Persistence
No software state is stored here; constants constrain runtime state allocated in `mipi-csis.c` and `media-dev.h`.

## Dependencies and Integration Points
Consumed by MIPI-CSIS implementation and the top-level media device for entity array sizing and link pad indices.

## Risks and Edge Cases
Lane-limit constants are not directly enforced in `mipi-csis.c`, which relies on DT `bus-width` as `max_num_lanes`; board descriptions must match hardware limits. Increasing entity count requires matching media-device array expectations.

## Test Signals
Compile-test link creation against pad constants, validate DT mux ids remain below `CSIS_MAX_ENTITIES`, and confirm default format dimensions are visible before userspace configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/mipi-csis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/Kconfig

## Purpose
Defines the Kconfig option for the Samsung S3C64XX CAMIF V4L2 camera host driver.

## Important APIs, Types, and Functions
The option is `VIDEO_S3C_CAMIF`, a tristate named "Samsung 3C64XX SoC Camera Interface driver". It selects media-controller, V4L2 subdev API, and vb2 DMA-contiguous support.

## Control Flow
Enabling the option makes the Makefile build the `s3c-camif` module or built-in object. Dependency constraints require V4L platform drivers, V4L2 video device support, I2C, PM, and either `ARCH_S3C64XX` or `COMPILE_TEST`.

## State and Persistence
Kconfig state is build-time configuration only. It persists through the kernel `.config`, not at runtime.

## Dependencies and Integration Points
Integrates the `s3c-camif` directory into the broader media/platform Samsung build. The selected symbols ensure the driver has media graph, subdev, and DMA buffer infrastructure.

## Risks and Edge Cases
The prompt says "3C64XX" rather than "S3C64XX", a cosmetic issue. `COMPILE_TEST` broadens build coverage but does not guarantee runtime-valid platform dependencies outside S3C64XX.

## Test Signals
Run `olddefconfig` and compile with `VIDEO_S3C_CAMIF=y`, `m`, and disabled; verify selected media/vb2 symbols; and compile-test on non-S3C architectures with `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/Makefile

## Purpose
Builds the Samsung S3C CAMIF driver objects under the `VIDEO_S3C_CAMIF` Kconfig option.

## Important APIs, Types, and Functions
Defines `s3c-camif-objs` as `camif-core.o`, `camif-capture.o`, and `camif-regs.o`, then adds `s3c-camif.o` to `obj-$(CONFIG_VIDEO_S3C_CAMIF)`.

## Control Flow
When the Kconfig symbol is enabled, Kbuild links the three component objects into one `s3c-camif` built-in object or module. When disabled, none of the directory's driver objects are built.

## State and Persistence
There is no runtime state; this is purely build-system metadata.

## Dependencies and Integration Points
Depends on the parent media Samsung Makefile including this directory and on Kconfig selecting `VIDEO_S3C_CAMIF`. It ties the core, capture, and register implementation files into one module.

## Risks and Edge Cases
The directory comment mentions `s3c244x/s3c64xx`, while Kconfig only exposes the S3C64XX driver option, so maintainers should verify whether that comment is historical. Missing any of the three object files breaks the module link.

## Test Signals
Build `CONFIG_VIDEO_S3C_CAMIF=m` and verify `s3c-camif.ko` contains all three objects; build `=y` for built-in linkage; and confirm clean no-op behavior when the option is unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/Makefile -->
