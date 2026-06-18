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
