# subset-b-004144 research

This grouped report covers selected Linux media platform driver files under `sources/distributed-fs/ceph-client/drivers/media/platform`. Each section preserves the original source path so reconciliation can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/mtk_vpu.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/mtk_vpu.h

## Purpose
`mtk_vpu.h` is the public MediaTek VPU client API header. It describes the small video processor used by codec, scaler, and media data path blocks and exposes the IPI, firmware, watchdog, capability, and memory-mapping entry points used by other MediaTek media drivers.

## Important APIs, Types, and Functions
`ipi_handler_t` is the interrupt callback signature invoked with message data and caller private state. `enum ipi_id` defines firmware channels for initialization, H.264/VP8/VP9 decode, H.264/VP8 encode, and MDP. `enum rst_id` defines watchdog reset clients for encoder, decoder, and MDP. Exported prototypes include `vpu_ipi_register()`, `vpu_ipi_send()`, `vpu_get_plat_device()`, `vpu_wdt_reg_handler()`, `vpu_get_vdec_hw_capa()`, `vpu_get_venc_hw_capa()`, `vpu_load_firmware()`, and `vpu_mapping_dm_addr()`.

## Control Flow
Clients obtain the VPU platform device, register one IPI handler per channel, load or rely on VPU firmware, and use `vpu_ipi_send()` to synchronously hand requests to firmware. Completion arrives later through the registered handler in interrupt context. Watchdog clients register reset callbacks that the VPU driver invokes when firmware watchdog recovery occurs.

## State and Persistence
This header owns no state directly. Runtime state is held by the VPU implementation: IPI handler tables, watchdog callbacks, firmware boot state, hardware capability masks, and mapped DTCM/DMEM windows. There is no filesystem persistence.

## Dependencies and Integration Points
The API depends on `struct platform_device` and is consumed by MediaTek codec and MDP drivers. It integrates the Linux AP side with VPU firmware through shared memory and interrupts.

## Risks and Edge Cases
Handlers run in interrupt context, so clients must avoid sleeping and must validate message lengths. `vpu_ipi_send()` only succeeds once firmware and the IPI channel are ready. `vpu_mapping_dm_addr()` returns `ERR_PTR(-EINVAL)` on invalid firmware memory addresses, so callers must not treat every non-NULL pointer as usable.

## Test Signals
Useful signals are successful firmware load and `IPI_VPU_INIT`, successful IPI round trips for codec channels, correct watchdog callback invocation, accurate decoder/encoder capability masks, and safe failure for invalid DMEM/DTCM mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/mtk_vpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/Kconfig

## Purpose
This Kconfig file defines the Microchip media platform driver menu and build switches for the ISC, XISC, shared ISC base, and CSI2DC bridge drivers.

## Important APIs, Types, and Functions
`VIDEO_MICROCHIP_ISC` enables the SAMA5D2 Image Sensor Controller module. `VIDEO_MICROCHIP_XISC` enables the SAMA7G5 eXtended ISC module. `VIDEO_MICROCHIP_ISC_BASE` is an internal tristate selected by both ISC variants. `VIDEO_MICROCHIP_CSI2DC` enables the CSI2 Demux Controller. The options select V4L2 media-controller, subdevice, fwnode, vb2 DMA-contig, and regmap-mmio support as needed.

## Control Flow
The user-visible ISC and XISC choices pull in the common base automatically, while CSI2DC builds independently as a bridge subdevice. All user-visible options are guarded by `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, relevant clock/OF dependencies, and `ARCH_AT91 || COMPILE_TEST`.

## State and Persistence
Kconfig state is persisted in the kernel build configuration. It does not create runtime state but determines which modules and symbols are compiled.

## Dependencies and Integration Points
The file integrates these drivers into the Linux media platform menu. It gates compilation against V4L2, media-controller, COMMON_CLK, OF for CSI2DC, and AT91 architecture support.

## Risks and Edge Cases
Because `VIDEO_MICROCHIP_ISC_BASE` is non-user-visible and defaults to `n`, direct builds of common code rely on the ISC/XISC selects. Missing `MEDIA_CONTROLLER` or `VIDEO_V4L2_SUBDEV_API` would break the graph-based probe paths, so the selects are part of the ABI contract for these drivers.

## Test Signals
Build tests should cover built-in and module configurations for ISC, XISC, CSI2DC, `COMPILE_TEST`, and disabled `V4L_PLATFORM_DRIVERS`. Expected module names are `microchip-isc`, `microchip-xisc`, and `microchip-csi2dc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/Makefile

## Purpose
This Makefile maps the Microchip media Kconfig symbols to kernel objects and composes the product-specific modules from common and per-SoC source files.

## Important APIs, Types, and Functions
`microchip-isc-objs` contains `microchip-sama5d2-isc.o`, `microchip-xisc-objs` contains `microchip-sama7g5-isc.o`, and `microchip-isc-common-objs` contains `microchip-isc-base.o`, `microchip-isc-clk.o`, and `microchip-isc-scaler.o`. `obj-$(CONFIG_VIDEO_MICROCHIP_*)` lines select the common, product, and CSI2DC objects.

## Control Flow
When `VIDEO_MICROCHIP_ISC_BASE` is selected, the common support module is built. The SAMA5D2 and SAMA7G5 front-end modules link against exported common symbols. CSI2DC is built as its own module when configured.

## State and Persistence
This file only influences build-time object aggregation. It does not define runtime state.

## Dependencies and Integration Points
The object layout matches the split between common exported ISC helpers and product-specific platform drivers. It integrates with Linux kbuild and the Kconfig symbols in the same directory.

## Risks and Edge Cases
The product modules depend on common exports such as `microchip_isc_interrupt`, `microchip_isc_pipeline_init`, and `isc_mc_init`; mismatched Kconfig selects or object naming changes would produce unresolved symbols.

