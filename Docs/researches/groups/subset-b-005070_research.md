# Research: subset-b-005070

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-eyeq5.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-eyeq5.c

## Purpose

This file implements the Mobileye EyeQ5/EyeQ6L pin controller as an auxiliary-bus driver. It exposes SoC pins, one-pin pinctrl groups, mux functions, GPIO fallback muxing, and generic pin configuration for pull-up, pull-down, bias-disable, and two-bit drive-strength fields. The hardware registers live in the parent OLB syscon area, but this driver receives the mapped base address through auxiliary device platform data rather than mapping resources itself.

The driver models a simple mux scheme: every pin can be either GPIO or exactly one pin-specific alternate function. Groups are deliberately 1:1 with pins, and group selectors equal pin numbers.

## Important APIs, Types, and Data

- `enum eq5p_regs` names the per-bank register slots: pull-down, pull-up, drive-strength low/high, and mux IOCR.
- `struct eq5p_bank` maps a bank to its pin count and register offsets.
- `struct eq5p_match_data` is the per-compatible static descriptor: pin array, function array, bank array, and counts.
- `struct eq5p_pinctrl` stores the live `pinctrl_desc`, OLB base pointer, and selected match data.
- `eq5p_eyeq5_pins`, `eq5p_eyeq5_functions`, and `eq5p_eyeq5_banks` describe 52 pins split across bank A and B.
- `eq5p_eyeq6lplus_pins`, `eq5p_eyeq6lplus_functions`, and `eq5p_eyeq6lplus_banks` describe 32 pins in one bank.
- `eq5p_match_table` binds `"mobileye,eyeq5-olb"` and `"mobileye,eyeq6lplus-olb"` to the correct static data.
- `eq5p_id_table` binds the auxiliary child name `"clk_eyeq.pinctrl"`.

The driver implements standard pinctrl callbacks through:

- `eq5p_pinctrl_ops`: group enumeration, single-pin group lookup, debug show, and `pinconf_generic_dt_node_to_map_pin`.
- `eq5p_pinmux_ops`: function enumeration, function-to-group lookup, `set_mux`, GPIO request enable, and `strict = true`.
- `eq5p_pinconf_ops`: generic pin config get/set and group get/set aliases because groups are pins.

## Control Flow

Probe starts in `eq5p_probe()`. It uses `of_match_node()` against the device node inherited from the parent OLB/clock driver, allocates `struct eq5p_pinctrl`, obtains the already-mapped base with `dev_get_platdata()`, fills `pinctrl_desc`, then calls `devm_pinctrl_register_and_init()` followed by `pinctrl_enable()`.

Pinctrl group callbacks return `data->npins`, pin names from the descriptor, and a pointer to each descriptor's pin number. Since groups and pins are identical, no dynamic group allocation is needed.

Pin muxing is handled by `eq5p_pinmux_set_mux()`. It converts the group selector/pin number to a bank plus local offset with `eq5p_pin_to_bank_offset()`, then writes one IOCR bit: `0` selects GPIO and `1` selects the alternate function. `eq5p_pinmux_gpio_request_enable()` routes GPIO requests through the same path with the fixed GPIO function selector.

Pin configuration starts by resolving the pin to a bank and offset. `eq5p_pinconf_get()` reads pull-up/pull-down bits and, for drive strength, selects `EQ5P_DS_LOW` or `EQ5P_DS_HIGH` after multiplying the local offset by two. `eq5p_pinconf_set()` applies a list of packed generic configs. Bias-disable clears both pull bits, pull-down sets PD and clears PU, pull-up clears PD and sets PU, and drive-strength delegates to `eq5p_pinconf_set_drive_strength()`.

Debug display reconstructs the active function by reading IOCR and scanning the non-GPIO function group lists for the pin name. It then prints function, bias, and drive strength.

## State and Persistence Behavior

Runtime state is mostly hardware register state plus immutable static descriptor tables. The only allocated software state is device-managed `struct eq5p_pinctrl`. Register changes are persistent until hardware reset or later pinctrl consumers reconfigure the same pins. There is no suspend/resume restore path in this file, so low-power behavior depends on the broader OLB/syscon and pinctrl core interactions.

