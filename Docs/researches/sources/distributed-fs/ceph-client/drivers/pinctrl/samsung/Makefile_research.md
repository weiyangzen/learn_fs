# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/Makefile

## Purpose

This Makefile maps Samsung pinctrl Kconfig symbols to object files. It is the build integration point for the common Samsung pinctrl core, Exynos common code, Exynos ARM/ARM64-specific code, and S3C64XX code.

## Important Rules

`obj-$(CONFIG_PINCTRL_SAMSUNG) += pinctrl-samsung.o` builds the common Samsung pinctrl core whenever a family driver selects the hidden common symbol. `CONFIG_PINCTRL_EXYNOS` adds `pinctrl-exynos.o`, `CONFIG_PINCTRL_EXYNOS_ARM` adds `pinctrl-exynos-arm.o`, `CONFIG_PINCTRL_EXYNOS_ARM64` adds `pinctrl-exynos-arm64.o`, and `CONFIG_PINCTRL_S3C64XX` adds `pinctrl-s3c64xx.o`.

## Control Flow And Integration

The file is evaluated by Kbuild after Kconfig has resolved symbols. It assumes `Kconfig` selects the common symbol before any family-specific object needs it. The Makefile contains no ordering constraints beyond line order; Kbuild links selected objects into the enclosing built-in or module archive as appropriate.

## State And Persistence

There is no runtime state. Build state is derived entirely from `CONFIG_*` variables.

## Risks

If a new Kconfig symbol is added without a corresponding Makefile rule, its driver will never build. If a Makefile rule references a symbol that cannot be selected, dead code can accumulate. If family drivers forget to select `PINCTRL_SAMSUNG`, they may build without the shared core object.

## Test Signals

Build matrix checks should confirm the expected `.o` files appear for each Kconfig combination, especially Exynos common-only, ARM-specific, ARM64-specific, S3C64XX, and compile-test configurations.
