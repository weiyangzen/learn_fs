# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/Kconfig

Purpose: Defines the Kconfig entries for the NXP S32 Common Chassis pinctrl core and the S32G2 SIUL2 pinctrl driver.

Important APIs, types, and symbols: `PINCTRL_S32CC` is a hidden boolean selected by SoC-specific drivers. It depends on `ARCH_S32 && OF` and selects `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCONF`, and `REGMAP_MMIO`. `PINCTRL_S32G2` is the visible option labeled "NXP S32G2 pinctrl driver"; it depends on `ARCH_S32 && OF`, selects `PINCTRL_S32CC`, and has help text for S32G2 family SoCs.

Control flow: There is no runtime control flow. Configuration flow is that enabling the visible S32G2 driver pulls in the common S32CC implementation and its generic pinctrl/pinmux/pinconf/regmap dependencies.

State and persistence: No runtime state. Build configuration persists in the kernel `.config` and determines whether `pinctrl-s32cc.o` and `pinctrl-s32g2.o` are compiled.

Dependencies and integration points: Integrates with the parent pinctrl Kconfig menu and Linux build system. It constrains these drivers to Open Firmware-enabled S32 architectures and ensures the common core can use generic pinctrl helpers and MMIO regmaps.

Risks: `PINCTRL_S32CC` is not user-visible, so any future SoC driver must select it or the common core will not build. `PINCTRL_S32G2` is a `bool`, not a tristate, matching the built-in registration pattern; changing module semantics would require driver and Makefile review.

Test signals: `make olddefconfig`/`menuconfig` visibility on `ARCH_S32`, expected symbol selection in `.config`, compile coverage with `CONFIG_PINCTRL_S32G2=y`, and absence of the option when `ARCH_S32` or `OF` is disabled validate this file.