`eq5p_update_bits()` performs unlocked read-modify-write cycles against shared OLB registers. The driver assumes these registers are not concurrently modified by another OLB user or that external serialization is sufficient.

## Dependencies and Integration Points

- Linux pinctrl, pinmux, and generic pinconf frameworks.
- Auxiliary bus registration through `module_auxiliary_driver()`.
- Parent Mobileye OLB/clock driver, which must provide the OF node and mapped base pointer.
- Device tree pinctrl bindings must use pin names/groups matching static descriptors and generic pinconf properties supported by `pinconf_generic_dt_node_to_map_pin`.
- GPIO integration uses `gpio_request_enable` and strict pinmux exclusion, but GPIO ranges are expected to be registered elsewhere.

## Risks and Edge Cases

- `eq5p_pinconf_set()` ignores the return value from `eq5p_pinconf_set_drive_strength()`. An invalid drive-strength argument logs an error in the helper but `eq5p_pinconf_set()` still continues and can return success if no later config fails.
- Register updates are plain read-modify-write without a lock or regmap update helper, so concurrent writers to the same OLB words could lose changes.
- The debug path assumes pin names are unique and group lists cover every alternate-function pin. A static table mismatch would show `unknown`.
- `eq5p_test_bit()` only warns for offsets greater than 31, which is valid for this hardware because banks are at most 32 pins; future bank definitions larger than 32 would be unsafe.
- Pull-up and pull-down are modeled as mutually exclusive during set, but get/debug can report both if boot firmware or another writer set both bits.
- The base pointer comes from platform data and is cast to `void __iomem *`; probe does not independently validate it.

## Test Signals

- Boot/probe logs should not show `failed registering pinctrl device` or `failed enabling pinctrl device`.
- Device tree states for EyeQ5/EyeQ6L should select expected functions and groups without `Unsupported pinconf` or invalid drive-strength errors.
- GPIO consumers should force IOCR bits low through `gpio_request_enable`.
- Debugfs pinctrl output should show expected `function=`, `bias=`, and `drive_strength=` values after applying test states.
- Hardware or register-level tests should verify DS low/high split around local pin offset 16 and bank B offset translation on EyeQ5.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-eyeq5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-falcon.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-falcon.c

## Purpose

This file implements pinctrl and pin configuration support for Lantiq Falcon SoCs. It uses the shared Lantiq pinctrl framework from `pinctrl-lantiq.h` for most generic mux/group/function handling, while this file supplies Falcon-specific pad register offsets, MFP tables, groups, functions, pinconf operations, pad-bank discovery, and mux application.

The hardware is arranged as up to five banks/ports of 32 pins. Each bank has mux registers per pin plus pull-up, pull-down, slew-rate, drive-current, and availability registers.

## Important APIs, Types, and Data

- Register macros include `LTQ_PADC_MUX(x)`, `LTQ_PADC_PUEN`, `LTQ_PADC_PDEN`, `LTQ_PADC_SRC`, `LTQ_PADC_DCC`, and `LTQ_PADC_AVAIL`.
- `PORTS`, `PINS`, `PORT(x)`, and `PORT_PIN(x)` map global GPIO numbers to pad bank and in-bank bit positions.
- `enum falcon_mux` defines Falcon mux function IDs, including GPIO, reset, NTR/PPS, MDIO, LED, SPI, ASC, I2C, HOSTIF/JTAG, SLIC/PCM, MII, PHY, and `NONE`.
- `falcon_pads` and `pad_count` are static arrays populated at probe from hardware availability registers.
- `falcon_mfp` lists each mux-capable pin and its function choices using `MFP_FALCON`.
- `falcon_grps` declares named pin groups such as `por`, `mdio`, `bootled`, `asc0`, `spi`, `i2c`, `jtag`, `slic`, `pcm`, and `asc1`.
- `falcon_funcs` maps external pinmux function names to group lists.
- `falcon_cfg_params` maps device-tree properties `lantiq,pull`, `lantiq,drive-current`, and `lantiq,slew-rate` to Lantiq pinconf parameters.
- Exported helpers `pinctrl_falcon_get_range_size()` and `pinctrl_falcon_add_gpio_range()` support Falcon GPIO drivers.

