# sources/distributed-fs/ceph-client/drivers/pinctrl/ti/Kconfig

## Purpose

This Kconfig fragment declares `PINCTRL_TI_IODELAY`, the build-time option for the Texas Instruments IO delay pin configuration driver. It makes the DRA7 IO delay module available as a tristate driver and constrains normal builds to OF-enabled DRA7 SoCs while allowing compile-test coverage.

## Important APIs, Types, and Functions

The key symbol is `config PINCTRL_TI_IODELAY`. It is `tristate "TI IODelay Module pinconf driver"`, depends on `OF && (SOC_DRA7XX || COMPILE_TEST)`, and selects `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCONF`, and `REGMAP_MMIO`. There are no functions or runtime data structures in this file; its API is the Kconfig symbol consumed by the Makefile and kernel configuration system.

## Control Flow

During Kconfig evaluation, the symbol appears only when dependencies are satisfied. If selected as built-in or module, the Makefile compiles `pinctrl-ti-iodelay.o`. The selected generic pinctrl and regmap features ensure that the C driver can use generic group helpers, generic pinconf handling, and MMIO regmap access without requiring the user to manually enable them.

## State and Persistence

The only persistent state is the generated kernel configuration value in `.config` and derived build artifacts. It does not persist hardware state.

## Dependencies and Integration Points

The file integrates the TI IO delay driver with Kconfig, architecture/SoC selection, Device Tree support, generic pinctrl infrastructure, and MMIO regmap support. It is paired directly with `drivers/pinctrl/ti/Makefile`.

## Risks

Dependency mistakes can hide the driver from valid DRA7 builds or enable it in unsupported environments. Missing `select` statements would turn into compile or link errors in `pinctrl-ti-iodelay.c`. Over-broad dependencies can increase build coverage but may expose assumptions about OF-only probing.

## Test Signals

Check `make olddefconfig` visibility for DRA7 and compile-test configurations. Build `PINCTRL_TI_IODELAY=y` and `m`, verify the object is included, and confirm `n` excludes it. A compile-test build is useful because the option is explicitly designed to support `COMPILE_TEST`.
