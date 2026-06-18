# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn301/dcn301_optc.c

## Purpose
`dcn301_optc.c` provides a DCN3.0.1 timing-generator function table. It reuses most DCN30 behavior but changes DRR disable behavior and manual-trigger setup.

## Important APIs, types, and functions
The DCN301-specific functions are `optc301_set_drr()`, `optc301_setup_manual_trigger()`, and `dcn301_timing_generator_init()`. The function table reuses DCN10 timing/blanking/stereo/CRC helpers, DCN20 enable/GSL/manual trigger programming, and DCN30 locks, blank color, ODM, DSC, pending-status, DMUB-aware vtotal min/max, and DRR trigger controls.

## Control flow
When DRR parameters contain valid min/max totals, `optc301_set_drr()` programs optional mid total, calls the function-table vtotal min/max hook, enables min/max selectors, clears lock/mask bits, and sets up manual trigger. When DRR is disabled or parameters are invalid, it clears min/max selectors and force-lock state, then writes vtotal min/max to zero through the active hook. Manual trigger setup programs TRIGA source 21 for the current pipe without the extra min/max selector workaround used by DCN20.

## State and persistence behavior
State is volatile OTG/OPTC register state plus the inherited `struct optc` fields. No persistent state exists.

## Dependencies and integration points
The file depends on DCN10, DCN20, and DCN30 helper implementations, `dcn301_optc.h`, DMUB service headers, DML/DCN30 headers, and tracing. It integrates with DCN301 resource construction and DRR/FAMS behavior.

## Risks and edge cases
The function table is named `dcn30_tg_funcs`, which is harmless but can confuse maintenance. DRR disable explicitly zeros min/max, which differs from DCN10/DCN30 and must match hardware expectations. Manual trigger setup omits DCN20's min/max selector workaround.

## Test signals
DRR enable/disable transitions, invalid DRR params, manual trigger behavior, DMUB and direct vtotal update paths, ODM combine/bypass, lock timing, and normal mode-set/CRC tests should be covered on DCN301 hardware.
