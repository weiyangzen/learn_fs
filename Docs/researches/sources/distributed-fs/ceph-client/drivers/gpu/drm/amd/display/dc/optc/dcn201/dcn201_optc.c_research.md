# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn201/dcn201_optc.c

## Purpose
`dcn201_optc.c` provides a DCN2.0.1 timing-generator function table. It largely reuses DCN10/DCN20 behavior but customizes timing validation, triplebuffer locking, OPTC source readback, and minimum timing limits for the DCN201 hardware subset.

## Important APIs, types, and functions
Key local helpers are `optc201_triplebuffer_lock()`, `optc201_triplebuffer_unlock()`, `optc201_validate_timing()`, and `optc201_get_optc_source()`. `dcn201_timing_generator_init()` installs the function table and capability limits. The table reuses DCN10 timing/blanking/DRR/CRC helpers and DCN20 enable, DSC, manual-trigger, and CRC-mode helpers.

## Control flow
Triplebuffer lock selects the instance in `OTG_GLOBAL_CONTROL0`, enables vupdate keepout, asserts master update lock, and waits for lock status. Unlock clears the lock and disables keepout. Validation mirrors DCN10 checks but does not block interlace explicitly; it verifies supported 3D formats, max totals, min blanking, and sync widths. Source readback returns only `OPTC_SEG0_SRC_SEL` and sets source count to one.

## State and persistence behavior
State is volatile OTG/OPTC register state plus `struct optc` min/max capability values initialized at construction. No persistent state exists.

## Dependencies and integration points
The file depends on `dcn201_optc.h`, DCN10 and DCN20 helper functions, register helpers, and timing-generator interfaces. It integrates with DCN201 resource construction where full DCN20 ODM/DWB behavior is not exposed.

## Risks and edge cases
Minimum HSync width is initialized to 8 here, unlike DCN20/DCN30 values of 4. The source readback intentionally reports one source and ignores `src_opp_id_1`; callers expecting ODM combine state must use a different generation path. Triplebuffer lock register selection differs from DCN30.

## Test signals
DCN201 mode validation around hsync width, interlace-like timings, triplebuffer lock/unlock, DSC setup, CRC, DRR, and source readback should be covered.
