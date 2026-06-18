# sources/distributed-fs/ceph-client/drivers/media/platform/ti/Makefile

## Purpose
Adds TI media driver subdirectories to the kernel media platform build.

## Important APIs, Types, And Functions
Unconditionally descends into `am437x/`, `cal/`, `vpe/`, `davinci/`, `j721e-csi2rx/`, `omap/`, and `omap3isp/`. Individual objects are gated by each subdirectory's Kconfig symbols.

## Control Flow
No runtime flow. Kbuild visits each subdirectory and lets local Makefiles decide which objects to emit.

## State And Persistence
No state beyond build output.

## Dependencies And Integration Points
This is the build integration point between `drivers/media/platform/ti` and all TI-specific media drivers.

## Risks
Removing a subdirectory here silently prevents all contained driver symbols from producing objects even if Kconfig still exposes them. Unconditional descent means subdirectory Makefiles must be robust for disabled configs.

## Test Signals
Targeted kernel builds should confirm each enabled TI Kconfig symbol produces its expected object or module.