## Control Flow

The platform driver is registered through `core_initcall_sync(pinctrl_falcon_init)`, so it initializes early. `pinctrl_falcon_probe()` scans all enabled device-tree nodes compatible with `"lantiq,pad-falcon"`. For each valid bank, it reads `lantiq,bank`, translates the MMIO resource, gets the bank clock from that pad platform device, maps the pad registers, reads `LTQ_PADC_AVAIL`, computes the number of pins with `fls(avail)`, loads pin descriptors named `ioN`, enables the clock, and accumulates the total pin count.

After bank discovery, probe fills `falcon_pctrl_desc.name` and `.npins`, attaches Falcon MFP/group/function arrays to `falcon_info`, then calls `ltq_pinctrl_register()`. The shared Lantiq core consumes `falcon_info`, including `apply_mux`, params, groups, and functions.

Mux writes are performed by `falcon_mux_apply()`, which validates the bank and writes the selected mux value to the pin-specific mux register. Pin configuration callbacks read and write per-port bit registers. `falcon_pinconf_get()` returns drive-current, slew-rate, or pull state. `falcon_pinconf_set()` selects the target register and writes the pin bit.

Debug output prints port, raw mux register value, pull, drive-current, slew-rate, and optional GPIO owner.

## State and Persistence Behavior

Driver state is primarily static global `falcon_info`, `falcon_pads`, and `pad_count`, plus MMIO mappings and clocks discovered at probe. Pin descriptors allocate names with `kasprintf()` in `lantiq_load_pin_desc()` and are not explicitly freed, which is acceptable for a non-removable early SoC driver but would matter for hot-unplug style reuse.

Pad configuration is persistent in hardware registers until reset or later reconfiguration. There is no removal path, clock disable path, suspend/resume replay, or explicit locking around pad register read/write operations in this file.

## Dependencies and Integration Points

- Shared Lantiq pinctrl infrastructure in `pinctrl-lantiq.h`, especially `struct ltq_pinmux_info`, `ltq_pinctrl_register()`, MFP parsing, and Lantiq pinconf packing.
- Lantiq SoC low-level register helpers from `<lantiq_soc.h>`.
- Device tree nodes compatible with `"lantiq,pinctrl-falcon"` and child/peer pad nodes compatible with `"lantiq,pad-falcon"` carrying `lantiq,bank`.
- GPIO drivers use `pinctrl_falcon_get_range_size()` and `pinctrl_falcon_add_gpio_range()` to integrate GPIO ranges with the pinctrl device.
- Clock framework is used for each pad bank clock.

## Risks and Edge Cases

- Probe uses the big-endian `lantiq,bank` property value directly as `*bank` without an explicit `be32_to_cpup()`. This may be intentional for this tree's conventions, but it is a notable endian-sensitive pattern.
- `falcon_pinconf_set()` writes only `BIT(PORT_PIN(pin))` to the selected config register. For pull configuration, switching pull direction does not explicitly clear the opposite pull register, and an argument other than `1` selects pull-up.
- `falcon_pinconf_set()` verifies the bit became set, but it cannot express disabling drive-current, slew-rate, or pull with the current write-only pattern.
- Group pinconf get/set return `-ENOTSUPP`; group-level pinconf requests in device tree will fail.
- Static globals make this driver effectively single-instance.
- `lantiq_load_pin_desc()` allocates pin names without checking allocation failure.
- Bank clocks are enabled but not disabled on later failures or module unload; this matches early SoC-driver style but is a resource-management limitation.

## Test Signals

