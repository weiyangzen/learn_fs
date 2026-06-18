# subset-b-005071 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ingenic.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ingenic.c

## Purpose
This file is the Linux pinctrl, pinmux, pinconf, GPIO, and GPIO IRQ driver for a broad set of Ingenic MIPS SoCs, from JZ4730/JZ4740-era parts through JZ47xx, X1000/X1500/X1600/X1830, and X2000/X2100 families. It combines static SoC pin-function tables with common register access code that adapts to several incompatible GPIO register layouts. The driver exposes named pin groups and functions to device tree consumers, exposes each 32-pin bank as a gpiochip, and chains per-bank GPIO interrupt controllers into the kernel IRQ subsystem.

## Important APIs, types, and functions
The central static model is `struct ingenic_chip_info`, which records the number of 32-pin banks, the per-bank register spacing, the SoC version, group/function tables, pull-up and pull-down capability bitmaps, and optional regmap access ranges. `struct ingenic_pinctrl` holds the device, regmap, pinctrl device, generated pin descriptors, selected chip info, and the currently registered gpiochip pointer. `struct ingenic_gpio_chip` wraps one gpiochip with its parent pinctrl state, IRQ line, and register base.

The table macros `INGENIC_PIN_GROUP()`, `INGENIC_PIN_GROUP_FUNCS()`, and `INGENIC_PIN_FUNCTION()` build Linux generic `group_desc` and `pinfunction` entries. The file defines large SoC-specific arrays for JZ4730, JZ4740, JZ4725B, JZ4750, JZ4755, JZ4760, JZ4770, JZ4775, JZ4780, X1000, X1500, X1600, X1830, X2000, and X2100. These cover common functions such as UART, SSI/SPI, SFC, MMC/SD, NEMC/EMC, NAND, I2C, I2S, DMIC, CIM, LCD/SLCD, PWM, MAC, HDMI DDC, and OTG VBUS.

Important runtime helpers include `is_soc_or_above()` for version-gated behavior based on enabled Kconfig SoCs, `ingenic_gpio_set_bit()` for regular set/clear register writes, `ingenic_gpio_shadow_set_bit()` and `ingenic_gpio_shadow_set_bit_load()` for newer shadow group-load registers, and `jz4730_gpio_set_bits()` / `jz4730_config_pin_function()` for two-bit-per-pin paired registers. GPIO IRQ behavior is implemented by `irq_set_type()`, `ingenic_gpio_irq_mask()`, `ingenic_gpio_irq_unmask()`, `ingenic_gpio_irq_enable()`, `ingenic_gpio_irq_disable()`, `ingenic_gpio_irq_ack()`, `ingenic_gpio_irq_set_type()`, and `ingenic_gpio_irq_handler()`. Pinmux and pinconf callbacks are `ingenic_pinmux_set_mux()`, `ingenic_pinmux_gpio_set_direction()`, `ingenic_pinconf_get()`, `ingenic_pinconf_set()`, and their group variants. Registration flows through `ingenic_pinctrl_probe()`, `ingenic_gpio_probe()`, and `ingenic_pinctrl_drv_register()`.

## Control flow
At `subsys_initcall` time, `ingenic_pinctrl_drv_register()` registers a platform driver by calling `platform_driver_probe()`, so the probe path is init-only. Device tree matching selects an `ingenic_chip_info` through `ingenic_pinctrl_of_matches`; entries are wrapped in `IF_ENABLED()` so incompatible SoC tables are unavailable when their Kconfig option is off. Probe maps the MMIO resource, creates a regmap with either a calculated `max_register` or SoC-specific access tables for sparse newer layouts, allocates one pin descriptor per physical GPIO line, and registers pinctrl operations.

After pinctrl registration, probe adds every static group with `pinctrl_generic_add_group()` and every static function with `pinmux_generic_add_pinfunction()`. It then scans child nodes matching `ingenic_gpio_of_matches`; each GPIO child must provide a `reg` bank number and an IRQ. `ingenic_gpio_probe()` creates a gpiochip named `GPIOA`, `GPIOB`, and so on, preserves the legacy global GPIO base as `bank * 32`, installs GPIO get/set/direction methods, wires an immutable `irq_chip`, and registers a chained parent interrupt handler.

