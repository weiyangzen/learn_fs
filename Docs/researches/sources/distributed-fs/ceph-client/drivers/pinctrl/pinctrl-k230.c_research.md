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
