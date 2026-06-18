# Research: subset-b-005073

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ocelot.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ocelot.c

## Purpose
This driver provides pinctrl, pinmux, pin configuration, GPIO, and optional GPIO IRQ support for Microchip/Microsemi Ocelot-family switch SoCs and descendants: Luton, Serval, Ocelot, Jaguar2, ServalT, Sparx5, LAN966x, LAN969x, and LAN9645xF. Most of the file is SoC-specific pin capability data; the executable logic converts those tables into Linux pinctrl function groups, writes ALT mode registers, exposes GPIO lines, and configures per-pin electrical settings where the matched SoC has a pinconf register block.

## Important APIs, Types, And Functions
`struct ocelot_pin_caps` records each pin number plus normal and alternate function selectors. `struct ocelot_pinctrl` is the live controller state: device, pinctrl descriptor copy, regmaps for GPIO/pinmux and optional pinconf, calculated stride values, GPIO chip, function-to-group map, workqueue, and pinconf bit layout. `struct ocelot_match_data` binds a compatible string to a `pinctrl_desc`, pinconf bit definitions, and alternate-mode count.

The pinctrl ops are `ocelot_pctl_get_groups_count()`, `ocelot_pctl_get_group_name()`, and `ocelot_pctl_get_group_pins()`, with one group per pin. The pinmux core is `ocelot_pin_function_idx()`, `ocelot_pinmux_set_mux()` for two-bit ALT encodings, and `lan966x_pinmux_set_mux()` for three-bit encodings. GPIO integration uses `ocelot_gpio_request_enable()`, `lan966x_gpio_request_enable()`, `ocelot_gpio_set_direction()`, and the `ocelot_gpiolib_chip` callbacks. Pinconf support is implemented by `ocelot_hw_get_value()`, `ocelot_hw_set_value()`, `ocelot_pinconf_get()`, and `ocelot_pinconf_set()`. IRQ support is in `ocelot_irq_handler()`, `ocelot_irq_set_type()`, `ocelot_irq_mask()`, `ocelot_irq_ack()`, `ocelot_irq_unmask()`, and the level-specific `ocelot_irq_unmask_level()`.

## Control Flow
Probe copies the matched descriptor, creates an ordered workqueue for deferred level IRQ replay, obtains and resets the optional shared `switch` reset control, computes GPIO bank stride and alternate-mode stride, creates the main MMIO regmap, optionally maps a second pinconf resource, builds function group lists from every pin's capability table, registers pinctrl, and then registers the GPIO chip. If a parent IRQ is present, `ocelot_gpiochip_register()` attaches an immutable irqchip and chained parent handler.

Function selection validates that the requested function is supported by the selected pin group, then writes the encoded mux value bit-by-bit into ALT registers. Older variants write ALT0 and ALT1; LAN966x/LAN969x/LAN9645x-compatible mux ops write ALT0 through ALT2. GPIO requests force mux bits back to GPIO on most variants, while LAN9645xF uses a no-op request path because its GPIO function is represented differently in the table. Pinconf reads and writes use optional per-pin registers for bias, drive strength, and Schmitt trigger, while output/input/level configs operate on GPIO OUT and OE registers.

GPIO IRQ handling reads interrupt-identification registers across all GPIO banks and dispatches child IRQs in the GPIO irqdomain. Edge IRQs use the normal irqchip. Level IRQs switch to `ocelot_level_irqchip`; unmask checks whether the line is still active, acknowledges stale latched edges when possible, reenables the line, and queues ordered work to re-enter the chained handler if an active level was missed while masked.

## State And Persistence
Runtime state is in `struct ocelot_pinctrl` and devm-managed allocations. The generated `info->func[]` group map persists for the lifetime of the device. Hardware mux, GPIO direction/value, interrupt enable/status, and pinconf registers persist until reset or later writes. There is no file-backed persistence. The ordered workqueue is destroyed by a devm action, and the GPIO/pinctrl registrations are devm-managed.

