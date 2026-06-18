<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Kconfig

## Purpose
Kconfig option for StarFive JH71XX PMU power-domain support.

## Important APIs, Types, And Functions
Defines `JH71XX_PMU`, defaulting to `ARCH_STARFIVE`, depending on PM and selecting `PM_GENERIC_DOMAINS`.

## Control Flow
Enables compilation of `jh71xx-pmu.o`.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
The symbol is available for StarFive platforms or compile testing and supports DT compatibles handled by the PMU driver.

## Risks
Disabling it prevents JH7110 PMU providers from binding, breaking devices with PMU power-domain references.

## Test Signals
StarFive and COMPILE_TEST builds should compile the driver and select generic PM domains.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/starfive/Kconfig -->
