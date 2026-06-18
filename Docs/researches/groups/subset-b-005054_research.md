# subset-b-005054 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6765.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6765.c

## Purpose
This file is the MediaTek MT6765 pinctrl SoC description for the Paris pinctrl framework. It does not implement pinctrl algorithms itself; instead it gives the shared MediaTek pinctrl core enough static data to expose 203 pins as GPIOs, mux groups, pin configuration targets, and external interrupt lines for the `mediatek,mt6765-pinctrl` device-tree compatible.

## Important APIs, Types, And Functions
The file builds `struct mtk_pin_field_calc` arrays for every register class used by the SoC: mode, direction, data input/output, Schmitt trigger, pull-down, pull-up, transmit/receive select timing, drive strength, PUPD, R0, R1, and input-enable select. `PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrap `PIN_FIELD_CALC()` for register bases selected by `_i_base`, with the plural form marking shared bit fields across a pin range.

`mt6765_reg_cals` maps the generic `PINCTRL_PIN_REG_*` enum slots to the MT6765 field arrays through `MTK_RANGE()`. `mt6765_eint_hw` declares the EINT controller layout: six ports, port mask `7`, 160 application-visible EINTs, 13 debounce counters, and `debounce_time_mt6765`. `mt6765_data` is the integration object consumed by `mtk_paris_pinctrl_probe()`: it points to `mtk_pins_mt6765`, the register calculations, EINT hardware, eight IOCFG base names, and the combo bias, raw drive, and advanced pull callbacks.

## Control Flow
Boot registration is simple. `arch_initcall(mt6765_pinctrl_init)` registers `mt6765_pinctrl_driver`. The platform bus matches `mediatek,mt6765-pinctrl`, attaches `mt6765_data` as match data, and calls `mtk_paris_pinctrl_probe()`. From that point, the shared Paris code maps the named register resources, registers pinctrl/gpio/eint providers, and uses the static range tables whenever consumers request mux, GPIO direction/value, bias, drive strength, Schmitt, timing, or EINT configuration.

## State And Persistence
There is no mutable software state in this file after registration. Runtime state is the hardware register contents written by the common pinctrl core. The source of persistence is the static register map: if a pin's base index, offset, bit start, bit width, or shared-field flag is wrong, all future pin configuration requests for that field persist to the wrong hardware location until reboot or reconfiguration.

## Dependencies And Integration Points
The driver depends on `pinctrl-mtk-mt6765.h` for the pin descriptors and debounce table, `pinctrl-paris.h` for the common probe and pinconf helpers, Linux platform-driver and OF matching infrastructure, and the device tree providing resources named `iocfg0` through `iocfg7`. It integrates with pinctrl consumers via generic pinctrl states, GPIO via the MediaTek common GPIO implementation, and interrupt consumers through the MediaTek EINT wiring.

## Risks
The major risk is table accuracy. MT6765 spreads configuration across eight IOCFG bases and many non-contiguous bit positions, so copy/paste mistakes can misroute a pin's bias, drive, input-enable, or timing control. The `npins` and `ngrps` values both derive from `ARRAY_SIZE(mtk_pins_mt6765)`, so header/table consistency is mandatory. Pull behavior depends on the combination of PU/PD plus PUPD/R0/R1 and advanced pull helpers; missing one of those register ranges can make some pins appear configurable while returning ineffective electrical settings.

## Test Signals
Useful signals include a boot log showing the platform driver binds without resource-name failures, pinctrl debugfs listing all MT6765 pins/groups, GPIO loopback tests for direction/data registers, device-tree pin state tests for alternate functions, bias and drive-strength readback through pinconf, EINT trigger/debounce tests across representative pins, and suspend/resume smoke tests for devices whose pins are configured before and after system sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6765.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6779.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6779.c

## Purpose
This file supplies the MT6779 SoC-specific register map and platform-driver glue for the MediaTek Paris pinctrl core. It describes 203 pins, their GPIO/mux registers, electrical configuration registers, EINT hardware, and the regional register base names required for `mediatek,mt6779-pinctrl`.

## Important APIs, Types, And Functions
`PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` adapt `PIN_FIELD_CALC()` for 32-bit register banks. The field arrays cover mode, direction, DI, DO, input enable select (`IES`), Schmitt trigger (`SMT`), pull-up, pull-down, drive strength, PUPD, R0, and R1. GPIO mode/direction/value are grouped mostly under base index 0, while electrical settings are distributed across seven IOCFG regions.

`mt6779_reg_cals` is the main bridge from generic pinctrl register requests to SoC-specific fields. `mt6779_pinctrl_register_base_names` names the required resources: `gpio`, `iocfg_rm`, `iocfg_br`, `iocfg_lm`, `iocfg_lb`, `iocfg_rt`, `iocfg_lt`, and `iocfg_tl`. `mt6779_eint_hw` declares six EINT ports, 195 AP EINT lines, 13 debounce counters, and `debounce_time_mt2701`. `mt6779_data` enables `ies_present`, combo bias helpers, raw drive helpers, and advanced pull helpers.

## Control Flow
`arch_initcall(mt6779_pinctrl_init)` registers a platform driver named `mt6779-pinctrl`. The OF match table associates `mediatek,mt6779-pinctrl` with `mt6779_data`. Probe is delegated entirely to `mtk_paris_pinctrl_probe()`, which consumes the register calculations and pin descriptors from `mtk_pins_mt6779` to register pinctrl, GPIO, and EINT services. Runtime calls from the pinctrl subsystem are resolved by looking up a pin/register class in `mt6779_reg_cals` and then reading or updating the computed MMIO field.

## State And Persistence
All durable driver knowledge is static const table data. Runtime persistence is in the SoC registers that the Paris core writes for pin muxing, GPIO state, bias, drive, Schmitt, and EINT debounce/trigger behavior. The `ies_present` flag affects whether input-enable operations are expected to use explicit IES registers rather than being treated as absent.

## Dependencies And Integration Points
The file depends on `pinctrl-mtk-mt6779.h` for pin descriptors, alternate function definitions, and debounce-time data, and on `pinctrl-paris.h` for registration and pinconf callbacks. It integrates with OF resource naming, platform-driver matching, generic pinctrl state selection, gpiolib operations, and MediaTek EINT handling.

## Risks
The key risk is regional base mismatch. A wrong `_i_base` routes a field to a valid but unrelated IOCFG block, producing subtle electrical failures rather than an obvious probe error. The PU/PD/PUPD/R0/R1 tables are not uniform across all pins, so advanced pull correctness depends on matching pin coverage to `mtk_pinconf_adv_pull_*` expectations. EINT metadata must also match the header's EINT-capable pin list; otherwise interrupt consumers may get missing, duplicate, or incorrectly debounced lines.

## Test Signals
Validation should include successful driver binding with all eight register resources present, debugfs inspection for 203 pins and groups, GPIO direction/value readback across low and high pin numbers, pinmux tests on pins from each IOCFG region, pinconf read/write tests for bias/drive/Schmitt/input-enable settings, and EINT edge/debounce tests across multiple AP EINT lines. Device-tree schema and boot tests should confirm the `mediatek,mt6779-pinctrl` compatible selects this data, not another MediaTek variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6779.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6795.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6795.c

## Purpose
This file is the MT6795 pinctrl data provider for the MediaTek Paris driver. It describes a 197-pin SoC using an older register layout with 15-bit and 16-bit field packing, explicit pull-enable/pull-select registers, selected PUPD/R0/R1 advanced pull fields, slew-rate control, EINT hardware, and PM-aware platform-driver registration.

## Important APIs, Types, And Functions
`PIN_FIELD15()`, `PIN_FIELD16()`, and `PINS_FIELD16()` wrap `PIN_FIELD_CALC()` with a single base index and 15- or 16-bit field stride. Basic GPIO controls are defined by `mt6795_pin_dir_range`, `mt6795_pin_pullen_range`, `mt6795_pin_pullsel_range`, `mt6795_pin_do_range`, `mt6795_pin_di_range`, and `mt6795_pin_mode_range`. Electrical configuration arrays cover IES, SMT, PUPD, R0, R1, drive strength, and slew rate.

`mt6795_reg_cals` exposes those arrays to the generic `PINCTRL_PIN_REG_*` lookup path. `mt6795_eint_hw` declares seven EINT ports, 224 AP EINT lines, 32 debounce counters, and `debounce_time_mt6795`. `mt6795_pull_type` is a per-pin policy table selecting `MTK_PULL_PULLSEL_TYPE` or `MTK_PULL_PUPD_R1R0_TYPE`, which is critical because the SoC uses both legacy pullsel and advanced resistor-controlled pull models. `mt6795_data` wires rev1 bias/drive callbacks, combo bias helpers, advanced pull helpers, `nfuncs = 8`, and the default MediaTek register base names.

## Control Flow
The init function `mtk_pinctrl_init()` is registered with `arch_initcall()` and registers `mt6795_pinctrl_driver`. OF matching on `mediatek,mt6795-pinctrl` supplies `mt6795_data` to `mtk_paris_pinctrl_probe()`. The driver also attaches `pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`, so system sleep state handling is delegated to the shared Paris PM operations when PM sleep is enabled.

## State And Persistence
No local runtime objects are allocated by this file. Static range tables and the pull-type array determine how the common driver mutates hardware state. Persistent hardware effects include mux mode, GPIO direction/data, pull enable/select, advanced pull resistor bits, Schmitt trigger, input-enable, drive strength, slew rate, and EINT debounce settings.

## Dependencies And Integration Points
The file depends on `pinctrl-mtk-mt6795.h` for `mtk_pins_mt6795` and debounce metadata, `pinctrl-paris.h` for the core implementation and rev1 pinconf helpers, the platform bus, and OF compatible matching. It integrates with pinctrl, gpiolib, IRQ/EINT handling, and PM sleep pin-state transitions.

## Risks
MT6795 has mixed pull models, so an incorrect `mt6795_pull_type` entry can route generic bias requests to the wrong register family. Some field tables contain peripheral-specific regions for keypad, DPI, and MSDC pins; mistakes in these ranges can break high-speed interfaces while ordinary GPIO tests still pass. The 15-bit mode packing and 16-bit control packing are unusual compared with newer 32-bit Paris SoCs, making stride and bit-width regressions likely when refactoring macros.

## Test Signals
Good signals include boot binding for `mediatek,mt6795-pinctrl`, pinctrl debugfs showing 197 pins and eight functions, GPIO tests for mode/direction/data, pull configuration tests on both legacy pullsel pins and PUPD/R0/R1 pins, drive/slew readback, EINT tests across multiple ports and debounce counters, and suspend/resume testing to exercise the Paris PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6795.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6797.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6797.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6878.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6878.c

## Purpose
This file describes the MT6878 pin controller for the MediaTek Paris core. It maps 196 pins across GPIO plus nine IOCFG regional bases, supplies basic GPIO and mux ranges, rich electrical configuration ranges, per-pin pull-type policy, EINT metadata, explicit EINT pin mapping, advanced drive support, and PM-aware platform-driver registration for `mediatek,mt6878-pinctrl`.

## Important APIs, Types, And Functions
`PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` wrap `PIN_FIELD_CALC()` for 32-bit registers and region-indexed bases. Basic pin control arrays cover mode, direction, DI, and DO. Electrical arrays cover IES, SMT, PU, PD, PUPD, R0, R1, normal drive, advanced drive (`DRV_ADV`), and resistor select (`RSEL`). `mt6878_pull_type` is a 196-entry policy table selecting among `MTK_PULL_PU_PD_TYPE`, `MTK_PULL_PU_PD_RSEL_TYPE`, and `MTK_PULL_PUPD_R1R0_TYPE`.

`mt6878_pinctrl_register_base_names` lists ten resource names: `gpio`, `iocfg_bl`, `iocfg_bm`, `iocfg_br`, `iocfg_bl1`, `iocfg_br1`, `iocfg_lm`, `iocfg_lt`, `iocfg_rm`, and `iocfg_rt`. `mt6878_eint_hw` declares one EINT port with port mask `31`, 216 AP EINT lines, 36 debounce counters, and `debounce_time_mt6878`. `mt6878_data` references `mtk_pins_mt6878`, `eint_pins_mt6878`, `nfuncs = 8`, combo bias helpers, the pull-type table, and advanced drive callbacks.

## Control Flow
The file registers `mt6878_pinctrl_driver` during `arch_initcall()`. OF matching on `mediatek,mt6878-pinctrl` provides `mt6878_data` to `mtk_paris_pinctrl_probe()`. The shared Paris implementation then maps all base resources, registers pinctrl/gpio/EINT providers, and uses `mt6878_reg_cals` to translate generic pinmux and pinconf operations into exact MMIO field accesses. Sleep handling is provided through `pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`.

## State And Persistence
All local data is const. Hardware state persists in the pin controller registers selected by the range tables. Because MT6878 supports multiple pull models and advanced drive fields, the static `pull_type`, `DRV_ADV`, and `RSEL` ranges directly determine whether a generic bias or drive-strength request writes simple PU/PD bits, PU/PD plus RSEL bits, PUPD/R0/R1 bits, raw drive bits, or advanced drive bits.

## Dependencies And Integration Points
The file depends on `pinctrl-mtk-mt6878.h` for pin and EINT-pin descriptors plus debounce metadata, and `pinctrl-paris.h` for the common implementation. It integrates with OF resource naming, pinctrl state selection, gpiolib, EINT/IRQ consumers, and PM sleep pinctrl transitions.

## Risks
MT6878's risk profile is dominated by table complexity. Ten register bases and several electrical models create many opportunities for a pin to target a plausible but wrong offset. The `PINCTRL_PIN_REG_SR` entry maps to `mt6878_pin_dir_range`, which is intentional only if the common core treats SR as unsupported or aliased for this SoC; it deserves scrutiny if slew-rate behavior is expected. The separate `eint_pin` map must remain synchronized with `mt6878_eint_hw` and the pin descriptor header. Advanced drive fields are sparse, so requests on unsupported pins should fail cleanly.

## Test Signals
Use boot/probe logs to verify all ten resources bind, debugfs to confirm 196 pins and eight functions, and targeted pinconf tests for each pull type. Exercise advanced drive on pins listed in `mt6878_pin_drv_adv_range` and verify unsupported pins do not write arbitrary fields. GPIO and mux tests should sample pins from every IOCFG base. EINT tests should cover the explicit EINT pin map, AP EINT numbering, and debounce behavior. Suspend/resume testing should validate the Paris PM integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6878.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6893.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6893.c

## Purpose
This file provides the MT6893 SoC data table for the MediaTek Paris pinctrl core. It describes 220 pins across ten named register bases, including mux/GPIO control, Schmitt/input-enable, pull-up/down, mixed advanced pull models, normal and advanced drive strength, RSEL fields, EINT hardware, and PM-aware platform-driver registration.

## Important APIs, Types, And Functions
`PIN_FIELD_BASE()` and `PINS_FIELD_BASE()` expand to `PIN_FIELD_CALC()` for 32-bit registers with base indices. Basic field arrays are `mt6893_pin_mode_range`, `mt6893_pin_dir_range`, `mt6893_pin_di_range`, and `mt6893_pin_do_range`. Electrical arrays include `mt6893_pin_smt_range`, `mt6893_pin_ies_range`, `mt6893_pin_pu_range`, `mt6893_pin_pd_range`, `mt6893_pin_drv_range`, `mt6893_pin_pupd_range`, `mt6893_pin_r0_range`, `mt6893_pin_r1_range`, `mt6893_pin_drv_adv_range`, and `mt6893_pin_rsel_range`.

`mt6893_pull_type` is a 220-entry per-pin selector for `MTK_PULL_PU_PD_TYPE`, `MTK_PULL_PUPD_R1R0_TYPE`, and `MTK_PULL_PU_PD_RSEL_TYPE`. `mt6893_pinctrl_register_base_name` names the resources as `base`, `rm`, `bm`, `bl`, `br`, `lm`, `lb`, `rt`, `lt`, and `tl`. `mt6893_reg_cals` maps all supported register classes, including `DRV_ADV` and `RSEL`. `mt6893_eint_hw` describes seven EINT ports, 224 AP EINT lines, 32 debounce counters, and `debounce_time_mt6765`. `mt6893_data` selects rev1 drive callbacks for normal drive, raw advanced drive callbacks for advanced drive, combo bias helpers, `nfuncs = 8`, and the pull-type table.

## Control Flow
`arch_initcall(mt6893_pinctrl_init)` registers the platform driver. The OF match table binds `mediatek,mt6893-pinctrl` and supplies `mt6893_data` to `mtk_paris_pinctrl_probe()`. The shared probe maps the named resources, registers pinctrl/gpio/EINT providers, and uses `mt6893_reg_cals` for subsequent pinmux and pinconf operations. PM sleep callbacks are enabled through `pm_sleep_ptr(&mtk_paris_pinctrl_pm_ops)`.

## State And Persistence
The file has no mutable state. It persists behavior by defining the static mapping from pin numbers to hardware fields. Runtime changes are MMIO register writes made by the Paris core for mux mode, GPIO state, bias, Schmitt, input enable, drive strength, advanced drive, RSEL, and EINT debounce/trigger state.

## Dependencies And Integration Points
The driver depends on `pinctrl-mtk-mt6893.h` for pin descriptors and debounce data, `pinctrl-paris.h` for probe and callbacks, OF platform binding, gpiolib, generic pinctrl/pinconf, MediaTek EINT, and PM sleep integration. Device tree must expose register resources with names matching `mt6893_pinctrl_register_base_name`.

## Risks
MT6893 has a large and irregular field map. Pull behavior is especially sensitive because different pins use PU/PD, PUPD/R0/R1, or PU/PD/RSEL models. The normal drive callbacks use rev1 helpers while advanced drive uses raw helpers, so field widths and value encoding must match the common helper's expectations. `PINCTRL_PIN_REG_SR` maps to the direction range, which should be reviewed if clients require explicit slew-rate control. The EINT debounce table reuses `debounce_time_mt6765`; this is probably intentional only if MT6893 shares timing values.

## Test Signals
Probe should succeed with all ten named resources. Debugfs should show 220 pins/groups and eight functions. Pinmux tests should sample pins in each region. Pinconf tests should cover each pull type, normal rev1 drive, raw advanced drive, Schmitt, IES, and unsupported-field behavior. EINT tests should cover several ports and debounce counters. Suspend/resume tests should confirm state restoration through the Paris PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6893.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7620.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7620.c

## Purpose
This file is the MT7620/RT2880-family pinmux table for the legacy `pinctrl-mtmips` driver. Unlike the Paris MediaTek mobile SoC files, it does not define per-pin electrical register fields. It declares mux-mode bit encodings and pin groups for common MT7620A peripheral functions, then registers a platform driver for `ralink,mt7620-pinctrl` and the fallback `ralink,rt2880-pinmux`.

## Important APIs, Types, And Functions
The `MT7620_GPIO_MODE_*` macros define shift positions, masks, GPIO fallback encodings, and function mode values for shared mux registers. Function arrays use `struct mtmips_pmx_func` and the `FUNC(name, value, first_pin, pin_count)` macro to describe alternatives such as I2C, SPI, UART lite, MDIO/refclk, RGMII, SPI refclk, EPHY, WLED, PA, UARTF/PCM/I2S combinations, watchdog reset/refclk, PCIe reset/refclk, and NAND/SD.

`mt7620a_pinmux_data` is the key table of `struct mtmips_pmx_group`. `GRP()` entries describe simple one-bit or direct mode selections, while `GRP_G()` entries include a mask, GPIO value, and shift for multi-bit groups. `mt7620_pinctrl_probe()` passes that table to `mtmips_pinctrl_init()`.

## Control Flow
`core_initcall_sync(mt7620_pinctrl_init)` registers the platform driver early and synchronously. On OF match, `mt7620_pinctrl_probe()` calls the shared MIPS pinctrl initializer with `mt7620a_pinmux_data`. The common `pinctrl-mtmips` code then exposes each group/function to pinctrl consumers and writes the SoC's global GPIO mode register fields when a function is selected.

## State And Persistence
This file contains static function/group tables only. Runtime state is held in the MT7620 GPIO mode register bits written by the shared mtmips driver. Because several peripheral blocks share pins and multi-bit encodings, selecting one function persists by excluding other functions in the same group until another state rewrites the group.

## Dependencies And Integration Points
The file depends on Linux module/platform/OF headers and `pinctrl-mtmips.h` for table types, macros, and `mtmips_pinctrl_init()`. It integrates with device-tree pinctrl states used by Ralink/MediaTek MIPS platform devices such as Ethernet, MDIO, PCIe, NAND/SD, UART, SPI, I2C, and LEDs.

## Risks
Shared mux groups are the main risk. UARTF, PCM, I2S, and GPIO alternatives overlap heavily and use a three-bit field; a wrong mode value can partially enable the wrong peripheral. Some groups use `GRP_G()` with explicit GPIO fallback values, so mask/shift mistakes can leave pins unavailable as GPIO. The compatible fallback to `ralink,rt2880-pinmux` means board DTS files may bind this table through a generic compatible, so behavioral changes can affect older boards.

## Test Signals
Validation should include boot binding, pinctrl debugfs group/function listing, and device-tree states for every group. Functional smoke tests should cover I2C, SPI, UART lite, UARTF alternatives, MDIO/refclk, RGMII1/RGMII2, PCIe reset/refclk, watchdog, NAND/SD selection, WLED, EPHY, and PA. GPIO fallback should be tested for every `GRP_G()` group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7621.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7621.c

## Purpose
This file describes MT7621 pinmux groups for the legacy `pinctrl-mtmips` framework. It maps global GPIO mode register encodings to named peripheral functions for `ralink,mt7621-pinctrl` and the fallback `ralink,rt2880-pinmux` compatible.

## Important APIs, Types, And Functions
The `MT7621_GPIO_MODE_*` macros define mode bits, masks, shifts, and GPIO fallback values for UARTs, I2C, JTAG, watchdog, PCIe, MDIO, RGMII, SPI, and SDHCI/NAND-related pin groups. Function arrays use `FUNC()` to describe each selectable function and its first pin/count span. Notable multiplexed groups include UART3 versus I2S/SPDIF3, UART2 versus PCM/SPDIF2, SPI versus NAND1, SDHCI versus NAND2, watchdog reset/refclk, and PCIe reset/refclk.

`mt7621_pinmux_data` is the `struct mtmips_pmx_group` table consumed by the common driver. It uses `GRP()` for direct selections and `GRP_G()` for masked multi-bit selections with GPIO fallback values. `mt7621_pinctrl_probe()` passes the table to `mtmips_pinctrl_init()`.

## Control Flow
`core_initcall_sync(mt7621_pinctrl_init)` registers the platform driver. OF matching invokes `mt7621_pinctrl_probe()`, which delegates initialization to `mtmips_pinctrl_init(pdev, mt7621_pinmux_data)`. After that, generic pinctrl state selection flows through the mtmips core, which writes the appropriate mode-field value for the requested group/function.

## State And Persistence
The file is stateless after registration. Hardware state persists in MT7621 global mode bits. Because many groups are mutually exclusive, selecting one function for a group persists until another pinctrl state changes the same masked field.

## Dependencies And Integration Points
It depends on `pinctrl-mtmips.h`, platform-device and OF support, and device-tree consumers using the exposed group/function names. It integrates with serial, I2C, audio, SPDIF, JTAG, watchdog, PCIe, MDIO, Ethernet RGMII, SPI, NAND, and SDHCI platform devices on MT7621 boards.

## Risks
The highest risk is incorrect multi-bit encoding for `GRP_G()` groups. UART2/UART3 audio alternatives, SPI/NAND, and SDHCI/NAND share pins and can break multiple board functions if mask, shift, or GPIO fallback values are wrong. The fallback compatible can broaden the impact of table changes. Since this file contains no pinconf/electrical metadata, consumers must not expect bias or drive control here.

## Test Signals
Test successful binding for both compatibles, debugfs group/function visibility, and mux selection for UART1/2/3, I2C, JTAG, watchdog, PCIe, MDIO, RGMII1/2, SPI/NAND1, and SDHCI/NAND2. GPIO fallback should be verified for masked groups, and board-level tests should cover boot media, network, serial console, and PCIe reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt7621.c -->
