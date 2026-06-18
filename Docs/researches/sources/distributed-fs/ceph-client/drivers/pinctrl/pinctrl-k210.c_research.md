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
