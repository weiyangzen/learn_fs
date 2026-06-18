# sources/distributed-fs/ceph-client/drivers/phy/intel/Makefile

## Purpose
Kbuild object mapping for Intel PHY drivers.

## Important APIs, types, and functions
Maps four config symbols to four object files: Keem Bay eMMC/USB and LGM combo/eMMC.

## Control flow
Kbuild includes objects according to `.config`.

## State and persistence
Build state only; no runtime state.

## Dependencies and integration points
Tied to adjacent Intel Kconfig entries and source filenames.

## Risks and test signals
Risk is stale object mapping. Test all four symbols as enabled/module where supported.
