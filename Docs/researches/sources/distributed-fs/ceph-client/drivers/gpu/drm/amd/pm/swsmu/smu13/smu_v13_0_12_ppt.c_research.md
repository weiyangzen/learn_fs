# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_12_ppt.c

## Purpose
`smu_v13_0_12_ppt.c` provides SMU v13.0.12 data-center extensions used by the broader v13.0.6/v13.0.12 stack. It defines feature/message mappings, initializes extra metric caches, synthesizes a driver PPT from static PMFW metrics, reports GPU/XCP/system/board temperature telemetry, and implements RAS EEPROM SMU callbacks for bad-page metadata.

## Important APIs And Functions
Exports include `smu_v13_0_12_feature_mask_map`, `smu_v13_0_12_message_map`, `smu_v13_0_12_tables_init`, `smu_v13_0_12_tables_fini`, `smu_v13_0_12_get_max_metrics_size`, `smu_v13_0_12_get_system_metrics_size`, `smu_v13_0_12_setup_driver_pptable`, `smu_v13_0_12_is_dpm_running`, `smu_v13_0_12_get_smu_metrics_data`, `smu_v13_0_12_get_system_power`, `smu_v13_0_12_get_npm_data`, `smu_v13_0_12_get_xcp_metrics`, and `smu_v13_0_12_get_gpu_metrics`.

Temperature integration uses `smu_v13_0_12_temp_funcs`. RAS integration uses `smu_v13_0_12_ras_smu_drv` and EEPROM callbacks for table version, bad-page count, MCA address, timestamp, IPID, and erase.

## Control Flow
Initialization creates a cached `SMU_TABLE_PMFW_SYSTEM_METRICS` buffer and driver tables for baseboard and GPU-board temperature metrics. Driver PPT setup lazily fetches static metrics, gets PMFW metrics version, converts Q10 values into limits and frequency tables, records SOC/AID/XCD UIDs, copies FRU strings, captures optional board voltage, PLDM, node-power, fast-PPT fields, initializes XGMI speed/width, and marks the PPT initialized.

Runtime metrics convert PMFW Q10 values into kernel-facing integers. System metrics are refreshed by requesting PMFW export, invalidating HDP, copying from the shared driver table, and updating cache time. GPU and XCP metrics aggregate per-XCC, per-VCN/JPEG, XGMI, PCIe, HBM/AID/XCD temperature, throttle residency, energy, and timestamp data.

## State And Persistence
State is cached in SMU table caches, driver metric tables, `SMU_TABLE_SMU_METRICS` version, `driver_pptable`, `dpm_context->board_volt`, `adev->uid_info`, `adev->fru_info`, and firmware PLDM version. RAS callbacks access persistent PMFW/RAS EEPROM data indirectly through mailbox messages.

## Dependencies And Integration Points
The file depends on `smu_v13_0_6_ppt.h` helpers and capability checks, v13.0.12 PMFW headers, XGMI mapping, FRU EEPROM, RAS EEPROM infrastructure, AMDGPU XCP APIs, UMC active masks, PCIe helpers, and shared SMU table-cache/copy helpers.

## Risks
Metrics schema drift and instance indexing are the main risks. Hardware masks are mapped through `GET_INST`; invalid masks can misreport data. HBM stack extraction assumes two UMC bits per stack. System metrics cache freshness matters for telemetry. RAS operations must handle EEPROM busy timeouts and reconstruct 64-bit fields correctly. Capability gates must match firmware support.

## Test Signals
Signals include static metrics/PPT initialization, UID and FRU population, XGMI speed/width reporting, multi-XCC GPU metrics, XCP partition filtering, system/node power sensors gated by capability, baseboard/GPU-board temperature metrics, RAS bad-page count/address/IPID/timestamp operations, and graceful handling of `-EIO` enabled-mask and `-EBUSY` EEPROM responses.