Pinmux requests arrive through generic pinmux helpers. `ingenic_pinmux_set_mux()` looks up the selected function and group, then interprets `group->data` either as a uniform mux mode 0..3 or as a per-pin mode array. Each pin is programmed by `ingenic_pinmux_set_pin_fn()`, which chooses different register sequences for X1000+ shadow registers, JZ4770-style `INT/MSK/PAT1/PAT0`, JZ4740-style `FUNC/TRIG/SELECT`, or JZ4730 paired function registers. GPIO direction requests use a parallel versioned register path in `ingenic_pinmux_gpio_set_direction()`.

Pin configuration requests first validate that every requested parameter is supported, then apply them one by one. Bias handling checks the SoC pull capability bitmaps before enabling pull-up or pull-down. X2000 uses independent pull-up/pull-down enable registers, X1830 uses two-bit pull fields split across low/high half-bank registers, X1600 has a pull-up register, JZ4770 uses inverted pull-enable semantics, JZ4740 uses pull-disable, and JZ4730 uses a pull-up register. Schmitt trigger and slew rate are available only on X1830 and newer. `PIN_CONFIG_LEVEL` switches the pin to GPIO output before setting the output register.

GPIO IRQs are chained per bank. The parent handler reads the SoC-specific flag register and dispatches each set bit with `generic_handle_domain_irq()`. IRQ type programming maps generic trigger types to the hardware `PAT/TRIG/DIR` fields. Hardware before X2000 cannot directly trigger on both edges; the driver emulates both-edge interrupts by configuring the opposite level/edge during ACK based on the current GPIO input value.

## State and persistence behavior
Persistent state is hardware register state in the pin controller and GPIO banks. The driver allocates device-managed pinctrl, regmap, gpiochip, and IRQ data; those objects live for the platform device lifetime. Static SoC tables live for the kernel image lifetime. The generated pin names are allocated with `kasprintf()` in probe and assigned to the pin descriptor array.

Pinmux, bias, output level, Schmitt trigger, slew rate, GPIO direction, IRQ mask/type/enable, and pending IRQ flags are all represented by MMIO registers accessed through regmap. There is no filesystem persistence and no software cache of mux or pinconf state. On SoCs with shadow load registers, the driver writes per-pin changes to shadow PZ registers and then commits a whole bank using `REG_PZ_GID2LD()`. Group configuration is not transactional: if setting a later pin fails, earlier pins remain configured.

One notable state limitation is `jzpc->gc`: it is overwritten for each GPIO bank registered. That works for many pinctrl callback paths only when translating pins relative to the current stored gpiochip is not required across all banks; `PIN_CONFIG_LEVEL` uses `jzpc->gc` to call `pinctrl_gpio_direction_output()`, so multi-bank behavior around that path deserves attention.

## Dependencies and integration points
The driver depends on Linux pinctrl core internals through local headers `core.h`, `pinconf.h`, and `pinmux.h`, generic pinctrl/group/function helpers, generic pinconf device-tree parsing, gpiolib, gpiolib IRQ support, the IRQ core, platform devices, firmware node APIs, OF matching, regmap-mmio, and Kconfig machine symbols such as `CONFIG_MACH_X2000`. Device tree integration uses parent pinctrl compatible strings such as `ingenic,x2000-pinctrl` and child GPIO compatible strings such as `ingenic,x2000-gpio`.

Downstream consumers are normal pinctrl state users in device tree, GPIO descriptor or legacy GPIO users, and interrupt consumers beneath GPIO banks. Function names and group names in the tables form the external ABI for board device trees, so changes must remain compatible with existing DTS files. The driver also integrates with wakeup through `irq_set_irq_wake()` on the parent bank IRQ.

## Risks
The largest risk is table accuracy. A wrong pin number, mode value, per-pin mode array, function/group membership, pull capability bitmap, or compatible-to-chip-info mapping can silently route board signals incorrectly. The version-gating helper `is_soc_or_above()` depends on the set of enabled Kconfig SoCs and the selected runtime version; unusual multi-SoC builds should be tested because branch selection changes register semantics.