## Test Signals
Build logs should show `microchip-isc-common.o` built when ISC or XISC is enabled, and module link should include the correct product object for `microchip-isc.ko` and `microchip-xisc.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-csi2dc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-csi2dc.c

## Purpose
`microchip-csi2dc.c` implements the Microchip SAMA7G5 CSI2 Demux Controller as a V4L2 subdevice and media bridge. It accepts MIPI CSI-2 or parallel/BT.656 input, configures the CSI2DC video pipe, and exposes a sink/source media entity to downstream capture blocks.

## Important APIs, Types, and Functions
`struct csi2dc_device` stores MMIO base, clocks, current format, media pads, async notifier, remote subdevice, and bus-mode flags. `struct csi2dc_format` maps V4L2 media-bus codes to CSI-2 data types. Pad operations are `csi2dc_enum_mbus_code()`, `csi2dc_get_fmt()`, and `csi2dc_set_fmt()`. Streaming and hardware setup use `csi2dc_power()`, `csi2dc_get_mbus_config()`, `csi2dc_vp_update()`, and `csi2dc_s_stream()`. Probe and graph setup are handled by `csi2dc_of_parse()`, `csi2dc_prepare_notifier()`, `csi2dc_async_bound()`, and `csi2dc_probe()`.

## Control Flow
Probe maps registers, acquires `pclk` and `scck`, initializes the subdevice and media pads, parses input/output endpoints, registers an async notifier for the upstream sensor or bridge, powers the hardware briefly to read the version, enables runtime PM, then registers the subdevice. Format negotiation only allows setting the sink pad and propagates the selected format to the source pad. On stream start, runtime PM resumes clocks, the remote bus configuration is read when available, `csi2dc_vp_update()` programs parallel or serial pipe registers, and the upstream subdevice is started. Stream stop turns off the upstream subdevice and releases runtime PM.

## State and Persistence
Runtime state is in `csi2dc_device`: current active media-bus format, current data type, virtual channel, clock-continuity mode, media graph links, and whether the video pipe/source pad exists. Hardware state is volatile MMIO programming in `GCFG`, `VPCFG`, `VPE`, and `PU`. No persistent storage exists.

## Dependencies and Integration Points
The driver depends on V4L2 subdevice APIs, async notifiers, fwnode graph parsing, runtime PM, COMMON_CLK, and MMIO resources. It integrates upstream with a sensor/CSI source and downstream with a parallel/BT.656 consumer such as XISC. DT compatible is `microchip,sama7g5-csi2dc`.

## Risks and Edge Cases
The loop in `csi2dc_set_fmt()` increments `fmt` inside and outside the `for` body, but only `try_fmt` is retained, so future edits should avoid assuming `fmt` remains sequential. `csi2dc_get_mbus_config()` logs failure but returns success, meaning stale DT clock-continuity flags may be used. The probe error path after enabling runtime PM does not explicitly power down before notifier cleanup, so runtime-PM lifetime should be checked during changes. Parallel mode bypasses serial video-pipe programming and only sets `GPIOSEL`.

## Test Signals
Test graph probing with and without an output endpoint, RAW8/RAW10/YUYV format propagation, MIPI continuous and non-continuous clock modes, parallel and BT.656 endpoints, runtime suspend/resume around streaming, and successful media links from upstream entity to CSI2DC sink and CSI2DC source to the capture consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-csi2dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-base.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-base.c

## Purpose
`microchip-isc-base.c` is the shared V4L2, media-controller, vb2, DMA, interrupt, control, and async-subdevice implementation for Microchip ISC and XISC capture devices. Product drivers provide format tables, register offsets, and hardware-specific callbacks while this file owns the capture device behavior.

## Important APIs, Types, and Functions
The vb2 path is implemented by `isc_queue_setup()`, `isc_buffer_prepare()`, `isc_start_streaming()`, `isc_stop_streaming()`, and `isc_buffer_queue()`. Format and media negotiation are handled by `isc_enum_fmt_vid_cap()`, `isc_try_fmt()`, `isc_set_fmt()`, `isc_link_validate()`, and `isc_find_format_by_code()`. Hardware programming is centralized in `isc_configure()`, `isc_set_pipeline()`, `isc_update_profile()`, `isc_crop_pfe()`, and `isc_start_dma()`. `microchip_isc_interrupt()` is exported for product drivers. Auto white balance uses `isc_set_histogram()`, `isc_awb_work()`, `isc_wb_update()`, and clustered V4L2 controls. Exported setup helpers include `microchip_isc_async_ops`, `microchip_isc_subdev_cleanup()`, `microchip_isc_pipeline_init()`, `isc_mc_init()`, `isc_mc_cleanup()`, and `microchip_isc_regmap_config`.

## Control Flow
Async completion initializes workqueues, mutexes, vb2 queues, controls, the video device, scaler links, and the media device. Opening the video node powers the bound subdevice and refreshes the active format. Media link validation reads the upstream subdevice format, validates it against supported ISC input formats, clamps dimensions, ensures capture dimensions match to prevent DMA overflow, decides whether direct dump is required, and activates the pipeline configuration. Streaming starts the media pipeline, starts the upstream subdevice, resumes runtime PM, programs PFE/RLP/DMA/pipeline/histogram registers, enables DMA-done interrupts, takes the first queued buffer, crops the PFE to the active frame, and starts DMA. The IRQ handler completes the current buffer, timestamps and sequences it, starts the next queued buffer, completes stop waiters, and schedules AWB work on histogram completion. Stop disables AWB, waits for frame completion, disables interrupts, releases runtime PM, stops the upstream subdevice, and returns outstanding buffers as errors.

## State and Persistence
`struct isc_device` holds all durable runtime state: active and trial V4L2 formats, active and trial pipeline configuration, current subdevice, DMA queue, current buffer, sequence number, stop flag, completion, AWB controls, histogram state, media device, scaler subdevice, and regmap fields for pipeline modules. Hardware register state is volatile and rebuilt on configure/start. There is no persistence across driver unload or power loss.

## Dependencies and Integration Points
The file depends on regmap MMIO, V4L2 controls/events/ioctls, media-controller graph APIs, async notifiers, vb2 DMA-contig, runtime PM, and product callbacks in `struct isc_device`. It integrates upstream with a single sensor/subdevice and internally with the scaler entity from `microchip-isc-scaler.c`.

## Risks and Edge Cases
The driver intentionally rejects frame-size mismatches at link validation because the PFE/DMA path could otherwise overrun buffers. Non-RAW sensors force direct dump because conversion pipeline stages require RAW Bayer input. AWB work races with frame DMA, so `awb_lock` and `awb_mutex` protect register updates and streaming-stop state; changes in this area must preserve that ordering. `isc_update_profile()` times out if no frame clocks the profile update. Error unwinding must return queued buffers to vb2 and keep media pipeline/runtime PM balanced.

## Test Signals
Exercise raw Bayer, YUV, RGB, and GREY input/output combinations; media link validation with mismatched sizes; vb2 streaming start/stop under queued and empty-buffer conditions; DMA-done interrupt sequencing; histogram/AWB auto and one-shot controls; runtime PM reference balance; and module builds for both SAMA5D2 ISC and SAMA7G5 XISC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-clk.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-clk.c

## Purpose
`microchip-isc-clk.c` implements common clock-provider support for the Microchip ISC generated clocks. It exposes ISC master/ISP clocks to the Linux clock framework and programs ISC clock selection/divider registers.

## Important APIs, Types, and Functions
`struct isc_clk` in the shared header backs each `clk_hw`. Clock operations include `isc_clk_prepare()`, `isc_clk_unprepare()`, `isc_clk_enable()`, `isc_clk_disable()`, `isc_clk_is_enabled()`, `isc_clk_recalc_rate()`, `isc_clk_determine_rate()`, `isc_clk_set_parent()`, `isc_clk_get_parent()`, and `isc_clk_set_rate()`. Exported lifecycle functions are `microchip_isc_clk_init()` and `microchip_isc_clk_cleanup()`.

## Control Flow
Initialization seeds all clock slots as invalid, registers `ISC_MCK`, and conditionally registers `ISC_ISPCK` only when the product driver sets `ispck_required`. Registration reads clock parents from DT, optionally uses `clock-output-names`, installs the clock ops, and registers an OF provider for `ISC_MCK`. Enable programs divider and parent fields in `ISC_CLKCFG`, writes `ISC_CLKEN`, and verifies the status bit. Prepare/unprepare pair runtime PM with a wait for the clock status synchronization bit to clear.

## State and Persistence
Per-clock state tracks selected parent, divider, regmap, device, and spinlock. Register state is volatile hardware state in `ISC_CLKCFG`, `ISC_CLKEN`, `ISC_CLKDIS`, and `ISC_CLKSR`. There is no persistent storage.

## Dependencies and Integration Points
The code depends on COMMON_CLK, OF clock parents, runtime PM, regmap, and the ISC product driver's `isc_device`. It provides clocks consumed by sensors or by the ISC driver itself.

## Risks and Edge Cases
Parent count must be between one and three, and ISPCK trims parent count to two when more parents exist. `isc_clk_determine_rate()` assumes `best_parent_hw` exists before debug printing, so no-parent cases must keep the earlier validation intact. Register programming is protected by a spinlock, but rate/parent values are software state applied on enable, so callers must respect `CLK_SET_RATE_GATE` and `CLK_SET_PARENT_GATE`.

## Test Signals
Validate DT parent parsing, `clock-output-names`, ISPCK-required and no-ISPCK products, rate rounding across parents/dividers, enable status polling, runtime PM balance from `prepare`/`unprepare`, and provider removal on driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-regs.h

## Purpose
`microchip-isc-regs.h` defines the register offsets, bit masks, field helpers, product-specific offset deltas, and packing constants used by the Microchip ISC and XISC drivers.

## Important APIs, Types, and Functions
The header covers control/status (`ISC_CTRLEN`, `ISC_CTRLDIS`, `ISC_CTRLSR`), PFE configuration, clock registers, interrupt registers, DPC, white balance, CFA, color correction, gamma, XISC scaler/VHXS, CSC, contrast/brightness, subsampling, RLP, histogram, DMA, version, and histogram-entry registers. Product deltas such as `ISC_SAMA5D2_*_OFFSET` and `ISC_SAMA7G5_*_OFFSET` let shared code address variant layouts.

## Control Flow
Runtime code includes this header and uses the constants to program blocks in the pipeline: PFE samples sensor data, optional DPC/WB/CFA/CC/GAM/CSC/CBC/subsampling/RLP stages transform it, DMA writes planes, and histogram/AWB logic consumes histogram entries.

## State and Persistence
The file defines no state. The constants describe volatile MMIO state owned by the hardware and programmed through regmap in other files.

## Dependencies and Integration Points
It depends on `linux/bitops.h` for `BIT()` and `GENMASK()`. It is integrated by the shared base, clock, scaler, and product-specific ISC/XISC files.

## Risks and Edge Cases
Many fields are shared across SAMA5D2 and SAMA7G5 but shifted by per-block offsets; using the wrong offset will program the wrong block. Some names retain historical typos such as `ISC_PFG_CFG0_BPS_*`, so renames can be risky for downstream code. YUV packing constants and DMA plane address offsets must remain aligned with vb2 size calculations.

## Test Signals
Compile coverage is the first signal. Runtime validation should include frame capture for all supported RLP/DMA modes, interrupt delivery for DMA and histogram, clock enable/disable status, AWB histogram reads, and product-specific SAMA5D2/SAMA7G5 register offset correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-scaler.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-scaler.c

## Purpose
`microchip-isc-scaler.c` exposes the ISC/XISC crop/scaler path as a V4L2 subdevice in the media graph. It models the PFE/scaler constraints between the upstream sensor and the capture video node.

## Important APIs, Types, and Functions
Pad operations are `isc_scaler_enum_mbus_code()`, `isc_scaler_set_fmt()`, `isc_scaler_get_fmt()`, and `isc_scaler_g_sel()`. State initialization is `isc_scaler_init_state()`. Exported lifecycle and graph helpers are `isc_scaler_init()` and `isc_scaler_link()`.

## Control Flow
`isc_mc_init()` calls `isc_scaler_init()` to create the scaler subdevice with sink and source pads. The scaler sink accepts any supported ISC input media-bus code and any frame size, while the source is clamped to the controller's maximum width/height. `isc_scaler_link()` creates immutable enabled links from sensor source to scaler sink and scaler source to ISC video sink after async subdevice binding completes.

## State and Persistence
Scaler state is stored in `isc->scaler_format[]` for sink/source pads and in media entity pad objects. Try formats and crop rectangles live in V4L2 subdevice state. No hardware state is programmed directly here; the actual crop/PFE limits are applied by the base streaming path.

## Dependencies and Integration Points
The file depends on V4L2 subdevice state, media entity APIs, `isc_find_format_by_code()`, and `struct isc_device`. It integrates the logical media graph with the base driver's link-validation and crop programming.

## Risks and Edge Cases
The source pad format is fixed from the sink but clamped to hardware limits, so applications that set a larger sink size must observe the source format before configuring capture. Selection support only reports crop bounds/current crop on the sink pad. Failed registration cleanup is owned by surrounding media-device teardown.

## Test Signals
Use `media-ctl` to verify immutable links, enumerate scaler bus codes, set sink formats above and below hardware maximums, inspect clamped source formats and crop bounds, and confirm capture dimensions match link validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc-scaler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc.h

## Purpose
`microchip-isc.h` is the shared private interface for Microchip ISC/XISC drivers. It defines common clock, buffer, async subdevice, format, pipeline, controls, register-offset, and device-state structures plus exported common helper prototypes.

## Important APIs, Types, and Functions
Important types include `struct isc_clk`, `struct isc_buffer`, `struct isc_subdev_entity`, `struct isc_format`, `struct fmt_config`, `struct isc_ctrls`, `struct isc_reg_offsets`, and `struct isc_device`. Pipeline bit masks describe DPC, WB, CFA, CC, GAM, VHXS, CSC, CBC, and subsampling stages. Exported prototypes include interrupt handling, pipeline initialization, clock initialization/cleanup, async ops, scaler initialization/linking, media-controller initialization/cleanup, and format lookup.

## Control Flow
Product drivers allocate and fill `struct isc_device`, selecting format arrays, register offsets, maximum dimensions, DMA burst settings, clock requirements, and callback hooks. Common code then uses this structure for V4L2 format negotiation, media graph registration, streaming, DMA queuing, AWB, and clock/pipeline programming.

## State and Persistence
`struct isc_device` is the central runtime state object. It persists while the platform device is bound and contains volatile kernel state for formats, controls, current buffers, media graph entities, locks, completion, and hardware callback configuration. Nothing is persisted across driver removal.

## Dependencies and Integration Points
The header depends on Linux clock-provider, platform-device, V4L2 control/device, and vb2 DMA-contig APIs. It ties together `microchip-isc-base.c`, `microchip-isc-clk.c`, `microchip-isc-scaler.c`, and the SAMA5D2/SAMA7G5 product drivers.

## Risks and Edge Cases
The anonymous callback struct in `struct isc_device` is a tight contract: product drivers must populate every callback used by `isc_set_pipeline()` and control initialization. Locking fields have distinct purposes and should not be collapsed. Format arrays mix input media-bus formats and output pixel formats, so code must use the correct size and pointer pair.

## Test Signals
Compile both product drivers, run probe/remove with clocks and subdevices present, validate all callbacks are set before streaming, and exercise the exported helper calls through ISC and XISC module loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-isc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-sama5d2-isc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-sama5d2-isc.c

## Purpose
`microchip-sama5d2-isc.c` is the SAMA5D2 product driver for the Microchip Image Sensor Controller. It supplies SAMA5D2 format tables, register offsets, clock policy, hardware callbacks, DT parsing, probe/remove, and runtime PM around the shared ISC base.

## Important APIs, Types, and Functions
The file defines SAMA5D2 output and input format tables, gamma tables, and callbacks `isc_sama5d2_config_csc()`, `isc_sama5d2_config_cbc()`, `isc_sama5d2_config_cc()`, `isc_sama5d2_config_ctrls()`, `isc_sama5d2_config_dpc()`, `isc_sama5d2_config_gam()`, `isc_sama5d2_config_rlp()`, and `isc_sama5d2_adapt_pipeline()`. Platform lifecycle is `microchip_isc_probe()`, `microchip_isc_remove()`, `isc_runtime_suspend()`, and `isc_runtime_resume()`.

## Control Flow
Probe allocates `isc_device`, maps MMIO through regmap, requests the IRQ using the common interrupt handler, assigns SAMA5D2 callbacks and format tables, sets 2592x1944 limits, configures 8-beat DMA bursts, marks ISPCK as mandatory, initializes pipeline fields, enables `hclock`, registers generated ISC clocks, registers V4L2, parses endpoints, registers async notifiers for remote sensors, reads hardware version, initializes media-controller/scaler support, enables runtime PM, enables and rates ISPCK to at least `hclock`, and reports the version. Removal reverses media, notifier, V4L2, clock, and PM setup.

## State and Persistence
State lives in the shared `isc_device`. SAMA5D2-specific persistent-in-driver state is static format/gamma tables and callback assignments. Hardware register state is rebuilt on stream setup and runtime resume.

## Dependencies and Integration Points
The driver binds `atmel,sama5d2-isc`, depends on common ISC exports, AT91 clock/reset resources, V4L2 fwnode endpoint parsing, and media-controller async graph binding. It integrates directly with sensors using parallel or BT.656 bus flags.

## Risks and Edge Cases
SAMA5D2 lacks DPC and special gamma configuration, so pipeline bits are masked by `ISC_SAMA5D2_PIPELINE`. Its RLP block treats planar and interleaved YUV through the YYCC mode, requiring the callback to rewrite YCYC. ISPCK setup is mandatory and error unwinding must avoid disabling an unprepared clock path incorrectly.

## Test Signals
Test probe with valid endpoints and clocks, RAW8/10/12 and YUV/GREY/RGB formats, BT.656 and polarity flags, ISPCK rate setup, runtime suspend/resume, media graph registration, and capture up to 2592x1944.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-sama5d2-isc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-sama7g5-isc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-sama7g5-isc.c

## Purpose
`microchip-sama7g5-isc.c` is the SAMA7G5 XISC product driver. It adapts the shared ISC base to the extended SAMA7G5 pipeline, including MIPI input flagging, wider format support, XISC register offsets, DPC/gamma behavior, and AXI DMA settings.

## Important APIs, Types, and Functions
The file defines SAMA7G5 output/input format tables, a bipartite gamma table, product callbacks `isc_sama7g5_config_csc()`, `isc_sama7g5_config_cbc()`, `isc_sama7g5_config_cc()`, `isc_sama7g5_config_ctrls()`, `isc_sama7g5_config_dpc()`, `isc_sama7g5_config_gam()`, `isc_sama7g5_config_rlp()`, and `isc_sama7g5_adapt_pipeline()`. DT/probe functions are `xisc_parse_dt()` and `microchip_xisc_probe()`, with runtime PM in `xisc_runtime_suspend()` and `xisc_runtime_resume()`.

## Control Flow
Probe maps MMIO, initializes regmap, requests the shared ISR, installs SAMA7G5 callbacks and offsets, configures 3264x2464 limits, uses 32-beat AXI DMA bursts, disables ISPCK because XISC is clocked by MCK, initializes pipeline regmap fields, enables `hclock`, registers generated clocks, registers V4L2, parses endpoints, registers async notifiers, reads the version at the SAMA7G5 offset, initializes the media graph/scaler, and enables runtime PM. DT parsing adds normal parallel/BT.656 polarity bits and optionally sets `ISC_PFE_CFG0_MIPI` when `microchip,mipi-mode` is present.

## State and Persistence
State lives in `isc_device` and static SAMA7G5 tables/callbacks. Hardware state is volatile and rebuilt during streaming or runtime resume. There is no persisted state.

## Dependencies and Integration Points
The driver binds `microchip,sama7g5-isc`, depends on shared ISC common code, regmap, V4L2 async/fwnode, hclock and generated MCK clocks, and can be connected behind `microchip-csi2dc` through MIPI mode.

## Risks and Edge Cases
The SAMA7G5 input table includes UYVY and output table includes UYVY/VYUY/Y16 not present in SAMA5D2, so format regression tests must be product-specific. DPC and bipartite gamma are configured only through callbacks. `microchip,mipi-mode` is a global device property, so mixed endpoint topologies would apply MIPI PFE mode to all parsed endpoints.

## Test Signals
Validate MIPI and parallel DT endpoints, capture through CSI2DC, supported UYVY/VYUY/Y16 formats, DPC bay selection, gamma bipartite bit, 32-beat DMA configuration, runtime PM hclock balance, and max-size capture at 3264x2464.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-sama7g5-isc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/Kconfig

## Purpose
This Kconfig file adds the Nuvoton media platform driver menu and the switch for the NPCM video capture/encode engine.

## Important APIs, Types, and Functions
`VIDEO_NPCM_VCD_ECE` is a tristate option for the NPCM Video Capture/Differentiation Engine and Encoding Compression Engine driver. It depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, and `ARCH_NPCM || COMPILE_TEST`, and selects `VIDEOBUF2_DMA_CONTIG`.

## Control Flow
When enabled, the build includes `npcm-video.o` and exposes a V4L2 capture driver for NPCM VCD/ECE hardware. No other options are selected here, so media-controller integration is not required by this driver.

## State and Persistence
Kconfig state is persisted in the kernel configuration and determines whether the driver is compiled as built-in, module, or not at all.

## Dependencies and Integration Points
The option integrates the Nuvoton BMC capture engine into the Linux media platform driver menu and gates it to NPCM SoCs or compile-test builds.

## Risks and Edge Cases
The driver also uses controls, DV timings, reserved memory, syscon regmaps, reset controls, and optional ECE resources; those are resolved through broader kernel dependencies and DT at build/runtime rather than all being explicit Kconfig selects.

## Test Signals
Build with `ARCH_NPCM`, with `COMPILE_TEST`, as module and built-in, and with the option disabled to ensure no stale object references remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/Makefile

## Purpose
This Makefile connects the Nuvoton NPCM VCD/ECE Kconfig symbol to its driver object.

## Important APIs, Types, and Functions
`obj-$(CONFIG_VIDEO_NPCM_VCD_ECE) += npcm-video.o` is the only build rule.

## Control Flow
Kbuild compiles and links `npcm-video.o` when `VIDEO_NPCM_VCD_ECE` is enabled. No multi-object module composition occurs.

## State and Persistence
This file has build-time effect only and no runtime state.

## Dependencies and Integration Points
It integrates with `drivers/media/platform/nuvoton/Kconfig` and the kernel media platform build.

## Risks and Edge Cases
The direct one-object mapping means any future split of register, V4L2, or ECE logic would require Makefile updates or unresolved symbols.

## Test Signals
Confirm `npcm-video.ko` is produced for module builds and no object is built when the Kconfig option is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/npcm-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/npcm-regs.h

## Purpose
`npcm-regs.h` defines register offsets, bit masks, field encodings, sizes, and timeouts for the Nuvoton NPCM Video Capture/Differentiation Engine, Encoding Compression Engine, GCR, and GFXI blocks.

## Important APIs, Types, and Functions
The VCD section defines frame-buffer addresses, line pitch, capture resolution, mode, command, status, interrupts, resolution-change timing, FIFO threshold, buffer size, bandwidth threshold, and timeout constants. The ECE section defines DDA control/status, framebuffer and encoded-data base addresses, rectangle position/dimension, line-pitch encoding, HEXTILE control, rectangle offset, tile size, and timeout. GCR/GFXI definitions cover display interface reset, mode, resolution counters, and graphics PLL fields.

## Control Flow
`npcm-video.c` uses these constants to reset hardware, detect resolution and pixel clock, configure line pitch, trigger capture or compare operations, process interrupts, and drive optional HEXTILE rectangle encoding.

## State and Persistence
The header defines no software state. The hardware registers are volatile state that the driver initializes on open/start and clears on stop/remove.

## Dependencies and Integration Points
It relies on bitfield macros from included kernel headers in the C file context. It is tightly coupled to the `npcm-video.c` register programming model and NPCM DT syscon resources.

## Risks and Edge Cases
Incorrect field widths can corrupt capture dimensions, line pitch, or rectangle offsets. `VCD_FB_SIZE` fixes support to 1920x1200 RGB565-sized buffers; future higher resolutions require coordinated memory and timing changes. Timeout constants affect IRQ recovery and encode polling behavior.

## Test Signals
Validate VCD capture at min/max resolutions, line-pitch selections 512 through 4096, interrupt status clear behavior, ECE HEXTILE rectangle offsets, GFXI resolution/pixel-clock reads, and reset sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/npcm-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/npcm-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/npcm-video.c

## Purpose
`npcm-video.c` implements the Nuvoton NPCM BMC video capture driver. It exposes the VCD capture/differentiation engine as a V4L2 capture device and optionally uses the ECE block to output changed rectangles in HEXTILE format.

## Important APIs, Types, and Functions
Core state types are `struct npcm_video`, `struct npcm_ece`, `struct npcm_video_buffer`, `struct npcm_video_addr`, and rectangle-list helpers. Hardware helpers include `npcm_video_init_reg()`, `npcm_video_vcd_ip_reset()`, `npcm_video_vcd_state_machine_reset()`, `npcm_video_gfx_reset()`, `npcm_video_detect_resolution()`, `npcm_video_set_resolution()`, and `npcm_video_start_frame()`. Encoding helpers include `npcm_video_ece_*()`, `npcm_video_raw()`, and `npcm_video_hextile()`. V4L2/vb2 operations cover format, DV timings, input status, custom NPCM controls, open/release, queue setup, buffer prepare/queue/finish, streaming start/stop, and the threaded IRQ `npcm_video_irq()`.

## Control Flow
Probe allocates driver state, maps VCD registers, gets reset, resolves GCR/GFXI syscons, maps the IRQ, initializes reserved memory and DMA mask, optionally initializes ECE from a phandle, then registers V4L2 controls, vb2 queue, and `/dev/video0`. On first open, `npcm_video_start()` initializes registers, allocates a coherent VCD source framebuffer, detects active host resolution, programs line pitch and frame-buffer addresses, and prepares ECE if available. Streaming starts by taking queued buffers and issuing a capture or compare command. The IRQ clears status, completes capture buffers by copying RGB565 or encoding HEXTILE rectangles, updates payload/timestamp/sequence, removes the buffer from the queue, and starts the next frame. Resolution-change interrupts mark the queue errored and emit a source-change event; FIFO errors restart capture. Stop disables interrupts/mode, frees framebuffer and rectangle tables, resets controls, and stops ECE on last client.

## State and Persistence
`struct npcm_video` stores V4L2 format, active/detected timings, input status, queued buffers, flags for streaming/capturing/resolution-change/stopped, sequence, source framebuffer, ECE client count, rectangle lists/counts, current capture command, and last operation. Hardware register state is rebuilt on open/start and cleared on stop. Reserved DMA memory may be provided by DT but no driver data persists across removal.

## Dependencies and Integration Points
The driver depends on V4L2, vb2 DMA-contig, custom UAPI controls from `uapi/linux/npcm-video.h`, syscon regmaps for `nuvoton,sysgcr` and `nuvoton,sysgfxi`, reset controls, reserved memory, IRQ handling, and optional ECE platform device phandle `nuvoton,ece`. Compatibles are `nuvoton,npcm750-vcd` and `nuvoton,npcm845-vcd`.

## Risks and Edge Cases
Probe uses `kzalloc_obj()` without devm/free cleanup on early failures, so error-path ownership should be checked before edits. `dev_get_drvdata()` in remove expects the V4L2 device drvdata path to be valid; setup changes must keep driver data consistent. HEXTILE output depends on rectangle-list allocation and ECE polling; failures can produce zero-sized payloads. Resolution change intentionally errors the vb2 queue, so userspace must re-query timings. Source framebuffer allocation failure leaves open partially initialized unless callers observe input status and subsequent cleanup.

## Test Signals
Test RGB565 and HEXTILE capture, complete and diff capture modes, queued-buffer starvation, min/max DV timings, source-change events, FIFO overrun recovery, ECE unavailable DT path, ECE rectangle count control updates on dequeue, reserved memory and 32-bit DMA mask handling, and open/release reference behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/npcm-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/Kconfig

## Purpose
This Kconfig file adds the NVIDIA media platform driver menu and includes the Tegra VDE submenu.

## Important APIs, Types, and Functions
The file contains a menu comment and sources `drivers/media/platform/nvidia/tegra-vde/Kconfig`.

## Control Flow
Selecting NVIDIA media platform options flows into the Tegra VDE Kconfig file where the actual driver option is defined.

## State and Persistence
It has build-configuration state only through included Kconfig symbols.

## Dependencies and Integration Points
It integrates the Tegra video decoder engine configuration into the broader Linux media platform hierarchy.

## Risks and Edge Cases
The source path must remain aligned with the Makefile directory layout. If additional NVIDIA media drivers are added, this file becomes the aggregation point.

## Test Signals
Run menuconfig/listnewconfig to confirm the NVIDIA comment and Tegra VDE option appear when media platform drivers are visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/Makefile

## Purpose
This Makefile descends into the NVIDIA Tegra VDE media driver directory.

## Important APIs, Types, and Functions
`obj-y += tegra-vde/` is the sole rule and lets the subdirectory Makefile decide whether to build the driver object.

## Control Flow
Kbuild always visits `tegra-vde/`; the subdirectory gates object generation on `CONFIG_VIDEO_TEGRA_VDE`.

## State and Persistence
This file has build-time effect only and no runtime state.

## Dependencies and Integration Points
It integrates the NVIDIA media platform directory with Linux kbuild recursion.

## Risks and Edge Cases
Adding future NVIDIA media subdirectories requires updating this aggregator. The unconditional recursion is safe because the child Makefile is config-gated.

## Test Signals
Build with `CONFIG_VIDEO_TEGRA_VDE=y/m/n` and confirm subdirectory traversal occurs while objects are only produced when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/Kconfig

## Purpose
This Kconfig file defines the NVIDIA Tegra Video Decoder Engine driver option.

## Important APIs, Types, and Functions
`VIDEO_TEGRA_VDE` is a tristate option depending on `V4L_MEM2MEM_DRIVERS`, `ARCH_TEGRA || COMPILE_TEST`, and `VIDEO_DEV`. It selects DMA shared buffers, IOMMU IOVA support, media-controller, SRAM, vb2 DMA-contig/SG, V4L2 H.264 controls, and V4L2 mem2mem core.

## Control Flow
When enabled, the Tegra VDE module is built and can expose a stateless H.264 mem2mem decoder device. Selected dependencies cover request API controls, media graph support, DMA-buf import, SRAM IRAM allocation, and buffer management.

## State and Persistence
Kconfig selection persists in the kernel build configuration and determines module availability.

## Dependencies and Integration Points
The driver integrates with V4L2 mem2mem, stateless H.264 control UAPI, Tegra SoC power/clock/reset, SRAM, IOMMU, and DMA-buf frameworks.

## Risks and Edge Cases
`COMPILE_TEST` can build the code away from Tegra hardware, but runtime probe still requires named MMIO resources, SRAM, resets, and clocks. Missing IOMMU support changes buffer contiguity requirements.

## Test Signals
Build as module and built-in on Tegra and compile-test configurations, verify selected dependencies are present, and run V4L2 compliance on hardware with stateless H.264 requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/Makefile

## Purpose
This Makefile composes the Tegra VDE driver module.

## Important APIs, Types, and Functions
`tegra-vde-y` includes `vde.o`, `iommu.o`, `dmabuf-cache.o`, `h264.o`, and `v4l2.o`. `obj-$(CONFIG_VIDEO_TEGRA_VDE) += tegra-vde.o` gates the final object.

## Control Flow
When `VIDEO_TEGRA_VDE` is enabled, kbuild links platform probe/power code, IOMMU helpers, DMA-buf cache, H.264 hardware programming, and V4L2 mem2mem glue into one module.

## State and Persistence
The file has build-time state only.

## Dependencies and Integration Points
The object list mirrors the internal module boundaries declared in `vde.h`.

## Risks and Edge Cases
Every object depends on shared `struct tegra_vde` and helper prototypes. Removing one object from the list will break exported-internal calls such as `tegra_vde_h264_decode_run()` or `tegra_vde_iommu_map()`.

## Test Signals
Build the module and inspect link errors, module symbol layout, and tracepoint generation from `vde.o` plus `trace.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/dmabuf-cache.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/dmabuf-cache.c