- Probe should log discovered pad banks and total pad count; absence of banks means no useful pinctrl registration.
- Device-tree mux states for ASC, SPI, I2C, MDIO, reset, LED, SLIC, PCM, and JTAG should result in expected `LTQ_PADC_MUX()` values.
- Pinconf reads after applying `lantiq,pull`, `lantiq,drive-current`, and `lantiq,slew-rate` should report expected packed values.
- GPIO range size should match `fls(LTQ_PADC_AVAIL)` for each bank.
- Debugfs pinconf output should show the correct port, mux value, pull, drive-current, slew-rate, and GPIO owner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-falcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-gemini.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-gemini.c

## Purpose

This file implements the Cortina/StorLink Gemini pin controller as a group-only pinctrl driver for 3512 and 3516 chip variants. It exposes large static pin tables, SoC-specific pin groups, mux functions, group drive-strength control, and per-pin Ethernet skew-delay controls. Most muxing is controlled through a global miscellaneous syscon register whose bits can have irreversible hardware semantics.

The driver is intentionally group-centric: consumers select named groups such as `idegrp`, `pcigrp`, `gmii_gmac0_grp`, `pflashgrp`, or GPIO subgroups rather than arbitrary individual pins.

## Important APIs, Types, and Data

- `struct gemini_pmx` stores the device, registered pinctrl device, parent syscon regmap, detected SoC variant flags, flash-pin state, and selected skew-delay config table.
- `struct gemini_pin_group` names a group, its pin array, mux clear/set masks for `GLOBAL_MISC_CTRL`, and optional `GLOBAL_IODRIVE` drive-strength mask.
- `struct gemini_pin_conf` maps one Ethernet pin to a skew-delay register and bitfield mask.
- Global registers include `GLOBAL_WORD_ID`, `GLOBAL_STATUS`, `GLOBAL_IODRIVE`, `GLOBAL_GMAC_CTRL_SKEW`, `GLOBAL_GMAC0_DATA_SKEW`, `GLOBAL_GMAC1_DATA_SKEW`, and `GLOBAL_MISC_CTRL`.
- `gemini_3512_pins` and `gemini_3516_pins` are package pin maps for the two supported chip IDs.
- `gemini_3512_pin_groups` and `gemini_3516_pin_groups` define fixed and muxable groups for DRAM, RTC, power, CIR on 3516, system, voltage control, ICE, IDE, SATA, USB, GMII, PCI, LPC, LCD, SSP, UART, TVC, flash, and GPIO banks.
- `gemini_pmx_functions` maps public pinmux function names to group-name lists.
- `gemini_confs_3512` and `gemini_confs_3516` enumerate the GMAC pins that accept `PIN_CONFIG_SKEW_DELAY`.

## Control Flow

Initialization happens at `arch_initcall(gemini_pmx_init)`, registering a platform driver for `"cortina,gemini-pinctrl"`. `gemini_pmx_probe()` allocates `struct gemini_pmx`, obtains the parent syscon regmap, reads `GLOBAL_WORD_ID`, and selects the 3512 or 3516 static pin table and skew config table. It logs the boot `GLOBAL_MISC_CTRL` state, reads `GLOBAL_STATUS_FLPIN` to decide whether the parallel-flash group should expose extended pins, and registers the pinctrl descriptor with `devm_pinctrl_register()`.

Group callbacks choose the correct SoC group array based on `is_3512` or `is_3516`. `gemini_get_group_pins()` has a special case: if the flash pin is set and the selected group is `pflashgrp`, it returns the extended parallel-flash pin array for the active SoC.

Muxing is performed by `gemini_pmx_set_mux()`. It selects the function and group, reads `GLOBAL_MISC_CTRL`, applies `regmap_update_bits()` using `grp->mask | grp->value`, reads back the register, computes the expected state, and logs any bit that did not transition as requested. The code separates bits to clear from bits to set, and prints human-readable pad group names for changed bits.

Pin config supports `PIN_CONFIG_SKEW_DELAY` on a fixed list of GMAC control/data pins. `gemini_pinconf_get()` reads the relevant bitfield and returns a 0-15 delay value. `gemini_pinconf_set()` validates the value, shifts it into the field, and updates the matching skew register.

