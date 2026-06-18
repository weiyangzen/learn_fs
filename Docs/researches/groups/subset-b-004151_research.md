# Research: subset-b-004151

Grouped research for Qualcomm Iris V4L2/VPU platform, power, resource, state, queueing, codec, and hardware-buffer code under `sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_common.h

## Purpose
Defines the shared platform-data contract used by Iris probe, resource, control, power, HFI, VPU, and buffer code. It is the central description format for SoC-specific capabilities: clocks, resets, interconnect votes, power domains, firmware image names, DMA mask, codec formats, firmware controls, internal-buffer lists, UBWC configuration, TrustZone carveout settings, and core/session limits.

## Important APIs, Types, And Constants
- `IRIS_PAS_ID`, `HW_RESPONSE_TIMEOUT_VALUE`, and `AUTOSUSPEND_DELAY_VALUE` define firmware authentication and timeout policy.
- Codec/session defaults include `DEFAULT_MAX_HOST_BUF_COUNT`, `DEFAULT_FPS`, `MAXIMUM_FPS`, `NUM_MBS_8K`, QP bounds, and `BITRATE_DEFAULT`.
- `enum stage_type` and `enum pipe_type` model HFI work mode and hardware pipe routing.
- `enum platform_clk_type` names logical clocks. `struct platform_clk_data` maps those logical IDs to DT clock names.
- `struct tz_cp_config` describes secure CP/nonpixel memory regions.
- `struct ubwc_config_data` carries UBWC tiling/bank configuration for gen2 platforms.
- `struct platform_inst_caps` stores per-session frame limits, max macroblocks, cycle coefficients, COMV count, and frame-rate limits.
- `enum platform_inst_fw_cap_type`, `enum platform_inst_fw_cap_flags`, and `struct platform_inst_fw_cap` define the firmware-control matrix, including cap ID, ranges, default value, HFI property ID, flags, and setter callback.
- `struct bw_info`, `struct iris_core_power`, `struct iris_inst_power`, and `struct icc_vote_data` back runtime clock and interconnect voting.
- `enum platform_pm_domain_type` indexes named PM domains consumed by VPU power-on/off code.
- `struct iris_platform_data` is the exported platform descriptor consumed by `iris_probe.c`, `iris_power.c`, `iris_vb2.c`, codec setup, and VPU buffer sizing.

## Control Flow And Integration Points
Platform C files populate `const struct iris_platform_data` instances declared here (`qcs8300_data`, `sc7280_data`, `sm8250_data`, `sm8550_data`, `sm8650_data`, `sm8750_data`). `iris_probe()` obtains one through `of_device_get_match_data()`, initializes HFI ops through callbacks in this struct, initializes resources from table pointers, and later exposes decoder/encoder devices. Session initialization copies the selected decoder or encoder firmware-cap table into each `iris_inst`. Power and buffer code then read the same platform data for bandwidth tables, clock IDs, VPU generation operations, pipe count, and internal buffer tables.

## State And Persistence Behavior
The header does not allocate or mutate state, but it defines the runtime state shape for core/instance power tracking and immutable platform tables. Platform data persists for the module lifetime as static const data, while per-instance mutable copies of `platform_inst_fw_cap` allow controls to change without modifying global platform descriptions.

## Dependencies
Depends on Linux bit macros and Iris buffer types. It forward-declares `iris_core` and `iris_inst`, and stores callback types implemented by HFI generation files, VPU generation files, and control setter code.

## Risks
- Table-size fields must match their table pointers; mismatches can cause skipped resources or out-of-bounds iteration in probe, power, and property code.
- `enum platform_inst_fw_cap_type` indexes `inst->fw_caps`; new caps must preserve `INST_FW_CAP_MAX` and all users that assume a dense array.
- Clock and PM-domain enum order must match platform table usage in VPU power code.
- HFI property IDs and setter callbacks are generation-specific; incorrect pairings can silently program invalid firmware properties.

## Test Signals
- Probe success for each compatible string validates table completeness for clocks, resets, ICC, PM domains, firmware, and V4L2 registration.
- V4L2 control enumeration/defaults validate `platform_inst_fw_cap` ranges and flags.
- Stream-on on decoder and encoder validates internal buffer table references, `get_vpu_buffer_size`, `vpu_ops`, and HFI parameter arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_gen1.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_gen1.c

## Purpose
Provides first-generation Iris/Venus platform data for SM8250 and SC7280. It binds HFI gen1 command/response operations, VPU2 power/frequency operations, decoder formats, encoder firmware controls, interconnect bandwidth tables, PM domains, clocks, reset names, firmware names, TrustZone carveout data, and internal buffer requirements into `sm8250_data` and `sc7280_data`.

## Important APIs, Types, And Data
- `platform_fmts_sm8250_dec` exposes decoder input formats H.264, HEVC, and VP9.
- `inst_fw_cap_sm8250_dec` supports gen1 decoder `PIPE` and `STAGE` controls.
- `inst_fw_cap_sm8250_enc` defines gen1 encoder controls for stage, H.264/HEVC profile and level, header mode, bitrate, bitrate mode, frame skip, frame RC, GOP size, entropy mode, and QP ranges.
- `platform_inst_cap_sm8250` sets session resolution and throughput limits.
- `iris_set_sm8250_preset_registers()` writes a fixed preset register at `reg_base + 0xB0088`.
- SM8250 tables describe ICC paths, reset IDs, decoder bandwidth points, power domains, OPP power domains, clocks, OPP clock, TZ CP carveout, HFI config-property arrays, and internal buffer types.
- `sm8250_data` and `sc7280_data` are exported platform descriptors.

## Control Flow And Integration Points
`iris_probe.c` selects this data for `"qcom,sm8250-venus"` or `"qcom,sc7280-venus"` when the legacy Venus driver is not enabled. Probe initializes gen1 HFI ops, resources from the table names, V4L2 capabilities from `inst_iris_fmts`, and session capability tables from `inst_fw_caps_*`. Stream-on uses the config-property lists and internal buffer tables; power scaling uses `sm8250_bw_table_dec` or `sc7280_bw_table_dec`; VPU control uses `iris_vpu2_ops`.

## State And Persistence Behavior
All descriptors and tables are static/global and persist for the module lifetime. The decoder fw-cap array is non-const because `PIPE` max/min/value are adjusted by platform data elsewhere. Per-session copies are created during decoder/encoder instance initialization.

## Dependencies
Depends on gen1 HFI defines and setters, common platform definitions, resource helpers, VPU buffer sizing, VPU common ops, and SC7280 supplemental tables from `iris_platform_sc7280.h`.

## Risks
- SC7280 reuses SM8250 caps and many tables but changes clocks, OPP power domain, bandwidth, pipe count, firmware name, and core throughput. Regression risk is high if shared tables are edited assuming one SoC.
- `inst_fw_cap_sm8250_enc` HFI IDs are gen1-specific; using gen2 IDs would break property programming.
- `num_vpp_pipe` directly affects buffer-size math and frequency calculations.
- The `dma_mask` upper bound and TZ CP region must stay compatible with firmware/IOMMU layout.

## Test Signals
- Boot/probe on SM8250 and SC7280 with the intended compatible string.
- Decoder stream-on for H.264/HEVC/VP9 and encoder stream-on for H.264/HEVC.
- V4L2 control tests for profile/level, bitrate, header mode, entropy, and QP controls.
- Runtime PM suspend/resume and firmware boot using `qcom/vpu-1.0/venus.mbn` or `qcom/vpu/vpu20_p1.mbn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_gen1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_gen2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_gen2.c