## Purpose
`dmabuf-cache.c` caches imported DMA-buf attachments and optional IOMMU mappings for the Tegra VDE driver. It avoids repeated attach/map/unmap churn while buffers are reused across decode jobs.

## Important APIs, Types, and Functions
`struct tegra_vde_cache_entry` records direction, attachment, SG table, IOVA, delayed unmap work, reference count, and list linkage. Public helpers are `tegra_vde_dmabuf_cache_map()`, `tegra_vde_dmabuf_cache_unmap()`, `tegra_vde_dmabuf_cache_unmap_sync()`, and `tegra_vde_dmabuf_cache_unmap_all()`. Internal cleanup is `tegra_vde_release_entry()` and delayed work callback `tegra_vde_delayed_unmap()`.

## Control Flow
Map first searches `vde->map_list` under `map_lock`. If an entry for the DMA-buf exists and pending delayed unmap can be canceled, it reuses the mapping, upgrades direction to bidirectional if needed, drops the caller's DMA-buf reference, returns the cached address, and increments refcount. New maps attach the DMA-buf, map the attachment, reject sparse SG tables without IOMMU, allocate a cache entry, optionally allocate/map an IOVA, and add it to the cache. Unmap decrements refcount and either releases immediately or schedules delayed release after five seconds. Sync/all cleanup drains delayed or all cache entries.