## Dependencies And Integration Points
The driver integrates with the Linux pinctrl, pinmux, pinconf-generic, GPIO, gpio-irqchip, regmap-mmio, reset-controller, platform-device, OF match, IRQ, and workqueue APIs. It depends on `ocelot_regmap_from_resource()` from the Ocelot platform support and on device tree compatible strings in `ocelot_pinctrl_of_match`. Consumers use standard pinctrl states, GPIO descriptors, and optional GPIO IRQs. A second MMIO resource enables extended pin configuration on variants whose descriptors include `confops`.

## Risks And Test Signals
The mux update writes multiple ALT registers independently, and the code documents the operation as racy because the encoded bits cannot be changed atomically. Pin tables are large and variant-specific; incorrect table entries can silently select the wrong hardware signal. Optional pinconf mapping returns `NULL` when the resource is absent, but pinconf ops still return `-EOPNOTSUPP` for unsupported hardware paths. Level IRQ replay depends on GFP_ATOMIC allocation and the ordered workqueue, so allocation failure can drop the synthetic retrigger. A likely code-review signal is the need to verify `REG_ALT()`/`altm_stride` calculations for high pin counts and LAN9645xF's `n_alt_modes`.

Useful tests include probe on each compatible, pinctrl state application for representative functions on low and high pins, GPIO request fallback to GPIO mode, bias/drive/Schmitt reads and writes on variants with pinconf resources, GPIO direction/value operations across bank boundaries, IRQ edge and level triggering, and removal/unbind paths that exercise devm cleanup and workqueue destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ocelot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-palmas.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-palmas.c

## Purpose
This driver exposes the pin mux and limited electrical configuration controls for TI Palmas/TPS65913/TPS80036 PMIC pins. It maps PMIC pad functions such as GPIO, LEDs, PWM, charger detect, USB ID/VBUS, SIM reset, secure/power-hold signals, DVFS pads, and enable pins into the Linux pinctrl subsystem, using Palmas MFD register accessors rather than direct MMIO.

## Important APIs, Types, And Functions
`struct palmas_pctrl_chip_info` is the live per-device state: parent `struct palmas`, device pointer, pinctrl device, pin/function/group arrays, and `pins_current_opt[]`, which caches the selected option for each group. `struct palmas_pin_function` describes a pinctrl function name, group list, and mux option value. `struct palmas_pingroup` describes one logical pin group, its register base/address/mask/shift, single pin number, and up to four option descriptors. `struct palmas_pin_info` links a mux option to optional pull-up/down and open-drain descriptors.

The main flows are `palmas_pinctrl_get_pin_mux()` for initial cache population, `palmas_pinctrl_set_mux()` for mux changes, `palmas_pinconf_get()` and `palmas_pinconf_set()` for generic bias/open-drain settings, and `palmas_pinctrl_probe()` for platform registration. DVFS pad controls are handled by `palmas_pinctrl_set_dvfs1()` and `palmas_pinctrl_set_dvfs2()`.

## Control Flow
Probe selects TPS65913 or TPS80036 group data from OF match data, reads boolean properties `ti,palmas-enable-dvfs1` and `ti,palmas-enable-dvfs2`, allocates chip state, fetches the parent Palmas MFD state with `dev_get_drvdata()`, assigns static pin/function/group tables, applies the DVFS secondary-pad bits, reads current hardware mux selections into `pins_current_opt[]`, names the shared `palmas_pinctrl_desc`, and registers pinctrl.

Pinctrl group APIs return one group per PMIC pad definition. `palmas_pinctrl_set_mux()` accepts either direct option selectors `PALMAS_PINMUX_OPTION0..3` or named logical function selectors. It validates that the selected group supports the option, handles groups with no mux register as fixed option 0, then calls `palmas_update_bits()` on the PMIC register and updates `pins_current_opt[group]`.

Pinconf first resolves the single-pin group by pin number, then chooses the active option descriptor from `pins_current_opt[]`. Bias operations use the selected option's `pud_info`; open-drain operations use `od_info`. Reads compare masked register values against table-defined normal, pull-up, pull-down, open-drain-enable, or open-drain-disable values. Writes reject unsupported values marked as negative and update only the relevant bits.

## State And Persistence
The driver caches current mux option per group in `pins_current_opt[]`; this is required because pinconf support depends on which option is active. Actual pin mux, pull, open-drain, and DVFS settings live in PMIC registers and persist according to PMIC reset/power behavior. There is no remove callback or external persistence; devm pinctrl registration and platform device lifetime own software state.

