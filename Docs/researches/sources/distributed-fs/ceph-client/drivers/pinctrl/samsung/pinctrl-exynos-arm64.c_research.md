# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos-arm64.c

## Purpose
This file is the ARM64 Exynos-family SoC data layer for the Samsung pinctrl driver. It covers many controllers, including Exynos2200, Exynos5433, Exynos7, Exynos7870, Exynos7885, Exynos850, Exynos8890, Exynos8895, Exynos9610, Exynos9810, Exynos990, ExynosAuto v9/v920, Tesla FSD, Google GS101, and Axis ARTPEC8/9. Like the ARM file, it exports data only; registration and runtime behavior are handled by `pinctrl-samsung.c` and Exynos helper logic in `pinctrl-exynos.c`.

## Important APIs, Types, and Data
The exported symbols are `exynos2200_of_data`, `exynos5433_of_data`, `exynos7_of_data`, `exynos7870_of_data`, `exynos7885_of_data`, `exynos850_of_data`, `exynos8890_of_data`, `exynos8895_of_data`, `exynos9610_of_data`, `exynos9810_of_data`, `exynos990_of_data`, `exynosautov9_of_data`, `exynosautov920_of_data`, `fsd_of_data`, `gs101_of_data`, `artpec8_of_data`, and `artpec9_of_data`. The file defines several register-layout variants: standard `bank_type_off` and `bank_type_alive`, Exynos5433 drive-width variants, Exynos7870 alive layout, Exynos850 4-bit pull/drive layouts, Exynos8895 3-bit drive layouts, and ARTPEC layouts.

The data uses macros from `pinctrl-exynos.h`: generic Exynos macros, Exynos5433 external-resource macros, Exynos7870/850/8895 variants, ExynosAuto v920 macros with explicit EINT control/mask/pend offsets, GS101 macros with filter configuration offsets, and ARTPEC macros. `no_retention_data` intentionally initializes retention control with no registers so the shared Exynos PMU pathway can still provide PMU regmap storage for wakeup mask programming on GS101 and ExynosAuto v920.

## Control Flow
For any matching compatible, the common driver selects the controller by OF alias, maps the main plus any extra memory resources, copies the bank tables, and registers pinctrl/gpio chips. `.eint_gpio_init` creates GPIO interrupt domains; `.eint_wkup_init` creates wakeup interrupt domains. Controllers that set `.suspend` and `.resume` feed Exynos, GS101, or ExynosAuto v920 suspend/resume helpers. GS101 and Exynos9610 banks carry EINT filter offsets used by the Exynos helper when saving/restoring and switching filters.

## State and Persistence
Most data is immutable `__initconst`, but a few arrays are not marked initconst, reflecting data used beyond init on some platforms. Runtime state is copied into devm-managed `samsung_pin_bank` structures. Suspend persistence depends on bank type widths and callbacks in the common driver plus Exynos callbacks. For Exynos5433, retention is split into general, audio, and FSYS/MMC groups. GS101 and ExynosAuto v920 use `no_retention_data` so the Exynos retention initializer still obtains PMU regmap-backed private data for wakeup mask writes, even with no pad-retention registers to release.

## Dependencies and Integration Points
This file depends on the shared Samsung headers, Exynos PMU register definitions, and the OF match table in `pinctrl-samsung.c`. It integrates with device tree compatible strings for Samsung, Google, Tesla, and Axis controllers and assumes `pinctrl` aliases map onto each SoC's controller order. It also integrates with Exynos wakeup interrupt compatible strings handled in `pinctrl-exynos.c`, such as `google,gs101-wakeup-eint` and `samsung,exynosautov920-wakeup-eint`.

## Risks
The largest risk is table drift: bank names, resource indexes, EINT offsets, and alias order must match hardware manuals and device tree bindings. ExynosAuto v920 banks use per-bank EINT register offsets instead of global offsets; mixing those with normal Exynos macros would corrupt interrupt programming. GS101 filter offsets are another fragile integration point because suspend switches wakeup banks to analog filter mode and resume restores digital filtering. Empty retention data is intentional but non-obvious; removing it would break wakeup mask programming that depends on retention private PMU data.

## Test Signals
Strong signals include DT binding validation for all compatibles, boot probe with every `pinctrl` alias, GPIO line naming matching bank-node names, pinmux/pinconf register programming on each bank layout variant, GPIO EINT and wakeup EINT delivery, GS101 wakeup mask writes across three PMU wakeup-mask registers, ExynosAuto v920 IRQ mask/pend/con offset tests, and suspend/resume tests proving pad state and EINT filters are preserved.
