# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8167.c

## Purpose

This file is the MT8167 legacy MediaTek pinctrl data driver. It describes the SoC's pin drive groups, special pull-up/down registers, IES and SMT ranges, register offsets, EINT capabilities, OF compatible, and platform-driver registration.

## Important APIs, Types, And Functions

Key objects are `mt8167_drv_grp`, `mt8167_pin_drv`, `mt8167_spec_pupd`, `mt8167_ies_set`, `mt8167_smt_set`, `mt8167_pinctrl_data`, `mt8167_pctrl_match`, and `mtk_pinctrl_driver`. The source uses the common legacy data model: `struct mtk_pinctrl_devdata` points at `mtk_pins_mt8167`, the drive tables, special pull tables, special IES/SMT tables, the shared `mtk_pctrl_spec_pull_set_samereg` helper, and `mtk_pconf_spec_set_ies_smt_range`.

Unlike some older files, this one includes `linux/module.h`, exports a `MODULE_DEVICE_TABLE(of, mt8167_pctrl_match)`, and enables `.pm = pm_sleep_ptr(&mtk_eint_pm_ops)` in the platform-driver struct.

## Control Flow

`mtk_pinctrl_init()` registers the platform driver at `arch_initcall`. On `mediatek,mt8167-pinctrl`, `mtk_pctrl_common_probe()` receives `mt8167_pinctrl_data` and initializes the common legacy pinctrl stack. The resulting callbacks use the static register layout for pinmux, GPIO direction, input, output, pull, drive, IES, SMT, and EINT operations.

MT8167 maps direction at `0x0000`, data out at `0x0100`, data in at `0x0200`, pinmux at `0x0300`, pull enable at `0x0500`, and pull select at `0x0600`. Special PUPD/R0/R1 settings cover selected pins in banks around 14-17, 21-23, 40-43, 68-73, and 104-120. IES/SMT are range-based and include separate higher-offset handling for special pins.

## State And Persistence

The file's own data is immutable after boot. Mutable state is owned by the common pinctrl object, the GPIO chip, the EINT object, and the underlying registers. Hardware pin state can survive within a power state but is not persisted by this file. EINT suspend/resume is integrated through `mtk_eint_pm_ops`, so interrupt-controller state has an explicit PM path compared with MT8127/MT8135.

## Dependencies And Integration Points

The driver depends on `pinctrl-mtk-common.h`, `pinctrl-mtk-mt8167.h`, the Linux platform/OF/regmap/pinctrl stack, and the MT65xx DT pinctrl constants. It advertises six EINT ports, 169 AP interrupt numbers, 64 debounce counters, and `debounce_time_mt6795`.

## Risks

The register tables contain sparse pin coverage. Pins 74-99 are mostly absent from drive and special-pull tables, which may be intentional package/function coverage but should match the SoC datasheet. `mt8167_smt_set` has a `0xA900` offset for pins 34-39 while neighboring SMT offsets are around `0xA00`/`0xA10`; this may be deliberate but is a high-value review point because a typo would misroute SMT control. EINT metadata must align with the pin descriptors in the header and with DT interrupt users. PM behavior relies on `CONFIG_PM_SLEEP` and the `pm_sleep_ptr()` wrapper.

## Test Signals

Useful validation includes build and module alias checks, successful probe with `mediatek,mt8167-pinctrl`, suspend/resume with wake-capable EINT lines, GPIO bank direction/value testing, pinmux tests for peripherals using high pin numbers, pull tests for all `mt8167_spec_pupd` clusters, IES/SMT tests including pins 34-39, and interrupt debounce tests across the expanded 64 debounce counters.
