# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7986.c

## Purpose
`pinctrl-mt7986.c` describes MT7986A and MT7986B pin controllers for the MediaTek Moore framework. It shares one register map and group/function set across two package variants, while using different pin descriptor arrays and EINT descriptors for A and B.

## Important APIs, Types, And Data
The file defines `MT7986_PIN()` for normal ballout pins and `MT7986_NOT_BALLOUT_PIN()` for MT7986B package holes. Register-base enum values identify `"gpio"`, `"iocfg_rt"`, `"iocfg_rb"`, `"iocfg_lt"`, `"iocfg_lb"`, `"iocfg_tr"`, and `"iocfg_tl"`. The comments document how these bases correspond to physical pad regions around the chip carrier.

Register calculators cover mode, direction, input/output, IES, SMT, PU, PD, drive, PUPD, R0, and R1 for pins 0-100. `mt7986_pull_type` marks pins 0-68 as PUPD/R1/R0 pull style and pins 69-100 as separate PU/PD style. `mt7986a_pins` names all 101 pads; `mt7986b_pins` intentionally marks pins 41-65 as not ballout while preserving numbering. Group/function tables expose watchdog, Wi-Fi LEDs, I2C, UART alternatives, SPI, PWM, eMMC, SNFI, PCIe, Ethernet MDIO/switch interrupt, PCM/I2S, and Wi-Fi front-end modes.

## Control Flow
Two platform drivers are registered at arch init: `mt7986a-pinctrl` and `mt7986b-pinctrl`. The compatible strings are `mediatek,mt7986a-pinctrl` and `mediatek,mt7986b-pinctrl`. Each probe calls `mtk_moore_pinctrl_probe()` with the matching SoC descriptor.

## State And Persistence
The file maintains no dynamic state. Runtime state is hardware register state owned by the common pinctrl operations. The A and B descriptors share `mt7986_reg_cals`, `mt7986_groups`, and `mt7986_functions`, but differ in `pins`, `npins`, and EINT hardware pointer. Both descriptors enable IES and combo bias handling, rev1 drive callbacks, and advanced pull callbacks.

## Dependencies And Integration Points
Integration points are the Moore pinctrl core, multiple IO configuration register resources named in device tree, MediaTek EINT, and board DTS pinctrl groups. The MT7986B not-ballout placeholders are an important package integration mechanism because they keep pin numbers stable while preventing named use of unavailable pads.

## Risks
The shared group table includes groups for pads that are not ballout on MT7986B; the common framework and board DTS must avoid selecting unavailable package pins. Some visible group metadata has array-length concerns, for example Wi-Fi 2G pin/function arrays appear uneven. Multi-base register maps raise the cost of incorrect base indices, and package-specific testing must ensure that A and B compatible strings do not accidentally expose invalid pads.

## Test Signals
Test signals include successful registration of both platform drivers, probe success for both compatibles, no DTS selection of `NULL` MT7986B pads, GPIO and EINT tests over available pins, combo bias tests across both pull types, drive-strength tests, and peripheral smoke tests for eMMC, SNFI, SPI, UART, I2C, PCIe reset/wake/clkreq, MDIO, switch interrupt, PCM/I2S, LEDs, watchdog, and Wi-Fi groups.
