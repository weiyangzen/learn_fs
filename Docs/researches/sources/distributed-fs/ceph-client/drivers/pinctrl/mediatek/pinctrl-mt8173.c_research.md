# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8173.c

## Purpose

This file provides the MT8173 legacy MediaTek pinctrl driver data. It defines special pull, IES, SMT, drive-strength, register-layout, EINT, OF, PM, and probe wiring for the MT8173 pin controller.

## Important APIs, Types, And Functions

Important objects are `mt8173_spec_pupd`, `mt8173_smt_set`, `mt8173_ies_set`, `mt8173_drv_grp`, `mt8173_pin_drv`, `mt8173_pinctrl_data`, `mt8173_pinctrl_probe()`, `mt8173_pctrl_match`, and `mtk_pinctrl_driver`. The file uses `struct mtk_pinctrl_devdata` from the legacy common layer and `mtk_pins_mt8173` from `pinctrl-mtk-mt8173.h`.

`mt8173_pinctrl_probe()` is a small local wrapper that calls `mtk_pctrl_init(pdev, &mt8173_pinctrl_data, NULL)`. Unlike drivers that use `.data` in the OF match and `mtk_pctrl_common_probe`, the compatible row here only lists `mediatek,mt8173-pinctrl`; the probe supplies the data directly.

## Control Flow

The driver registers at `arch_initcall`. Device-tree matching invokes `mt8173_pinctrl_probe()`, which enters the same legacy `mtk_pctrl_init()` path used by the common probe. The common path resolves the pinctrl regmap, builds groups, registers pinctrl and GPIO operations, creates the GPIO-to-pin range, and initializes EINT.

Pin configuration is table-driven. Standard register offsets are direction `0x0000`, pull enable `0x0100`, pull select `0x0200`, data out `0x0400`, data in `0x0500`, and pinmux `0x0600`. Special pulls mostly cover keypad and MSDC pins. IES and SMT ranges cover normal pads and several MSDC-specific register blocks. Drive strength uses three drive classes and a large `mt8173_pin_drv` table rooted at `DRV_BASE` plus peripheral-specific offsets.

## State And Persistence

All local data is static const. The wrapper probe has no extra state. Runtime state is allocated and owned by `mtk_pctrl_init()`, including `struct mtk_pinctrl`, GPIO chip, pinctrl device, and EINT state. Register values persist only as hardware state. The driver enables `.pm = pm_sleep_ptr(&mtk_eint_pm_ops)`, so EINT suspend/resume is integrated with the device PM path.

## Dependencies And Integration Points

Dependencies include the legacy MediaTek common pinctrl core, regmap/syscon DT plumbing, generic pinctrl/GPIO, EINT support, `pinctrl-mtk-mt8173.h`, and `dt-bindings/pinctrl/mt65xx.h`. EINT metadata advertises six ports, 224 AP interrupt numbers, 16 debounce counters, and `debounce_time_mt2701`.

## Risks

Because the OF match row does not carry `.data`, switching this file to `mtk_pctrl_common_probe` without adding match data would break probing. The drive table includes a repeated pin 85 entry with different offsets, which may represent hardware-specific overlapping control but should be treated as a review hot spot. MSDC and keypad special pull entries must match board electrical requirements; wrong R0/R1/PUPD bit positions can cause boot-media instability. EINT `ap_num` is larger than the pin count, so header EINT mapping and interrupt-controller assumptions need explicit validation.

## Test Signals

Signals include successful compile, probe on `mediatek,mt8173-pinctrl`, GPIO/pinmux registration, EINT suspend/resume testing, keypad row/column pull tests, MSDC0-3 signal pull and drive tests, drive-strength tests around the duplicated pin 85 entry, GPIO direction/value tests across low and high banks, and interrupt debounce validation on representative EINT-capable pins.