## Dependencies And Integration Points
The driver depends on the Palmas MFD core (`palmas_read()` and `palmas_update_bits()`), Palmas register definitions, platform device binding from the parent MFD, OF match data, pinctrl core, pinmux ops, pinconf generic helpers, and `pinctrl-utils`. Device tree consumers use standard pinctrl states plus the Palmas-specific compatible strings `ti,palmas-pinctrl`, `ti,tps65913-pinctrl`, and `ti,tps80036-pinctrl`.

## Risks And Test Signals
`palmas_pinctrl_desc` is a static mutable descriptor whose `name` is overwritten at probe, so multiple instances would share descriptor metadata. Pinconf correctness depends on `pins_current_opt[]` matching hardware; direct PMIC register writes by another driver would make the cache stale. Some pins/options intentionally lack pull or open-drain data and return `-ENOTSUPP`, which can expose invalid board pinctrl states. Probe applies DVFS writes before checking their return values in aggregate; failures are logged inside helpers but not fatal.

Useful tests include probing each compatible, reading initial mux state from hardware, applying direct option and named function mux selections, validating unsupported option rejection, exercising bias disable/up/down and open-drain on supported and unsupported pads, checking DVFS property effects on `PALMAS_PRIMARY_SECONDARY_PAD3`, and confirming PMIC register update failures propagate for mux and pinconf paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-palmas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pef2256.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pef2256.c

## Purpose
This is the pinctrl/pinmux driver for the Lantiq/Infineon PEF2256 FALC56 line interface. It exposes the four receive port pins and four transmit port pins as one-pin groups and programs their Port Configuration registers to select line-interface signals or, on newer silicon, GPIO-style functions.

## Important APIs, Types, And Functions
`struct pef2256_pinreg_desc` stores the register offset and field mask for one pin group. `struct pef2256_function_desc` maps a function name to allowed groups and the encoded register value. `struct pef2256_pinctrl` holds device, parent regmap, detected hardware version, local `pinctrl_desc`, and the version-specific function table. Pinctrl ops are `pef2256_get_groups_count()`, `pef2256_get_group_name()`, and `pef2256_get_group_pins()`. Pinmux ops are `pef2256_get_functions_count()`, `pef2256_get_function_name()`, `pef2256_get_function_groups()`, and `pef2256_set_mux()`.

Version-specific static tables define v1.2 and v2.x pin descriptors and functions. `pef2256_reset_pinmux()` writes a safe initial mux to PC1 through PC4, `pef2256_register_pinctrl()` selects the table for the detected version and registers pinctrl, and `pef2256_pinctrl_probe()` wires the driver to the parent PEF2256 MFD/framer device.

## Control Flow
Probe allocates driver state, assigns the child device fwnode from the parent, retrieves the parent `struct pef2256`, fetches its regmap and version through exported helpers, stores platform driver data, resets all port configuration registers to a safe non-conflicting mux, and registers pinctrl. Group enumeration is direct: one group equals one pin. Function enumeration is selected by hardware version; v2.x adds LOS and GPIO-like GPI/GPOH/GPOL choices that v1.2 lacks.

`pef2256_set_mux()` receives a function selector and group selector from pinctrl. It fetches the group's `pef2256_pinreg_desc` from `pinctrl_pin_desc.drv_data`, gets the selected function's pre-encoded value, and calls `regmap_update_bits()` on the relevant PC register field. For functions allowed on both RP and XP groups in v2.x, the encoded value combines both field positions; the group's mask ensures only the relevant nibble is written.

## State And Persistence
The driver has minimal software state: detected version and selected static tables. Pin mux state persists in PEF2256 PC1-PC4 hardware registers. The reset function intentionally overwrites reset defaults because the hardware reset values would mux all RP pins to SYPR and all XP pins to SYPX, while only one pin can validly drive each such signal. No runtime cache of mux state is kept.

## Dependencies And Integration Points
This driver depends on the parent PEF2256 framer/MFD object, `pef2256_get_regmap()`, `pef2256_get_version()`, Linux regmap, platform device registration, and the pinctrl/pinmux core. It uses `pinconf_generic_dt_node_to_map_pin()` for DT mapping despite implementing mux-only behavior; no pinconf ops are registered. The platform driver name is `lantiq-pef2256-pinctrl`.