## Purpose
Defines second-generation Iris platform data for SM8550, SM8650, SM8750, and QCS8300. It adds AV1 decode support, gen2 HFI property mappings, richer decoder/encoder firmware capability tables, UBWC configuration, subscribe/config property arrays, and VPU3/VPU33/VPU35 generation choices.

## Important APIs, Types, And Data
- `platform_fmts_sm8550_dec` supports H.264, HEVC, VP9, and AV1 decoder input.
- `inst_fw_cap_sm8550_dec` maps gen2 decoder caps such as profiles, levels, AV1 tier/DRAP/film grain/super block, host max counts, stage, pipe, POC, coded frames, bit depth, and RAP start to `HFI_PROP_*` IDs.
- `inst_fw_cap_sm8550_enc` maps encoder profile/level, stage, header mode, SPS/PPS prepend flag, bitrate/peak bitrate, bitrate mode, frame skip, frame RC, GOP, entropy, QP ranges and explicit frame QPs, host max counts, rotation, flips, and intra-refresh controls.
- `platform_inst_cap_sm8550` and `platform_inst_cap_qcs8300` define SoC limits; QCS8300 is reduced to 4096 dimensions and lower firmware cycle coefficients.
- `iris_set_sm8550_preset_registers()` writes the same preset register as gen1.
- Tables cover SM8550 ICC, reset, bandwidth, PM domains, OPP domains, clocks, OPP clocks, UBWC config, TZ CP region, HFI config parameters, HFI subscribed properties, and internal buffer tables.
- Exported descriptors: `sm8550_data`, `sm8650_data`, `sm8750_data`, and `qcs8300_data`.

## Control Flow And Integration Points
`iris_probe.c` selects these descriptors for `"qcom,sm8550-iris"`, `"qcom,sm8650-iris"`, `"qcom,sm8750-iris"`, and `"qcom,qcs8300-iris"`. The descriptors initialize gen2 HFI command/response ops and feed V4L2 format enumeration, control setup, stream-on property programming, HFI subscriptions, internal buffer creation, power scaling, VPU firmware boot, and runtime PM. SM8650 mostly reuses SM8550 tables but swaps VPU ops, buffer sizing, reset tables, controller resets, and firmware. SM8750 swaps VPU35 ops, reset and clock tables, and firmware. QCS8300 reuses SM8550 logic with QCS8300 session caps, two VPP pipes, lower throughput, and a different firmware name.

## State And Persistence Behavior
The platform tables are static and module-lifetime. Per-instance firmware caps are copied from the const platform arrays into each instance, where controls mutate values. Config and subscription arrays are immutable and determine the firmware properties negotiated during stream-on and event handling.

## Dependencies
Depends on gen2 HFI defines, Iris control setters, VPU buffer sizing, common VPU ops, and board-specific headers `iris_platform_qcs8300.h`, `iris_platform_sm8650.h`, and `iris_platform_sm8750.h`.

## Risks
- Gen2 capability arrays are large and couple V4L2 control values, HFI property IDs, setter functions, port flags, and dynamic flags. A wrong setter or flag can expose unsupported dynamic controls or program the wrong port.
- SM8650/SM8750/QCS8300 inherit most SM8550 tables; changes to shared arrays affect multiple SoCs.
- AV1-specific caps and internal buffers must stay consistent with buffer sizing and HFI response parsing.
- `num_vpp_pipe`, `max_core_mbpf`, and `max_core_mbps` are used for admission and sizing, so bad values become stream-on failures or insufficient allocation.

## Test Signals
- Probe and firmware boot for all four compatible strings.
- V4L2 format enumeration includes AV1 decode on gen2 platforms.
- Control enumeration/default validation for dynamic bitrate, QP, rotation/flip, intra-refresh, and AV1 caps.
- Decode stream-on for H.264/HEVC/VP9/AV1 and encoder stream-on for H.264/HEVC on SM8550-family hardware.
- HFI subscription events for no-output/source-change and AV1 compression/complexity properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_gen2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_qcs8300.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_qcs8300.h

## Purpose
Supplies QCS8300-specific instance capability limits for inclusion by `iris_platform_gen2.c`.

## Important APIs And Data
- `platform_inst_cap_qcs8300` sets min/max dimensions, max macroblocks per frame, VPP/FW cycle coefficients, COMV count, and max frame/operating rate.
- Limits are narrower than SM8550: max frame width/height are 4096 and `max_mbpf` is based on 4096x2176.

## Control Flow And Integration Points
`qcs8300_data` in `iris_platform_gen2.c` references this struct through `.inst_caps`. Admission checks in `iris_vb2.c`, frame-size enumeration in `iris_vidc.c`, core throughput checks in `iris_utils.c`, and AV1 persistent buffer sizing all consume these caps.

## State And Persistence Behavior
The struct is static platform data. It is not mutated at runtime.

## Dependencies
Depends on `struct platform_inst_caps` and `MAXIMUM_FPS` from `iris_platform_common.h`, which must be included before this header.

## Risks
- Because this is a header with a static definition, it should only be included where intended; multiple inclusions in different C files would create separate private copies.
- Incorrect cap values can expose unsupported resolutions or reject valid QCS8300 workloads.

## Test Signals
- `VIDIOC_ENUM_FRAMESIZES` on QCS8300 reports 96 to 4096 limits.
- Stream-on rejects resolutions above QCS8300 capacity and accepts supported 4K-class workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_qcs8300.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sc7280.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sc7280.h

## Purpose
Provides SC7280-specific bandwidth, OPP power-domain, clock, and OPP clock tables used by gen1 platform data.

## Important APIs And Data
- `sc7280_bw_table_dec` maps descending decode macroblocks-per-second breakpoints to DDR bandwidth votes.
- `sc7280_opp_pd_table` names the `"cx"` OPP power domain.
- `sc7280_clk_table` maps Iris logical clocks to `"core"`, `"iface"`, `"bus"`, `"vcodec_core"`, and `"vcodec_bus"`.
- `sc7280_opp_clk_table` uses `"vcodec_core"` for OPP rate selection.

## Control Flow And Integration Points
`sc7280_data` in `iris_platform_gen1.c` references these tables. Probe resolves their clock/PM-domain names from DT, power scaling reads the bandwidth table, and VPU/resource helpers look up logical clock types through `iris_prepare_enable_clock()`.

## State And Persistence Behavior
All data is static const and immutable at runtime.

## Dependencies
Requires `struct bw_info`, `struct platform_clk_data`, and `IRIS_*_CLK` enum definitions from `iris_platform_common.h`.

## Risks
- DT clock names must match these strings exactly; mismatches fail probe or VPU power transitions.
- Bandwidth points are consumed by a linear lookup in `iris_power.c`; table ordering matters.

## Test Signals
- SC7280 probe validates clock and OPP-domain names.
- Decode workloads at 1080p/4K and 30/60 fps should produce the expected ICC vote tiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sc7280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sm8650.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sm8650.h

## Purpose
Supplies SM8650-specific reset-name tables used by `sm8650_data`.

## Important APIs And Data
- `sm8650_clk_reset_table` lists `"bus"` and `"core"` resets.
- `sm8650_controller_reset_table` lists the `"xo"` controller reset.

## Control Flow And Integration Points
`iris_platform_gen2.c` assigns these arrays to `.clk_rst_tbl` and `.controller_rst_tbl` for `sm8650_data`. `iris_probe.c` resolves them via `iris_init_resets()`, and VPU33 controller power-off code asserts/deasserts the controller reset during low-power teardown.

