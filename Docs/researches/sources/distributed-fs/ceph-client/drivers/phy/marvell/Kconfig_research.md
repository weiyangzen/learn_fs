# sources/distributed-fs/ceph-client/drivers/phy/marvell/Kconfig

## Purpose
Kconfig menu entries for Marvell PHY drivers, including the Armada375 USB cluster and Armada38x COMPHY files in this work item plus other Marvell PHYs in the same directory.

## Important APIs, types, and functions
Relevant symbols here are `ARMADA375_USBCLUSTER_PHY` and `PHY_MVEBU_A38X_COMPHY`; the file also defines Berlin, A3700, CP110, SATA, PXA, and MMP3 PHY options.

## Control flow
Symbols gate object builds and select `GENERIC_PHY`. Some defaults are SoC-dependent, such as `ARMADA375_USBCLUSTER_PHY` defaulting y for `MACH_ARMADA_375`.

## State and persistence
Only build configuration state.

## Dependencies and integration points
Consumed by the Marvell Makefile and architecture/config dependency graph (`ARCH_MVEBU`, `OF`, `HAS_IOMEM`, `HAVE_ARM_SMCCC`, etc.).

## Risks and test signals
Risks are dependency mismatches and default-y behavior unexpectedly including built-in code. Test Marvell defconfigs, `COMPILE_TEST`, and selected module builds.