## Risks And Test Signals
The safe reset writes ignore `regmap_write()` return values, so bus failures during reset are not reported before registration. Function value correctness is version-sensitive, especially because v1.2 RP and XP masks differ from v2.x masks. The compound GPIO function encodings rely on masks to discard irrelevant bits. There is no OF match table in this child driver; successful binding depends on the parent creating the platform device with the expected name and data.

Useful tests include probe for both PEF2256 v1.2 and v2.x, verification that PC1-PC4 are reset to the intended safe values, muxing every RP-only and XP-only function onto each legal group, confirming v2.x GPI/GPOH/GPOL work on all eight groups, checking unsupported function/group combinations are not emitted by pinctrl group lists, and forcing regmap failures to validate propagation from `set_mux()` and registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pef2256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.c

## Purpose
This driver supports Microchip PIC32MZ DA pin control and GPIO. It exposes Peripheral Pin Select input/output muxing, analog/digital mode selection, pull-up/down, open-drain, GPIO direction/value, and change-notification GPIO interrupts. Pinctrl and GPIO banks are registered as separate platform drivers that share static bank metadata.

## Important APIs, Types, And Functions
`struct pic32_pinctrl` stores the PPS MMIO base, clock, pinctrl device, pin/function/group tables, and shared GPIO bank table. `struct pic32_gpio_bank` stores one bank's MMIO base, instance number, gpiochip, and clock. `struct pic32_function`, `struct pic32_pin_group`, and `struct pic32_desc_function` describe which named peripheral functions can be muxed onto each remappable pin and what PPS register/value pair must be written.

The pinmux path is `pic32_pinmux_enable()`, which scans the selected group's function descriptors and writes the PPS mux register. GPIO and pinmux integration uses `pic32_gpio_request_enable()` to clear analog mode, `pic32_gpio_set_direction()`, and the gpiochip callbacks. Pinconf is provided by `pic32_pinconf_get()` and `pic32_pinconf_set()`, including custom generic parameters `microchip,digital` and `microchip,analog`. IRQ support is implemented by `pic32_gpio_irq_set_type()`, `pic32_gpio_irq_ack()`, `pic32_gpio_irq_mask()`, `pic32_gpio_irq_unmask()`, `pic32_gpio_get_pending()`, and `pic32_gpio_irq_handler()`.

## Control Flow
`pic32_pinctrl_probe()` maps the PPS register resource, enables the clock, assigns static pin/function/group arrays, fills `pic32_pinctrl_desc` including custom pinconf parameters, and registers pinctrl. `pic32_gpio_probe()` reads the `microchip,gpio-bank` property, selects a static bank, maps that bank's PORT register resource, gets its IRQ and clock, configures the gpiochip parent, attaches an immutable irqchip with a chained parent handler, and registers the gpiochip with devm. Both platform drivers are registered at `arch_initcall`.

When a pinctrl mux state is applied, the driver looks up the selected function name inside the selected group's descriptor list and writes `muxval` to `pctl->reg_base + muxreg`. GPIO requests clear the selected bank's ANSEL bit through PIC32's SET/CLR alias register scheme. GPIO direction uses TRIS set for input and clear for output, while values use PORT set/clear aliases. Pinconf reads and writes manipulate CNPU, CNPD, ANSEL, ODCU, TRIS, and output level through the bank registers.

GPIO IRQ setup only accepts edge rising, falling, or both. It configures CNEN for rising, CNNE for falling, sets the CNCON edge bit, and switches the child handler to `handle_edge_irq`. The chained parent handler reads CNF status, filters it through enabled rising/falling registers, and dispatches pending child IRQs. Masking clears CNCON ON for the whole bank; unmasking sets it again.

## State And Persistence
Software state is mostly static tables and per-device pointers. The `pic32_gpio_banks[]` array is global and shared between the pinctrl and GPIO platform devices; each GPIO probe fills MMIO, clock, parent, and irqchip fields for one bank. Hardware state persists in PPS and PORT registers until reset or later writes. No software cache tracks mux or pinconf values.

