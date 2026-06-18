# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik-db8500.c

## Purpose
This file is the DB8500 SoC data provider for the common Nomadik pinctrl driver. It enumerates the routed DB8500 GPIO-capable pads, names each pad by GPIO number and package ball, defines pin groups for alternate-function columns A, B, C, and extended ALT-C1 through ALT-C4 selections, groups those pin groups into named pinmux functions, and supplies the DB8500 PRCM GPIOCR metadata needed for ALT-Cx selections.

## Important APIs, types, and functions
The main output is `nmk_pinctrl_db8500_init()`, which stores the address of static `nmk_db8500_soc` in the caller-provided `const struct nmk_pinctrl_soc_data **`. `nmk_db8500_soc` points at `nmk_db8500_pins`, `nmk_db8500_groups`, `nmk_db8500_functions`, `db8500_altcx_pins`, and `db8500_prcm_gpiocr_regs`. The table uses `PINCTRL_PIN()`, `NMK_PIN_GROUP()`, local `DB8500_FUNC_GROUPS()`, local `FUNCTION()`, and `PRCM_GPIOCR_ALTCX()` macros from the pinctrl and gpio-nomadik contracts.

## Control flow
There is no active runtime control flow beyond `nmk_pinctrl_db8500_init()`. During `pinctrl-nomadik.c` probe, the compatible string `stericsson,db8500-pinctrl` causes the core driver to call this init function. Later, pinctrl core callbacks index the provided arrays: group callbacks expose `nmk_db8500_groups`, mux callbacks choose a group's `altsetting`, and DB8500 ALT-Cx mux requests also pass through the PRCM GPIOCR metadata so the common driver can set or clear the selected extended alternate function.

## State and persistence behavior
All data in this file is immutable static SoC description. Persistent hardware state is created only when the common driver consumes the tables and writes GPIO AFSLA/AFSLB and PRCM GPIOCR registers. The pin list intentionally contains GPIO-number holes; consumers must treat `npins` as descriptor count, not as a dense maximum GPIO number.

## Dependencies and integration points
The file depends on Linux pinctrl descriptors and `linux/gpio/gpio-nomadik.h` for Nomadik group/function/SoC structures and PRCM ALT-Cx macros. It integrates directly with `pinctrl-nomadik.c`, which owns registration and register writes. The group names are device-tree visible through the common driver's `groups` and `function` properties, so board DTS files rely on these exact strings.

## Risks
This is data-heavy and typo-sensitive. A group name typo can break a function's group list at runtime even though the file compiles; notable examples to audit are function strings that must exactly match `NMK_PIN_GROUP()` names. Wrong ALT-Cx PRCM register indices or control bits can select unrelated debug, memory, modem, or RF functions. Pin holes and ball-name mappings should be checked against the datasheet because an incorrect GPIO number silently programs the wrong pad.

## Test signals
Useful checks include build coverage for `CONFIG_PINCTRL_NOMADIK`, probe on a DB8500 device tree with a valid `prcm` phandle, pinctrl debugfs group/function enumeration, mux requests for plain ALT-A/B/C and ALT-C1..C4 groups, and board-level smoke tests for UART, MMC, LCD, I2C, SPI, USB, and debug functions named in this table.
