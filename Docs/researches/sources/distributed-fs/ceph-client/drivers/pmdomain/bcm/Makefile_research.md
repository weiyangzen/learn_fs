# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/Makefile

Purpose: Kbuild mapping for Broadcom PM-domain drivers.

Important APIs/types/functions: maps `CONFIG_BCM_PMB` to `bcm-pmb.o`, `CONFIG_BCM2835_POWER` to `bcm2835-power.o`, `CONFIG_BCM63XX_POWER` to `bcm63xx-power.o`, and `CONFIG_RASPBERRYPI_POWER` to `raspberrypi-power.o`.

Control flow: no runtime flow.

State and persistence: build output follows `.config`.

Dependencies/integration: synchronized with `bcm/Kconfig`.

Risks: stale object mapping prevents selected provider from building.

Test signals: targeted builds with each Broadcom PM-domain symbol enabled.
