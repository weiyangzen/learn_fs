# sources/distributed-fs/ceph-client/drivers/pinctrl/microchip/Kconfig

## Purpose
This Kconfig fragment declares Microchip pinctrl configuration symbols for PIC64GX GPIO2 and PolarFire SoC pinctrl drivers.

## Important APIs, Types, and Entries
- `PINCTRL_PIC64GX` is a bool for the PIC64GX GPIO2 pinctrl driver. It depends on `ARCH_MICROCHIP || COMPILE_TEST` and `OF`, and selects `GENERIC_PINCONF` plus `REGMAP_MMIO`.
- `PINCTRL_POLARFIRE_SOC` is a bool for PolarFire SoC pinctrl drivers. It depends on `ARCH_MICROCHIP || COMPILE_TEST` and `OF`, and selects `GENERIC_PINCTRL`.

## Control Flow
There is no runtime control flow. Kconfig selection controls which objects the Makefile includes and which pinctrl helper frameworks are guaranteed available at compile time.

## State and Persistence
The only state is build configuration. It persists in the kernel `.config` and determines built-in object inclusion because the symbols are bools.

## Dependencies and Integration Points
The entries integrate with architecture selection, device tree support, generic pinctrl/pinconf helpers, and the local Makefile. `PINCTRL_POLARFIRE_SOC` builds both IOMUX0 and MSSIO objects.

## Risks
`PINCTRL_POLARFIRE_SOC` selects `GENERIC_PINCTRL` but the MSSIO driver also uses generic pinconf APIs and custom params; build coverage must ensure transitive pinconf availability is sufficient. Bool-only symbols mean these drivers are not independently modular from Kconfig even though the C files use `module_platform_driver()`.

## Test Signals
Run configuration/build tests with `ARCH_MICROCHIP`, with `COMPILE_TEST`, and with each symbol disabled/enabled. Confirm the expected objects appear in the build and no missing generic pinctrl/pinconf symbols occur.
