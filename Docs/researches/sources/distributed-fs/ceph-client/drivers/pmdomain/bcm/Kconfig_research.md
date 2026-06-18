# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/Kconfig

Purpose: Kconfig menu for Broadcom PM-domain providers.

Important APIs/types/functions: defines `BCM2835_POWER`, `RASPBERRYPI_POWER`, `BCM_PMB`, and `BCM63XX_POWER`. Symbols select generic PM domains as needed; BCM2835 also selects reset controller, Raspberry Pi firmware domains require built-in `RASPBERRYPI_FIRMWARE=y`, BCM PMB targets BCMBCA, and BCM63xx targets BMIPS.

Control flow: no runtime flow; chooses which Broadcom provider implementations are built.

State and persistence: `.config` controls build inclusion and defaults for matching architectures.

Dependencies/integration: consumed by `bcm/Makefile`; help text warns that Raspberry Pi firmware-owned domains must use the firmware driver instead of direct BCM2835 PM register access.

Risks: selecting the wrong provider for firmware-owned Raspberry Pi domains can conflict with firmware. Built-in firmware dependency for `RASPBERRYPI_POWER` is intentional for early availability.

Test signals: architecture defconfig coverage, compile-test builds, and boot tests on BCM2835/Raspberry Pi/BCMBCA/BMIPS platforms.
