# subset-b-004163 research

This grouped report covers Samsung Exynos G-Scaler, FIMC/CAMIF, and FIMC-IS media driver files. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-m2m.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-m2m.c

## Purpose
`gsc-m2m.c` implements the V4L2 memory-to-memory video node for the Exynos5 G-Scaler. It accepts source and destination multi-planar buffers, validates formats/selections, prepares DMA addresses, schedules one hardware conversion job through the V4L2 mem2mem framework, and completes both queues on the frame-done interrupt path.

## Important APIs, Types, and Functions
The public entry points are `gsc_register_m2m_device()`, `gsc_unregister_m2m_device()`, and `gsc_m2m_job_finish()`. Core scheduling is handled by `gsc_m2m_device_run()`, `gsc_m2m_job_abort()`, `gsc_m2m_ctx_stop_req()`, and `gsc_get_bufs()`. The vb2 queue operations are `gsc_m2m_queue_setup()`, `gsc_m2m_buf_prepare()`, `gsc_m2m_buf_queue()`, `gsc_m2m_start_streaming()`, and `gsc_m2m_stop_streaming()`. The ioctl table covers format enumeration/get/try/set, REQBUFS/EXPBUF/QBUF/DQBUF, stream on/off, and crop/compose selection through `gsc_m2m_g_selection()` and `gsc_m2m_s_selection()`.

## Control Flow
Open allocates a per-file `struct gsc_ctx`, creates controls, initializes source/destination defaults, and creates a V4L2 m2m context with output and capture vb2 queues. Streaming resumes runtime PM, buffers are queued into the m2m context, and `gsc_m2m_device_run()` becomes the hardware launch point. It marks `ST_M2M_PEND`, detects context changes, handles stop requests, prepares DMA addresses for the next source and destination buffers, writes input/output base addresses, programs all G-Scaler registers when `GSC_PARAMS` is set, triggers shadow-register update, and enables the hardware. The IRQ-side caller invokes `gsc_m2m_job_finish()`, which removes one source and one destination buffer, copies timestamp metadata, marks both vb2 buffers done, and notifies `v4l2_m2m_job_finish()`.

## State and Persistence
State is volatile per device and per context. `gsc->m2m.ctx`, `gsc->m2m.refcnt`, `gsc->state`, and `ctx->state` coordinate open users, pending jobs, parameter reprogramming, stop requests, and aborts. Runtime PM references are held while each queue streams. No persistent storage exists; all hardware state is rederived from current `gsc_ctx`, `gsc_frame`, controls, and queued buffers.

## Dependencies and Integration Points
The file depends on V4L2 mem2mem, vb2 DMA-contig memory, V4L2 ioctl helpers, runtime PM, and GSC core/register helpers such as `gsc_prepare_addr()`, `gsc_set_scaler_info()`, `gsc_try_fmt_mplane()`, `gsc_try_selection()`, and `gsc_hw_*()`. It integrates with the platform probe path through `gsc_register_m2m_device()` and with the interrupt handler through `gsc_m2m_job_finish()`.

## Risks and Edge Cases
Stop handling depends on a frame interrupt clearing `GSC_CTX_STOP_REQ`; a missing interrupt falls back to timeout and error-completion. `gsc_m2m_device_run()` logs address/scaler errors but does not complete buffers on those paths directly, so callers rely on scheduler/abort cleanup. Selection handling maps compose targets to the source frame and crop targets to the destination frame, which is easy to misread. REQBUFS rejects counts larger than hardware input/output buffer limits. Context switching forces full reprogramming by setting `GSC_PARAMS`.

## Test Signals
Useful validation includes open/close reference counts, runtime PM get/put balance, m2m format set rejection while queues stream, min/max buffer count limits, crop/compose `LE` and `GE` selection constraints, scaler ratio rejection, timestamp propagation from source to destination, abort during active job, and frame-done completion for RGB, YUV planar, tiled, rotated, and alpha formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-m2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-regs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-regs.c

## Purpose
`gsc-regs.c` is the low-level G-Scaler register programming layer. It converts the active `struct gsc_ctx` source/destination frames, controls, scaler ratios, paths, and DMA addresses into MMIO writes defined by `gsc-regs.h`.

## Important APIs, Types, and Functions
Reset and interrupt helpers include `gsc_hw_set_sw_reset()`, `gsc_wait_reset()`, `gsc_hw_set_frm_done_irq_mask()`, and `gsc_hw_set_gsc_irq_enable()`. Buffer helpers program masks and addresses with `gsc_hw_set_input_buf_masking()`, `gsc_hw_set_output_buf_masking()`, `gsc_hw_set_input_addr()`, and `gsc_hw_set_output_addr()`. Pipeline setup is handled by `gsc_hw_set_input_path()`, `gsc_hw_set_in_size()`, `gsc_hw_set_in_image_format()`, `gsc_hw_set_output_path()`, `gsc_hw_set_out_size()`, `gsc_hw_set_out_image_format()`, `gsc_hw_set_prescaler()`, `gsc_hw_set_mainscaler()`, `gsc_hw_set_rotation()`, `gsc_hw_set_global_alpha()`, and `gsc_hw_set_sfr_update()`.

## Control Flow
The m2m run path writes DMA addresses for the selected buffer slot and, when parameters are dirty, enables buffer slots and interrupts, computes scaler data in the core layer, then calls these helpers in input, output, scaler, rotation, and alpha order. Each helper reads the relevant control register, clears only the fields it owns, sets format/path/rotation bits from `ctx`, and writes the result back. `gsc_hw_set_sfr_update()` is the final handoff that tells hardware to latch shadow registers.

## State and Persistence
State is entirely MMIO-backed and volatile. The helper functions do not keep a software shadow, so correctness depends on clearing masks before setting new fields and on the caller serializing access with the device spinlock. Reset polling waits up to 50 ms for `GSC_SW_RESET` to clear.

## Dependencies and Integration Points
The file depends on Linux `readl()`/`writel()`, delay helpers, `gsc-core.h` frame/control structures, and the register field macros in `gsc-regs.h`. It is consumed by the GSC mem2mem and core interrupt/control paths.

## Risks and Edge Cases
Format decisions are tightly coupled to `gsc_fmt` fields such as `num_comp`, `num_planes`, `depth`, chroma order, and tiled state; inconsistent format descriptors will program invalid hardware combinations. Rotation swaps output scaled dimensions for 90/270 degrees. RGB color range selection depends on V4L2 colorspace. Output local path forces YUV444 rather than DMA layout. Address writes cast DMA addresses to register-width values and assume the hardware-visible address fits the register layout.

