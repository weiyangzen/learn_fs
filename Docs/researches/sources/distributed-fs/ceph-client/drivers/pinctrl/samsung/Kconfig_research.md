# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/Kconfig

## Purpose

This `Kconfig` fragment defines the build-time configuration symbols for Samsung pin control drivers. It separates a private common symbol, SoC-family visible symbols, and architecture-specific helper objects for Exynos ARM and ARM64 support.

## Important Symbols And Dependencies

`PINCTRL_SAMSUNG` is a hidden boolean selected by all Samsung pinctrl implementations. It selects `GPIOLIB`, `PINMUX`, and `PINCONF`, ensuring the common Samsung driver builds only when the core pinctrl/GPIO infrastructure is available. `PINCTRL_EXYNOS` is the visible common Exynos/S5PV210 option. It depends on `ARCH_EXYNOS`, `ARCH_S5PV210`, or `COMPILE_TEST && OF`, selects the common Samsung symbol, and conditionally selects `PINCTRL_EXYNOS_ARM` or `PINCTRL_EXYNOS_ARM64` based on architecture. `PINCTRL_EXYNOS_ARM` and `PINCTRL_EXYNOS_ARM64` depend on `PINCTRL_EXYNOS` and are visible only for compile-test coverage. `PINCTRL_S3C64XX` is the visible S3C64XX option and depends on `ARCH_S3C64XX` or `COMPILE_TEST && OF`.

## Control Flow And Integration

Kconfig selection controls the object list in the sibling Makefile. Enabling either Exynos or S3C64XX selects the shared Samsung core object. Exynos selects additional architecture-specific object files so the common Exynos driver can be paired with ARMv7 or ARMv8 data/quirk code.

## State And Persistence

This file has no runtime state. Its state is the kernel `.config`, which determines what objects are compiled into the kernel or module build.

## Risks

Incorrect select/dependency logic can omit required common infrastructure or build architecture-specific files for the wrong target. The hidden common symbol is selected, not user-enabled, so any new Samsung family symbol must remember to select it. Compile-test dependencies require OF because these drivers are DT-oriented.

## Test Signals

Useful checks include `olddefconfig`/`allmodconfig`/`allyesconfig` coverage for Exynos, S5PV210, S3C64XX, ARM, ARM64, and `COMPILE_TEST && OF`, plus verifying that selected symbols produce the expected object list in the Makefile.
