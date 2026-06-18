<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/common/Kconfig

## Purpose
Defines hidden ARM common support configuration symbols for legacy companion chips and SoC helper code.

## Important APIs/types/functions
- `SA1111` selects `ZONE_DMA` on `ARCH_SA1100`.
- `KRAIT_L2_ACCESSORS`, `SHARP_LOCOMO`, `SHARP_PARAM`, and `SHARP_SCOOP` are boolean feature symbols selected by platforms or drivers.

## Control flow
Kconfig selection controls which objects from `arch/arm/common/Makefile` are compiled.

## State and persistence behavior
No runtime state. The selected symbols persist in `.config` and drive object inclusion.

## Dependencies and integration points
Integrated by ARM platform Kconfig files and `arch/arm/common/Makefile`. `SA1111` changes DMA zoning behavior for SA1100 builds.

## Risks and edge cases
These are hidden symbols, so platform Kconfig must select them correctly. Incorrect selection can either omit required platform support or include legacy code on unsupported boards.

## Test signals
Inspect `.config` for platform builds using SA1111, LoCoMo, Sharp SL params, Scoop, and Krait L2 accessors; run `make ARCH=arm olddefconfig` and compile affected platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/Kconfig -->