## Test Signals
Tests should observe reset completion, IRQ mask/enable toggles, correct MMIO fields for single-, two-, and three-plane formats, tiled NV12 handling, chroma order variants, RGB565/RGB32 range and alpha fields, 0/90/180/270 rotations plus flips, scaler ratio register values, and shadow register update before hardware enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-regs.h

## Purpose
`gsc-regs.h` defines the G-Scaler MMIO register offsets and bitfield construction macros used by `gsc-regs.c`. It is the hardware contract for enable/reset/IRQ, input and output formats, scaling ratios, image sizes, offsets, and DMA base-address slots.

## Important APIs, Types, and Functions
The header exports constants for `GSC_ENABLE`, `GSC_SW_RESET`, `GSC_IRQ`, `GSC_IN_CON`, `GSC_SRCIMG_SIZE`, `GSC_SRCIMG_OFFSET`, `GSC_CROPPED_SIZE`, `GSC_OUT_CON`, `GSC_SCALED_SIZE`, prescaler/main-scaler ratio registers, destination size/offset registers, and Y/Cb/Cr input/output address mask/base registers. It provides field macros such as `GSC_SRCIMG_WIDTH(x)`, `GSC_CROPPED_HEIGHT(x)`, `GSC_OUT_GLOBAL_ALPHA(x)`, `GSC_PRESC_H_RATIO(x)`, and indexed address macros like `GSC_IN_BASE_ADDR_Y(n)`.

## Control Flow
There is no executable control flow. The macros are composed by the register helper layer before `writel()` calls.

## State and Persistence
No software state is stored here. The values describe volatile hardware registers.

## Dependencies and Integration Points
This header is included indirectly through `gsc-core.h` and directly supports `gsc-regs.c`. Its field names mirror the G-Scaler hardware block and must remain synchronized with format and scaler logic in the GSC core.

## Risks and Edge Cases
Several macros shift caller-provided values without range checking, so callers must clamp dimensions, offsets, ratios, and alpha before composing register fields. The indexed DMA base macros encode fixed slot spacing; using an index beyond the hardware buffer count would address unintended registers. Typographical names such as `OEDER` are part of the internal API and should be changed only with all users.

## Test Signals
Compile-time coverage comes from all helper call sites resolving these macros. Runtime validation is register trace or hardware behavior for every supported format/path: enable, reset, frame-done IRQ, crop/scale sizes, input/output path selection, buffer masks, and indexed Y/Cb/Cr address programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/Kconfig

## Purpose
This Kconfig file declares the Samsung S5P/Exynos4 camera subsystem menu and build-time feature switches for FIMC, MIPI-CSIS, FIMC-LITE, and FIMC-IS support.

## Important APIs, Types, and Functions
`VIDEO_SAMSUNG_EXYNOS4_IS` is the top-level tristate and selects media-controller, V4L2 subdev API, and V4L2 fwnode support. `VIDEO_EXYNOS4_IS_COMMON` builds shared helpers. `VIDEO_S5P_FIMC` enables the FIMC/CAMIF camera interface and mem2mem postprocessor. `VIDEO_S5P_MIPI_CSIS` enables the MIPI-CSI2 receiver. `VIDEO_EXYNOS_FIMC_LITE` enables FIMC-LITE. `VIDEO_EXYNOS4_FIMC_IS` enables the Exynos4x12 imaging subsystem, firmware loader, and DMA support. `VIDEO_EXYNOS4_ISP_DMA_CAPTURE` optionally adds ISP direct DMA capture and defaults to enabled when FIMC-IS is selected.

## Control Flow
There is no runtime control flow. Build configuration gates compilation by dependencies on V4L platform drivers, OF, common clock, I2C, DMA, regulator, SoC symbols, and compile-test.

## State and Persistence
Configuration state is persisted in the kernel `.config`. It determines which modules or built-in objects exist but stores no runtime driver state.

## Dependencies and Integration Points
The selections tie this directory into V4L2, media controller, videobuf2 DMA-contig, mem2mem, firmware loading, MFD syscon, fwnode parsing, and platform-specific Exynos/S5PV210 architecture symbols. The `Makefile` consumes these symbols to produce `s5p-fimc`, `s5p-csis`, `exynos-fimc-lite`, `exynos-fimc-is`, and `exynos4-is-common` objects.

## Risks and Edge Cases
Selecting FIMC requires I2C even for configurations primarily using memory-to-memory operation. FIMC-IS depends on external firmware and setfile assets at runtime, which Kconfig cannot validate. `COMPILE_TEST` can build drivers outside native platforms, so probe paths must handle missing DT resources gracefully.

