<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Makefile

## Purpose
Kbuild mapping for Samsung Exynos PM domains.

## Important APIs, Types, And Functions
Maps `CONFIG_EXYNOS_PM_DOMAINS` to `exynos-pm-domains.o`.

## Control Flow
Kbuild includes the Exynos driver when the symbol is enabled.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the Kconfig symbol and source object name.

## Risks
Incorrect mapping would omit the provider from Exynos builds.

## Test Signals
A Samsung/Exynos build with the config enabled should compile this object.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/Makefile -->
