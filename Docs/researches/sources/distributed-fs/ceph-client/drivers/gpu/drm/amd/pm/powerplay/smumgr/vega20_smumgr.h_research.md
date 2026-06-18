# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega20_smumgr.h

Purpose: private Vega20 SMU11 manager declarations and exported helper prototypes. It describes table metadata sized by SMU11 `TABLE_COUNT`, feature-mask split constants, activity-monitor helpers, PPTABLE address setup, and SMC RAM running detection.

Important APIs and types: `struct smu_table_entry`, `struct smu_table_array`, and `struct vega20_smumgr` mirror the table metadata used by the C implementation. `SMU_FEATURES_LOW_MASK/HIGH_MASK` and shifts split 64-bit feature masks across low/high SMU messages. Exported helpers are `vega20_enable_smc_features()`, `vega20_get_enabled_smc_features()`, `vega20_set_activity_monitor_coeff()`, `vega20_get_activity_monitor_coeff()`, `vega20_set_pptable_driver_address()`, and `vega20_is_smc_ram_running()`.

Control flow and integration: other Vega20 PowerPlay modules can include this header to query feature state, move activity monitor coefficients, set the PPTABLE address before SMU consumption, and check MP1 firmware readiness. The implementation owns allocation and transfer details.

State, dependencies, and risks: the header defines driver-resident metadata for VRAM-backed SMU tables and relies on `smu11_driver_if.h` for table IDs and payload types. Risks are table enum drift, duplicated `struct smu_table_entry` names among sibling headers, and feature-mask split mistakes. Compile coverage plus table and feature tests are the main signals.
