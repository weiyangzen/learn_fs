# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt2712.h

## Purpose

`pinctrl-mtk-mt2712.h` is the static pin descriptor table for the MediaTek MT2712 pin controller driver. It defines `mtk_pins_mt2712[]`, a 210-entry `static const struct mtk_desc_pin` array covering pins 0 through 209. Each entry binds a Linux pin number and human-readable pad name to EINT metadata and the mux values that the older MediaTek common pinctrl driver can select.

This file contains descriptor data only. It does not implement executable control flow by itself, but it is included by `pinctrl-mt2712.c`, whose `mt2712_pinctrl_data` passes this table to `mtk_pctrl_common_probe`.

## Important APIs, Types, And Data

The table uses the older `pinctrl-mtk-common.h` descriptor API:

- `MTK_PIN(PINCTRL_PIN(number, name), pad, chip, eint, functions...)` expands into one `struct mtk_desc_pin`.
- `PINCTRL_PIN()` supplies the pinctrl core-visible pin number and pin name.
- `MTK_EINT_FUNCTION(eintmux, eintnum)` records the mux value and external interrupt number for a pin, or `NO_EINT_SUPPORT`.
- `MTK_FUNCTION(muxval, name)` describes one mux selector option. MT2712 uses mux values 0 through 7, with value 0 consistently representing GPIO mode.

The table has 210 `MTK_PIN` entries, 901 `MTK_FUNCTION` descriptors, and 210 EINT descriptors. The first pins are named `EINT0` through `EINT3`, then PWM, USB VBUS/ID, keypad, camera clocks, PCM, NAND, MSDC, Ethernet, UART, I2C, SPI, JTAG, display, audio, and PCIe-oriented pads. The final entries are `PERSTB_P0`, `CLKREQN_P0`, `WAKEEN_P0`, `PERSTB_P1`, `CLKREQN_P1`, and `WAKEEN_P1`.

## Control Flow And Runtime Use

At build time this header contributes `mtk_pins_mt2712[]` to `pinctrl-mt2712.c`. At probe time the platform driver matching `mediatek,mt2712-pinctrl` passes `mt2712_pinctrl_data` to `mtk_pctrl_common_probe`; that devdata references this header's pin table and companion arrays in the `.c` file for drive strength, pull-up/down, input-enable, and Schmitt-trigger handling.

At runtime the generic MediaTek pinctrl callbacks use the pin table to expose pins, groups, mux functions, GPIO mode, and EINT mapping to the Linux pinctrl, GPIO, and interrupt subsystems. Device-tree pinctrl states select function names or mux values; the common driver translates those choices into mode register writes using the register offsets and masks provided by the MT2712 `.c` file.

## State And Persistence Behavior

The header stores immutable static descriptor data. It has no heap allocation, no reference-counting, no file-backed persistence, and no direct hardware state. Runtime state lives in the common driver structures created at probe and in the hardware registers programmed through regmap. The only long-lived effect of this header is the compiled-in pin capability map that determines which mux/EINT configurations the driver will accept.

## Dependencies And Integration Points

Direct dependencies are `<linux/pinctrl/pinctrl.h>` and `pinctrl-mtk-common.h`. The header depends on the semantics of `struct mtk_desc_pin`, `struct mtk_desc_function`, and `struct mtk_desc_eint`.

The main integration point is `pinctrl-mt2712.c`, where `mt2712_pinctrl_data` sets `.pins = mtk_pins_mt2712`, `.npins = ARRAY_SIZE(mtk_pins_mt2712)`, EINT hardware properties, and older common-driver register offsets. The companion driver registers via `arch_initcall`, uses `mtk_pctrl_common_probe`, and wires EINT suspend/resume through `mtk_eint_pm_ops`.

## Risks And Edge Cases

The table is hardware-contract data, so most risks are silent misconfiguration rather than local crashes. Wrong mux names or mux values can route a peripheral to the wrong pad. Wrong EINT numbers can break wakeup or interrupt delivery. Pads with `NO_EINT_SUPPORT` must stay aligned with hardware and device-tree expectations. Because the table is positional and large, accidental insertion, deletion, or renumbering can desynchronize pin numbers from companion drive-strength and special pull arrays in `pinctrl-mt2712.c`.

Another risk is duplicate or unexpected function naming. Device-tree users and debugfs output rely on stable function names such as `MSDC*`, `I2C*`, `SPI*`, `GBE*`, `TDM*`, and debug monitor functions. Renaming a function is a binding-visible change even when the numeric mux value is unchanged.

## Test Signals

Useful validation signals include successful kernel build of the MT2712 pinctrl driver, boot-time probe of `mediatek,mt2712-pinctrl`, no pinctrl lookup failures for board DTS pin states, and debugfs pin listings showing 210 pins with expected names and mux options. Hardware tests should cover GPIO direction/value, pinmux for major buses such as MSDC, I2C, SPI, UART, Ethernet, display/audio, and EINT trigger/wakeup paths. Regression checks should compare `ARRAY_SIZE(mtk_pins_mt2712)` with `.npins`, confirm pin numbers remain contiguous 0-209, and spot-check EINT numbering against the SoC datasheet and DTS users.