## State And Persistence Behavior
Static const reset-name data, immutable for module lifetime.

## Dependencies
The arrays are plain string tables but their meaning depends on reset-controller entries in SM8650 DT and VPU33 power code.

## Risks
- Missing or renamed DT resets cause probe failure or incomplete controller reset handling.
- The `"xo"` reset is only used when `controller_rst_tbl_size` is nonzero, so size propagation in platform data is critical.

## Test Signals
- SM8650 probe succeeds with all reset controls resolved.
- Runtime suspend/resume and close/open loops exercise VPU33 controller reset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sm8650.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sm8750.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sm8750.h

## Purpose
Provides SM8750-specific reset and clock tables used by the VPU35 platform descriptor.

## Important APIs And Data
- `sm8750_clk_reset_table` names `"bus0"`, `"bus1"`, `"core"`, and `"vcodec0_core"` resets.
- `sm8750_clk_table` maps logical clocks to `"iface"`, `"core"`, `"vcodec0_core"`, `"iface1"`, `"core_freerun"`, and `"vcodec0_core_freerun"`.

## Control Flow And Integration Points
`sm8750_data` in `iris_platform_gen2.c` uses these arrays. Probe resolves all clocks/resets, while VPU35 power-on/off code uses the logical clock types for AXI, hardware, and freerun clocks.

## State And Persistence Behavior
Static const platform tables; no runtime mutation.

## Dependencies
Depends on `struct platform_clk_data` and logical clock enum definitions from `iris_platform_common.h`.

## Risks
- SM8750 introduces additional AXI and freerun clocks. Missing logical-clock mapping causes `iris_prepare_enable_clock()` to fail during power-on.
- Reset names must stay synchronized with device-tree bindings.

## Test Signals
- Probe on SM8750 validates the clock/reset names.
- Firmware boot and runtime PM exercise VPU35 freerun clock enable/disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sm8750.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_power.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_power.c

## Purpose
Implements per-session and aggregate power scaling for Iris. It calculates DDR interconnect bandwidth and VPU clock votes from active queued input, then applies aggregate votes across all live sessions.

## Important APIs And Functions
- `iris_calc_bw()` converts resolution and fps to macroblocks per second and chooses a DDR bandwidth tier from the platform decoder bandwidth table.
- `iris_set_interconnects()` sums `instance->power.icc_bw` across sessions with `max_input_data_size` and calls `iris_set_icc_bw()`.
- `iris_vote_interconnects()` derives the current session vote from source format width/height at `DEFAULT_FPS`.
- `iris_set_clocks()` sums `instance->power.min_freq` and calls `iris_opp_set_rate()`.
- `iris_scale_clocks()` scans queued source buffers to find maximum compressed input data size, asks platform `vpu_ops->calc_freq()` for a frequency vote, and updates aggregate clocks.
- `iris_scale_power()` resumes runtime PM if needed, then scales clocks and interconnects.

## Control Flow And Integration Points
Codec queue paths call `iris_scale_power()` when buffers are queued or stream-on begins. The clock calculation delegates to VPU generation-specific `calc_freq` operations. Interconnect programming delegates to `iris_resources.c`. Aggregation is guarded by `core->lock` and only counts sessions that have observed input data.

## State And Persistence Behavior
Updates mutable per-instance `inst->max_input_data_size`, `inst->power.min_freq`, and `inst->power.icc_bw`, plus aggregate `core->power.clk_freq` and `core->power.icc_bw`. Votes persist until later scaling or teardown resets resources.

## Dependencies
Depends on V4L2 mem2mem queued-buffer iteration, PM runtime, `iris_resources` OPP/ICC helpers, platform bandwidth tables, and VPU generation ops.

## Risks
- `iris_calc_bw()` uses `DEFAULT_FPS` rather than actual session frame/operating rate, so bandwidth votes may be approximate.
- `iris_scale_power()` ignores the return value of `iris_scale_power(inst)` in `iris_vb2_start_streaming()` call sites, so failures may be hidden depending on caller.
- Aggregation skips sessions with zero `max_input_data_size`; early stream-on before input data may under-vote clocks.
- Table ordering in `bw_tbl_dec` controls selected ICC votes.

## Test Signals
- Instrument ICC/OPP votes while queueing different resolutions and compressed frame sizes.
- Multi-session tests should show aggregate clock and bandwidth increases.
- Runtime autosuspend/resume tests should verify scaling works after suspended state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_power.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_power.h

## Purpose
Declares the Iris power-scaling entry point.

## Important APIs
- `int iris_scale_power(struct iris_inst *inst);` recalculates and applies clock and interconnect votes for a session.

## Control Flow And Integration Points
Included by vb2 and codec queue paths so stream-on/qbuf can request updated power votes. Implementation is in `iris_power.c`.

## State And Persistence Behavior
The header owns no state.

## Dependencies
Forward-declares `struct iris_inst`; implementation depends on PM runtime, V4L2 mem2mem, platform VPU ops, and resource helpers.

## Risks
Callers must check the return value if power scaling failure should abort the current operation.

## Test Signals
Compile coverage catches signature drift; runtime stream-on/qbuf paths exercise the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_probe.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_probe.c

## Purpose
Implements the platform driver lifecycle for Qualcomm Iris. It binds DT compatibles to platform data, maps registers/IRQ, initializes HFI and hardware resources, registers V4L2 decoder/encoder video devices, sets DMA constraints, and wires runtime/system PM.

## Important APIs And Functions
- `iris_init_icc()` allocates `icc_bulk_data` from platform ICC table and obtains interconnect paths.
- `iris_init_power_domains()` attaches normal and OPP PM domains, configures OPP clocks, and loads the OPP table.
- `iris_init_clocks()` obtains all clocks from DT.
- `iris_init_reset_table()` and `iris_init_resets()` resolve bulk reset controls, including optional controller resets.
- `iris_register_video_device()` creates decoder or encoder `video_device` objects with selected ioctl ops.
- `iris_probe()` allocates `iris_core`, maps MMIO, obtains IRQ, initializes ops, resources, caps, V4L2 devices, DMA mask/segments, and runtime PM autosuspend.
- `iris_remove()` unregisters devices and deinitializes core state.
- `iris_sys_error_handler()` deinitializes and reinitializes the core after system error.
- `iris_pm_suspend()` and `iris_pm_resume()` call HFI PM hooks only when the core is initialized.

## Control Flow And Integration Points
`module_platform_driver()` registers `qcom_iris_driver`. DT matching selects one `iris_platform_data` entry. Probe initializes generic V4L2/vb2 ops through `iris_init_ops()`, then platform-specific HFI ops through callbacks in the matched platform data. Decoder and encoder devices share the same core but expose different names and ioctl tables. Runtime PM is enabled after successful device registration and DMA setup.

## State And Persistence Behavior
Creates the long-lived `iris_core` devm allocation with lock, instance list, response packet, completion, delayed system-error work, resource handles, and video-device pointers. Core state starts at `IRIS_CORE_DEINIT`; actual firmware/core initialization occurs later on open. Devm-managed resources are released by device core; V4L2 devices are explicitly unregistered on remove/error.

## Dependencies
Uses Linux platform, IRQ, clk, ICC, PM-domain, OPP, reset, PM runtime, DMA, and V4L2 subsystems. Integrates with `iris_core`, `iris_ctrls`, `iris_vidc`, HFI ISR/handlers, and all exported platform data.

