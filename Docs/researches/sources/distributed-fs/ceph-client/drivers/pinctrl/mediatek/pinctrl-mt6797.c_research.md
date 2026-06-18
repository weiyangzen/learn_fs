# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6797.c

## Purpose
This is a minimal MT6797 pinctrl wrapper for the MediaTek Paris framework. It describes only the base GPIO register calculations needed for mux mode, direction, input value, and output value across 262 pins, then registers the `mediatek,mt6797-pinctrl` platform driver.

## Important APIs, Types, And Functions
The file defines four `struct mtk_pin_field_calc` arrays: `mt6797_pin_mode_range`, `mt6797_pin_dir_range`, `mt6797_pin_di_range`, and `mt6797_pin_do_range`. Each uses `PIN_FIELD()` for pins 0 through 261 with GPIO-bank offsets for mode (`0x300`), direction (`0x0`), DI (`0x200`), and DO (`0x100`). `mt6797_reg_cals` maps those arrays to `PINCTRL_PIN_REG_MODE`, `DIR`, `DI`, and `DO`.

`mt6797_pinctrl_register_base_names` declares the resources `gpio`, `iocfgl`, `iocfgb`, `iocfgr`, and `iocfgt`, even though this file only provides generic GPIO register fields. `mt6797_data` points to `mtk_pins_mt6797`, sets `npins` and `ngrps` from that header table, records `gpio_m = 0`, and supplies the base-name list. Probe is handled by `mtk_paris_pinctrl_probe()`.

## Control Flow
`arch_initcall(mt6797_pinctrl_init)` registers `mt6797_pinctrl_driver`. When a device-tree node matches `mediatek,mt6797-pinctrl`, the platform core invokes the common Paris probe with `mt6797_data`. Runtime pinmux and GPIO requests are handled by the shared core using the four field maps in `mt6797_reg_cals`.

## State And Persistence
The file contains only static descriptors. Runtime state persists in the MT6797 GPIO/mux registers written by the shared core. There are no local EINT descriptors, bias callbacks, drive callbacks, advanced pull tables, or PM hooks in this file, so those capabilities are absent unless supplied elsewhere in the platform.

## Dependencies And Integration Points
It depends on `pinctrl-mtk-mt6797.h` for pin definitions and on `pinctrl-paris.h` for the shared MediaTek pinctrl implementation. It integrates with platform-driver matching and generic pinctrl/gpio consumers. The declared base names must match the register resources exposed by device tree.

## Risks
The limited register map means consumers expecting bias, drive, Schmitt, EINT, or advanced pull operations may receive unsupported-operation behavior from the common driver. The high pin count raises header consistency risk: `PIN_FIELD(0, 261, ...)` must match the actual `mtk_pins_mt6797` descriptors. A base-name mismatch will prevent resource mapping at probe, while a mode offset mismatch would break most alternate-function selection.

## Test Signals
Test binding through a `mediatek,mt6797-pinctrl` node, confirm all five register resources map, verify debugfs lists 262 pins/groups, and exercise GPIO direction/data and pinmux mode selection across low, middle, and high pin numbers. Also test that unsupported pinconf requests fail predictably rather than silently changing unrelated registers.
