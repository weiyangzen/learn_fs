# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8127.c

## Purpose

This file is the SoC data driver for the MediaTek MT8127 pin controller. It does not implement new pinctrl algorithms; it supplies MT8127-specific pin tables, register offsets, drive-strength classes, special pull-up/down rules, input-enable rules, Schmitt-trigger rules, EINT metadata, and the platform-driver binding used by the shared legacy MediaTek pinctrl core.

## Important APIs, Types, And Functions

The important local objects are `mt8127_drv_grp`, `mt8127_pin_drv`, `mt8127_spec_pupd`, `mt8127_ies_set`, `mt8127_smt_set`, `mt8127_pinctrl_data`, `mt8127_pctrl_match`, `mtk_pinctrl_driver`, and `mtk_pinctrl_init`. The data is expressed through common types from `pinctrl-mtk-common.h`: `struct mtk_drv_group_desc`, `struct mtk_pin_drv_grp`, `struct mtk_pin_spec_pupd_set_samereg`, `struct mtk_pin_ies_smt_set`, and `struct mtk_pinctrl_devdata`. The source depends on `pinctrl-mtk-mt8127.h` for `mtk_pins_mt8127`.

The driver uses `mtk_pctrl_common_probe` directly. The OF match row associates `mediatek,mt8127-pinctrl` with `&mt8127_pinctrl_data`, so the common probe retrieves the data with `device_get_match_data()` and passes it to `mtk_pctrl_init()`.

## Control Flow

At `arch_initcall` time, `mtk_pinctrl_init()` registers the platform driver. When a matching device-tree node appears, the common probe initializes the legacy pinctrl instance from the static `mt8127_pinctrl_data`. That shared initialization obtains the syscon regmap from `mediatek,pctl-regmap`, builds pin groups, registers pinctrl/pinmux/pinconf ops, creates a GPIO chip, maps GPIOs to pinctrl pins, and initializes EINT because `ap_num` is nonzero.

Runtime pin operations are table-driven. GPIO direction, output, input, pull enable/select, and pinmux use the offsets in `mt8127_pinctrl_data`; drive strength uses `mt8127_pin_drv` plus `mt8127_drv_grp`; special pull pins use `mtk_pctrl_spec_pull_set_samereg`; IES/SMT irregular ranges use `mtk_pconf_spec_set_ies_smt_range`.

## State And Persistence

All MT8127 metadata is `static const`; the source owns no mutable software state and no on-disk persistence. Runtime state lives in the shared `struct mtk_pinctrl`, GPIO chip, EINT object, and hardware registers reached through regmap. Register writes persist only as SoC hardware state until reset, power loss, or later pinctrl operations. This driver does not wire explicit PM ops, so suspend/resume behavior relies on the common framework and platform hardware retention.

## Dependencies And Integration Points

The file integrates with Linux platform-driver matching, OF compatible lookup, the generic pinctrl/GPIO subsystems, MediaTek legacy pinctrl helpers, MediaTek EINT support, and DT pin configuration constants from `dt-bindings/pinctrl/mt65xx.h`. The EINT block advertises six ports, 143 AP interrupt numbers, 16 debounce counters, and `debounce_time_mt2701`.

## Risks

The main risk is descriptor accuracy: incorrect pin numbers, offsets, bit positions, or drive-group classes silently program the wrong pad. The special pull table is sparse and covers keypad, EINT, and MSDC pins; pins omitted from `mt8127_spec_pupd` fall back to normal pull handling, so omissions can break board-level pulls. `type1_start`/`type1_end` are set to 143 only, which is a narrow legacy address split and should match the datasheet. EINT `ap_num`, debounce count, and pin descriptor EINT indices must stay consistent with `pinctrl-mtk-mt8127.h`.

## Test Signals

Useful signals are a successful kernel build with this driver enabled, DT probe with `mediatek,mt8127-pinctrl`, absence of `Cannot find pinctrl regmap`/registration errors, GPIO direction/value tests across several banks, pinmux selection for active board peripherals, pull-up/down tests on the listed special pins, IES/SMT configuration tests, and EINT debounce/interrupt tests on keypad, EINT, and MSDC-adjacent pins.