## Risks
- Error unwinding must unregister video devices and V4L2 device in the right order; probe registers decoder before encoder.
- `of_device_get_match_data()` must return valid platform data; missing match data would crash later.
- Optional controller resets are only initialized when size is nonzero; platform size/table consistency is critical.
- The driver disables IRQ after request; firmware/core init must later enable it correctly.
- `iris_remove()` unregisters both `vdev_dec` and `vdev_enc`; partial probe failures must avoid later remove paths with unset pointers.

## Test Signals
- Probe/unbind tests for each compatible string.
- Failure injection around ICC/PM-domain/clock/reset/video registration validates unwind.
- Runtime PM suspend/resume while streaming and idle.
- System-error work path triggers deinit/init recovery without leaking devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_resources.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_resources.c

## Purpose
Provides low-level resource helpers for interconnect bandwidth, OPP rate selection, PM-domain enable/disable, and logical clock enable/disable.

## Important APIs And Functions
- `iris_set_icc_bw()` clamps requested `"video-mem"` bandwidth to platform min/max, suppresses small changes below `BW_THRESHOLD`, updates `core->power.icc_bw`, and calls `icc_bulk_set_bw()`.
- `iris_unset_icc_bw()` clears all ICC votes.
- `iris_opp_set_rate()` resolves a recommended OPP for a frequency and applies it with `dev_pm_opp_set_opp()`.
- `iris_enable_power_domains()` sets max OPP then runtime-resumes a PM-domain device.
- `iris_disable_power_domains()` sets zero OPP then runtime-puts the PM-domain device.
- `iris_get_clk_by_type()` maps an Iris logical clock type to a runtime `struct clk *` using platform clock-name tables and devm bulk clocks.
- `iris_prepare_enable_clock()` and `iris_disable_unprepare_clock()` wrap clock lookup plus enable/disable.

## Control Flow And Integration Points
Probe fills `core->icc_tbl`, `core->clock_tbl`, `core->pmdomain_tbl`, and OPP config. Power scaling calls `iris_set_icc_bw()` and `iris_opp_set_rate()`. VPU generation power-on/off code uses PM-domain and clock helpers to sequence hardware.

## State And Persistence Behavior
Mutates aggregate `core->power.icc_bw` and the in-memory ICC bulk table. Clock and PM-domain references are devm/probe state; helpers do not persist additional state.

## Dependencies
Linux clk, devfreq/OPP, interconnect, PM-domain, PM runtime, reset includes, and `iris_core` platform data.

## Risks
- `iris_enable_power_domains()` returns negative `pm_runtime_get_sync()` errors without balancing a failed get, matching common kernel risk patterns.
- `iris_opp_set_rate(ULONG_MAX)` assumes an OPP table can resolve a max rate.
- Clock lookup depends on exact string matches between platform data and DT.
- `BW_THRESHOLD` suppresses small vote changes, which can hide expected test-observed transitions.

## Test Signals
- PM-domain and clock enable failure injection should unwind in VPU power code.
- Trace ICC votes for clamp and threshold behavior.
- Validate every logical clock used by platform VPU ops resolves on each SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_resources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_resources.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_resources.h

## Purpose
Declares resource-management helpers used by power, probe, and VPU generation code.

## Important APIs
- OPP: `iris_opp_set_rate()`.
- PM domains: `iris_enable_power_domains()`, `iris_disable_power_domains()`.
- ICC: `iris_set_icc_bw()`, `iris_unset_icc_bw()`.
- Clocks: `iris_prepare_enable_clock()`, `iris_disable_unprepare_clock()`.

## Control Flow And Integration Points
Included by platform, power, and VPU files. The functions are implemented in `iris_resources.c` and operate on `iris_core` resources initialized by `iris_probe.c`.

## State And Persistence Behavior
No state in the header; callers mutate core resource state through the implementation.

## Dependencies
Requires `struct device`, `struct iris_core`, and `enum platform_clk_type` declarations from surrounding includes.

## Risks
Header users must include platform-common definitions before using clock-type APIs.

## Test Signals
Build coverage verifies function prototypes across VPU/power users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_resources.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_state.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_state.c

## Purpose
Implements the Iris instance state machine and sub-state transitions for stream lifecycle, dynamic resolution change, drain, pause, and command admission.

## Important APIs And Functions
- `iris_allow_inst_state_change()` encodes legal transitions among INIT, input-streaming, output-streaming, streaming, and deinit states.
- `iris_inst_change_state()` applies a state transition, with ERROR allowed from any non-error state and no-op behavior after error.
- `iris_inst_state_change_streamon()` and `iris_inst_state_change_streamoff()` translate V4L2 plane stream-on/off into instance state transitions.
- `iris_inst_allow_sub_state()` validates sub-state bits against the current main state.
- `iris_inst_change_sub_state()` atomically clears and sets sub-state bits after conflict/range validation.
- `iris_inst_sub_state_change_drc()`, `_drain_last()`, `_drc_last()`, and `_pause()` encode higher-level DRC/drain/pause sequences.
- `iris_drc_pending()` and `iris_drain_pending()` report complete pending DRC/drain last-buffer conditions.
- `iris_allow_cmd()` gates V4L2 START/STOP decoder/encoder commands based on queue streaming state and sub-state.

## Control Flow And Integration Points
vb2 stream-on/off paths call the plane transition helpers through codec/HFI processing. HFI response handling and codec command paths set DRC/drain sub-states. `iris_vidc.c` command ioctls call `iris_allow_cmd()` before dispatching to decoder/encoder start/stop handlers. `iris_vb2.c` uses pending DRC/drain sub-states to synthesize LAST/EOS on capture buffers.

## State And Persistence Behavior
Mutates `inst->state` and `inst->sub_state`. These persist for the instance lifetime and are protected by caller-held `inst->lock` in most call paths. Error state is sticky: state-change helpers no-op once in `IRIS_INST_ERROR`.

## Dependencies
Depends on V4L2 mem2mem queue helpers and `iris_instance.h` definitions.

## Risks
- A debug message in `iris_inst_change_state()` prints `inst->state` after assignment as both old/new source; the message does not show the true old state.
- Sub-state validation uses bitmask comparisons; new sub-states must update `IRIS_INST_SUB_STATES`, allowed-state logic, and command logic.
- Incorrect DRC/drain sequencing can deadlock clients waiting for LAST/EOS or reject valid START commands.

## Test Signals
- Stream-on/off permutations for output-only, capture-only, both queues, and teardown.
- Decoder dynamic-resolution-change tests with source-change events and LAST buffer.
- Decoder/encoder drain STOP then START command tests.
- Error injection should make subsequent state transitions no-op and queue operations fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_state.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_state.h

## Purpose
Defines Iris core and instance lifecycle states, instance sub-state bitflags, and state-machine APIs.

## Important APIs And Types
- `enum iris_core_state`: DEINIT, INIT, ERROR.
- `enum iris_inst_state`: DEINIT, INIT, INPUT_STREAMING, OUTPUT_STREAMING, STREAMING, ERROR.
- `enum iris_inst_sub_state`: FIRST_IPSC, DRC, DRC_LAST, DRAIN, DRAIN_LAST, INPUT_PAUSE, OUTPUT_PAUSE, LOAD_RESOURCES.
- Public helpers include main/sub-state transitions, DRC/drain/pause helpers, command admission, and pending-state predicates.

## Control Flow And Integration Points
Included by instance, core, vb2, V4L2 command, HFI response, and codec files. The documented ASCII diagrams describe legal lifecycle movement and are implemented in `iris_state.c`.

