# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-paris.c

## Purpose
This is the MediaTek Paris common pinctrl driver for newer SoCs using per-pin vendor bindings. It supplies shared pinctrl, pinmux, pinconf, GPIO, EINT, debugfs, and PM behavior for SoC drivers that provide an `mtk_pin_soc` descriptor and `struct mtk_pin_desc` tables.

## Important APIs, Types, And Functions
The exported entry point is `mtk_paris_pinctrl_probe()`, which allocates `struct mtk_pinctrl`, maps named register bases, builds one-pin groups, registers and enables pinctrl, builds EINT, and registers a gpiochip. `mtk_pctrl_show_one_pin()` is exported for debug display. `mtk_paris_pinctrl_pm_ops` wraps EINT suspend/resume. Pinconf uses custom parameters `mediatek,tdsel`, `mediatek,rdsel`, `mediatek,pull-up-adv`, `mediatek,pull-down-adv`, and `mediatek,drive-strength-adv`, and bridges advanced drive strength encoding to standard `PIN_CONFIG_DRIVE_STRENGTH_UA` for 125, 250, 500, and 1000 uA.

## Control Flow
Devicetree mapping starts at `mtk_pctrl_dt_node_to_map()`, iterating child nodes and calling `mtk_pctrl_dt_subnode_to_map()`. Each child must have `pinmux`; generic pinconf properties are parsed once and attached to each one-pin group. `MTK_GET_PIN_NO()` and `MTK_GET_PIN_FUNC()` decode pin/function cells, the pin/function pair is validated against the SoC pin's function list, then mux and optional group config maps are added. Mux application validates the requested selector and writes `PINCTRL_PIN_REG_MODE`. GPIO request forces GPIO mode; direction, value, input, debounce, and IRQ routing delegate to common-v2 register helpers and EINT helpers.

## State And Persistence
Runtime state lives in `struct mtk_pinctrl`: mapped register bases, gpiochip, SoC data pointer, EINT handle, generated groups, group names, spinlock, and `rsel_si_unit` DT flag. The driver mutates hardware registers for mux, direction, output, input-enable, Schmitt, bias, drive, and EINT debounce. There is no storage persistence; suspend/resume calls EINT PM helpers only.

## Dependencies
The driver depends on `pinctrl-mtk-common-v2.h`, `mtk-eint.h`, Linux pinctrl/pinconf/gpio subsystems, named platform resources, and SoC descriptors with valid register calculators and optional callback hooks. It assumes one pin per group and direct indexing by pin number into `hw->soc->pins`.

## Risks
The global static `mtk_desc` is modified at probe time, which can be risky if multiple Paris instances with different SoC data probe concurrently. `mtk_pctrl_build_state()` allocates `ngrps` groups but iterates `npins`, so SoC descriptors must keep those counts consistent. Advanced drive-strength fallback disables advanced drive mode when no uA or explicit advanced setting is present; this can surprise board authors. Virtual GPIO handling is special in direction and debug paths and must be represented consistently by SoC data.

## Test Signals
Test with build coverage for multiple Paris SoCs, DT parsing failures for invalid pin/function cells, pinconf get/set for bias, input, Schmitt, level, drive-strength and custom fields, gpiochip direction/value operations, GPIO-to-IRQ mapping and debounce, debugfs pin dumps, and suspend/resume with EINT wake sources. Multi-instance SoC testing is useful because of the shared static descriptor.
