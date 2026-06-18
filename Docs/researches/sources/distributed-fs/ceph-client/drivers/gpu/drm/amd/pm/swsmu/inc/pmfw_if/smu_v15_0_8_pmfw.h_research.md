<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_pmfw.h

## Purpose

`smu_v15_0_8_pmfw.h` is the SMU 15.0.8 PMFW interface header. It defines firmware-facing constants, feature IDs, telemetry dimensions, metric table versions, and packed/aligned table layouts that the SMU15 platform driver uses when exchanging data with PMFW. The file is a binary contract, not executable logic.

## Important APIs, Types, and Functions

The header exports DPM level counts for VCLK, DCLK, SOCCLK, LCLK, UCLK, FCLK, XGMI, PCIe, and guardband/margin tables; product/FRU string lengths; `FEATURE_ID_*` values through `NUM_FEATURES`; MGCG feature IDs; PCIe link-speed, GFX guardband, GFX DVM margin, system/node/SVI temperature, and system power enums. The main data types are packed/aligned `MetricsTable_t`, `SystemMetricsTable_t`, `VfMetricsTable_t`, `FRUProductInfo_t`, and `StaticMetricsTable_t`. Table version macros include `SMU_METRICS_TABLE_VERSION`, `SMU_SYSTEM_METRICS_TABLE_VERSION`, `SMU_VF_METRICS_TABLE_VERSION`, and `SMU_STATIC_METRICS_TABLE_VERSION`.

## Control Flow

There is no local control flow. Runtime flow is controlled by consumers such as `smu15/smu_v15_0_8_ppt.c`: the driver sends PPSMC messages, requests metric/static/system/VF tables, maps returned bytes onto these layouts, and then converts fields into hwmon, GPU metrics, RAS, NVML-style, and power-management values.

## State and Persistence Behavior

The file stores no runtime state. Its structures describe PMFW-owned snapshots and accumulators: temperature/power/frequency/activity counters, PCIe error accumulators, throttler residency counters, XGMI bandwidth accumulators, FRU identity strings, public serial numbers, PLDM version, and power limits. Values persist only in firmware/device state and in driver-side cached copies after table transfers.

## Dependencies

The header depends on Linux integer typedefs and compiler support for `__attribute__((packed, aligned(4)))` and `#pragma pack(push, 4)`. Consumers must pair it with SMU15 common code, `smu_v15_0_8_ppsmc.h`, and the correct PMFW driver-interface version. Array dimensions such as HBM, XCD, VCN, JPEG, and PCIe lanes are part of the ABI.

## Integration Points

It is directly included by the SMU15.0.8 PPT implementation, which uses the feature IDs and table definitions to validate firmware versions, request metrics, expose GPU metrics, query static inventory, handle system/node telemetry, and set or query power/frequency limits. The FRU/static metrics content also integrates with management tooling and RAS/monitoring surfaces.

## Risks and Edge Cases

The dominant risk is ABI drift: field order, packing, alignment, table version, and array counts must match PMFW exactly. Misinterpreting Celsius, millivolts, MHz, accumulators, or invalid sentinel values can report wrong telemetry or apply wrong limits. Several arrays are sized for multi-die/multi-XCD OAM platforms; consumers must bound indexes and respect unused sentinel fields. Feature IDs are numeric firmware protocol values and should not be renumbered.

## Test Signals

Useful signals include successful build of SMU15.0.8 code, driver-interface-version checks, metrics-version checks, table transfer success for metrics/system/static/VF tables, sane hwmon/GPU metrics values, FRU strings with expected bounds, and suspend/resume or reset paths that refresh cached metrics without layout faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_8_pmfw.h -->