Register semantics vary substantially across generations. Incorrectly using set/clear registers, shadow registers, inverted pull-enable bits, or JZ4730 paired fields can corrupt unrelated pins. Both-edge IRQ emulation before X2000 has inherent race windows: input changes between flag read, ACK, and type reprogramming can lose or duplicate an edge. IRQ type handling accepts unknown types by installing `handle_bad_irq` but still calls `irq_set_type()` with the default low-level mapping, so invalid trigger requests should be observed carefully.

The probe path preserves a fixed legacy global GPIO namespace and explicitly warns not to expand it. Any new bank or non-32-pin bank support would risk breaking legacy numbering. `ingenic_pinctrl_probe()` uses plain `kasprintf()` for pin names under a devm-allocated descriptor array; if not freed elsewhere, this is acceptable for init/probe lifetime but not devm-managed. Several functions ignore `regmap_read()` return values, which can hide bus or access-table failures. Group config has no rollback, and `PIN_CONFIG_LEVEL` depends on the single `jzpc->gc` pointer despite per-bank gpiochip registration.

## Test signals
Build coverage should include representative Kconfig combinations for old JZ4740-like, JZ4770-like, X1000/X1600, X1830, X2000, and X2100 paths. Device-tree validation should ensure every compatible has the expected `reg`, IRQ, groups, functions, and pinconf parameters. Runtime smoke tests should inspect `/sys/kernel/debug/pinctrl`, request each advertised function on at least one board per family, toggle GPIO input/output, read back direction, and verify bias get/set on pins with and without pull capability.

IRQ tests should cover edge rising, edge falling, emulated both-edge on pre-X2000, hardware both-edge on X2000+, level high/low, mask/unmask, wake enable, and pending flag ACK. Pinconf tests should cover unsupported Schmitt/slew on older SoCs, invalid pull-up/down on unsupported pins, group config with mismatched get values, and `PIN_CONFIG_LEVEL` on nonzero banks. Hardware validation is especially important for SFC/MMC/LCD/MAC functions because those table entries often use alternate ports and per-pin function arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ingenic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-k210.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-k210.c

## Purpose
This file implements the Kendryte/Canaan K210 FPIOA pin controller driver. The K210 FPIOA is a flexible crossbar where many internal functions can be assigned to any of 48 external IO pins, with per-pin electrical configuration and separate power-domain voltage selection groups. The driver registers built-in pinctrl, pinmux, and pinconf operations for early platform use.

## Important APIs, types, and functions
`struct k210_fpioa` describes the MMIO layout: 48 pin configuration registers plus 8 input tie enable and tie value words covering 256 functions. `struct k210_fpioa_data` stores the device, registered pinctrl device, FPIOA MMIO pointer, sysctl regmap, and sysctl power register offset. The pin array `k210_pins` exposes IO_0 through IO_47, and `k210_group_names` adds one group per pin plus eight zero-pin power-domain groups named A0, A1, A2, B3, B4, B5, C6, and C7.

`enum k210_pinctrl_mode_id`, `k210_pinconf_mode_id_to_mode`, and `struct k210_pcf_info` map every FPIOA function ID from `dt-bindings/pinctrl/k210-fpioa.h` to a default electrical mode. The large `k210_pcf_infos` table covers JTAG, SPI, UART, GPIOHS, GPIO, I2S, I2C, DVP/SCCB, timers, internals, constants, and debug functions. Pinconf uses generic parameters plus custom `output-polarity-invert` and `input-polarity-invert`, represented as `PIN_CONFIG_OUTPUT_INVERT` and `PIN_CONFIG_INPUT_INVERT`. Important functions are `k210_pinmux_set_pin_function()`, `k210_pinconf_set_param()`, `k210_pinconf_group_set()`, `k210_pinctrl_dt_subnode_to_map()`, `k210_fpioa_init_ties()`, and `k210_fpioa_probe()`.