Group config supports `PIN_CONFIG_DRIVE_STRENGTH` only for groups with a nonzero `driving_mask`. Accepted strengths are 4, 8, 12, and 16 mA, encoded as 0-3 in `GLOBAL_IODRIVE`.

## State and Persistence Behavior

The mutable software state is the device-managed `struct gemini_pmx`, including variant selection and `flash_pin`. Pin tables, group arrays, function arrays, and pin config arrays are immutable static data.

Hardware state is stored in parent syscon registers. `GLOBAL_MISC_CTRL` is especially important because the comments document one-way behavior: some `*_ENABLE` bits cannot be re-enabled after being disabled, and some `*_DISABLE` bits cannot be disabled again after enabling a flash configuration. This means an incorrect mux request can have persistent effects until a hardware reset and may not be reversible by a later pinctrl state.

There is no suspend/resume replay logic. Regmap provides update serialization at the register access layer, but semantic conflicts between consumers are managed only by pinctrl state selection and static group masks/values.

## Dependencies and Integration Points

- Parent syscon/MFD node must expose the Gemini global registers via `syscon_node_to_regmap(parent->of_node)`.
- Linux pinctrl, pinmux, and generic pinconf frameworks.
- Device tree consumers use generic pinctrl maps through `pinconf_generic_dt_node_to_map_all`.
- Ethernet MAC/PHY board tuning can use per-pin `skew-delay` on the enumerated GMAC pins.
- Storage, PCI, display, UART, SSP, TVC, and GPIO consumers depend on the group/function names in `gemini_pmx_functions` and the SoC-specific group tables.
- The global flash-pin strap from `GLOBAL_STATUS_FLPIN` changes the pin list exposed for `pflashgrp`.

## Risks and Edge Cases

- `gemini_pmx_set_mux()` logs hardware transition failures but always returns `0`, so consumers may believe an irreversible or blocked mux operation succeeded.
- `expected = before &= ~grp->mask;` mutates `before` after it was already masked for logging, so the later error log's `before` value is not the original masked boot value. The expected calculation still matches the intended clear/set operation, but the diagnostic field is misleading.
- `for_each_set_bit(i, &tmp, PADS_MAXBIT)` uses `PADS_MAXBIT` as the bit-count limit, which excludes bit 27 despite `PADS_MAXBIT` being defined as 27. This can skip reporting GMAC1 bit 27 transitions.
- The function table has `.name = "dram"` but `.num_groups = ARRAY_SIZE(idegrps)`. Both arrays currently have one element, so behavior is unchanged, but the initializer is semantically wrong and fragile.
- `pflashgrps` includes `"pflashextgrp"`, but neither the 3512 nor 3516 group tables define a group with that name. The extended flash behavior is instead implemented by returning extended pins for `pflashgrp` when `flash_pin` is set. A device tree reference to `pflashextgrp` may fail group lookup.
- Many mux bits have one-way semantics. Test code and board files must avoid probing incompatible states in arbitrary order.
- Only selected GMAC pins support `PIN_CONFIG_SKEW_DELAY`; other pins correctly return `-ENOTSUPP`.
- Group drive strength is only available for IDE, GMAC0, GMAC1, and PCI groups with `driving_mask`; other group requests fail with `-EINVAL`.

## Test Signals

- Probe should detect chip ID `0x3512` or `0x3516`, log initial `GLOBAL_MISC_CTRL`, report flash-pin state, and register the pinctrl driver.
- Device-tree pinmux states for each major peripheral group should produce expected `GLOBAL_MISC_CTRL` changes and no hardware-limitation error logs.
- Tests should cover 3512 and 3516 group enumeration because the pin numbers differ substantially.
- When `GLOBAL_STATUS_FLPIN` is set, `pflashgrp` should expose the extended pin array; when clear, it should expose the normal array.
- Ethernet skew-delay set/get should round-trip values 0 through 15 on each listed GMAC pin and reject values above 15.
- Group drive-strength tests should accept 4/8/12/16 mA on supported groups and reject unsupported strengths or unsupported groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-gemini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-generic.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-generic.c

## Purpose