## State and Persistence
Runtime state is the cache list in `struct tegra_vde`, each entry's reference count, delayed work, DMA-buf attachment, SG table, and IOVA. There is no persistence beyond the device lifetime.

## Dependencies and Integration Points
The code depends on DMA-buf attachment APIs, SG tables, IOVA/IOMMU helpers from `iommu.c`, workqueues, and `vde->map_lock`. It is used by the V4L2 buffer path for imported buffers.

## Risks and Edge Cases
If delayed work is already running, map skips that entry and creates a new one. Direction changes are handled by marking bidirectional, but the original DMA mapping direction may already be fixed. Non-IOMMU operation rejects non-contiguous SG tables, so imported buffers must be physically contiguous. `tegra_vde_dmabuf_cache_unmap_all()` loops until delayed work can be canceled, yielding with `schedule()`.

## Test Signals
Test repeated decode with the same DMA-buf, immediate release and delayed-release paths, sync cleanup on stream teardown, non-contiguous DMA-buf rejection without IOMMU, IOMMU map/unmap balance, and module unload with no pending cache entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/dmabuf-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/h264.c

## Purpose
`h264.c` translates stateless V4L2 H.264 request controls and vb2 buffers into Tegra VDE hardware context programming, starts a decode, and waits for completion.

## Important APIs, Types, and Functions
`struct tegra_vde_h264_decoder_ctx` stores the hardware-ready SPS/PPS/decode parameters. `struct h264_reflists` stores temporary P/B reference lists. Hardware helpers include `tegra_vde_wait_mbe()`, `tegra_vde_setup_mbe_frame_idx()`, `tegra_vde_wait_bsev()`, `tegra_vde_push_to_bsev_icmdqueue()`, `tegra_vde_setup_frameid()`, `tegra_setup_frameidx()`, `tegra_vde_setup_iram_tables()`, `tegra_vde_setup_hw_context()`, and `tegra_vde_decode_frame()`. Public codec operations are `tegra_vde_h264_decode_run()` and `tegra_vde_h264_decode_wait()`.