## Control flow
The built-in platform driver matches `canaan,k210-fpioa`. Probe allocates driver data, maps the FPIOA registers, enables the `ref` clock and optional `pclk`, looks up the sysctl power regmap through the `canaan,k210-sysctl-power` phandle with one argument, initializes input ties, and registers the pinctrl descriptor with `pinctrl_register()`.

At registration time the pinctrl core sees 56 groups: the first 48 are single-pin groups and the last 8 are power-domain groups with zero pins. Every function can be mapped to any of the first 48 pin groups; `k210_pinmux_get_function_groups()` reports only the 48 pin groups for muxing. `k210_pinmux_set_mux()` rejects power-domain groups and writes the selected function plus default mode bits into the target pin register through `k210_pinmux_set_pin_function()`.

Device-tree parsing supports two shapes. If a node has a `groups` string list and no strings are counted as an error, it delegates to generic group config parsing, which is mainly useful for the power-domain groups. Otherwise it parses `pinmux` u32 cells, extracts the pin and function with `K210_PG_PIN` and `K210_PG_FUNC`, adds a mux map for each cell, and optionally adds parsed generic pin configs as per-pin config maps. The parent node and each available child node are parsed by `k210_pinctrl_dt_node_to_map()`.

Pinconf set validates pin range, then applies configs sequentially. Bias disable clears pull bits; pull-up or pull-down require nonzero arguments; drive strength accepts mA or microamp forms and selects the strongest hardware level no greater than the requested current; input, output, Schmitt, slew, and polarity bits update the pin register. `PIN_CONFIG_LEVEL` first selects the special constant function, then sets output mode and optionally inverts data output to produce a logical low. Power-source group config writes one bit per zero-pin group to the sysctl power register, selecting 1.8 V when set and 3.3 V when clear.

## State and persistence behavior
Persistent state is the K210 FPIOA register block and the sysctl power register. Each pin register stores the function ID, drive strength, output/input enable and inversion bits, pull-up/down, slew, Schmitt, and raw input state. The driver does not cache pin state in software. `k210_fpioa_init_ties()` writes tie values before tie enables for functions whose default mode is `IN_TIE`, giving unconnected internal inputs a stable value. Power-domain voltage state is written with `regmap_update_bits()` in the sysctl regmap.

All allocations in probe except `pinctrl_register()` are device-managed. The registered pinctrl device pointer is stored in driver data, but the file does not define a remove path because the platform driver is built in. Pinconf operations are sequential and non-transactional; a later invalid parameter leaves earlier register updates in place.

## Dependencies and integration points
The driver depends on Linux pinctrl, pinmux, generic pinconf, pinctrl map utilities, regmap, clk, MMIO accessors, syscon lookup, OF platform matching, and the K210 FPIOA dt-binding header. Board DTS files provide `pinmux` cells using the binding's function IDs and optionally power-domain group config through `groups`. The sysctl integration is required for IO bank voltage selection.

Consumers include K210 serial, SPI, I2C, I2S, camera/DVP, GPIOHS/GPIO, timers, JTAG, and other SoC blocks that route signals through FPIOA. Because the FPIOA is a crossbar, function-to-pin validity is intentionally permissive at the driver level; board and binding correctness determine electrical validity.

## Risks
`K210_PC_BIAS_MASK` is defined as `(K210_PC_PU & K210_PC_PD)`, which evaluates to zero because the pull-up and pull-down bits differ. As a result, bias disable does not clear either pull bit, and drive or function defaults may leave stale bias bits unless later configs explicitly overwrite them. Pull-up and pull-down setters also OR their target bit without clearing the opposite bit, so simultaneous pull-up and pull-down can be represented.

The pinmux path directly indexes `k210_pcf_infos[func]` after extracting the function from device tree. There is no explicit `func >= ARRAY_SIZE(k210_pcf_infos)` check in the DT parser or mux setter, so malformed bindings can index past the table. The `PIN_CONFIG_LEVEL` path changes the pin's function to `CONSTANT`, which is useful but can surprise callers that expected a pure output-level update on the current mux. Group configs reject selectors below 48, so per-pin electrical config should be expressed through `pinmux` entries rather than normal pin groups.