## State And Persistence Behavior
Defines the values stored in `iris_core.state`, `iris_inst.state`, and `iris_inst.sub_state`.

## Dependencies
Uses Linux `BIT()` macro through included contexts and forward-declares `struct iris_inst`.

## Risks
The enum integer values are used in debug and state comparisons; changing order affects persisted in-memory behavior and should be treated as ABI-like inside the driver.

## Test Signals
Build coverage plus lifecycle tests through V4L2 stream-on/off and command ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_utils.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_utils.c

## Purpose
Provides shared helpers for resolution comparison, macroblock accounting, split-mode detection, buffer completion, firmware response waits, instance lookup, aggregate core admission checks, and rotation predicates.

## Important APIs And Functions
- `iris_res_is_less_than()` compares two resolutions using macroblocks and side limits.
- `iris_get_mbpf()` computes macroblocks per frame from max(source format, crop).
- `iris_split_mode_enabled()` returns true for NV12 and QC08C capture/output layouts that use DPB split mode.
- `iris_helper_buffers_done()` drains all queued src or dst m2m buffers with a vb2 state.
- `iris_wait_for_session_response()` waits for session or flush completion with platform timeout, temporarily releasing `inst->lock`, and marks the instance error on timeout.
- `iris_get_instance()` looks up an instance by firmware session ID under `core->lock`.
- `iris_check_core_mbpf()` and `iris_check_core_mbps()` enforce aggregate core capacity across all instances.
- `is_rotation_90_or_270()` checks the ROTATION firmware cap.

## Control Flow And Integration Points
Admission checks are called from vb2 queue setup/start and encoder parameter changes. HFI response code can resolve instances by session ID. Command/close paths use completion waiting. Buffer queue error paths use `iris_helper_buffers_done()`. VPU buffer sizing uses split-mode and rotation helpers.

## State And Persistence Behavior
Mostly read-only. `iris_wait_for_session_response()` mutates instance state to ERROR on timeout. Buffer completion drains queued vb2 buffers and changes their userspace-visible state.

## Dependencies
Depends on PM runtime include, V4L2 mem2mem, `iris_instance`, and utility header definitions.

## Risks
- `iris_wait_for_session_response()` unlocks and relocks `inst->lock`; callers must be prepared for concurrent state changes while waiting.
- Aggregate core checks include all instances and use current format/crop/rate fields; races are controlled only if callers hold appropriate locks.
- Split-mode detection is hard-coded to two formats and affects DPB allocation and buffer sizing.

## Test Signals
- Multi-session admission tests for macroblocks per frame and per second.
- Firmware response timeout injection should mark instance ERROR.
- DRC/split-mode streams validate DPB count and output sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_utils.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_utils.h

## Purpose
Declares shared Iris utility types and helper functions.

## Important APIs And Types
- Metadata structs: `iris_hfi_rect_desc`, `iris_hfi_frame_info`, and `iris_ts_metadata`.
- `NUM_MBS_PER_FRAME(height, width)` macro computes 16x16 macroblock count.
- `iris_v4l2_type_to_driver()` maps V4L2 OUTPUT to `BUF_INPUT` and all other types to `BUF_OUTPUT`.
- Function declarations cover resolution comparison, MBPF, split mode, instance lookup, buffer draining, response waiting, core capacity checks, and rotation.

## Control Flow And Integration Points
Included broadly by codec, vb2, VPU buffer, HFI response, and control code. The inline V4L2-to-driver mapping is used in queue paths to select Iris buffer type.

## State And Persistence Behavior
No state in the header; declared helpers operate on `iris_inst` and `iris_core`.

## Dependencies
Includes `iris_buffer.h` and relies on V4L2 types being visible to users.

## Risks
`iris_v4l2_type_to_driver()` treats any non-output type as output/capture driver buffer, so callers should validate V4L2 type before using it.

## Test Signals
Compile coverage and queue-type tests through vb2 stream-on/qbuf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vb2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vb2.c

## Purpose
Implements videobuf2 queue operations for Iris V4L2 mem2mem sessions: queue setup, buffer initialization/preparation/validation, stream-on/off, and buffer queueing.

## Important APIs And Functions
- `iris_check_inst_mbpf()`, `iris_check_resolution_supported()`, and `iris_check_session_supported()` validate instance membership, aggregate core capacity, per-instance macroblocks, and frame dimensions.
- `iris_vb2_buf_init()` stores the DMA-contiguous plane address in `iris_buffer.device_addr`.
- `iris_vb2_queue_setup()` validates requested plane count/size, opens the firmware session once, and transitions the instance to INIT.
- `iris_vb2_start_streaming()` scales power, validates support, dispatches stream-on to decoder/encoder input/output helpers, then queues deferred user/internal buffers when both planes are ready.
- `iris_vb2_stop_streaming()` calls `iris_session_streamoff()` and completes remaining buffers with ERROR.
- `iris_vb2_buf_prepare()` validates field and plane sizes unless DRC is in progress.
- `iris_vb2_buf_out_validate()` forces output field to NONE.
- `iris_vb2_buf_queue()` rejects empty output payloads, handles DRC/drain LAST-buffer EOS synthesis on capture, queues buffers into v4l2-m2m, and dispatches to decoder/encoder qbuf.

## Control Flow And Integration Points
`iris_vidc.c` installs these operations in `vb2_ops`. Userspace `REQBUFS`, `STREAMON`, `QBUF`, and `STREAMOFF` reach this file through V4L2 mem2mem helpers. The file dispatches domain-specific behavior to `iris_vdec.c` or `iris_venc.c`, uses `iris_power.c` for scaling, uses state helpers for errors, and uses VPU buffer sizing for buffer-size validation.

## State And Persistence Behavior
Sets per-buffer DMA address and Iris buffer attributes. Opens the firmware session once using `inst->once_per_session_set`. Mutates instance state on queue setup/start errors. DRC/drain capture queueing may set `V4L2_BUF_FLAG_LAST`, increment capture sequence, mark m2m stopped, queue EOS event, and set `inst->last_buffer_dequeued`.

## Dependencies
Depends on V4L2 mem2mem, videobuf2 DMA-contig, V4L2 events, Iris common/session/buffer/power/codec helpers.

## Risks
- `iris_vb2_start_streaming()` calls `iris_scale_power(inst)` but does not check its return value.
- Queue setup opens the firmware session before both queues necessarily stream; error paths must close during release.
- During DRC, size validation is relaxed, so later firmware/buffer logic must handle resized buffers correctly.
- EOS/LAST synthesis depends on precise sub-state bits; missed bit clearing can make subsequent capture buffers complete as LAST incorrectly.

## Test Signals
- V4L2 compliance for reqbufs/qbuf/streamon/streamoff.
- Empty output-buffer qbuf rejection.
- DRC and drain tests should observe LAST/EOS exactly once.
- Stream-on failure injection should return queued buffers and mark instance error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vb2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vb2.h

## Purpose
Declares Iris vb2 operation callbacks.

## Important APIs
- Buffer lifecycle: `iris_vb2_buf_init()`, `iris_vb2_buf_prepare()`, `iris_vb2_buf_out_validate()`, `iris_vb2_buf_queue()`.
- Queue lifecycle: `iris_vb2_queue_setup()`, `iris_vb2_start_streaming()`, `iris_vb2_stop_streaming()`.

## Control Flow And Integration Points
`iris_vidc.c` references these functions in its static `vb2_ops` table for both decoder and encoder queues.

## State And Persistence Behavior
No header state; implementation mutates instances, queues, and buffers.

