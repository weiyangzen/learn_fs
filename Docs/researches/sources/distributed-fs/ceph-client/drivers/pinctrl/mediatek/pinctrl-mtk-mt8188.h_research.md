# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mtk-mt8188.h

## Purpose

`pinctrl-mtk-mt8188.h` defines the MT8188 pin descriptor table for the MediaTek Paris pinctrl driver. Its `mtk_pins_mt8188` array has 190 static const descriptors for GPIO0 through GPIO189. Each descriptor maps a pad to EINT metadata, a drive group, and up to eight mux-function names.

The table is included by `pinctrl-mt8188.c`, where `mt8188_data` uses it as the source of pin and group definitions. The companion `.c` file supplies register ranges, pull/resistance settings, EINT hardware limits, and callbacks. This header's role is to expose the SoC's pad-function matrix to Linux pinctrl, GPIO, and device-tree consumers.

## Important APIs, Types, And Data

- `mtk_pins_mt8188`: static const `struct mtk_pin_desc` array.
- 190 `MTK_PIN` entries and 1104 `MTK_FUNCTION` entries, making this one of the denser mux tables in this group.
- Function names often carry direction/bank prefixes such as `B0_`, `B1_`, `I0_`, `I1_`, and `O_`. Those prefixes are meaningful hardware naming, not local C types.
- `DRV_GRP4` covers GPIO0-GPIO176. GPIO177-GPIO189 are fixed descriptors with `DRV_FIXED` and `MTK_FUNCTION(0, NULL)`.
- Peripheral coverage includes SPI master ports, UART, DMIC, I2S/TDM/SPDIF audio, PWM, clock monitor/reference signals, HDMI/CEC hotplug-related signals, APU/VPU/IPU/ADSP/SCP/CCU/JTAG, DPI/display, camera, I2C, MSDC0/1/2, SPMI, LVTS, and debug monitor alternatives.

## Control Flow

This header has no runtime logic. The `MTK_PIN` and `MTK_FUNCTION` initializers are expanded at compile time into descriptor data. At probe, the Paris core consumes `mt8188_data.pins` and registers each pin as a group. When clients apply mux states, the core resolves the requested pin/group and mux value against this descriptor table before using register ranges from `pinctrl-mt8188.c` to program hardware.

## State And Persistence

All state in this file is compile-time static metadata. There are no mutable globals, allocations, locks, or persistence paths. Runtime pin state persists only in SoC pinctrl registers, and suspend/resume handling comes from the common Paris driver and SoC data in the companion `.c` file.

## Dependencies And Integration Points

- Depends on `pinctrl-paris.h` for the descriptor macros and common types.
- Included by `pinctrl-mt8188.c`, where `mt8188_data` assigns `.pins = mtk_pins_mt8188`, `.npins` and `.ngrps` from `ARRAY_SIZE`, `.nfuncs = 8`, `.gpio_m = 0`, `.eint_hw = &mt8188_eint_hw`, register base names, pull type tables, resistance-selection ranges, and bias/drive callbacks.
- EINT descriptors must align with `mt8188_eint_hw.ap_num = 225`; fixed pins GPIO177-GPIO189 map to EINT212-EINT224.
- Function names and mux values must match board DTS pinctrl definitions and hardware documentation.

## Risks

- The prefix-heavy function names make copy/paste errors hard to detect; swapping `I0_`, `I1_`, `O_`, `B0_`, or `B1_` can invert signal direction or select a different physical bank.
- GPIO177-GPIO189 have `DRV_FIXED` and NULL function names. Common debug or mux enumeration code must tolerate NULL function descriptors.
- The guard macro's closing comment spells `__PINCTRL__MTK_MT8188_H`, while the actual guard macro is `__PINCTRL_MTK_MT8188_H`. This is only a comment mismatch, but it can mislead manual review.
- A single descriptor count change affects both pin and group counts because `.ngrps` equals `ARRAY_SIZE(mtk_pins_mt8188)`.
- Dense shared mux values among debug, JTAG, media, audio, and storage functions increase the risk of board-level conflicts that compile cleanly.

## Test Signals

- Build with MT8188 pinctrl enabled and run sparse/checkpatch-style static checks for table syntax regressions.
- Probe on MT8188 hardware and confirm 190 pins/groups are visible through pinctrl debugfs.
- Exercise DTS pinmux states for audio, SPI, I2C, display/HDMI, camera, MSDC, SPMI, and JTAG/debug paths.
- Verify fixed GPIO177-GPIO189 enumeration and any EINT behavior expected for EINT212-EINT224.
- Compare pin descriptor names and mux values against the MT8188 datasheet or generated vendor source when changing the table.