This file provides a helper for pinctrl drivers that do not predefine pin groups and functions in C. It parses device-tree pin nodes that provide numeric `pins` and a `function`, dynamically creates generic pin groups and pinmux functions, and adds pinmux plus optional pinconf mappings for the pinctrl core.

The exported API is `pinctrl_generic_pins_function_dt_node_to_map()`.

## Important APIs, Types, and Data

- `pinctrl_generic_pins_function_dt_subnode_to_map()` handles one DT node containing a `pins` array and `function` string.
- `pinctrl_generic_pins_function_dt_node_to_map()` handles either a single pins node or a parent node with multiple child pins nodes.
- It uses `pinctrl_utils_reserve_map()`, `pinctrl_utils_add_map_mux()`, and `pinctrl_utils_add_map_configs()` to build `struct pinctrl_map` entries.
- It uses `pinctrl_generic_add_group()` to create groups and `pinmux_generic_add_function()` to create functions.
- It uses `pinconf_generic_parse_dt_config()` to parse generic pin configuration properties.

## Control Flow

The top-level function initializes `*maps = NULL` and `*num_maps = 0`. If the node itself has a `pins` property, it allocates a one-entry `group_names` array, parses the node as a single group, then adds one generic function named after the node.

If the node lacks `pins`, it is treated as a parent. The function first counts available children, allocates `group_names` for that count, then iterates children with `for_each_available_child_of_node_scoped()`. Each child is parsed into a group and map entries, and the group name is appended. Finally, one generic function named after the parent is registered with all collected groups.

The subnode parser validates that `pins` contains at least one u32, builds a group name from `parent.child`, allocates arrays for pin numbers and per-pin function pointers, reads each pin index, reads the node's `function` string, reserves and adds one mux map, registers the group with the pins and function array, parses optional pin configs, and adds a group config map if any configs exist.

On errors after maps have been allocated, the top-level function frees the map array with `pinctrl_utils_free_map()` before returning `dev_err_probe()`.

## State and Persistence Behavior

The helper creates persistent generic groups and functions inside the pinctrl device's generic pinctrl/pinmux data structures. Allocations for group names, pin arrays, function arrays, and parent group-name arrays are device-managed through `devm_*`, while parsed pinconf configs are freed after being copied into pinctrl maps.

There is no hardware state in this file. Hardware effects occur later when the pinctrl core applies the maps through the consuming driver's pinmux and pinconf operations.

## Dependencies and Integration Points

- Device tree nodes must provide `pins` as u32 pin numbers and `function` as a string.
- Drivers using this helper must use generic pinctrl/pinmux infrastructure capable of storing dynamically added groups and functions.
- Generic pinconf properties are parsed by `pinconf_generic_parse_dt_config()`.
- The helper is exported with `EXPORT_SYMBOL_GPL`, so GPL-compatible pinctrl drivers can use it as their `.dt_node_to_map` implementation.

## Risks and Edge Cases

- `reserve` is always `1`, and the helper calls `pinctrl_utils_reserve_map()` separately for mux and config maps. That is correct but relies on the utility growing the map array incrementally.
- The same `function` string is read once per pin into every slot of the `functions` array. This matches the generic group API shape but does not support per-pin alternate function strings inside one group.
- If a parent node has no available children, the function adds a generic function with zero groups. That may be accepted by the generic pinmux core but is likely not useful.
- The single-node path names the group as `np.np` because parent and child arguments are the same node in the helper call. That is intentional from current formatting but can surprise binding authors inspecting debug output.
- The helper expects numeric pin IDs rather than named pins, so it depends on stable pin numbering in the consuming driver.

## Test Signals

- DT states with one node containing `pins` and `function` should create one mux map and optional group config map.
- DT states with a parent and multiple available children should create one generic function named after the parent and one group per child.
- Invalid or missing `pins` should log `invalid pinctrl group` and fail.
- Missing `function`, malformed `pins`, or unsupported pinconf properties should return errors and free any already allocated maps.
- Drivers using the helper should show dynamically added group/function names in pinctrl debugfs and should apply configs through their own pinconf ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-generic.c -->
