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
