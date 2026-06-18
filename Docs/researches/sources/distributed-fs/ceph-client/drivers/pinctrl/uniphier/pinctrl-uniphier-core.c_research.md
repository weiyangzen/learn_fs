# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-core.c

## Purpose

This file is the shared UniPhier pin controller implementation used by the SoC-specific UniPhier pin table drivers. It translates `struct uniphier_pinctrl_socdata` tables into Linux pinctrl, pinmux, and generic pinconf operations, accesses the controller through a syscon-backed regmap, and saves/restores the pin controller register ranges across system sleep.

## Important APIs, Types, And Functions

The central runtime object is `struct uniphier_pinctrl_priv`, which owns the `pinctrl_desc`, registered `pinctrl_dev`, syscon `regmap`, SoC data pointer, and a sleep-save list of `struct uniphier_pinctrl_reg_region`. Register bases are fixed around pinmux, load-pinmux, drive strength, pull, and input-enable blocks.

Pinctrl group callbacks expose SoC groups from `socdata`; debugfs `uniphier_pctl_pin_dbg_show()` decodes packed per-pin drive and pull metadata. Pinconf helpers handle bias, drive strength, and input enable through `uniphier_conf_get_drvctrl_data()`, `uniphier_conf_pin_bias_get()`, `uniphier_conf_pin_drive_get()`, `uniphier_conf_pin_input_enable_get()`, setters for those attributes, and per-pin/per-group config entry points. Pinmux helpers expose functions/groups and program selections through `uniphier_pmx_set_one_mux()`, `uniphier_pmx_set_mux()`, and `uniphier_pmx_gpio_request_enable()`. `uniphier_pinctrl_probe()` is the exported shared probe used by each SoC driver.

## Control Flow

A SoC-specific platform driver calls `uniphier_pinctrl_probe(pdev, socdata)`. The probe validates that the SoC data has pins, groups, functions, and counts; allocates private data; obtains the parent syscon regmap; fills the pinctrl descriptor; initializes suspend-save metadata; registers the pinctrl device; and stores driver data.

Device-tree pinctrl state parsing is delegated to `pinconf_generic_dt_node_to_map_all()`. Pin config set walks each requested config and dispatches to bias, drive, or input-enable setters. Group config loops over every pin in the group and stops on the first failing pin.

Pinmux selection flows from `uniphier_pmx_set_mux()` to `uniphier_pmx_set_one_mux()` for each pin in the selected group. Each pin is first input-enabled when possible. A negative mux value means a dedicated pin and no pinmux register write. Otherwise the function computes register, shift, width, and stride from SoC capability flags. GPIO request muxing uses the selected GPIO range, calls the SoC `get_gpio_muxval()` callback, and then reuses the one-pin mux setter. The pinmux ops set `.strict = true`.

## State And Persistence

All SoC pin, group, and function descriptions are immutable static data supplied by companion files. Runtime mutable state is the devm-allocated private structure, the pinctrl core state, and hardware registers reached through regmap. Bias, drive, input-enable, GPIO, and mux changes persist as hardware register state until overwritten, reset, or power loss.

With `CONFIG_PM_SLEEP`, `uniphier_pinctrl_pm_init()` scans all pins to find the highest drive, pull, and input-enable register indices described by the SoC data, creates register-region save buffers, and registers late system sleep callbacks. Suspend bulk-reads each range; resume bulk-writes the saved values and reloads pinmux for debug-mux-separate SoCs. There is no on-disk persistence.

## Dependencies And Integration Points

The file integrates with Linux pinctrl, pinmux, pinconf-generic, pinctrl-utils, platform-driver, OF, regmap, syscon, debugfs/seq_file, and device PM infrastructure. It depends on `pinctrl-uniphier.h` for packed per-pin metadata accessors, SoC data structures, capability flags, and group/function macros. SoC files provide `get_gpio_muxval()` policy and OF-compatible platform drivers.

## Risks

The shared code assumes SoC tables are internally consistent: group pin arrays must align with mux value arrays, packed drive/pull/input indices must fit the hardware register layout, and GPIO range IDs must match SoC GPIO numbering. Drive setting rounds down to the greatest supported strength not exceeding the requested value, rejecting only values below the minimum, so callers expecting exact drive strength may observe a lower effective value.

Input-enable handling is capability-sensitive. Without `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`, disabling a single pin is rejected because one bit may be shared by multiple pins; with the capability, the pin number overrides the packed `iectrl` field. Pinmux register calculation also changes with `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE`; mislabeling that flag can write the wrong mux halves or omit the required load strobe. Suspend-save sizing is derived from descriptor indices, so incomplete SoC data can leave registers unrestored.

## Test Signals

Useful signals include successful builds, probe success for each SoC compatible, no missing-socdata or regmap errors, pinctrl state application from DT, debugfs pin metadata matching expected pull/drive classes, GPIO request/mux tests across normal and XIRQ GPIO ranges, bias and drive-strength get/set tests for all drive types, input-enable tests on per-pin and shared-controller SoCs, and suspend/resume tests verifying pinmux, pull, drive, and input-enable restoration.