## Control Flow
Decode run prepares H.264 decode, SPS, and PPS controls, rejects unsupported CABAC and field pictures, derives hardware context values, builds current and reference frame descriptors from vb2 buffers and DPB timestamps, validates context limits, locks the VDE, resumes runtime PM, resets MC and VDE hardware, programs frame-id and IRAM reference tables, writes BSEV/SXE/MBE/PPE/MCE/TFE/VDMA registers and command queues, then starts SXE decode for the macroblock count. Decode wait waits up to one second for the ISR completion, reports read-byte/macroblock progress on timeout, aborts by asserting MC and VDE resets, drops runtime PM, and unlocks the device.

## State and Persistence
Per-job state includes `vde->frames[]`, `vde->bitstream_data_addr`, hardware register programming, IRAM reference tables, and the decode completion. Persistent driver state is the VDE mutex, runtime PM state, SoC feature flag for reference-picture marking, and auxiliary buffers attached to vb2 buffers. No state persists across driver removal.

## Dependencies and Integration Points
The file depends on V4L2 stateless H.264 controls and reflist helpers, V4L2 mem2mem queues, vb2 buffer metadata, Tegra reset/runtime PM, register wrappers and tracepoints, and shared structures from `vde.h`. It is invoked by the V4L2 mem2mem job runner in `v4l2.c`.

