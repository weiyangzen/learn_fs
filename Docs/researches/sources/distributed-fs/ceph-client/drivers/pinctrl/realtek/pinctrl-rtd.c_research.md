# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd.c

## Purpose
This file implements the shared Realtek DHC SoC pinctrl core. SoC-specific Realtek pinctrl drivers provide static pin/group/function/mux/config descriptor tables; this core registers a pinctrl device, handles mux selection and GPIO muxing, applies generic and custom pinconf settings through MMIO regmap updates, and optionally saves/restores configured register ranges across system sleep.

## Important APIs, Types, and Functions
- `struct rtd_pinctrl` is runtime state: device, pinctrl device, MMIO base, pinctrl descriptor, pointer to SoC descriptor, regmap, and optional saved register arrays.
- Custom pinconf parameters are `realtek,drive-strength-p`, `realtek,drive-strength-n`, `realtek,duty-cycle`, and `realtek,high-vil-microvolt`.
- Pinctrl ops: `rtd_pinctrl_get_groups_count()`, `rtd_pinctrl_get_group_name()`, `rtd_pinctrl_get_group_pins()`, and `rtd_pinctrl_dbg_show()`.
- Pinmux ops: `rtd_pinctrl_get_functions_count()`, `rtd_pinctrl_get_function_name()`, `rtd_pinctrl_get_function_groups()`, `rtd_pinctrl_set_mux()`, and `rtd_pinctrl_gpio_request_enable()`.
- Lookup helpers: `rtd_pinctrl_find_mux()`, `rtd_pinctrl_set_one_mux()`, `rtd_pinctrl_get_pin_by_number()`, `rtd_pinctrl_find_config()`, and `rtd_pinctrl_find_sconfig()`.
- Pinconf core: `rtd_pconf_parse_conf()` maps generic/custom pin configs into register offset/mask/value updates; `rtd_pin_config_set()` and `rtd_pin_config_group_set()` apply configs to one pin or a group.
- `rtd_pinctrl_probe()` is exported for SoC-specific drivers and performs MMIO mapping, regmap creation, pinctrl registration, platform drvdata setup, and optional PM save-buffer allocation.
- `realtek_pinctrl_suspend()` and `realtek_pinctrl_resume()` save/restore descriptor-specified register ranges.
- `realtek_pinctrl_pm_ops` is exported for SoC drivers to attach to their platform drivers.

## Control Flow
SoC-specific probe calls `rtd_pinctrl_probe(pdev, desc)`. The core allocates runtime state, maps MMIO resource 0, stores the SoC descriptor, fills a `struct pinctrl_desc` with SoC pins and shared ops, initializes an MMIO regmap, registers pinctrl, stores drvdata, and allocates save buffers if `desc->pin_range` exists.

Pinctrl group/function queries return descriptor data directly. Mux setting gets the selected function name, fetches group pins, and calls `rtd_pinctrl_set_one_mux()` for each pin. That helper finds the pin mux descriptor, scans its function table for the requested name, and applies the function's mux value with `regmap_update_bits()`. GPIO request enable is implemented by selecting the `gpio` function for the requested pin.

Pinconf setting flows through `rtd_pconf_parse_conf()`. For each config it finds the pin's electrical config descriptor, computes absolute bit positions from `base_bit` plus feature-specific offsets, handles special cases where offsets cross a 32-bit register boundary, then updates the regmap. It supports Schmitt input, push-pull/bias disable, pull-up/down, drive strength, power source, slew rate, input voltage, high VIL, P/N drive strength, and duty cycle. Group config applies the same configs to each pin in the selected group.

Suspend iterates descriptor-provided register ranges, reading every 32-bit entry into `saved_regs`. Resume writes the saved values back in the same order.

## State and Persistence
Runtime state is in `struct rtd_pinctrl`; static hardware description remains in SoC descriptors from the header. Register state is persistent in hardware until changed. If `pin_range` is supplied, suspend/resume preserve selected pinctrl register ranges in `saved_regs`; otherwise suspend/resume are no-ops. The driver does not cache arbitrary pinconf state beyond optional saved registers.

## Dependencies and Integration Points
The core depends on Linux pinctrl, pinmux, generic pinconf, regmap MMIO, platform resources, OF, and descriptor definitions from `pinctrl-rtd.h`. It is exported to SoC files in the same Realtek family. Device tree pinctrl states are parsed by `pinconf_generic_dt_node_to_map_all`, so DT nodes can combine mux and pinconf properties. GPIO integration is through pinctrl's `gpio_request_enable`, not through a gpiochip in this core.

## Risks and Edge Cases
- `rtd_pconf_parse_conf()` sets `set_val` for slew rate but computes `val = arg << sr_off` instead of `set_val << sr_off`; this appears to write literal 10/20/30 into a 2-bit field and should be reviewed.
- `RTD_HIGH_VIL` computes `val = 1` rather than `BIT(hvil_off)`, so nonzero `hvil_off` likely writes the wrong bit.
- `RTD_DUTY_CYCLE` uses `config_desc->reg_offset` instead of `sconfig_desc->reg_offset`, unlike P/N drive strength; this may target the wrong register for special configs.
- `rtd_pinctrl_find_config()` indexes `configs[pin]` directly, assuming config arrays are indexed by pin number and large enough.
- `rtd_pinctrl_find_mux()` indexes `muxes[pin]` directly, with the same descriptor-size assumption.
- `rtd_pin_config_get()` returns `-ENOTSUPP` for all params, so readback of applied pinconf is not supported.
- The core has no gpiochip; GPIO electrical or mux requests rely on other Realtek GPIO support plus pinctrl muxing.

## Test Signals
Build tests should cover the exported symbols and each SoC descriptor driver. Runtime tests should apply representative DT pinctrl states for muxing, pull-up/down, Schmitt, drive strength, voltage, slew, high-VIL, P/N drive, and duty cycle, then verify register bits. Suspend/resume tests should confirm descriptor ranges are restored. Static analysis should focus on descriptor index bounds and the bit-value concerns noted above.
