# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/Makefile

## Purpose
Build composition for the AMD Address Translation Library module/object.

## Important APIs, types, and functions
`amd_atl-y` is composed from `access.o`, `core.o`, `dehash.o`, `denormalize.o`, `map.o`, `system.o`, and `umc.o`. `amd_atl-$(CONFIG_AMD_ATL_PRM)` adds `prm.o`. `obj-$(CONFIG_AMD_ATL) += amd_atl.o` gates final output.

## Control flow
No runtime flow. Link order places low-level access/core/dehash/denormalize before map/system/umc and optional PRM.

## State and persistence
No runtime state.

## Dependencies and integration
Works with `drivers/ras/amd/atl/Kconfig`. The object composition matches prototypes in `internal.h`, where these compilation units share `df_cfg` and translation helpers.

## Risks
Missing any object breaks cross-file symbols such as `get_df_system_info()`, `get_address_map()`, or `convert_umc_mca_addr_to_sys_addr()`. Optional PRM code must remain fully guarded by `CONFIG_AMD_ATL_PRM`.

## Test signals
Build ATL as module and built-in, with and without `CONFIG_AMD_ATL_PRM`, and verify all cross-object symbols resolve.