## Dependencies
Requires vb2 types and Iris instance definitions in including files.

## Risks
Signature changes must stay synchronized with the V4L2/vb2 callback table.

## Test Signals
Compile coverage and V4L2 queue lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vdec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vdec.c

## Purpose
Implements decoder-specific V4L2 session initialization, format enumeration/try/set, event subscription, source-change notification, stream-on sequencing, buffer queueing, and decoder START/STOP command handling.

## Important APIs And Functions
- `iris_vdec_inst_init()` allocates source/capture formats, sets defaults, initializes buffer counts/sizes, copies decoder firmware caps, and initializes controls.
- `iris_vdec_formats_cap` exposes NV12 and QC08C capture formats.
- `find_format()` and `find_format_by_index()` search platform compressed input formats or local capture formats.
- `iris_vdec_enum_fmt()`, `iris_vdec_try_fmt()`, and `iris_vdec_s_fmt()` implement decoder format negotiation with alignment and colorimetry propagation.
- `iris_vdec_validate_format()` validates either compressed or raw decoder formats.
- `iris_vdec_subscribe_event()` supports EOS, source-change, and control events.
- `iris_vdec_src_change()` queues `V4L2_EVENT_SOURCE_CHANGE` for resolution changes.
- `iris_vdec_streamon_input()` sets input properties, allocates persistent buffers, creates/queues input-side internal buffers, and sends stream-on input.
- `iris_vdec_streamon_output()` sets capture config params, creates/queues output-side internal buffers, sends stream-on output, and unwinds with streamoff on error.
- `iris_vdec_qbuf()` converts vb2 buffer to Iris buffer, stores timestamp metadata for input, defers if queue is not streaming, scales power, and queues to firmware.
- `iris_vdec_start_cmd()` resumes after DRC or drain last-buffer state and clears sub-state bits.
- `iris_vdec_stop_cmd()` sends firmware drain and marks drain sub-state.

## Control Flow And Integration Points
`iris_vidc.c` dispatches decoder ioctls here. `iris_vb2.c` calls stream-on and qbuf helpers. HFI responses trigger source-change and completion behavior in other files. VPU buffer sizing is queried whenever formats or buffer counts change.

## State And Persistence Behavior
Allocates and owns `inst->fmt_src`/`fmt_dst` until close. Mutates `inst->codec`, crop, colorimetry, buffer sizes/counts, firmware caps copy, sub-state bits, last-buffer state, and timestamp metadata. Source-change and drain state persists until START command clears it.

## Dependencies
V4L2 events/mem2mem, Iris buffer/common/control/instance/power/VPU-buffer helpers, and HFI command ops.

## Risks
- `iris_vdec_inst_init()` allocates two format objects but does not check for allocation failure before dereferencing; unlike encoder init, this can fail unsafely under memory pressure.
- Width/height zero is accepted for bitstream input and replaced with defaults; clients must handle later source-change to real dimensions.
- Capture try-fmt clamps dimensions to source dimensions while source queue streams, affecting DRC behavior.
- Stream-on output error handling must avoid leaking internal buffers after partial creation.

## Test Signals
- V4L2 decode format enumeration and set/try format tests for compressed input and NV12/QC08C output.
- H.264/HEVC/VP9/AV1 decode stream-on, qbuf, source-change, drain STOP/START, and EOS event tests.
- Low-memory fault injection around `kzalloc_obj()` and internal buffer creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vdec.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vdec.h

## Purpose
Declares decoder-specific Iris operations used by generic V4L2 and vb2 code.

## Important APIs
Includes instance init, enum/try/set/validate format, event subscription, source-change event, stream-on input/output, qbuf, and decoder START/STOP command handlers.

## Control Flow And Integration Points
`iris_vidc.c` uses the ioctl-facing helpers. `iris_vb2.c` uses stream-on/qbuf helpers. HFI response code can call source-change notification.

## State And Persistence Behavior
No header state; implementation mutates decoder session format, crop, buffers, and sub-state.

## Dependencies
Requires V4L2 types and `struct iris_inst`.

## Risks
Prototype drift impacts generic dispatch in `iris_vidc.c` and queue dispatch in `iris_vb2.c`.

## Test Signals
Build coverage plus decoder V4L2 lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vdec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_venc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_venc.c

## Purpose
Implements encoder-specific V4L2 session initialization, raw/compressed format negotiation, crop selection, frame-rate parameters, event subscription, stream-on sequencing, buffer queueing, and encoder START/STOP drain handling.

## Important APIs And Functions
- `iris_venc_inst_init()` allocates formats, sets default H.264 capture and NV12 output, initializes crop/rates/scaling fields, copies encoder firmware caps, and initializes controls.
- `iris_venc_formats_cap` exposes H.264 and HEVC compressed capture formats.
- `iris_venc_formats_out` exposes NV12 and QC08C raw input formats.
- `iris_venc_enum_fmt()`, `iris_venc_try_fmt()`, and `iris_venc_s_fmt()` implement format negotiation.
- `iris_venc_s_fmt_input()` aligns raw input, propagates colorimetry, updates crop and scaling defaults, and refreshes output format if dimensions changed.
- `iris_venc_s_fmt_output()` sets compressed codec, bitstream dimensions, optional scaling dimensions, output buffer size, and colorimetry.
- `iris_venc_validate_format()` checks raw or compressed formats.
- `iris_venc_subscribe_event()` supports EOS and control events.
- `iris_venc_s_selection()` implements output crop and updates encoded output dimensions.
- `iris_venc_s_param()`/`iris_venc_g_param()` set/get operating rate and frame rate with cap and core-throughput checks.
- `iris_venc_streamon_input()` and `iris_venc_streamon_output()` set firmware properties, allocate ARP persistent buffers, create/queue internal buffers, and send stream-on.
- `iris_venc_qbuf()` converts and queues buffers, with timestamp metadata on raw input and deferred behavior before queue streaming.
- `iris_venc_start_cmd()` resumes after drain-last and clears drain/pause sub-states.
- `iris_venc_stop_cmd()` sends firmware drain, sets drain sub-state, and scales power.

## Control Flow And Integration Points
Generic V4L2 ioctls in `iris_vidc.c` dispatch encoder operations here. vb2 stream/qbuf paths call encoder helpers from `iris_vb2.c`. Control setters use `inst->fw_caps` copied from platform gen1/gen2 data. VPU buffer sizing uses encoder dimensions, scaling, rotation, codec, and rate-control state.

## State And Persistence Behavior
Owns `inst->fmt_src`, `fmt_dst`, codec, crop, `operating_rate`, `frame_rate`, raw/scaled encoder dimensions, buffer counts/sizes, firmware caps, and drain sub-states. Format and parameter changes persist until changed or instance close.

## Dependencies
Depends on V4L2 events/mem2mem, Iris buffer/common/control/instance/power/VPU-buffer helpers, HFI command ops, and platform caps.

## Risks
- Output format helper name (`iris_venc_s_fmt_output`) refers to V4L2 capture/compressed output; caller context must avoid confusing raw output plane terminology.
- Scaling is inferred when compressed dimensions differ from raw input dimensions and affects VPSS buffer allocation.
- Frame-rate changes while streaming run aggregate core MBPF/MBPS checks; failure resets only the changed rate to default.
- Stream-on output allocates ARP buffers too; repeated or partial error paths need leak coverage.