The driver uses raw `readl()` / `writel()` without locking around read-modify-write pinconf operations. Concurrent consumers configuring the same pin can lose updates. The hardware supports many internal/debug/reserved functions; table mistakes in default mode IDs can cause floating inputs, unintended output drivers, or inverted signal polarity.

## Test signals
Compile tests should build the driver with the K210 binding header and check for table/function count mismatches. Device-tree negative tests should use invalid pin numbers, invalid function IDs, power-domain groups in pinmux, and unsupported group configs. Runtime tests should verify muxing representative functions onto arbitrary pins, including GPIOHS, normal GPIO, SPI, I2C, SCCB, DVP, I2S, and UART.

Pinconf tests should read back registers through debugfs or MMIO traces after bias, drive strength in mA and uA, input enable, output enable, Schmitt, slew, output invert, input invert, and `PIN_CONFIG_LEVEL`. Power-source tests should configure all eight domain groups and verify sysctl bits and actual IO voltage selection. Tie initialization can be checked by confirming the expected `tie_val` and `tie_en` bits for `IN_TIE` functions immediately after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-k210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-k230.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-k230.c

## Purpose
This file implements a device-tree-described pinctrl, pinmux, and pinconf driver for the Canaan K230 pin controller. Unlike the K210 driver's static function table, the K230 driver parses functions, groups, pins, mux values, and per-pin configs from child nodes in the board/device tree, then applies mux selection and electrical settings to 64 IO registers.

## Important APIs, types, and functions
The hardware model is 64 pins, each with a 32-bit register at `pin * 4`. Bit definitions include Schmitt trigger (`K230_PC_ST`), drive strength (`K230_PC_DS`), bias pull-down/up (`K230_PC_PD`, `K230_PC_PU`, `K230_PC_BIAS`), output enable, input enable, power source (`K230_PC_MSC`), slew rate, and mux select (`K230_PC_SEL`).

`struct k230_pin_conf` stores one parsed pin's mux function value and generic pinconf array. `struct k230_pin_group` stores a group name, pin array, pin count, and per-pin configuration data. `struct k230_pmx_func` stores a function name, group names, group indexes, and group count. `struct k230_pinctrl` is the driver state: device, pinctrl descriptor/device, regmap, MMIO base, dynamic group/function arrays, and counts.

Core callbacks include group accessors `k230_get_groups_count()`, `k230_get_group_name()`, and `k230_get_group_pins()`, DT mapping via `k230_dt_node_to_map()` / `k230_dt_free_map()`, pinconf get/set via `k230_pinconf_get()`, `k230_pinconf_set_param()`, and `k230_pinconf_set()`, and pinmux operations `k230_get_functions_count()`, `k230_get_fname()`, `k230_get_groups()`, and `k230_set_mux()`. Device tree parsing is implemented by `k230_pinctrl_child_count()`, `k230_pinctrl_parse_dt()`, `k230_pinctrl_parse_functions()`, and `k230_pinctrl_parse_groups()`. Probe and module registration are handled by `k230_pinctrl_probe()` and `module_platform_driver()`.

## Control flow
Probe matches `canaan,k230-pinctrl`, allocates `struct k230_pinctrl`, fills a runtime `pinctrl_desc`, maps the MMIO resource, creates a regmap over the register block, parses device tree, and registers pinctrl with `devm_pinctrl_register()`.

Device tree parsing first counts top-level child nodes as functions and their child nodes as groups. It allocates arrays sized to those counts. Each top-level function node records its name and child group count. Each group child must contain a `pinmux` property; every u32 entry encodes the pin number in the upper bits and the mux function value in the low 8 bits. For each pin entry, `k230_pinctrl_parse_groups()` records the pin number, the mux value, and a parsed copy of the group's generic pinconf configs. The group name is the child node name, and the function name is the parent node name.

