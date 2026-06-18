# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/Kconfig

## Purpose
This Kconfig file declares build-time configuration symbols for Nuvoton pinctrl/GPIO drivers: WPCM450, NPCM7XX, NPCM8XX, the MA35 common core, and MA35D1. It encodes architecture or compile-test constraints and selects the pinctrl, pinmux, pinconf, GPIO, IRQ, and syscon dependencies required by each driver family.

## Important APIs, types, and functions
The relevant symbols are `PINCTRL_WPCM450`, `PINCTRL_NPCM7XX`, `PINCTRL_NPCM8XX`, hidden `PINCTRL_MA35`, and user-visible `PINCTRL_MA35D1`. `PINCTRL_MA35D1` selects `PINCTRL_MA35`, which in turn selects generic pinctrl groups/functions/config, gpiolib, generic GPIO, irqchip support, and `MFD_SYSCON`.

## Control flow
Kconfig has no runtime flow. During configuration, visible symbols are offered when their `depends on` expressions are satisfied. Enabling `PINCTRL_MA35D1` causes the hidden common MA35 symbol to be selected, so the Makefile builds both `pinctrl-ma35.o` and `pinctrl-ma35d1.o`.

## State and persistence behavior
The persistent state is the kernel `.config`. These symbols determine whether driver objects are built in, built as modules where supported, or omitted. `PINCTRL_NPCM7XX`, `PINCTRL_MA35`, and `PINCTRL_MA35D1` are `bool`, so their objects are built-in when enabled; WPCM450 and NPCM8XX are `tristate`.

## Dependencies and integration points
The file integrates with `drivers/pinctrl/nuvoton/Makefile` via `obj-$(CONFIG_...)` entries. It depends on architecture symbols such as `ARCH_WPCM450`, `ARCH_NPCM7XX`, `ARCH_NPCM`, and `ARCH_MA35`, while allowing broader compile coverage through `COMPILE_TEST`. All entries require OF.

## Risks
Incorrect `select` lines can produce link failures or drivers without required framework support. The hidden `PINCTRL_MA35` split is important: enabling only the SoC wrapper without the common core would fail to link `ma35_pinctrl_probe()` and PM helpers. Bool-only choices prevent module builds for some drivers, so changing symbol type affects initialization timing and module ABI.

## Test signals
Validation is mostly build-matrix based: compile with each architecture symbol, with `COMPILE_TEST`, and with combinations of built-in/tristate drivers. For MA35D1, confirm that selecting `PINCTRL_MA35D1` also builds the common MA35 object and satisfies syscon, generic pinconf, gpiolib, and irqchip dependencies.
