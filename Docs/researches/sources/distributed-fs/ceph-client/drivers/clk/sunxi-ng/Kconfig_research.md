# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/Kconfig

## Purpose
`sunxi-ng/Kconfig` declares the build-time configuration surface for the Allwinner "sunxi-ng" clock control unit drivers. It provides the umbrella `SUNXI_CCU` option and individual SoC-family options for main CCUs, PRCM/R CCUs, display-engine CCUs, RTC CCUs, MCU CCUs, and older family-specific CCM support.

The file controls which clock providers can be built into the kernel or as modules, and it ties those providers to architecture or machine-family dependencies.

## Important APIs, Types, And Functions
This is Kconfig data, not C code. The important symbols are:

- `SUNXI_CCU`: tristate umbrella option for Allwinner CCU support. It depends on `ARCH_SUNXI || COMPILE_TEST`, selects `RESET_CONTROLLER`, and defaults to `ARCH_SUNXI`.
- SoC-specific tristates such as `SUN20I_D1_CCU`, `SUN20I_D1_R_CCU`, `SUN50I_A100_CCU`, `SUN50I_A100_R_CCU`, `SUN4I_A10_CCU`, `SUN50I_H6_CCU`, `SUN50I_H616_CCU`, `SUN55I_A523_CCU`, and others.
- `SUN5I_CCU` is a special bool that depends on `SUNXI_CCU=y`, so it is built only when the shared CCU core is built-in.

## Control Flow
There is no runtime flow. Kconfig evaluation determines whether the common `sunxi-ccu` library objects and each SoC provider object are compiled. The outer `if SUNXI_CCU` block hides SoC choices until common support is enabled.

Dependency expressions steer build availability: ARM32 machine symbols enable older families, `ARM64` enables newer 64-bit families, `RISCV` enables D1/R528/T113-related support, and `COMPILE_TEST` allows wider build coverage.

## State And Persistence
The persistent state is the kernel configuration result stored in `.config` and any generated autoconf files. It affects which modules exist and which device-tree compatible strings can bind at runtime. There is no runtime mutable state in this file.

Because clock providers can be `tristate`, module versus built-in selection affects probe timing and availability for early boot consumers. The `SUNXI_CCU` umbrella also selects reset-controller support because most CCU providers expose resets alongside clocks.

## Dependencies And Integration Points
The Kconfig symbols integrate directly with `sunxi-ng/Makefile` through `obj-$(CONFIG_...)` entries. They also integrate with SoC platform Kconfig symbols, device-tree compatible strings in the C files, Linux CCF, reset-controller framework, and driver/module autoloading.

The selected clock drivers are dependencies for nearly every Allwinner platform peripheral: CPU/fabric clocks, memory bus, MMC, USB, Ethernet, display, camera, audio, serial buses, timers, crypto, and PRCM/RTC domains.

## Risks
Wrong dependencies can hide a required clock provider for valid boards or enable an invalid provider for incompatible builds. Changing `tristate` to `bool` or vice versa can alter module load timing. Removing `select RESET_CONTROLLER` can compile clock providers but break reset-controller registration.

The D1/R528/T113 options deliberately include `RISCV` as well as `MACH_SUN8I`; dropping either side can regress one architecture. The `SUN5I_CCU` built-in dependency is also unusual and should not be generalized without checking why that legacy provider requires built-in common support.

## Test Signals
Build validation should include `allyesconfig`/`allmodconfig` or targeted `COMPILE_TEST` builds for ARM, ARM64, and RISC-V. Runtime signals are that device-tree CCU compatibles select a built provider, modules can autoload when allowed, and clock/reset providers probe before dependent devices.
