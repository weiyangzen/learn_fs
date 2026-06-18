# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8135.c

## Purpose

This file provides the legacy MediaTek pinctrl data driver for MT8135. It defines the SoC-specific register layout, drive-strength groupings, a custom special pull-up/down implementation, EINT metadata, and the `mediatek,mt8135-pinctrl` platform binding.

## Important APIs, Types, And Functions

Besides the normal legacy tables, this file introduces a local `struct mtk_spec_pull_set` and `SPEC_PULL()` macro because MT8135 special pulls use separate PUPD, R0, and R1 offsets that do not fit the same-register helper used by several neighboring SoCs. Key objects are `mt8135_drv_grp`, `mt8135_pin_drv`, `spec_pupd`, `spec_pull_set()`, `mt8135_pinctrl_data`, and `mt8135_pctrl_match`.

`spec_pull_set()` is the main local function. It searches `spec_pupd` for the requested pin, selects the PUPD set or reset register according to `isup`, writes the PUPD bit, then writes R0 and R1 set/reset registers according to `MTK_PUPD_SET_R1R0_00`, `_01`, `_10`, or `_11`. Unsupported pins or invalid R1/R0 encodings return `-EINVAL`.

## Control Flow

The platform driver is registered at `arch_initcall`. The common probe receives `mt8135_pinctrl_data` from OF match data and calls `mtk_pctrl_init()`. The common path builds pinctrl groups, registers pinctrl/pinmux/pinconf operations, registers the GPIO chip, maps GPIO ranges, and initializes EINT.

At runtime, ordinary pin operations use the legacy register offsets: direction at `0x0000`, IES at `0x0100`, pull enable at `0x0200`, SMT at `0x0300`, pull select at `0x0400`, data out at `0x0800`, data in at `0x0A00`, and mux at `0x0C00`. Drive configuration is looked up through `mt8135_pin_drv` and `mt8135_drv_grp`. Special pull handling is redirected to the local `spec_pull_set()` via `.spec_pull_set`.

## State And Persistence

All pin metadata is static const. `spec_pull_set()` has no persistent local state; it only computes register addresses and writes through the regmap supplied by the common core. MT8135 is notable because `mtk_pctrl_init()` supports a second `mediatek,pctl-regmap` phandle specifically for 8135-style dual base addressing, so board DT correctness is part of the runtime state contract. Hardware register settings persist until reset, power transition, or later pinctrl changes.

## Dependencies And Integration Points

The driver depends on `pinctrl-mtk-common.h`, `pinctrl-mtk-mt8135.h`, Linux platform/OF/regmap APIs, the generic pinctrl and GPIO subsystems, and `dt-bindings/pinctrl/mt65xx.h`. EINT metadata reports six ports, 192 AP interrupt numbers, 16 debounce counters, and `debounce_time_mt2701`.

## Risks

The custom pull routine is order-sensitive and table-sensitive: wrong offsets or bit numbers in `spec_pupd` program PUPD/R0/R1 inconsistently. The code writes raw bit numbers to set/clear aliases, matching the legacy MediaTek register convention; if the regmap does not expose those aliases, pulls fail. Several drive entries cover discontinuous pin ranges and high pin numbers such as 181-202, so pin descriptor alignment with `mtk_pins_mt8135` is critical. Dual-regmap DT setup is another risk because missing or swapped phandles can make only part of the controller usable.

## Test Signals

Good tests include build coverage, OF probe for `mediatek,mt8135-pinctrl`, validation that one or two `mediatek,pctl-regmap` phandles resolve as intended, GPIO direction/value tests, mux tests for peripherals spanning both register bases, drive-strength reads/writes on representative drive classes, pull configuration tests for pins in `spec_pupd`, and EINT interrupt/debounce tests up to the advertised AP interrupt range.
