# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt8196.c

## Purpose
`pinctrl-mt8196.c` is the SoC data and platform-driver binding for the MediaTek MT8196 pin controller. It does not implement generic pinctrl algorithms itself; instead it describes MT8196 register geometry, pull/drive capabilities, EINT wiring, register base names, and callback choices consumed by the newer MediaTek Paris/v2 pinctrl stack.

## Important APIs, Types, And Data
- `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrap `PIN_FIELD_CALC()` with explicit register-base indexes. They are central because MT8196 has many IO configuration banks, not just one `base`.
- `mt8196_pin_*_range[]` arrays map pin numbers to register fields for mode, direction, input, output, Schmitt trigger, input enable, pull controls, drive strength, advanced drive, and RSEL. These are consumed through `struct mtk_pin_reg_calc`.
- `mt8196_pin_rsel_val_range[]` maps pins and RSEL indexes to pull-up and pull-down resistance values. This lets the combo bias helper accept either encoded RSEL values or SI-unit resistance requests when the core enables that mode.
- `mt8196_pull_type[]` assigns each pin one of the v2 pull-control models such as PU/PD, PUPD/R0/R1, RSEL, or pulldown-only.
- `mt8196_pinctrl_register_base_names[]` declares 16 MMIO base names: `base`, `rt`, `rm1`, `rm2`, `rb`, `bm1`, `bm2`, `bm3`, `lt`, `lm1`, `lm2`, `lb1`, `lb2`, `tm1`, `tm2`, `tm3`.
- `mt8196_data` points at the MT8196 pin descriptors, EINT pins, register calculators, pull type table, RSEL table, EINT hardware, and v2 bias/drive callbacks.

## Control Flow
At `arch_initcall`, `mt8196_pinctrl_init()` registers `mt8196_pinctrl_driver`. Device-tree matching on `mediatek,mt8196-pinctrl` passes `mt8196_data` to `mtk_paris_pinctrl_probe`. The Paris probe maps named resources, registers pinctrl/GPIO/EINT state, and calls back through the v2 helpers. Runtime pinmux and pinconf operations resolve a pin and field through `mt8196_reg_cals`, then read or update the calculated MMIO bitfield.

## State And Persistence
The file only contains static const SoC descriptions and a platform driver. Runtime state is owned by the Paris/v2 core in `struct mtk_pinctrl`: mapped register bases, group data, GPIO chip, EINT object, and locks. Hardware state persists in pinctrl registers and is not cached here. Suspend/resume is delegated through `mtk_paris_pinctrl_pm_ops`.

## Dependencies And Integration Points
This file depends on `pinctrl-mtk-mt8196.h` for pin descriptors and EINT pin mappings, `pinctrl-paris.h` for the probe and PM implementation, `pinctrl-mtk-common-v2.h` types/macros, the Linux platform-driver/device-tree framework, and the MediaTek EINT support. Board DTS files must provide the compatible string and named register resources in the same order expected by `mt8196_pinctrl_register_base_names`.

## Risks
Register range tables are dense and hand-maintained. A wrong base index, offset, or bit silently routes pinconf to the wrong IO bank. The v2 lookup path assumes each `mt8196_pin_*_range[]` table is ordered by pin range for binary search. Pull behavior depends on `mt8196_pull_type[]`; a mismatch between pull type and available register ranges will surface as `-ENOTSUPP` or wrong pull configuration. The EINT count is larger than the GPIO pin count, so virtual/non-GPIO EINT mappings must remain consistent with the pin descriptor data.

## Test Signals
Build with the MT8196 pin header and Paris/v2 pinctrl support. Boot an MT8196 device tree and verify `mediatek,mt8196-pinctrl` probes, all 16 base resources map, and EINT initializes. Exercise representative pins from each base bank for mode, direction, input, output, SMT/IES, pull, drive, advanced drive, RSEL, GPIO-to-IRQ, and debounce.
