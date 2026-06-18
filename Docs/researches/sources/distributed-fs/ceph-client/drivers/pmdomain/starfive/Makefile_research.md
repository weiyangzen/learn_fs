<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Makefile

## Purpose
Kbuild mapping for the StarFive JH71XX PMU driver.

## Important APIs, Types, And Functions
Maps `CONFIG_JH71XX_PMU` to `jh71xx-pmu.o`.

## Control Flow
Kbuild includes the PMU driver when configured.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the StarFive Kconfig symbol.

## Risks
Incorrect mapping would drop JH71XX PMU support from builds.

## Test Signals
Compile with `CONFIG_JH71XX_PMU=y`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Makefile -->