## Risks and Edge Cases
The hardware cannot decode CABAC or field pictures without preprocessing, so the driver returns `-EOPNOTSUPP`. It assumes all slices in a frame share one frame type; non-uniform frames may fail in hardware. Plane and auxiliary-buffer size validation is critical before DMA. Reset ordering asserts the memory client first on abort to avoid bus lockups or memory corruption. IOVA allocation reserves problematic address ranges in `iommu.c` because hardware address wrapping can break BSEV.

## Test Signals
Run stateless H.264 baseline and supported non-CABAC streams, P- and B-frame DPB reference cases, unsupported CABAC/field-picture rejection, malformed SPS/PPS range validation, undersized output plane and aux-buffer rejection, decode timeout diagnostics, runtime PM/reset balance, and tracepoint capture for register and IRAM programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/iommu.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/iommu.c

## Purpose
`iommu.c` provides IOMMU and IOVA-domain support for the Tegra VDE driver. It maps SG tables into VDE-visible IOVA space and initializes/deinitializes the VDE IOMMU domain.

## Important APIs, Types, and Functions
Public functions are `tegra_vde_iommu_map()`, `tegra_vde_iommu_unmap()`, `tegra_vde_iommu_init()`, and `tegra_vde_iommu_deinit()`. Initialization also handles legacy ARM DMA-IOMMU mappings when `CONFIG_ARM_DMA_USE_IOMMU` is enabled.

