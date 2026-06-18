# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/core.c

## Purpose
Owns AMD ATL module initialization and the central normalized-address to system-physical-address pipeline.

## Important APIs, types, and functions
Defines global `struct df_config df_cfg __read_mostly`. `norm_to_sys_addr()` is the main translation entry. `add_base_and_hole()` and `remove_base_and_hole()` apply DRAM base and legacy MMIO hole adjustments. Helpers include `addr_over_limit()`, `legacy_hole_en()`, `get_base_addr()`, `late_hole_remove()`, and `check_for_legacy_df_access()`. `amd_atl_init()` detects supported CPUs/northbridges, initializes DF info, pins the module refcount, and registers `convert_umc_mca_addr_to_sys_addr` as the decoder.

## Control flow
Init matches SMCA or Zen CPUs, requires at least one AMD northbridge, sets legacy FICAA access based on family/model, calls `get_df_system_info()`, pins the module, and registers the decoder. Translation rejects unknown DF revision, seeds `addr_ctx`, checks legacy-hole prerequisites, determines node ID, finds the DRAM address map, denormalizes interleave bits, conditionally adds base/hole before or after dehash based on revision/mode, dehashes, then validates against DRAM limit.

## State and persistence
`df_cfg` caches system-wide Data Fabric revision, masks, shifts, number of maps, DRAM hole base, and flags. The registered RAS decoder persists until module exit, though the module increments its own refcount to discourage unload. No on-disk persistence.

## Dependencies and integration
Depends on x86 CPU feature matching, AMD northbridge/node helpers, ATL map/system/UMC functions, RAS decoder registration, module APIs, and memory failure/RAS configuration.

## Risks
Returning `-EINVAL` as `unsigned long` relies on consumers recognizing error-valued addresses. Translation correctness depends on complete `df_cfg` and map discovery from other files. Late versus early hole/base ordering is revision-sensitive. Forced unload is possible despite the self-refcount comment and would unregister the decoder.

## Test signals
Boot/init on unsupported CPUs, missing northbridge, legacy Family 17h/19h models, supported DF2/DF3/DF3.5/DF4/DF4.5 systems, hole-enabled maps with and without hole base, address over limit, and known normalized-to-SPA vectors per interleave mode.
