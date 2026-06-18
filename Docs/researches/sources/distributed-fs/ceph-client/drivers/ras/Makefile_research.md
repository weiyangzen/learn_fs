# sources/distributed-fs/ceph-client/drivers/ras/Makefile

## Purpose
Build rules for the RAS driver subtree.

## Important APIs, types, and functions
Includes `ras.o` for `CONFIG_RAS`, `debugfs.o` for `CONFIG_DEBUG_FS`, `cec.o` for `CONFIG_RAS_CEC`, `amd/fmpm.o` for `CONFIG_RAS_FMPM`, and always descends into `amd/atl/` through `obj-y`.

## Control flow
No runtime flow. Kbuild selects objects from configuration. The unconditional `obj-y += amd/atl/` lets the ATL subdirectory Makefile decide whether to emit `amd_atl.o`.

## State and persistence
No runtime state.

## Dependencies and integration
Follows symbols from `drivers/ras/Kconfig` and nested AMD ATL Kconfig. Integrates common RAS core, debugfs support, corrected-error collector, FMPM, and AMD ATL.

## Risks
The unconditional subdirectory descent is safe only if nested Makefiles are properly config-gated; current ATL Makefile is gated by `CONFIG_AMD_ATL`.

## Test signals
Build with `RAS=n`, `DEBUG_FS=y/n`, `RAS_CEC=y/m/n`, `RAS_FMPM=m/y`, and `AMD_ATL=m/y` to verify object inclusion.
