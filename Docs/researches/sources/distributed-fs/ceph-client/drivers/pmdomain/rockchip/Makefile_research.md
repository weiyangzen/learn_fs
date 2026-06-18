<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Makefile

## Purpose
Kbuild mapping for the Rockchip power-domain driver.

## Important APIs, Types, And Functions
Maps `CONFIG_ROCKCHIP_PM_DOMAINS` to `pm-domains.o`.

## Control Flow
Kbuild includes the driver object when the Kconfig symbol is enabled.

## State And Persistence Behavior
No runtime state.

## Dependencies And Integration Points
Depends on the Rockchip Kconfig symbol and source file name staying aligned.

## Risks
A stale object mapping would silently drop the platform provider from builds.

## Test Signals
`make drivers/pmdomain/rockchip/` under `CONFIG_ROCKCHIP_PM_DOMAINS=y` should produce `pm-domains.o`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/rockchip/Makefile -->