## Dependencies And Integration Points
The driver depends on platform MMIO resources, clocks, OF platform devices, pinctrl/pinmux/pinconf core, gpiochip and gpio-irqchip APIs, `pinctrl-utils`, and PIC32 SET/CLR alias macros from `linux/platform_data/pic32.h`. `pinctrl-pic32.h` supplies PPS and PORT register offsets. Device tree compatibles are `microchip,pic32mzda-pinctrl` and `microchip,pic32mzda-gpio`, with GPIO bank identity carried by `microchip,gpio-bank`.

## Risks And Test Signals
The shared static `pic32_gpio_banks[]` means repeated probes, partial probe failures, or multiple SoC instances would reuse mutable bank state. `pic32_gpio_get_pending()` appears to use `(mask && cnne_fall)` instead of `(mask & cnne_fall)`, which can report falling-enabled status incorrectly whenever any CNNE bit is set. `pic32_gpio_irq_ack()` writes zero to CNF rather than a bit mask or clear alias, which should be checked against hardware semantics. IRQ mask/unmask toggles CNCON ON for the whole bank, so masking one child IRQ can affect sibling GPIO interrupts. The driver includes `spinlock.h` but uses no explicit locking around read-modify-write pinconf paths.

Useful tests include PPS muxing for representative input and output functions, GPIO request clearing analog mode, custom `microchip,digital`/`analog` pinconf parsing, pull-up/down/open-drain/direction/value behavior per bank, GPIO IRQ rising/falling/both-edge delivery, sibling IRQ behavior when one child is masked, invalid bank property handling, and build tests that catch descriptor/register-offset drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.h

## Purpose
This header centralizes PIC32MZ DA pinctrl register offsets used by `pinctrl-pic32.c`. It defines PORT register offsets for each GPIO bank and Peripheral Pin Select input/output register offsets for remappable peripheral functions and pins.

## Important APIs, Types, And Functions
The file contains macros only. PORT bank offsets include `ANSEL_REG`, `TRIS_REG`, `PORT_REG`, `LAT_REG`, `ODCU_REG`, `CNPU_REG`, `CNPD_REG`, `CNCON_REG`, `CNEN_REG`, `CNSTAT_REG`, `CNNE_REG`, and `CNF_REG`. Input PPS offsets include `INT1R` through `INT4R`, timer clock inputs, input capture inputs, UART RX/CTS inputs, SPI SDI/SS inputs, CAN RX inputs, and reference clock inputs. Output PPS offsets include remappable pin output registers such as `RPA14R`, `RPB0R`, `RPC1R`, `RPD0R`, `RPE3R`, `RPF0R`, and `RPG0R`.

## Control Flow
There is no runtime control flow in this header. The C driver consumes these constants in static pin group tables and when calculating bank register accesses. PPS mux writes use the input/output register macros as `muxreg` values, while GPIO and pinconf callbacks use the PORT register macros relative to each bank's MMIO base.

## State And Persistence
The header has no software state. Its constants define addresses of hardware state that persists in the PIC32 peripheral registers. Any incorrect offset here directly changes which hardware register the driver reads or writes.

## Dependencies And Integration Points
The header is included only by the PIC32 pinctrl implementation in this subset. It depends on the including file for SET/CLR alias address transforms and for the MMIO base. It forms a compact contract between the large static pin group tables and the low-level register writes.

## Risks And Test Signals
Risk is table accuracy: a single incorrect PPS offset can route a peripheral to the wrong pin or fail to route it at all. The header does not encode field widths or valid mux values, so those must remain consistent with `pic32_groups[]`. Tests should verify muxing for every register family, compare offsets against the PIC32MZ DA datasheet, and build-test that every macro referenced by `pinctrl-pic32.c` remains defined.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pistachio.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pistachio.c

## Purpose
This driver provides pinctrl, pinmux, pinconf, GPIO, and GPIO IRQ support for the Imagination Pistachio SoC system pin controller. It covers 90 MFIO pins plus special non-GPIO pins, maps multiplexed peripheral/debug/scenario functions, exposes electrical pad controls, and registers six GPIO banks as child gpiochips.