## Test Signals
- H.264/HEVC encode format negotiation for NV12/QC08C input.
- Crop and scaling tests verify output bitstream dimensions and VPSS allocation.
- `VIDIOC_S_PARM`/`G_PARM` for operating/frame rate and max-rate rejection.
- Drain STOP/START sequence with EOS/LAST behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_venc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_venc.h

## Purpose
Declares encoder-specific Iris operations used by generic V4L2 and vb2 code.

## Important APIs
Includes instance init, enum/try/set/validate format, event subscription, crop selection, stream parameters, stream-on input/output, qbuf, and encoder START/STOP command handlers.

## Control Flow And Integration Points
`iris_vidc.c` dispatches encoder ioctls here, and `iris_vb2.c` dispatches stream/qbuf operations here for encoder sessions.

## State And Persistence Behavior
No header state; implementation mutates encoder session formats, crop, rates, scaling fields, buffers, and drain state.

## Dependencies
Requires V4L2 types and `struct iris_inst`.

## Risks
Header guard uses `_IRIS_VENC_H_` while most Iris headers use double-underscore names; functionally fine but style differs.

## Test Signals
Compile coverage plus encoder V4L2 lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_venc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vidc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vidc.c

## Purpose
Provides the V4L2 file operations, mem2mem queue initialization, ioctl dispatch, session open/close, and ops-table initialization for Iris decoder and encoder video devices.

## Important APIs And Functions
- `iris_v4l2_fh_init()`/`deinit()` manage V4L2 file handles and control handler attachment.
- `iris_add_session()`/`remove_session()` maintain `core->instances` with max-session gating.
- `iris_m2m_queue_init()` initializes OUTPUT and CAPTURE vb2 queues using DMA-contig memory and Iris vb2 ops.
- `iris_open()` identifies decoder vs encoder by video-device name, runtime-resumes and initializes the core, allocates a generation-specific instance, initializes locks/lists/completions/m2m context, calls decoder/encoder instance init, and registers the session.
- `iris_session_close()` sends HFI session close and waits for response.
- `iris_check_num_queued_internal_buffers()` reports internal buffer leaks on close.
- `iris_close()` frees controls, m2m context, firmware session, internal buffers, session list entry, locks, formats, and instance.
- ioctl helpers dispatch enum/try/set/get format, frame sizes, frame intervals, querycap, selection, event subscription, stream parameters, and decoder/encoder commands.
- Static `iris_v4l2_file_ops`, `iris_vb2_ops`, `iris_v4l2_ioctl_ops_dec`, and `iris_v4l2_ioctl_ops_enc` are installed by `iris_init_ops()`.

## Control Flow And Integration Points
`iris_probe.c` calls `iris_init_ops()` then installs the file/ioctl ops into decoder and encoder `video_device`s. Userspace open creates an Iris instance and m2m queues. Generic V4L2 ioctls reach dispatch helpers here, then call decoder/encoder-specific code. vb2 queue callbacks come from `iris_vb2.c`.

## State And Persistence Behavior
Creates per-open `iris_inst` state: session ID, domain, locks, buffer lists, completions, V4L2 fh, m2m device/context, formats, controls, rates, and firmware caps. `iris_close()` tears all of it down and checks for unreleased internal buffers. Core state is initialized on open and shared by sessions.

## Dependencies
Depends on PM runtime, V4L2 ioctl/event/mem2mem, videobuf2 DMA-contig, Iris instance/decoder/encoder/vb2/VPU-buffer/platform definitions, and HFI/core operations.

## Risks
- `iris_add_session()` silently does not add the instance if max-session count is reached, but `iris_open()` still returns success; later queue setup detects missing instance and fails. This is a behavioral risk for userspace.
- Device role detection depends on exact `video_device.name` strings.
- Close order is delicate: m2m context is released before firmware close and buffer destruction while `inst->lock` is later acquired.
- Internal buffer leak checks only log errors; they do not fail close.
- `iris_m2m_device_run()` is empty because firmware work is queue-driven; mem2mem scheduler behavior relies on explicit buffer completion elsewhere.

## Test Signals
- Open/close stress across max session count.
- V4L2 compliance for decoder and encoder device nodes.
- Frame-size/interval enumeration for supported and unsupported formats.
- Leak/error injection in stream-on followed by close should not leave internal buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vidc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vidc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vidc.h

## Purpose
Declares the generic Iris V4L2 ops initialization and file open/close entry points.

## Important APIs
- `iris_init_ops(struct iris_core *core)` installs static V4L2/vb2 ops into the core.
- `iris_open()` and `iris_close()` are file operations used by video devices.

## Control Flow And Integration Points
`iris_probe.c` calls `iris_init_ops()` and registers video devices whose file ops call `iris_open()` and `iris_close()`.

## State And Persistence Behavior
No header state; implementation creates and destroys per-file instances.

## Dependencies
Requires `struct iris_core` and `struct file` declarations in including code.

## Risks
Open/close prototypes are externally visible through static file ops; signature drift breaks V4L2 integration.

## Test Signals
Compile coverage plus video-device open/close tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vidc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu2.c

## Purpose
Provides VPU2 generation operations, chiefly frequency calculation for gen1 platforms.

## Important APIs And Functions
- `iris_vpu2_calc_freq()` computes required frequency from source/crop macroblocks per frame, default FPS, platform VPP/VSP cycle coefficients, and compressed input data size.
- `iris_vpu2_ops` supplies generic VPU power on/off/controller/hwmode operations plus the VPU2-specific `calc_freq`.

## Control Flow And Integration Points
Gen1 platform data assigns `.vpu_ops = &iris_vpu2_ops`. Power scaling calls `vpu_ops->calc_freq()` after scanning queued source buffers. Core/firmware init and runtime PM call the power/controller functions through VPU common code.

## State And Persistence Behavior
No persistent state. Frequency calculation reads instance format, crop, and platform caps.

## Dependencies
Depends on VPU common power helpers, register defines, `iris_instance`, and platform instance caps.

## Risks
- Uses `DEFAULT_FPS` instead of actual frame/operating rate.
- Data-size contribution is included only in VSP frequency and can dominate for high-bitrate inputs.
- Cycle coefficients in platform caps must be valid for VPU2.

## Test Signals
- Power-scaling traces on SM8250/SC7280 with varied resolution and input sizes.
- Runtime PM firmware boot and shutdown on VPU2 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu3x.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu3x.c

## Purpose
Implements VPU3/VPU33/VPU35 generation-specific power sequencing and operation tables.

## Important APIs And Functions
- `iris_vpu3x_hw_power_collapsed()` checks wrapper core power status.
- `iris_vpu3_power_off_hardware()` waits for idle VPP pipes, toggles NoC reset request/ack, resets the AHB bridge, and powers off hardware.
- `iris_vpu33_power_off_hardware()` uses an LPI handshake loop before bridge reset and hardware power-off.
- `iris_vpu33_power_off_controller()` sequences controller NoC LPI, debug bridge, clock halt, resets, AON MVP NoC reset, XO reset assertion/deassertion, clock disable, and PM-domain shutdown.
- `iris_vpu35_power_on_hw()` enables hardware power domain and AXI/HW freerun/HW clocks.
- `iris_vpu35_power_off_hw()` reuses VPU33 hardware shutdown plus freerun/AXI clock disable.
- `iris_vpu3_ops`, `iris_vpu33_ops`, and `iris_vpu35_ops` export generation-specific power and frequency function tables.

## Control Flow And Integration Points
Gen2 platform data selects these ops: SM8550/QCS8300 use VPU3, SM8650 uses VPU33, SM8750 uses VPU35. Core init/deinit and runtime PM call the ops through common VPU code. Resource helpers perform clock and PM-domain actions based on platform clock/domain tables.

