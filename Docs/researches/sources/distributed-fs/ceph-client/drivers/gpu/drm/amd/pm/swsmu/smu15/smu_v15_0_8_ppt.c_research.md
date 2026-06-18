<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.c

## Purpose

This file is the SMU v15.0.8 PPT implementation for a large multi-die/discrete platform with extended PM metrics, system metrics, FRU/product data, XGMI data, RAS-related messages, fast PPT limits, and board temperature metrics. `smu_v15_0_8_set_ppt_funcs()` installs the function table, clock/feature/table maps, MP1 mailbox, temperature metric callbacks, and `SMU15_DRIVER_IF_VERSION_SMU_V15_0_8`.

## Important APIs, Types, And Tables

Important maps are `smu_v15_0_8_message_map`, `smu_v15_0_8_clk_map`, `smu_v15_0_8_feature_mask_map`, and `smu_v15_0_8_table_map`. Important table types are `MetricsTable_t`, `StaticMetricsTable_t`, `SystemMetricsTable_t`, `PPTable_t`, `struct smu_v15_0_8_gpu_metrics`, `struct smu_v15_0_8_baseboard_temp_metrics`, and `struct smu_v15_0_8_gpuboard_temp_metrics`. Main functions include table initialization/finalization, metrics retrieval, static metrics to driver PPTABLE conversion, DPM table setup, sensor reads, GPU/system/temp metrics export, power-limit handlers, fast PPT handlers, IRQ handling, mode2 reset, OD editing, and performance-level handling.

## Control Flow

Table initialization declares PMSTATUSLOG, SMU metrics, and PMFW system metrics tables, allocates driver PPTABLE and metrics CPU buffers with cleanup attributes, initializes GPU/baseboard/GPU-board driver metric caches, initializes a cached system metrics table, and creates a metrics mutex. It also allocates `smu_15_0_dpm_context` and DPM policy storage. Finalization tears down driver metric caches, the system metrics cache, the mutex, and then delegates broader allocation cleanup to common v15 finalization.

Unlike v14 and v15.0.0, `setup_pptable()` is mostly a placeholder and the driver PPTABLE is synthesized later from PMFW static metrics in `smu_v15_0_8_set_driver_pptable()`. That path fetches the static metrics table, records the metrics version, converts Q10 firmware values into integer clocks/power/thermal limits, populates public serial numbers and AMDGPU UID records for SOC/MID/AID/XCD, copies FRU product strings, stores PPT1 fast-limit bounds, PLDM version, board input voltage, and XGMI max speed/width. `set_default_dpm_table()` then builds fine-grained GFX/FCLK/GL2 and discrete UCLK tables plus fixed SOC/VCLK/DCLK entries from the synthesized PPTABLE.

Metrics reads send `GetMetricsTable`, invalidate HDP, copy from the driver table, and cache under `metrics_lock`; system metrics use a separate cache buffer and PMFW command. Sensor reads expose GPU/memory activity, input power, hotspot/HBM temperatures, board voltage, and node power manager values. GPU metrics export fills per-XCC, per-MID, per-AID, per-VCN, HBM, throttling residency, XGMI, and activity accumulator fields. Temperature metric callbacks expose baseboard data only for physical node 0 and GPU board data for all nodes.

Performance and OD control are deliberately narrow. Manual mode permits GFX min/max and UCLK max edits; auto mode restores default GFX range and UCLK max. Fast PPT limit support validates `PPT1Min/Max` before sending `SetFastPptLimit`; normal PPT falls back to common v15. Mode2 reset sends an async reset message, waits 200 ms, then polls for an ACK under the message lock.

## State And Persistence

The file persists runtime state in `driver_pptable->init`, synthesized PPTABLE fields, `metrics_table`, system metrics cache, driver metric caches, DPM tables, DPM policies, `smu->pstate_table` current/custom bounds, `dpm_context->board_volt`, `adev->unique_id`, `adev->fru_info`, `adev->firmware.pldm_version`, UID records, XGMI max data, IRQ source setup, and throttle status used by delayed logging. Metrics caches are time-based; static PPTABLE synthesis is guarded by `pptable->init` so it happens once per allocation lifetime.

## Dependencies And Integration Points

This file depends on v15 common helpers, PMFW headers for v15.0.8, MP1 register definitions, AMDGPU FRU and UID helpers, XGMI topology helpers, UMC active masks, RAS/throttle interrupt handling, SMU table cache helpers, Q10 metric conversions, and AMDGPU sysfs metric/sensor/OD/performance interfaces. It also exposes RAS-priority message mappings for MCA and bad-page PMFW commands used elsewhere through the common SMU message layer.

## Risks And Edge Cases

`smu_v15_0_8_clk_map` only maps UCLK and carries a TODO, so common clock-to-ASIC translation is incomplete for this ASIC. `setup_pptable()` is a placeholder; callers must reach `set_default_dpm_table()` before any logic depends on synthesized PPTABLE values. `smu_v15_0_8_get_enabled_mask()` comments mention 128 feature bits but requests only two out args and converts the default feature count, which may miss higher feature bits. `smu_v15_0_8_get_gpu_metrics()` sets `mid_mask` from `adev->aid_mask`, which may be suspicious if MID and AID masks diverge. HBM stack iteration mutates a local mask by nibbles and assumes active-mask grouping is valid. Manual OD rejects `min >= max`, which can prevent setting a single fixed GFX frequency. Several paths return `-EOPNOTSUPP` for unsupported deterministic/profile levels or missing PPT1 data, so UI callers need graceful fallback.

## Test Signals

Useful tests include IP 15.0.8 boot, static metrics/PPTABLE synthesis, FRU product export, UID population for SOC/MID/AID/XCD, XGMI speed/width publication, `gpu_metrics` v1.9 reads with populated multi-instance arrays, raw PM metrics header sizing, baseboard and GPU-board temp metric reads on node 0 and nonzero nodes, HBM temperature calculation with several UMC masks, fast PPT get/set bounds, normal PPT get/set, manual OD GFX/UCLK edits, auto restore, mode2 reset ACK timing, MP1 throttle interrupt logging, and SR-IOV/multi-VF thermal-range bypass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.c -->