## Control Flow
Init gets the device IOMMU group; absence of a group means the driver operates without an IOMMU. If a legacy ARM DMA mapping exists, it detaches/releases it, then allocates a paging domain, initializes the IOVA allocator using the domain page size, attaches the group, reserves static invalid-address space from `0x60000000` to `0x70000000`, and reserves the last page to avoid BSEV end-address wraparound. Map aligns the requested size, allocates an IOVA near the aperture end, maps the SG table read/write into the domain, and returns the IOVA. Unmap removes the mapping and frees the IOVA. Deinit frees reservations, detaches, releases IOVA cache/domain, frees the IOMMU domain, and drops the group.

## State and Persistence
State lives in `vde->domain`, `vde->group`, `vde->iova`, and reservation pointers. Mappings are volatile runtime DMA state and are also referenced by BOs and DMA-buf cache entries. There is no persistence.

## Dependencies and Integration Points
The file depends on Linux IOMMU, IOVA allocator, platform device infrastructure, optional ARM DMA-IOMMU compatibility, and the VDE buffer/cache code.

## Risks and Edge Cases
No IOMMU group is a valid path, but it forces other code to require physically contiguous buffers. Failure after attaching must unwind reservations, IOVA domain, cache, domain, and group in the right order. The reserved ranges encode hardware quirks; removing them can reintroduce invalid access traps or address wrap failures.

