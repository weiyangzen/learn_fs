<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Kconfig

## Purpose
Kconfig entry for Rockchip generic power-domain support.

## Important APIs, Types, And Functions
Defines `ROCKCHIP_PM_DOMAINS`, a boolean option defaulting to `ARCH_ROCKCHIP`, depending on PM, ARM SMCCC discovery, and regulator support, and selecting `PM_GENERIC_DOMAINS`.

## Control Flow
Configuration enables compilation of `pm-domains.o` through the Rockchip Makefile.

## State And Persistence Behavior
No runtime state; it only affects kernel configuration.

## Dependencies And Integration Points
The dependency on `HAVE_ARM_SMCCC_DISCOVERY` matches the driver path that informs firmware of power-domain state through SMCCC when available. Regulator dependency supports domains with optional supplies.

## Risks
Disabling this option removes power-domain providers for Rockchip SoCs, likely breaking devices with `power-domains` references. Missing dependencies would cause compile or runtime integration failures.

## Test Signals
Build with `ARCH_ROCKCHIP=y` and `COMPILE_TEST=y` should select or expose this symbol and compile `pm-domains.o`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Kconfig -->