## State And Persistence Behavior
Mutates hardware registers, reset lines, clocks, PM-domain states, and controller power state. It does not store software state beyond using `iris_core` resource handles.

## Dependencies
Linux iopoll/reset helpers, Iris VPU common helpers, register defines, resource clock/domain helpers, and platform `num_vpp_pipe`/reset/clock/domain tables.

## Risks
- Poll timeouts fall through to disable paths and often return 0 from controller power-off, so hardware handshake failures may be logged but not propagated.
- VPU33 controller shutdown assumes controller reset table and clock reset table are present and ordered for platform.
- LPI handshake loops retry 1000 times; incorrect register behavior can add latency.
- VPU35 clock sequencing requires freerun clocks that only SM8750 tables provide.

## Test Signals
- Runtime PM suspend/resume and open/close loops on SM8550, SM8650, and SM8750.
- Fault injection for readl poll timeouts and reset-control failures.
- Register tracing should show NoC LPI/reset/bridge reset sequences per generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu3x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu4x.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu4x.c

## Purpose
Implements VPU4x-specific hardware power sequencing, including efuse-gated subdomains for VPP0, VPP1, and APV.

## Important APIs And Functions
- `iris_vpu4x_genpd_set_hwmode()` toggles genpd hardware mode across HW/VPP/APV domains, skipping efuse-disabled subdomains and rolling back on error.
- `iris_vpu4x_power_on_apv()` and `_power_off_apv()` enable/disable APV PM domain and clock, perform NoC LPI/reset handshakes, and reset the APV bridge.
- `iris_vpu4x_ahb_sync_reset_apv()` and `_hardware()` reset APV or core AHB bridges.
- `iris_vpu4x_enable_hardware_clocks()` and `_disable_hardware_clocks()` sequence AXI, HW freerun, HW, BSE, VPP0, and VPP1 clocks with efuse guards.
- `iris_vpu4x_power_on_hardware()` enables efuse-available PM domains/clocks and optional APV.
- `iris_vpu4x_power_off_hardware()` disables hwmode, powers off APV, waits for core idle/LPI/reset, resets AHB bridge, disables clocks, and powers down domains.
- `iris_vpu4x_set_hwmode()` resets APV/core bridges and enables genpd hwmode.
- `iris_vpu4x_ops` exports the VPU4x operation table.

## Control Flow And Integration Points
Although none of the listed platform data selects `iris_vpu4x_ops`, the file defines the next-generation operation table for platforms that include VPU4x support. It uses the same resource helpers and PM-domain enum values defined in platform common data.

## State And Persistence Behavior
Reads efuse state from `WRAPPER_EFUSE_MONITOR`, mutates PM-domain hardware mode, PM-domain runtime state, clocks, and hardware reset/LPI registers. No additional software persistence.

## Dependencies
Linux iopoll/reset helpers, VPU common controller functions, register defines, and resource clock/PM-domain helpers. Requires platform data with APV/VPP PM domains and BSE/VPP/APV clock mappings when used.

## Risks
- Efuse bits dynamically remove subdomains; tests must cover disabled VPP/APV combinations.
- Some poll return values in power-off paths are not propagated, so logs may be the only signal of timeout.
- Clock/domain unwind paths are complex and must stay symmetric with power-on.
- `iris_vpu4x_enc_line_size()` passes `inst->codec` as the HFI standard argument even though helper comparisons expect HFI codec constants in related code; this needs integration review if VPU4x encoder is enabled.

## Test Signals
- Platform bring-up with efuse combinations for all subdomains.
- Runtime PM suspend/resume loops with register tracing for LPI/reset ack.
- Failure injection at each clock/PM-domain enable step to validate unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu4x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_buffer.c

## Purpose
Calculates firmware/internal buffer sizes and buffer counts for Iris decode and encode sessions across codecs and VPU generations. It is the sizing oracle for BIN, COMV, NON_COMV, LINE, PERSIST, DPB, SCRATCH, VPSS, ARP, and PARTIAL buffers.

## Important APIs And Functions
- Decode sizing helpers cover H.264/HEVC/VP9/AV1 BIN buffers, COMV, persistent buffers, non-COMV, line buffers, AV1 IBC/PARTIAL buffers, DPB split mode, and VPU4x-specific VP9/persist line sizing.
- Encode sizing helpers cover bitstream/bin buffers, COMV, non-COMV, line buffers, VPU33/VPU4x line variants, DPB/reference/UBWC metadata, ARP, VPSS/scaling, SCRATCH1, and SCRATCH2.
- `is_scaling_enabled()` detects encoder scaling from source and destination dimensions.
- `output_min_count()` chooses decoder capture minimum counts, including firmware-provided reconfig counts and VP9/AV1 defaults.
- `struct iris_vpu_buf_type_handle` maps Iris buffer types to size functions.
- `iris_vpu_buf_size()` dispatches base VPU2/VPU3 sizes for decoder/encoder.
- `iris_vpu33_buf_size()` reuses base decoder sizing but overrides encoder LINE sizing for VPU33.
- `iris_vpu4x_buf_size()` provides VPU4x-specific decoder and encoder sizing dispatch.
- `iris_vpu_buf_count()` returns required counts for user and internal buffer types.

## Control Flow And Integration Points
Codec init and format setters call `iris_get_buffer_size()`/`iris_vpu_buf_count()` through higher-level buffer helpers to set V4L2 `sizeimage` and min counts. Stream-on code creates internal buffers according to platform internal-buffer tables and these size/count calculations. Platform data selects the generation-specific top-level sizing function through `.get_vpu_buffer_size`. vb2 prepare validates user buffer plane sizes against computed sizes.

## State And Persistence Behavior
The file does not allocate buffers itself. It reads mutable session state: domain, codec, formats, crop, firmware caps (`STAGE`, `DRAP`, `ROTATION`), `hfi_rc_type`, firmware min output count, output buffer count, platform pipe count, and platform caps. Returned sizes influence persistent per-session buffer metadata and actual DMA allocations elsewhere.

## Dependencies
Depends on `iris_instance.h`, `iris_vpu_buffer.h`, HFI gen1/gen2 define constants, V4L2 pixel formats, firmware cap values, and platform `num_vpp_pipe`/caps.

## Risks
- Many calculations use 32-bit arithmetic on width/height/products; high resolutions or bad inputs can overflow before alignment.
- Codec-specific constants from HFI headers must match firmware expectations exactly; undersizing internal buffers can cause firmware memory corruption or decode/encode failure.
- Rotation changes encoder bitstream width/height and therefore internal buffer sizes; dynamic rotation must be synchronized with allocation timing.
- DRAP/AV1 and split-mode branches alter COMV/PERSIST/DPB sizes; mismatched control values and buffer creation can under-allocate.
- VPU4x encoder sizing uses `inst->codec` where helper logic appears to expect HFI encode-standard constants, requiring careful validation before enabling.

## Test Signals
- Unit-style size checks for representative resolutions/codecs/pipe counts against firmware reference values.
- End-to-end decode for H.264/HEVC/VP9/AV1 at 1080p, 4K, and 8K-class limits.
- Encoder tests for H.264/HEVC, stage 1/2, CBR/VBR/CQ, rotation 90/270, scaling, and crop.
- DRC tests where `fw_min_count` changes output count and DPB count.
- KASAN/KFENCE and firmware error logs during stream-on catch under-allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_buffer.c -->
