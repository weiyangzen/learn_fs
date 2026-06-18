# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos-arm.c

## Purpose
This file is the ARMv7/S5P/Exynos SoC data layer for the shared Samsung pinctrl, pinmux, pinconf, GPIO, and external interrupt driver. It does not register a platform driver directly. Instead, it exports `samsung_pinctrl_of_match_data` instances consumed by `pinctrl-samsung.c` through the OF match table when `CONFIG_PINCTRL_EXYNOS_ARM` is enabled.

## Important APIs, Types, and Data
The central outputs are `s5pv210_of_data`, `exynos3250_of_data`, `exynos4210_of_data`, `exynos4x12_of_data`, `exynos5250_of_data`, `exynos5260_of_data`, `exynos5410_of_data`, and `exynos5420_of_data`. Each wraps an array of `struct samsung_pin_ctrl`, and each controller points at one or more arrays of `struct samsung_pin_bank_data`. The file uses common Exynos macros from `pinctrl-exynos.h`, especially `EXYNOS_PIN_BANK_EINTG`, `EXYNOS_PIN_BANK_EINTW`, and `EXYNOS_PIN_BANK_EINTN`, to describe GPIO interrupt banks, wakeup interrupt banks, and non-interrupt banks.

It defines two bank register layouts, `bank_type_off` and `bank_type_alive`, covering standard Exynos ARM register fields for function, data, pull, drive, and power-down configuration. S5PV210 is a special case: `s5pv210_pud_value_init()` overrides pull encoding values, and `s5pv210_retention_init()` maps the old clock controller node to provide retention release through `s5pv210_retention_disable()`.

## Control Flow
The source is declarative. At boot, `pinctrl-samsung.c` matches a compatible string such as `samsung,exynos4210-pinctrl`, retrieves the associated exported `*_of_data`, chooses a controller instance by the `pinctrl` OF alias, maps resources, copies bank data into runtime `samsung_pin_bank` objects, and invokes callbacks listed in each `samsung_pin_ctrl`. For controllers that set `.eint_gpio_init` or `.eint_wkup_init`, interrupt domains are initialized in `pinctrl-exynos.c`. For controllers that set `.suspend`, `.resume`, and `.retention_data`, suspend/resume and pad retention are coordinated by the common driver and Exynos callbacks.

## State and Persistence
The source-level state is static `__initconst` data. Runtime state is created by the common driver from these tables. Retention persistence is encoded through `struct samsung_retention_data` tables, including shared PMU refcounting through `exynos_shared_retention_refcnt` for Exynos3250/4/5420 style controllers. S5PV210 persists a mapped clock controller base in retention private data because retention control is not PMU-regmap based on that platform.

## Dependencies and Integration Points
This file depends on `pinctrl-samsung.h` for shared structures, `pinctrl-exynos.h` for Exynos bank macros and callback declarations, and Exynos PMU register definitions from `linux/soc/samsung/exynos-regs-pmu.h`. Integration is through exported `*_of_data` symbols referenced by the Samsung platform driver's OF match table. It also depends on device tree alias ordering: multi-controller SoCs rely on `of_alias_get_id(node, "pinctrl")` matching the order of `samsung_pin_ctrl` entries.

## Risks
The bank arrays often include comments that EINTG banks must start ordered by EINT group number. If a bank is moved out of service-register order, demuxed GPIO interrupts can be routed to the wrong bank. Retention register grouping is SoC-specific and shared across controllers; incorrect `retention_data` or refcount use can leave pads retained or released at the wrong time after suspend. S5PV210 direct clock-controller mapping has a resource lifetime risk because it is obtained outside normal platform resource management.

## Test Signals
Useful test signals are successful probe for each compatible, pinctrl states applying `samsung,pin-function` and config properties, GPIO request/direction/value operations across every bank, EINT GPIO IRQ delivery by service-register group, wakeup IRQ delivery from suspend, and suspend/resume preserving function/pull/drive registers. Device-tree binding checks should verify bank node names and `pinctrl` aliases for every listed controller.