## Important APIs, Types, And Functions
`struct pistachio_pinctrl` stores the system pinctrl MMIO base, pinctrl device, static pin/function/group tables, and GPIO bank table. `struct pistachio_function` describes a function's legal groups and optional scenario selector metadata. `struct pistachio_pin_group` describes one pin, up to three mux options, and the function-select register field. `struct pistachio_gpio_bank` stores per-bank base, pin range, gpiochip, and backpointer.

The pinmux path is `pistachio_pinmux_enable()`, which writes function-select fields and optional scenario fields, then disables GPIO mode for that pin. Pinconf is handled by `pistachio_pinconf_get()` and `pistachio_pinconf_set()` for Schmitt trigger, high-Z, pull-up/down, bus hold, slew rate, and 2/4/8/12 mA drive strength. GPIO helpers include `gpio_mask_writel()`, `gpio_enable()`, `gpio_disable()`, and gpiochip callbacks for direction, get, set, and get_direction. IRQ support is implemented by `pistachio_gpio_irq_set_type()`, ack/mask/unmask/startup callbacks, and `pistachio_gpio_irq_handler()`.

## Control Flow
Probe allocates controller state, maps one MMIO resource, assigns static tables, registers pinctrl, and then calls `pistachio_gpio_register()`. GPIO registration iterates expected child nodes named `gpio0` through `gpio5`, requires each to have `gpio-controller`, obtains its IRQ, initializes the bank base at `GPIO_BANK_BASE(i)`, attaches a fwnode-aware gpiochip and immutable irqchip, adds the gpiochip, and adds a pin range linking bank GPIO offsets back to pinctrl pins. On failure, already-added gpiochips are removed manually.

Pinctrl group and function enumeration directly reflect the static arrays. For muxable MFIO groups, `pistachio_pinmux_enable()` finds which of the group's three mux slots matches the selected function, updates the correct function-select field, and for functions with scenario lists updates `PADS_SCENARIO_SELECT` to the index of the selected group in that scenario list. After muxing, it finds any GPIO range covering the pin and disables GPIO bit-enable for the bank offset so the peripheral function owns the pad.

GPIO registers use a masked write convention: bit `16 + offset` authorizes writing bit `offset`, implemented by `gpio_mask_writel()`. Direction input clears OUTPUT_EN and enables the GPIO bit; output writes the value, sets OUTPUT_EN, and enables the bit. IRQ type programming supports rising, falling, both-edge, level-high, and level-low by configuring polarity, edge/level mode, and single/dual edge registers. The chained handler dispatches enabled interrupt-status bits for up to 16 pins per bank.

## State And Persistence
Runtime software state is stored in the controller object and the static mutable `pistachio_gpio_banks[]` entries initialized during probe. Hardware state includes pad pull/drive/slew/Schmitt registers, mux function-select and scenario registers, GPIO enable/output/direction, and interrupt configuration/status. There is no persistent storage and no remove callback; probe failure after gpiochip registration is cleaned manually, while successful registration relies on platform lifetime.

## Dependencies And Integration Points
The driver depends on platform MMIO, firmware child nodes, OF/property APIs, pinctrl/pinmux/pinconf core, gpiochip and gpio-irqchip APIs, IRQ handling, `pinctrl-utils`, and standard pinconf generic properties. It binds to `img,pistachio-system-pinctrl`. GPIO consumers use child gpio-controller nodes; pinctrl consumers use the parent pinctrl device and named groups/functions.

## Risks And Test Signals
GPIO bank registration is not devm-managed after success, and there is no remove path, which is acceptable for built-in arch-init registration but risky for hot-unbind assumptions. The static GPIO bank array is mutable global state and would not support multiple controller instances cleanly. `gpio_mask_writel()` depends on the hardware masked-write convention; any register that does not follow it would be corrupted. Mux/scenario validation is table-driven, so wrong scenario arrays can program the wrong scenario index. Pinconf read-modify-write paths have no explicit locking.

Useful tests include probe with all six child GPIO nodes, failure cleanup when a child node or IRQ is missing, muxing plain fixed MFIO groups and three-option mux groups, scenario functions such as `spdif_in` and MIPS trace variants, GPIO enable/disable interaction when switching between GPIO and peripheral mux, all supported pinconf properties and drive strengths, GPIO IRQ rising/falling/both/level modes, and bank 5 behavior with only 10 pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pistachio.c -->
