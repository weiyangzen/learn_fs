# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega12_smumgr.h

Purpose: private Vega12 SMU manager declarations. It defines table metadata sized by Vega12's SMU9 `TABLE_COUNT`, feature-mask split constants, and exported feature control helpers.

Important APIs and types: `struct smu_table_entry` stores version, size, MC address, CPU table pointer, and BO handle. `struct smu_table_array` contains `entry[TABLE_COUNT]`; `struct vega12_smumgr` embeds it. `SMU_FEATURES_LOW_MASK/HIGH_MASK` and shifts encode the split between low and high SMU feature messages. Exports are `vega12_enable_smc_features()` and `vega12_get_enabled_smc_features()`.

Control flow and state: implementation code fills each entry during init and uses indexes directly as SMU protocol table IDs. The table state remains driver-resident until transfer messages copy payloads to or from SMU-owned memory.

Dependencies, integration, and risks: depends on `hwmgr.h`, `vega12/smu9_driver_if.h`, and `vega12_hwmgr.h`. The largest coupling risk is that `TABLE_COUNT` and enum values must stay synchronized with firmware headers. Compile coverage, feature-mask tests for high bits, and table allocation/transfer tests are the main signals.