## Test Signals
Important signals are `allyesconfig`/`allmodconfig` build coverage, module names matching help text, dependency failures when required subsystems are absent, successful compile-test on non-Exynos architectures, and optional inclusion/exclusion of `fimc-isp-video.o` through `VIDEO_EXYNOS4_ISP_DMA_CAPTURE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/Makefile

## Purpose
The Makefile maps the Kconfig symbols for the Exynos4 camera subsystem to concrete object lists and loadable module targets.

## Important APIs, Types, and Functions
It builds `s5p-fimc-objs` from FIMC core, register, mem2mem, capture, and media-device code. It builds `exynos-fimc-lite-objs`, `s5p-csis-objs`, and `exynos4-is-common-objs`. `exynos-fimc-is-objs` combines FIMC-IS core, ISP, sensor, register, parameter, error, and ISP-I2C code, with `fimc-isp-video.o` appended when `CONFIG_VIDEO_EXYNOS4_ISP_DMA_CAPTURE=y`.

## Control Flow
There is no runtime control flow. Kbuild expands `obj-$(CONFIG_...)` lines to include or omit each module or built-in object.

## State and Persistence
Build state is produced under the kernel object tree. The file stores no runtime state.

## Dependencies and Integration Points
This file integrates the directory with Kbuild and the Kconfig symbols defined in the sibling `Kconfig`. Object grouping determines module boundaries and therefore symbol visibility and initialization order within each module.

## Risks and Edge Cases
Changing object membership can break module init dependencies, especially FIMC-IS registering its private ISP-I2C driver before the platform driver. Optional ISP DMA capture must remain conditional or references to video capture objects may appear without the corresponding Kconfig support.

## Test Signals
Build tests should check each individual symbol as module and built-in, verify `exynos-fimc-is` links with and without ISP DMA capture, and confirm module names match user-visible Kconfig help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/common.c

## Purpose
`common.c` provides shared helper routines exported to Samsung Exynos camera subsystem drivers. It locates the remote sensor at the head of a media pipeline and fills common V4L2 capability strings.

## Important APIs, Types, and Functions
`fimc_find_remote_sensor()` walks upstream through media pads until it finds a V4L2 subdevice whose group id is `GRP_ID_FIMC_IS_SENSOR` or `GRP_ID_SENSOR`. `__fimc_vidioc_querycap()` copies the device driver name into the V4L2 `driver` and `card` fields. Both functions are exported with `EXPORT_SYMBOL()`.

## Control Flow
`fimc_find_remote_sensor()` starts at entity pad 0, follows remote source pads while the current pad is a sink, converts V4L2 subdev entities to `struct v4l2_subdev`, and stops on a matching sensor group id or a broken/non-subdev link. `__fimc_vidioc_querycap()` is a direct string-copy helper.

## State and Persistence
The helpers are stateless and derive results from the live media graph and device driver metadata.

## Dependencies and Integration Points
The file depends on media entity and V4L2 subdev helpers plus Exynos FIMC group ids from `media/drv-intf/exynos-fimc.h`. FIMC capture uses `fimc_find_remote_sensor()` when enabling links and inherits sensor controls, while capture video nodes use `__fimc_vidioc_querycap()`.

## Risks and Edge Cases
The graph walk assumes pad 0 is the sink on intermediate subdevices, matching this subsystem's convention. Broken links or non-subdev entities return `NULL`. Callers must hold the graph mutex or otherwise guarantee streaming graph stability, as documented in the comment.

## Test Signals
Validate sensor discovery through direct sensor-to-FIMC links, CSIS/FIMC-LITE intermediate links, FIMC-IS sensor group ids, disconnected links returning `NULL`, and querycap strings on all video nodes using the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/common.h

## Purpose
`common.h` declares the shared Exynos4 camera helper functions implemented in `common.c`.

## Important APIs, Types, and Functions
It declares `fimc_find_remote_sensor(struct media_entity *entity)` and `__fimc_vidioc_querycap(struct device *dev, struct v4l2_capability *cap)`.

## Control Flow
There is no executable control flow.

## State and Persistence
The header stores no state and only exposes helper prototypes.

## Dependencies and Integration Points
It includes Linux device and videodev2 definitions plus media entity and V4L2 subdev headers so FIMC, FIMC-IS, and shared capture code can use common helper declarations.

## Risks and Edge Cases
The header intentionally has a small API surface. Any signature changes must be coordinated with exported symbol users and module builds.

## Test Signals
Compile coverage of FIMC capture and any other users verifies declarations and exported definitions remain aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-capture.c

## Purpose
`fimc-capture.c` implements the FIMC camera capture video node and FIMC processing subdevice. It manages media graph links, pipeline format negotiation, capture vb2 queues, frame buffer scheduling, interrupt-time buffer completion, crop/compose selection, and suspend/resume cleanup for camera and ISP writeback capture.

## Important APIs, Types, and Functions
Hardware and stream lifecycle functions include `fimc_capture_hw_init()`, `fimc_capture_state_cleanup()`, `fimc_stop_capture()`, `fimc_capture_suspend()`, and `fimc_capture_resume()`. IRQ-time scheduling is in `fimc_capture_irq_handler()` and `fimc_capture_config_update()`. vb2 callbacks are `queue_setup()`, `buffer_prepare()`, `buffer_queue()`, `start_streaming()`, and `stop_streaming()`. User-facing ioctl helpers include format, input, stream, reqbufs, and selection handlers such as `__video_try_or_set_format()`, `fimc_cap_streamon()`, and `fimc_cap_s_selection()`. Media/subdev integration uses `fimc_link_setup()`, `fimc_pipeline_try_format()`, `fimc_pipeline_validate()`, `fimc_subdev_get_fmt()`, `fimc_subdev_set_fmt()`, `fimc_subdev_get_selection()`, `fimc_subdev_set_selection()`, `fimc_initialize_capture_subdev()`, and `fimc_unregister_capture_subdev()`.

## Control Flow
Probe initializes the capture subdev, and the subdev `registered()` callback creates both mem2mem and capture video nodes. Opening capture blocks concurrent m2m use, resumes runtime PM, opens the media pipeline for the first file handle, and applies default format. Format setting either drives the whole upstream pipeline or, in user-subdev API mode, trusts active subdev formats after validation. Stream-on starts the media pipeline, stores current source configuration, validates links when needed, and delegates to vb2. When enough buffers are queued, `buffer_queue()` or `start_streaming()` programs output addresses, activates capture, and starts upstream streaming. Each frame interrupt completes the oldest active buffer, moves a pending buffer into the hardware slot ring, optionally supplies embedded-data buffers to CSIS, applies deferred configuration changes, and stops capture when the last buffer drains.

## State and Persistence
Runtime state lives in `fimc->state`, `fimc->vid_cap`, and the capture `struct fimc_ctx`. `ST_CAPT_*` bits represent pending/running/streaming/suspended/shutdown/JPEG/config-apply states. `pending_buf_q`, `active_buf_q`, `active_buf_cnt`, `buf_index`, and `frame_count` track buffer ownership. Formats are stored in `ci_fmt`, `wb_fmt`, `s_frame`, and `d_frame`; source configuration is copied from sensor hostdata at stream-on. No persistent storage exists.

## Dependencies and Integration Points
The file depends on V4L2 video ioctl helpers, V4L2 subdev pad operations, media controller graph APIs, vb2 DMA-contig, runtime PM, FIMC register helpers, `media-dev.h` pipeline callbacks, common sensor discovery, and optional MIPI-CSIS `s_rx_buffer` support for embedded metadata. It integrates with the core IRQ handler via `fimc_capture_irq_handler()`.

## Risks and Edge Cases
Capture and mem2mem are mutually exclusive through state bits and the device mutex. JPEG/user-defined formats disable scaling/cropping and require sensor frame descriptors to size payloads. The buffer slot ring has `FIMC_MAX_OUT_BUFS` hardware slots while user-requested buffer count may differ. Suspend cleanup moves active buffers back to pending, whereas normal stop completes them with error. Several paths depend on graph locking discipline to avoid nested media locks. Pipeline validation must catch mismatched pad formats or undersized compressed buffers before streaming.

## Test Signals
Test direct camera, CSIS, FIMC-LITE, and FIMC-IS writeback pipelines; default format on first open; link setup and sensor control inheritance; TRY/S_FMT with and without user-subdev API; JPEG payload/frame descriptor handling; one-buffer and multi-buffer capture; metadata plane handoff to CSIS; crop/compose bounds and deferred config updates during streaming; streamoff cleanup; suspend/resume with queued buffers; and sensor end-of-frame notifications completing still capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-core.c

## Purpose
`fimc-core.c` provides common FIMC/CAMIF device infrastructure: supported pixel formats, scaler calculations, DMA address derivation, V4L2 controls, format helpers, clock/probe/remove handling, IRQ dispatch, runtime PM, and platform/OF variant data.

## Important APIs, Types, and Functions
Format helpers include `fimc_get_format()`, `fimc_find_format()`, `fimc_adjust_mplane_format()`, and `__fimc_get_format()`. Scaler and DMA helpers include `fimc_check_scaler_ratio()`, `fimc_set_scaler_info()`, `fimc_prepare_addr()`, `fimc_set_yuv_order()`, and `fimc_prepare_dma_offset()`. Control APIs are `fimc_ctrls_create()`, `fimc_ctrls_delete()`, `fimc_ctrls_activate()`, and `fimc_alpha_ctrl_update()`. Driver lifecycle is handled by `fimc_parse_dt()`, `fimc_probe()`, PM callbacks, `fimc_remove()`, `fimc_register_driver()`, and `fimc_unregister_driver()`. `fimc_irq_handler()` dispatches completion to either mem2mem or capture paths.

## Control Flow
Probe parses DT or platform data, validates the entity id, initializes locks and waitqueues, maps registers, acquires clocks, sets bus clock rate, enables the bus clock, requests the IRQ, initializes the capture subdev, enables runtime PM, and configures DMA segment limits. Runtime resume enables the gate clock, resets hardware, and resumes capture or mem2mem. Runtime suspend stops capture or m2m, then disables the gate clock. The IRQ handler clears hardware IRQ state, then either completes a pending m2m job, handles m2m suspend synchronization, or forwards capture frame handling.

## State and Persistence
Device state is kept in `struct fimc_dev`, especially `state` bits, `variant`, `drv_data`, clocks, mapped registers, `m2m`, and `vid_cap`. Per-operation state lives in `struct fimc_ctx`, frame descriptors, scaler values, effect settings, and controls. No persistent storage is used; hardware configuration is regenerated after reset/resume.

## Dependencies and Integration Points
The file depends on V4L2/vb2, media-controller headers, runtime PM, common clock framework, platform/OF APIs, syscon regmap for ISP writeback, FIMC register helpers, media-device pipeline code, and the FIMC mem2mem/capture modules. OF compatibles include S5PV210, Exynos4210, and Exynos4212 variants.

## Risks and Edge Cases
Scaler math rejects 64x or greater downscale ratios and swaps target dimensions for rotation. DMA address derivation assumes plane layout consistency for packed, planar, multi-planar, metadata, and tiled formats. Runtime PM chooses capture over m2m when capture is busy. `fimc_probe()` has early-return paths after clock enable where cleanup must remain correct. OF `samsung,lcd-wb` instances are rejected because they are not normal camera/video postprocessor nodes.

## Test Signals
Build and probe each compatible, validate DT pixel-limit parsing, clock rate/enable failure unwinding, IRQ routing for m2m and capture, scaler ratio and copy-mode calculations, DMA addresses for all supported formats, control activation/inactivation and alpha range updates, runtime suspend/resume during capture and m2m jobs, and remove cleanup of subdev, DMA limits, and clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-core.h

## Purpose
`fimc-core.h` is the central internal API for the FIMC/CAMIF driver. It defines device state flags, datapath and color enums, frame/scaler/buffer/control/device structures, inline helpers, queue helpers, and cross-file prototypes.

## Important APIs, Types, and Functions
Key types include `struct fimc_dma_offset`, `struct fimc_effect`, `struct fimc_scaler`, `struct fimc_addr`, `struct fimc_vid_buffer`, `struct fimc_frame`, `struct fimc_m2m_device`, `struct fimc_vid_cap`, `struct fimc_pix_limit`, `struct fimc_variant`, `struct fimc_drvdata`, `struct fimc_dev`, `struct fimc_ctrls`, and `struct fimc_ctx`. Important inline helpers include `file_to_ctx()`, `set_frame_bounds()`, `set_frame_crop()`, `fimc_get_format_depth()`, `fimc_capture_active()`, `fimc_ctx_state_set()`, `fimc_ctx_state_is_set()`, `tiled_fmt()`, `fimc_jpeg_fourcc()`, `fimc_user_defined_mbus_fmt()`, `fimc_get_alpha_mask()`, `ctx_get_frame()`, and active/pending queue add/pop helpers.

## Control Flow
The header does not own top-level flow, but its inline helpers define shared locking and queue manipulation behavior. `fimc_capture_active()` takes the device spinlock before testing capture run/pending bits. Context state helpers serialize `ctx->state` through the device spinlock. Buffer queue helpers assume the caller already holds `fimc->slock`.

## State and Persistence
The header defines the in-memory layout for all FIMC runtime state. Important state bit groups separate low-power, mem2mem, and capture operation. Frame structures persist current negotiated format/crop/DMA offsets only for the lifetime of the context.

## Dependencies and Integration Points
It includes platform, regmap, spinlock, V4L2, vb2, media entity, mem2mem, mediabus, and Exynos FIMC interface headers. It ties together `fimc-core.c`, `fimc-m2m.c`, `fimc-capture.c`, and `fimc-reg.c`, and exposes registration hooks used by the media-device layer.

## Risks and Edge Cases
Inline queue helpers are not self-locking and can corrupt lists if used without `slock`. `ctx_get_frame()` maps output buffers to source frames only for m2m contexts; capture contexts use capture buffer types for destination frames. State bits are shared across capture and m2m, so additions must avoid semantic overlap. The prototype for `fimc_register_m2m_device()` includes a `v4l2_device *` parameter here, so it must stay synchronized with the implementation in this source tree.

## Test Signals
Compile coverage across FIMC core/m2m/capture/register files is the main signal. Runtime tests should exercise state helpers under concurrent streamon/streamoff, active/pending queue transitions, JPEG/user-defined helpers, tiled format paths, alpha mask values, and frame selection for both capture and m2m buffer types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-command.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-command.h

## Purpose
`fimc-is-command.h` defines the mailbox command protocol between the host CPU and the FIMC-IS firmware running on the ISP Cortex-A5, plus packed register-layout structures for the shared MCU control mailbox block.

## Important APIs, Types, and Functions
Host-to-IS commands include scenario changes, stream on/off, parameter set/get, tune/status, sensor open/close, power down, setfile address/load, and message test/config commands. IS-to-host commands include sensor count requests, shot/face marks, frame done, AA done, not-ready, and reply done/not-done. `enum fimc_is_scenario` selects preview/capture still/video configurations. `struct is_common_regs` and `struct is_mcuctl_reg` model the common ISSR mailbox and interrupt/control register area.

## Control Flow
There is no executable flow. `fimc-is.c` and `fimc-is-regs.c` write command ids and arguments into `MCUCTL_REG_ISSR(n)` registers using these constants, then signal firmware with an interrupt generation register. The IRQ handler decodes firmware replies using the same constants.

## State and Persistence
No software state is stored here. The packed structures describe volatile MMIO layout and firmware ABI state.

## Dependencies and Integration Points
The header is included by the FIMC-IS core, register, and parameter paths. Its numeric values must match the firmware command-set version `FIMC_IS_COMMAND_VER`.

## Risks and Edge Cases
Any command id or packed layout mismatch breaks host/firmware synchronization. The header provides fixed four-argument common register arrays, while some driver-side structures allow more decoded arguments, so call sites must respect the actual hardware mailbox fields they read.

## Test Signals
Validate firmware boot handshake (`IHC_GET_SENSOR_NUM`), sensor open/close, setfile address/load, mode changes for all scenarios, stream on/off replies, set-parameter completion, not-done error reporting, and register dumps matching the expected ISSR layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-errno.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-errno.c

## Purpose
`fimc-is-errno.c` translates FIMC-IS firmware error numbers into symbolic strings for kernel logs.

## Important APIs, Types, and Functions
The sole exported function is `fimc_is_strerr(unsigned int error)`. It masks off `IS_ERROR_TIME_OUT_FLAG` before switching on the base error value and returns a string literal for general, sensor, ISP, DRC, and FD errors, falling back to `"Unknown"`.

## Control Flow
The FIMC-IS general IRQ handler calls this helper when it receives `IH_REPLY_NOT_DONE`. The function strips the timeout flag, matches known enum constants from `fimc-is-errno.h`, and returns the string used in `pr_err()` output.

## State and Persistence
The function is stateless and stores no data beyond string literals in the text/rodata segment.

## Dependencies and Integration Points
It depends on error constants from `fimc-is-errno.h` and integrates with firmware reply handling in `fimc-is.c`.

## Risks and Edge Cases
The mapping is incomplete relative to all constants in the header; unknown or newer firmware errors print `"Unknown"`. Timeout status is only indicated separately by callers checking `IS_ERROR_TIME_OUT_FLAG`, not by the returned string.

## Test Signals
Test known general, sensor, ISP, DRC, and FD errors, timeout-flag masking, unknown-value fallback, and IRQ not-done logs containing both command id and decoded error text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-errno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-errno.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-errno.h

## Purpose
`fimc-is-errno.h` defines the FIMC-IS firmware error ABI: high-level firmware command failures, per-subblock power/path/frame errors, set-parameter validation errors, and the timeout flag.

## Important APIs, Types, and Functions
The first anonymous enum defines `IS_ERROR_*` values grouped by general, sensor, ISP, DRC, scaler, ODC, DIS, TDNR, scalerP, FD, and unknown categories. `IS_ERROR_TIME_OUT_FLAG` marks timeout-qualified errors. `enum fimc_is_error` defines lower-level set-parameter errors for common/control/OTF/DMA/global/sensor/ISP/FD/scaler parameter validation. The header declares `fimc_is_strerr()`.

## Control Flow
There is no executable flow. The constants are consumed by firmware reply logging and by parameter structure `err` fields.

## State and Persistence
No runtime state is stored here. Values are part of the host/firmware ABI and must remain stable for matching firmware.

## Dependencies and Integration Points
The header is included by FIMC-IS core, register, and parameter code. `fimc-is-errno.c` implements the string mapping for selected top-level error values.

## Risks and Edge Cases
The driver only decodes a subset of all defined errors to strings. Numeric ranges overlap in conceptual categories between top-level `IS_ERROR_*` and set-parameter `ERROR_*` values, so callers must know which ABI field they are interpreting. The version macro is decimal-looking but written with a leading zero, so it should be treated as a legacy marker rather than arithmetic input.

## Test Signals
Useful checks include compilation of all enum users, not-done logging for representative error categories, timeout-flag handling, parameter command failure recovery, and firmware compatibility tests against expected numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-i2c.c

## Purpose
`fimc-is-i2c.c` registers a Linux I2C adapter that represents the ISP-owned sensor control bus. The host CPU does not perform transfers; the adapter exists so sensor client devices can bind and so runtime PM can propagate through the device hierarchy.

## Important APIs, Types, and Functions
`struct fimc_is_i2c` stores an `i2c_adapter` and the `i2c_isp` clock. `is_i2c_func()` advertises `I2C_FUNC_I2C` through an otherwise empty `i2c_algorithm`. Probe/remove are `fimc_is_i2c_probe()` and `fimc_is_i2c_remove()`. Runtime/system PM callbacks enable or disable the bus clock. Module-level registration is exposed through `fimc_is_register_i2c_driver()` and `fimc_is_unregister_i2c_driver()`.

## Control Flow
The FIMC-IS module init registers this platform driver before the main FIMC-IS platform driver. Probe allocates state, gets the `i2c_isp` clock, initializes and registers the I2C adapter, enables runtime PM, and clears `ignore_children` after adapter registration. Runtime resume prepares/enables the clock, and runtime suspend disables it. Remove disables runtime PM and unregisters the adapter.

## State and Persistence
State is per platform device and contains only the adapter and clock handle. Runtime PM state is managed by the PM core. There is no persistent storage and no actual host-side transfer state.

## Dependencies and Integration Points
The file depends on the I2C core, common clock framework, runtime PM, platform bus, OF matching for `samsung,exynos4212-i2c-isp`, and FIMC-IS module init/exit.

## Risks and Edge Cases
Because the algorithm has no transfer callback, any client attempting normal I2C transactions would fail despite advertised I2C functionality; the design assumes firmware controls the bus. Clearing `ignore_children` is important for sensor client PM propagation. Probe-time client PM calls are assumed absent, as noted in the comments.

## Test Signals
Validate adapter registration under the ISP I2C DT node, sensor child device binding without host transfers, runtime PM clock enable/disable from child activity, system suspend/resume when runtime active or suspended, and clean unregister during module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-i2c.h

## Purpose
`fimc-is-i2c.h` declares module-internal registration helpers for the FIMC-IS ISP I2C platform driver.

## Important APIs, Types, and Functions
It declares `fimc_is_register_i2c_driver()` and `fimc_is_unregister_i2c_driver()`.

## Control Flow
There is no executable flow. The FIMC-IS module init/exit functions call these helpers.

## State and Persistence
The header stores no state.

## Dependencies and Integration Points
It is included by `fimc-is.c` so the main FIMC-IS module can register the ISP I2C adapter driver before registering the FIMC-IS platform driver.

## Risks and Edge Cases
The header intentionally exposes only registration hooks. Init ordering is important: failure to register the main platform driver should unregister this I2C driver to avoid leaving a partial module setup.

## Test Signals
Compile-time checks and module init failure-injection should verify that registration/unregistration symbols match the implementation and unwind order remains correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-param.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-param.c

## Purpose
`fimc-is-param.c` maintains the host-side FIMC-IS pipeline parameter cache and copies dirty parameter blocks into the DMA-shared firmware region before `HIC_SET_PARAMETER`. It also provides helpers to initialize and mutate ISP, sensor, DRC, and face-detection parameters.

## Important APIs, Types, and Functions
Low-level update helpers are `__fimc_is_hw_update_param()`, `__get_pending_param_count()`, and `__is_hw_update_params()`. Configuration helpers include `__is_set_frame_size()`, `fimc_is_hw_get_sensor_max_framerate()`, `__is_set_sensor()`, `__is_set_isp_flash()`, `__is_set_isp_awb()`, `__is_set_isp_effect()`, `__is_set_isp_iso()`, `__is_set_isp_adjust()`, `__is_set_isp_metering()`, `__is_set_isp_afc()`, `__is_set_drc_control()`, `__is_set_fd_control()`, the `__is_set_fd_config_*()` family, and `fimc_is_set_initial_params()`.

## Control Flow
Callers update fields in `is->config[is->config_index]` and mark parameter bits with `fimc_is_set_param_bit()`. Before sending parameters, `__is_hw_update_params()` walks the dirty bitmaps, copies selected 64-byte parameter blocks into `is->is_p_region->parameter`, and leaves the firmware command layer to write the mailbox and wait for completion. Initialization fills defaults for all four scenarios, enabling ISP/DRC/FD OTF paths, disabling unused DMA inputs/outputs, configuring default 3A, flash, AWB, ISO, metering, AFC, and FD options.

## State and Persistence
The primary state is `struct chain_config config[IS_SC_MAX]`, per-scenario dirty bitmaps `p_region_index[0..1]`, and the shared DMA parameter region pointed to by `is->is_p_region`. Updates are volatile and synchronized partly by `is->slock` for pending-count reads; memory barriers are used by the command layer before firmware consumption.

## Dependencies and Integration Points
The file depends on FIMC-IS core structures, command/error constants, register command helpers, V4L2 media bus frame formats, bit operations, and sensor metadata. `fimc-is.c` calls `fimc_is_set_initial_params()` during hardware initialization, while ISP controls call the individual setters and then `fimc_is_itf_s_param()`.

## Risks and Edge Cases
Only a subset of the parameter ABI is copied by `__fimc_is_hw_update_param()`; dirty bits for unsupported blocks would return `-EINVAL` or be ignored by loop ranges. FD parameter bits live above bit 31, and helpers manually inspect `p_region_index[1]` with `PARAM_FD_CONFIG - 32`, so bit-index mistakes are likely. Some defaults set duplicate `width` fields in DMA input structures and rely on packed ABI layout. Sensor framerate defaults depend on only the first `is->sensor` entry.

## Test Signals
Validate initial parameter upload for all scenarios, dirty bit counts matching copied blocks, frame-size updates marking ISP/DRC/FD OTF bits, sensor framerate zero and explicit FPS behavior, ISP controls setting combined command masks, FD config command accumulation across multiple setters, set-parameter timeout recovery, and firmware rejection logs for invalid parameter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-param.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-param.h

## Purpose
`fimc-is-param.h` defines the FIMC-IS firmware parameter-region ABI, including parameter bit numbers, timeout and default capture constants, control/format/error values, packed parameter structures, tuning/EXIF/frame/face/shared-memory structures, and parameter helper prototypes.

## Important APIs, Types, and Functions
Important definitions include `FIMC_IS_CONFIG_TIMEOUT`, default frame sizes/rates, `FIMC_IS_REGION_VER`, `FIMC_IS_MAGIC_NUMBER`, `FIMC_IS_PARAM_MAX_SIZE`, `enum is_param_bit`, FIMC-IS interrupt numbers, OTF/DMA/control command values, ISP 3A/flash/AWB/effect/ISO/adjust/metering/AFC constants, and FD configuration constants. Packed ABI types include `struct param_control`, `param_otf_input`, `param_dma_input`, `param_otf_output`, `param_dma_output`, all ISP/FD/scaler parameter structs, `struct is_param_region`, `struct is_region`, `struct is_share_region`, and `struct sensor_open_extended`.

## Control Flow
There is no executable control flow, but the layout controls how `fimc-is-param.c` copies 64-byte parameter entries and how firmware interprets the DMA-shared `struct is_region`.

## State and Persistence
The header defines volatile shared-memory state exchanged with firmware. The driver allocates the region in coherent DMA memory; the ABI fields persist only while the driver and firmware session are active.

## Dependencies and Integration Points
The header is included by the FIMC-IS core, parameter update code, ISP subdevice controls, and register command layer. It depends on packed structure layout remaining compatible with the firmware blob and setfile.

## Risks and Edge Cases
Packed structure sizes and reserved arrays must keep each parameter block at `FIMC_IS_PARAM_MAX_SIZE`; accidental field changes can corrupt following firmware fields. `FIMC_IS_PARAM_SIZE` is based on `FIMC_IS_REGION_SIZE + 1`, which should not be confused with a byte-exact struct size. The ABI includes many blocks not fully manipulated by current code, so unused constants may be firmware-facing but untested. FD bits cross the first 32-bit dirty bitmap boundary.

## Test Signals
Use compile-time size/offset checks where possible, firmware boot magic-number validation, successful initial parameter upload, frame/face metadata interpretation, DMA2 output address array offset use by ISP video, shared-region firmware version/debug data, and failure injection for invalid OTF/DMA/FD parameter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-regs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-regs.c

## Purpose
`fimc-is-regs.c` implements mailbox/register operations used to communicate with FIMC-IS firmware: clearing interrupts, waiting for firmware mailbox readiness, sending host commands, reading reply arguments, setting ISP buffer masks, and synchronous interface wrappers for parameter and mode changes.

## Important APIs, Types, and Functions
Interrupt helpers include `fimc_is_fw_clear_irq1()`, `fimc_is_fw_clear_irq2()`, and `fimc_is_hw_set_intgr0_gd0()`. Mailbox readiness and argument helpers are `fimc_is_hw_wait_intmsr0_intmsd0()` and `fimc_is_hw_get_params()`. Command helpers include `fimc_is_hw_set_param()`, `fimc_is_hw_set_sensor_num()`, `fimc_is_hw_close_sensor()`, `fimc_is_hw_get_setfile_addr()`, `fimc_is_hw_load_setfile()`, `fimc_is_hw_change_mode()`, `fimc_is_hw_stream_on()`, `fimc_is_hw_stream_off()`, and `fimc_is_hw_subip_power_off()`. Synchronous wrappers are `fimc_is_itf_s_param()` and `fimc_is_itf_mode_change()`.

## Control Flow
Most command helpers wait until interrupt mask/status register 0 indicates the mailbox slot is idle, write a command id and arguments to ISSR registers, then generate host-to-firmware interrupt GD0. `fimc_is_itf_s_param()` optionally copies dirty parameters into the shared region, clears the completion bit, sends `HIC_SET_PARAMETER`, and waits for the IRQ handler to set `IS_ST_BLOCK_CMD_CLEARED`. `fimc_is_itf_mode_change()` sends the scenario command corresponding to `config_index` and waits for `IS_ST_CHANGE_MODE`.

## State and Persistence
State is split between volatile MCUCTL registers and driver state bits in `is->state`. Parameter dirty bitmaps in `is->config` are passed as two ISSR arguments. No persistent storage exists.

## Dependencies and Integration Points
The file depends on inline `mcuctl_read()`/`mcuctl_write()` from `fimc-is.h`, command constants from `fimc-is-command.h`, parameter update helpers from `fimc-is-param.h`, and the core waitqueue/state-bit mechanism in `fimc-is.c`.

## Risks and Edge Cases
`fimc_is_hw_wait_intmsr0_intmsd0()` spins for about 2 ms and returns a timeout, but many command helpers ignore that return value and continue writing registers. `fimc_is_hw_get_params()` limits reads to four arguments, while driver-side reply arrays are larger. `fimc_is_hw_set_isp_buf_mask()` treats a single set bit as not enough buffers and only logs instead of failing. Mode-change command lookup depends on `config_index` staying below the scenario array size.

## Test Signals
Exercise all host commands with firmware present, timeout behavior when the mailbox stays busy, set-parameter completion and not-done paths, mode changes for all four scenarios, stream on/off state bits, setfile address/load handshake, close-sensor id matching, ISP DMA buffer masks, and IRQ clear side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-regs.h

## Purpose
`fimc-is-regs.h` defines FIMC-IS watchdog, MCUCTL, interrupt, ISSR mailbox, and PMU ISP register offsets and bitfield macros, plus prototypes for the register command helpers.

## Important APIs, Types, and Functions
Key register constants include `REG_WDT_ISP`, `MCUCTL_BASE`, `MCUCTL_REG_MCUCTRL`, `MCUCTL_REG_BBOAR`, interrupt generation/clear/mask/status registers 0/1/2, `MCUCTL_REG_ISSR(n)`, and PMU offsets such as `REG_PMU_ISP_ARM_CONFIGURATION`, `REG_PMU_ISP_ARM_STATUS`, and `REG_PMU_ISP_ARM_OPTION`. Bit helpers include `INTGR0_INTGD()`, `INTMSR0_GET_INTMSD()`, and related interrupt field macros. Prototypes expose IRQ clear, mailbox, stream, sensor, setfile, parameter, mode, and sub-IP power helpers.

## Control Flow
There is no executable flow. These macros are composed by `fimc-is-regs.c` and `fimc-is.c` before MMIO accesses.

## State and Persistence
No software state is stored here. The constants describe volatile hardware registers and host/firmware mailbox slots.

## Dependencies and Integration Points
The header is included by FIMC-IS core, register, and parameter code. It depends on `struct fimc_is` being declared by included core headers and on the hardware/firmware register ABI.

## Risks and Edge Cases
Register offsets are absolute within the mapped resource layout used by this driver. Any DT resource that maps a different base window will break accesses. Several bitfield macros accept unchecked indexes. The comment naming for some interrupt clear bits is easy to confuse because host-to-VIC and ISP-to-host register groups use different bit ranges.

## Test Signals
Validate firmware boot using `BBOAR` and PMU registers, host-to-IS interrupt generation, IS-to-host interrupt clear, ISSR command/reply layout, stream/setfile/sensor command register traces, and PMU power-off status polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-sensor.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-sensor.c

## Purpose
`fimc-is-sensor.c` maps OF sensor compatible strings to FIMC-IS firmware sensor metadata.

## Important APIs, Types, and Functions
It defines `s5k6a3_drvdata` with firmware sensor id `FIMC_IS_SENSOR_ID_S5K6A3` and open timeout `S5K6A3_OPEN_TIMEOUT`. The OF match table recognizes `samsung,s5k6a3`. `fimc_is_sensor_get_drvdata()` returns the matched `struct sensor_drv_data`.

## Control Flow
FIMC-IS probe scans ISP I2C child nodes and calls `fimc_is_sensor_get_drvdata()` for each sensor node. This function performs `of_match_node()` and returns match data or `NULL`.

## State and Persistence
The only state is static constant match data. Runtime sensor state is stored in `struct fimc_is_sensor` in `fimc-is.h`.

## Dependencies and Integration Points
The file depends on OF matching and `fimc-is-sensor.h`. FIMC-IS uses the returned id and timeout in `fimc_is_parse_sensor_config()` and `fimc_is_hw_open_sensor()`.

## Risks and Edge Cases
Only S5K6A3 is supported here. Additional sensors require both firmware id metadata and OF match entries. A missing match causes FIMC-IS sensor parsing to fail probe/init for that sensor.

## Test Signals
Validate OF matching for `samsung,s5k6a3`, rejection of unsupported sensors, correct firmware id passed in `HIC_OPEN_SENSOR`, and timeout behavior using the S5K6A3 open timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-sensor.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-sensor.h

## Purpose
`fimc-is-sensor.h` defines FIMC-IS sensor ids, supported sensor constants, ISP I2C bus ids, sensor metadata structures, and the OF metadata lookup prototype.

## Important APIs, Types, and Functions
Important constants are `S5K6A3_OPEN_TIMEOUT`, `S5K6A3_SENSOR_WIDTH`, `S5K6A3_SENSOR_HEIGHT`, `enum fimc_is_sensor_id`, `IS_SENSOR_CTRL_BUS_I2C0`, and `IS_SENSOR_CTRL_BUS_I2C1`. `struct sensor_drv_data` stores firmware sensor id and open timeout. `struct fimc_is_sensor` stores matched driver data, ISP I2C bus index, and test-pattern flag. The header declares `fimc_is_sensor_get_drvdata()`.

## Control Flow
There is no executable control flow. FIMC-IS parsing and open-sensor command flow consume these definitions.

## State and Persistence
The header defines in-memory sensor state fields but does not allocate or persist them.

## Dependencies and Integration Points
It includes OF and basic type headers and is included by FIMC-IS core, register, and sensor lookup code.

## Risks and Edge Cases
The enum exposes several sensor ids but only S5K6A3 has match data in the implementation. Width/height constants are not automatically enforced by the parser. The `test_pattern` byte influences initial ISP OTF input format when set by higher-level code.

## Test Signals
Compile coverage, OF sensor parsing, firmware open command arguments, default sensor framerate selection, and test-pattern initialization paths are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-sensor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is.c

## Purpose
`fimc-is.c` is the main Exynos4x12 FIMC-IS platform driver. It manages clocks, firmware and setfile loading, coherent firmware memory, Cortex-A5 ISP CPU power control, mailbox IRQ handling, sensor discovery, subdevice registration, runtime PM, debugfs firmware logs, and module init/exit including the ISP I2C adapter driver.

## Important APIs, Types, and Functions
Clock helpers are `fimc_is_get_clocks()`, `fimc_is_put_clocks()`, `fimc_is_setup_clocks()`, `fimc_is_enable_clocks()`, and `fimc_is_disable_clocks()`. Firmware/memory helpers include `fimc_is_request_firmware()`, `fimc_is_load_firmware()`, `fimc_is_alloc_cpu_memory()`, `fimc_is_free_cpu_memory()`, `fimc_is_load_setfile()`, and `fimc_is_start_firmware()`. Hardware sequencing uses `fimc_is_cpu_set_power()`, `fimc_is_wait_event()`, `fimc_is_hw_open_sensor()`, and `fimc_is_hw_initialize()`. IRQ handling is split between `fimc_is_irq_handler()` and `fimc_is_general_irq_handler()`. Probe/remove and PM are implemented by `fimc_is_probe()`, `fimc_is_remove()`, runtime/system PM callbacks, and module init/exit.

## Control Flow
Module init first registers the ISP I2C driver, then the FIMC-IS platform driver. Probe allocates `struct fimc_is`, maps MCUCTL and PMU registers, parses IRQ, gets clocks, requests IRQ, enables runtime PM, resumes the device, sets DMA segment limits, populates child platform devices, registers ISP/sensor subdevs, creates debugfs, and starts asynchronous firmware loading. Firmware loading validates size, allocates aligned coherent memory, copies firmware, extracts description/version strings, initializes shared chip fields, stores the firmware pointer, and later `fimc_is_start_firmware()` copies it into working memory and powers the A5. Initialization opens the first sensor, obtains and loads the setfile, checks firmware magic, streams off, uploads initial parameters for all scenarios, and marks init done.

## State and Persistence
`struct fimc_is` holds all runtime state: clocks, MMIO bases, IRQ waitqueue, state bits, sensor index, firmware/setfile metadata, DMA memory, shared parameter and shared-info pointers, ISP/sensor subdevices, face-detection header, per-scenario configs, locks, and debugfs dentry. Firmware and setfile contents reside in coherent memory during operation. There is no filesystem persistence beyond loading firmware files from the kernel firmware search path.

## Dependencies and Integration Points
The driver depends on OF address/IRQ/graph/platform population, firmware loader, DMA coherent allocation, vb2 DMA-contig segment limits, runtime PM, common clock, debugfs, FIMC-IS command/register/parameter/error helpers, FIMC ISP subdevice code, FIMC-IS sensor metadata, media-device pipeline infrastructure, and the ISP I2C adapter driver. It matches `samsung,exynos4212-fimc-is`.

## Risks and Edge Cases
Firmware loading is asynchronous; users must not assume firmware memory is ready before state indicates it. The firmware pointer is intentionally retained and replaced after releasing any previous one, so cleanup must release it exactly once. Memory alignment is checked against a 26-bit mask and rejects unsuitable DMA addresses. Sensor parsing supports a bounded sensor array but increments after parsing; index limit handling must prevent overflow. Many command waits depend on IRQ state bits being set by firmware replies. System suspend returns `-EBUSY` if the A5 is powered. PMU lookup supports a deprecated child-node fallback. Several error paths after runtime resume must unwind clocks, IRQ, PMU mapping, subdevs, debugfs, and DMA memory.

## Test Signals
Validate probe with complete and missing DT resources, clock parent/rate programming, runtime PM enable/disable, firmware request success/failure and size bounds, coherent memory alignment failure injection, A5 power-on/off status, firmware boot handshake, sensor open and setfile load, magic-number validation, initial parameter uploads for all scenarios, general IRQ replies including not-done errors, frame-done ISP IRQ dispatch, debugfs `fw_log`, suspend refusal while A5 is powered, and module init unwind when either I2C or platform registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is.h

## Purpose
`fimc-is.h` is the central internal header for the Exynos4x12 FIMC-IS driver. It defines firmware filenames, memory layout, clock ids, driver state bits, autofocus state enums, firmware/memory/setfile/command/config structures, the main `struct fimc_is`, MMIO accessors, memory barriers, parameter dirty-bit helpers, and core function prototypes.

## Important APIs, Types, and Functions
Important constants include `FIMC_IS_DRV_NAME`, firmware and setfile filenames, firmware load/power timeouts, sensor count, CPU memory size, debug/shared/region offsets, firmware metadata lengths, firmware size bounds, and ISP clock frequencies. Key enums define `ISS_CLK_*` ids and `IS_ST_*` state bits. Key structures include `struct fimc_is_firmware`, `struct fimc_is_memory`, `struct i2h_cmd`, `struct h2i_cmd`, `struct fimc_is_setfile`, `struct chain_config`, and `struct fimc_is`. Inline helpers include `fimc_isp_to_is()`, `__get_curr_is_config()`, `fimc_is_mem_barrier()`, `fimc_is_set_param_bit()`, `fimc_is_set_param_ctrl_cmd()`, `mcuctl_read/write()`, and `pmuisp_read/write()`.

## Control Flow
The header does not own top-level flow, but its inline helpers are used throughout the driver. Register helpers perform raw MMIO reads/writes against mapped MCUCTL and PMU bases. Parameter helpers mark dirty bits in the active `chain_config`. `fimc_is_mem_barrier()` enforces ordering before firmware consumes shared memory.

## State and Persistence
`struct fimc_is` defines the persistent in-kernel state for one platform device lifetime. State bits represent firmware power, sensor open, setfile loaded, init done, stream on/off, mode changes, command completion, zoom, and sub-IP power. Firmware memory and shared parameter pointers are valid only after successful asynchronous firmware allocation.

## Dependencies and Integration Points
The header includes clock, platform, spinlock, V4L2 controls, vb2, ISP subdevice, command, sensor, parameter, and register headers. It binds FIMC-IS core code to ISP video/control, sensor lookup, register mailbox, and parameter update modules.

## Risks and Edge Cases
The main struct mixes sleepable mutex-protected state, spinlock-protected IRQ/MMIO state, firmware-owned DMA memory, and async firmware-loading state; callers must respect locking and readiness. Dirty-bit operations assume `config_index` is valid. MMIO accessors do no range checking. Firmware memory offsets are hard-coded ABI values and must fit inside the allocated CPU memory.

## Test Signals
Compile coverage across all FIMC-IS modules, state-bit transitions during firmware boot and stream commands, MMIO register traces, parameter dirty-bit marking, memory barrier placement before mailbox commands, debug/shared-region offsets, and cleanup after partial probe failures are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is.h -->
