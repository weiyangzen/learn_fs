# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/Kconfig

Purpose: Defines kernel configuration symbols for Aspeed pinctrl support. It separates the hidden common Aspeed pinctrl core from selectable generation-specific drivers for G4, G5, and G6 SoCs.

Important APIs and types: `PINCTRL_ASPEED` is a hidden bool selected by generation drivers. It depends on `(ARCH_ASPEED || COMPILE_TEST) && OF` and selects `MFD_SYSCON`, `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, and `REGMAP_MMIO`. User-visible bools are `PINCTRL_ASPEED_G4`, `PINCTRL_ASPEED_G5`, and `PINCTRL_ASPEED_G6`, each depending on the matching `MACH_ASPEED_G*` or `COMPILE_TEST` plus OF, and each selecting the common symbol.

Control flow: Kconfig evaluation enables the common symbol only when at least one generation-specific symbol is selected. The selected symbols drive object inclusion in the Aspeed `Makefile`; there is no runtime logic in this file. Help text notes that GPIO is provided by a separate GPIO driver, so these options cover pinmux/pinconf rather than GPIO ownership.

State and persistence: No runtime state. Persistent effect is the build configuration recorded in `.config`, which determines whether Aspeed pinctrl objects are compiled into the kernel or module build.

Dependencies and integration points: Integrates with the top-level pinctrl Kconfig tree and the Aspeed machine symbols. The selected framework symbols ensure the Aspeed implementation has syscon/regmap MMIO access and generic pinctrl/pinconf infrastructure. Generation-specific drivers compile under `COMPILE_TEST` to catch build drift outside Aspeed platforms.

Risks: Missing selected dependencies would surface as compile failures or missing framework APIs. Because generation options are bools rather than tristates, they follow built-in kernel semantics rather than module selection. The hidden common symbol cannot be enabled directly, so adding a new generation driver must remember to select `PINCTRL_ASPEED`.

Test signals: Run Kconfig builds for `MACH_ASPEED_G4`, `MACH_ASPEED_G5`, `MACH_ASPEED_G6`, and `COMPILE_TEST`; verify that selecting each generation pulls in `PINCTRL_ASPEED` and its framework dependencies; and confirm that GPIO remains provided by the separate Aspeed GPIO configuration.