## Test Signals
Test hardware with and without IOMMU, SG-table map/unmap balance, allocation near aperture boundaries, init failure unwinding with forced errors, imported non-contiguous buffers, and deinit after cached mappings are drained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/trace.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/trace.h

## Purpose
`trace.h` defines ftrace tracepoints for Tegra VDE register access and H.264 reference-table programming.

## Important APIs, Types, and Functions
The `register_access` event class backs `vde_writel` and `vde_readl`, recording hardware block name, offset, and value. `vde_setup_iram_entry` records IRAM reference-list entries and auxiliary addresses. `vde_ref_l0` and `vde_ref_l1` record reference-list ordering details. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` enable tracepoint generation from `vde.c`.

## Control Flow
`vde.c` defines `CREATE_TRACE_POINTS` and includes this header so the tracepoints are instantiated once. Register wrapper functions call `trace_vde_writel()` and `trace_vde_readl()`, while `h264.c` calls IRAM/reference tracepoints during hardware context setup.

## State and Persistence
Tracepoints do not hold persistent driver state. When enabled, they emit runtime events into the kernel tracing buffers.

## Dependencies and Integration Points
The file depends on Linux tracepoint infrastructure and `vde.h` for `struct tegra_vde` and register base naming. It integrates with ftrace/perf debugging workflows.

## Risks and Edge Cases
The include path is relative to the kernel trace build expectations and must match the source location. `tegra_vde_reg_base_name()` must remain available for trace fast assignment. Trace payloads expose register values and frame numbers useful for debugging but should not be assumed stable ABI.

## Test Signals
Enable Tegra VDE trace events under tracefs during decode, confirm read/write events name SXE/BSEV/MBE/etc. correctly, verify IRAM entry traces match DPB setup, and build with tracing enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/trace.h -->
