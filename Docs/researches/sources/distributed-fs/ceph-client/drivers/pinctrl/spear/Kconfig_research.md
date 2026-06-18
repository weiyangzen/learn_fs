## `sources/distributed-fs/ceph-client/drivers/pinctrl/spear/Kconfig`

Purpose: Kconfig integration for STMicroelectronics SPEAr pinctrl and PLGPIO support.

Important APIs/types/functions: the menu is gated by `if PLAT_SPEAR`. `PINCTRL_SPEAR` is the common bool depending on `OF` and selecting `PINMUX`. `PINCTRL_SPEAR3XX` depends on `ARCH_SPEAR3XX` and selects the common driver. SoC symbols `PINCTRL_SPEAR300`, `PINCTRL_SPEAR310`, `PINCTRL_SPEAR320`, `PINCTRL_SPEAR1310`, and `PINCTRL_SPEAR1340` depend on their machine symbols and select appropriate common/PLGPIO support. `PINCTRL_SPEAR_PLGPIO` depends on `GPIOLIB && PINCTRL_SPEAR` and selects `GPIOLIB_IRQCHIP`.

Control flow: no runtime flow. Kconfig choices control which common, SoC-specific, and PLGPIO objects are built.

State and persistence: no runtime state; persistent effect is build configuration.

Dependencies and integration: connects legacy SPEAr platform symbols to pinctrl and GPIO infrastructure. Risks include the whole menu being hidden outside `PLAT_SPEAR`, limiting compile-test exposure, and platform-specific selections making dead-code build regressions easier to miss. Test signals include SPEAr defconfig builds, each machine symbol selecting expected objects, and build coverage for PLGPIO IRQ support when selected.