When the pinctrl core maps a DT state, `k230_dt_node_to_map()` looks up a function by the config node name. It creates one mux map per group and one per-pin config map for every pin in that group, pointing at the parsed config arrays. When the core selects a function/group, `k230_set_mux()` loops over the group's pins and writes each parsed mux function value into the `K230_PC_SEL` field. It also stores the selected group pointer in `k230_pins[pins[cnt]].drv_data`, which debug display later uses to print the selected group.

Pinconf get reads the pin register and converts the requested generic parameter to a packed argument. Pinconf set validates `pin < K230_NPINS`, reads the pin register, modifies the requested field, and writes the whole register back. Supported parameters are Schmitt trigger, drive strength, bias disable/pull-down/pull-up, output enable, input enable, power source, and slew rate.

## State and persistence behavior
Persistent state is the MMIO register state for all 64 pins. The driver dynamically stores parsed function and group topology in devm-managed arrays for the platform device lifetime. Parsed pinconf arrays are allocated by `pinconf_generic_parse_dt_config()` and referenced directly by pinctrl maps; `k230_dt_free_map()` frees only the map array, not the parsed configs. Debug state for the last selected mux group is stored in the global static `k230_pins[].drv_data` entries.

Mux and pinconf writes are not cached. `k230_set_mux()` updates only the mux select bits and leaves electrical config to the separate config maps generated from the same group node. `k230_pinconf_set_param()` does read-modify-write updates for each requested config, so sequential configs on one pin accumulate. There is no rollback if a later config fails after earlier fields have been written.

## Dependencies and integration points
The file depends on Linux module/platform infrastructure, OF child iteration and property parsing, MMIO resource mapping, regmap-mmio, pinctrl/pinmux/pinconf core APIs, generic pinconf DT parsing, and debugfs sequence output. Device tree is the main integration contract: top-level child names become function names, nested child names become group names, and `pinmux` cells define pin/function pairs. Downstream K230 peripheral nodes reference those function/group names through normal pinctrl states.

## Risks
Several parser choices are fragile. `k230_pinctrl_parse_functions()` declares `idx` and `i` as static locals, so their values persist across calls and across devices. That is harmless only for a single probe with a single pinctrl instance; reprobe or multiple instances can index past the allocated group array. `k230_pinctrl_parse_groups()` does not validate `grp->pins[i] < K230_NPINS`, so malformed `pinmux` values can later index outside `k230_pins` or write beyond the hardware register range. The mux function value is taken from the low 8 bits but the register field is only 3 bits wide, so values above 7 are silently masked by `K230_PC_SEL` during writes.

Bias setters OR pull-up or pull-down bits without clearing the opposite bias bit; requesting pull-up after pull-down can leave both bits set. `PIN_CONFIG_OUTPUT_ENABLE` and `PIN_CONFIG_INPUT_ENABLE` reject an argument of zero, so consumers cannot disable those enables through the generic parameter even though `k230_pinconf_get()` reports them as boolean state. Drive strength accepts any argument and masks it into four bits without range validation or unit conversion, making binding semantics important.

The DT map stores pointers to parsed config arrays owned by group data. That is efficient, but stale pointers would be a risk if parse lifetime ever changed. `k230_pins` is a global static descriptor array, and `drv_data` is mutated at runtime, so multiple controller instances would share debug state. Error handling generally returns the first parse or register failure but has no cleanup beyond devm resources.

## Test signals
Build tests should cover module compilation and warnings for the K230 driver. Device-tree validation should include missing `pinmux`, malformed pin numbers, too-large mux values, functions with zero groups, duplicate group names, and unsupported generic pinconf parameters. Runtime tests should inspect `/sys/kernel/debug/pinctrl` to verify function/group counts, group pins, mux selection, and debug output after changing states.

Hardware tests should select representative peripheral groups, verify the `K230_PC_SEL` field for each pin, and then verify Schmitt, drive, bias, input enable, output enable, power source, and slew-rate fields. Negative pinconf tests should check that output/input disable attempts return `-EINVAL`, unsupported params return `-EINVAL`, and out-of-range pins are rejected. Reprobe or multiple-instance tests would expose the static parser index and global `drv_data` risks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-k230.c -->
