# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vega10_smumgr.h

Purpose: private Vega10 SMU manager declarations for the PowerPlay SMU9 path. It declares the driver-side table bookkeeping structs and exported helpers for SMU feature control.

Important APIs and types: `MAX_SMU_TABLE` fixes the local table array size at five entries. `struct smu_table_entry` records table version, byte size, SMU table ID, GPU MC address, CPU mapping pointer, and BO handle. `struct smu_table_array` wraps the fixed entries, and `struct vega10_smumgr` stores that array as the backend. Exported functions are `vega10_enable_smc_features()` and `vega10_get_enabled_smc_features()`.

Control flow and integration: `vega10_smumgr.c` allocates and fills these entries during init, then table-manager calls use the metadata to validate and transfer tables. Other Vega10 PowerPlay code can include this header to toggle or query SMU feature state.

State and persistence: the header defines driver-owned metadata only; persistence to VRAM and SMU state occurs in the C file through AMDGPU BOs and SMU transfer messages. The explicit `table_id` member distinguishes local array indexes from SMU protocol table IDs.

Dependencies, risks, and tests: depends on AMDGPU BO and `pp_hwmgr` declarations from the surrounding include graph. Main risks are `MAX_SMU_TABLE` staying aligned with enum usage and duplicate type names across sibling Vega headers if included together. Compile tests and allocation/transfer table coverage are the practical signals.
