<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/st/Kconfig

## Purpose
Kconfig option for ST-Ericsson ux500 power-domain support.

## Important APIs, Types, And Functions
Defines `UX500_PM_DOMAIN`, defaulting to `ARCH_U8500` and buildable with `COMPILE_TEST`.

## Control Flow
Enables `ste-ux500-pm-domain.o` through the ST Makefile.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the U8500 architecture or compile-test mode and integrates with DT compatible `stericsson,ux500-pm-domains`.

## Risks
The option is simple and lacks explicit `PM_GENERIC_DOMAINS` dependency; platform configs must ensure genpd support is available.

## Test Signals
U8500 and COMPILE_TEST builds should compile the driver.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/Kconfig -->
