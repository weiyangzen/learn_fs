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
