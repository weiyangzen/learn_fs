# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g5.c

## Purpose

`pinctrl-aspeed-g5.c` is the AST2500, or Aspeed generation 5, SoC-specific pin controller description. It extends the same shared Aspeed pinctrl architecture used by AST2400 with AST2500 package balls, alternate functions, pin groups, pinconf ranges, and generation-specific register handling. It binds device-tree compatible `aspeed,ast2500-pinctrl` and legacy `aspeed,g5-pinctrl`.

The file is primarily a generated-style hardware table, but it has more runtime logic than the G4 file. AST2500 pin expressions can reference not only the SCU regmap but also external GFX and LPC syscon regmaps, so the file implements lazy external regmap acquisition and a custom expression evaluator. It also carries an AST2500 strap-write quirk where setting bits in `HW_STRAP1` requires clearing through `HW_REVISION_ID`.

## Important APIs, Types, And Data

- Register offset macros mirror AST2500 datasheet names: `SCU2C`, `SCU3C`, `SCU48`, `HW_STRAP1`, `HW_REVISION_ID`, `SCU80`, `SCU84`, `SCU88`, `SCU8C`, `SCU90`, `SCU94`, `SCUA0`, `SCUA4`, `SCUA8`, `SCUAC`, and `HW_STRAP2`.
- `ASPEED_G5_NR_PINS` is 236, covering GPIO banks through GPIOAC plus non-GPIO USB pins and reserved numbering holes.
- `COND1` and `COND2` are reusable SCU condition descriptors. Many AST2500 alternate functions are gated by SCU90 bit 6 or SCU94 bits 1:0 in addition to their per-pin enable bits.
- `LHCR0` is an LPC Host Control Register offset used through `ASPEED_IP_LPC`. `GFX064` is a graphics block register offset used through `ASPEED_IP_GFX`.
- `SIG_EXPR_DECL_SINGLE()`, `SIG_EXPR_LIST_DECL_SINGLE`, and `SIG_EXPR_LIST_DECL_DUAL` wrap shared expression macros and generate signal descriptors tagged with signal and function names.
- Pin declaration macros create `struct aspeed_pin_desc` data for each package ball. Function and group declaration macros create the symbols later referenced by `aspeed_g5_groups[]` and `aspeed_g5_functions[]`.
- `aspeed_g5_pins[]` is the Linux pin descriptor array. Probe sets the runtime pin number for each element before registration.
- `aspeed_g5_groups[]` and `aspeed_g5_functions[]` expose the AST2500 function/group ABI to Linux pinctrl and device tree.
- `aspeed_g5_configs[]` maps generic pinconf parameters to AST2500 SCU bit ranges. It covers bank pull-down/disable controls, RGMII drive-strength bits, RGMII receive/transmit pull-downs, ADC pull-downs, and D/E passthrough debounce enable bits.
- `aspeed_g5_pin_config_map[]` maps generic arguments to hardware values, matching G4: pull-down enabled/disabled, bias disabled, and 8 mA or 16 mA drive strength.
- `aspeed_g5_ops` provides both `.eval = aspeed_g5_sig_expr_eval` and `.set = aspeed_g5_sig_expr_set` because AST2500 expressions can reference external IP blocks.
- `aspeed_g5_pinctrl_data`, `aspeed_g5_pinmux_ops`, `aspeed_g5_pinctrl_ops`, `aspeed_g5_conf_ops`, and `aspeed_g5_pinctrl_desc` connect these tables to the shared Aspeed implementation and Linux pinctrl core.
- `aspeed_g5_pinctrl_driver` is registered from `arch_initcall(aspeed_g5_pinctrl_init)`.

## Functional Coverage

The AST2500 pin tables cover the major SoC multiplexing domains:

- GPIO banks A through AC, including holes where some GPIO ranges are not exposed as normal pins.
- Basic platform signals such as MAC link indicators, `USBCKI`, LPC power and reset signals, `OSCCLK`, `PEWAKE`, watchdog resets, and BMC interrupt lines.
- SD and I2C: `SD1`, `SD2`, I2C buses 3 through 14, plus `SCL1/SDA1` and `SCL2/SDA2` on GPIOY4-Y7.
- MDIO, RGMII, and RMII Ethernet modes, with RMII/RGMII strap descriptors and extra RMII clock output descriptors through `SCU48`.
- UART/modem-style pins and grouped `UART6`.
- GPIO D/E passthrough groups for host front-panel loopback use.
- LPC host-controller and LPC+ modes through `LPCHC` and `LPCPLUS`, including descriptors in the external LPC regmap.
- eSPI and LPC LAD fallback signals on GPIOAC pins, gated by `HW_STRAP1[25]` or `SCUAC` bits.
- SPI and flash functions: `SPI1`, `SPI1DEBUG`, `SPI1PASSTHRU`, `SPI1CS1`, `SPI2*`, firmware SPI chip selects, and parallel NOR `PNOR`.
- SGPIO master/slave functions `SGPM`, `SGPS1`, and `SGPS2`, plus SALT signals 1 through 14.
- Video input `VPI24` and video output `VPO`, including graphics-block CRT/DVO enable and edge-mode descriptors.
- VGA/DDC pins, VGA BIOS ROM, DASH alternate pins, PWM 0 through 7, ADC 0 through 15, and USB modes `USB2AH`, `USB2AD`, `USB11BHID`, `USB2BD`, and `USB2BH`.

## Control Flow

Initialization:

1. `arch_initcall(aspeed_g5_pinctrl_init)` registers the platform driver.
2. A platform device matches `aspeed,ast2500-pinctrl` or the legacy compatible.
3. `aspeed_g5_pinctrl_probe()` assigns each `aspeed_g5_pins[i].number = i`.
4. It stores `&pdev->dev` in `aspeed_g5_pinctrl_data.pinmux.dev`. This is required by the G5 regmap acquisition and error logging paths.
5. It calls the shared `aspeed_pinctrl_probe()`, which acquires the parent SCU syscon regmap, stores it in `pinmux.maps[ASPEED_IP_SCU]`, registers the pinctrl device, and attaches driver data.

Mux selection uses the same shared control flow as G4:

1. `aspeed_pinmux_set_mux()` receives a function and group selector from Linux pinctrl.
2. For every pin in the selected group, it walks priority levels in the pin descriptor.
3. It disables expressions for higher-priority signal levels until it reaches an expression tagged with the requested function name.
4. It enables the matching expression.
5. On AST2500, expression evaluation and writes use `aspeed_g5_sig_expr_eval()` and `aspeed_g5_sig_expr_set()` so descriptors can touch SCU, GFX, or LPC regmaps.

GPIO request flow is shared through `aspeed_gpio_request_enable()`. It disables higher-priority functions and then enables or exposes the pin-specific GPIO expression, while avoiding confusion with passthrough functions whose names begin with `GPI` but whose signal and function names differ.

Pin configuration flow is also shared. The AST2500 file supplies config descriptors; `aspeed_pin_config_set()` and related functions find applicable ranges and call `regmap_update_bits()` on the SCU regmap.

## External Regmap Acquisition

`aspeed_g5_acquire_regmap()` is the key addition over G4:

- For `ASPEED_IP_SCU`, it warns if the SCU map is missing and returns the already-populated SCU map.
- It rejects out-of-range IP indexes with `-EINVAL`.
- If a map is already cached in `ctx->maps[ip]`, it returns it.
- For `ASPEED_IP_GFX`, it parses `aspeed,external-nodes` phandle index 0 from the pinctrl node, converts that node to a syscon regmap with `syscon_node_to_regmap()`, caches it in `ctx->maps[ASPEED_IP_GFX]`, and logs a debug message.
- For `ASPEED_IP_LPC`, it parses `aspeed,external-nodes` phandle index 1. It requires the phandle's parent to be compatible with `aspeed,ast2500-lpc-v2`, then converts the parent to a syscon regmap, caches it in `ctx->maps[ASPEED_IP_LPC]`, and logs a debug message.
- Missing phandles return `-ENODEV`; syscon conversion errors are propagated.

The lazy design means boards that never request GFX- or LPC-backed pin functions do not need those maps at probe time, but any pinctrl state that evaluates or sets those descriptors must have correct external-node references.

## AST2500 Expression Evaluation And Setting

`aspeed_g5_sig_expr_eval()` loops over an expression's descriptors and calls `aspeed_g5_acquire_regmap()` for each descriptor's IP block. It then calls `aspeed_sig_desc_eval()` on the acquired map. Any descriptor that evaluates false causes the whole expression to return false; errors propagate.

`aspeed_g5_sig_expr_set()` mirrors the G4 setter with AST2500 additions:

- It computes the shifted write value for each descriptor from `enable` or `disable`.
- It acquires the descriptor's regmap, returning a logged error if acquisition fails.
- It skips most `HW_STRAP1` descriptors and all `HW_STRAP2` descriptors, treating strap configuration as hardware or early-firmware state.
- It allows the same documented exceptions as G4: GPID/GPIE passthrough bits 21 and 22, and SPI1 mode bits 12 and 13.
- For writable `HW_STRAP1` descriptors, it implements the AST2500 behavior that set bits in `SCU70` are cleared from `SCU7C` by writing `~val & desc->mask` to `HW_REVISION_ID` when needed.
- It applies descriptor writes with `regmap_update_bits()`.
- After all writes, it re-evaluates the expression for the requested state and returns `-EPERM` if the hardware state still does not match.

One subtlety is that `aspeed_g5_sig_expr_eval()` uses `aspeed_g5_acquire_regmap()`, but `aspeed_g5_sig_expr_set()` calls the shared `aspeed_sig_expr_eval()` after writing, relying on the maps having been acquired during the write loop. This is valid for descriptors in the expression that were just processed.

## State And Persistence

This driver owns no dynamic allocations except regmap references returned by syscon helpers and cached in the shared `pinmux.maps[]` array. Persistent runtime state is register state:

- Probe mutates `aspeed_g5_pins[].number` and stores `pinmux.dev`.
- Shared probe fills `aspeed_g5_pinctrl_data.scu` and `pinmux.maps[ASPEED_IP_SCU]`.
- Lazy acquisition fills `pinmux.maps[ASPEED_IP_GFX]` and `pinmux.maps[ASPEED_IP_LPC]` the first time those IPs are needed.
- Pinmux settings persist as SCU, GFX, or LPC register bit changes.
- Pinconf settings persist as SCU register bit changes.
- Strap registers are mostly observed and not modified. Allowed strap exceptions are intentionally persistent hardware state changes.
- There is no remove callback; the driver is intended to bind early and remain active for the life of the system.

## Dependencies And Integration Points

- Linux pinctrl, pinmux, and pinconf frameworks provide the user-facing API and device-tree state application.
- Shared Aspeed code in `pinctrl-aspeed.c` implements function/group enumeration, priority-based muxing, GPIO request handling, pinconf get/set, and registration.
- Shared macro/data definitions in `pinmux-aspeed.h` define the signal expression model used by the dense per-pin table.
- Regmap and syscon provide access to SCU, GFX, and LPC registers.
- Device tree must provide the pinctrl node under an SCU syscon parent. For GFX or LPC-backed functions, `aspeed,external-nodes` phandles must point to the expected graphics node and LPC child/parent topology.
- `of_parse_phandle()` and `of_device_is_compatible()` are used directly for AST2500 external nodes.
- Function and group names are consumed by AST2500 board device trees and by peripheral drivers requesting pinctrl states for Ethernet, LPC/eSPI, flash, USB, video, ADC, I2C, SD/MMC, SPI, GPIO, PWM, and serial interfaces.

## Risks And Edge Cases

- The AST2500 table is large and dense. Descriptor ordering, function tags, and priority grouping must be exact; otherwise the shared mux algorithm may disable or enable the wrong signal.
- External regmap acquisition is lazy, so a system can boot until a specific pinctrl state references GFX or LPC and then fail with `-ENODEV` or a syscon error. Device-tree validation should cover `aspeed,external-nodes`.
- The LPC path checks `np->parent` compatibility but returns `-ENODEV` without `of_node_put(np)` on the incompatible-parent path. In this source snapshot that is a potential device-node reference leak if the phandle exists but has the wrong parent.
- For LPC, `syscon_node_to_regmap(np->parent)` is called and then `of_node_put(np)` releases only the child node reference. This assumes the parent node lifetime is stable, which is generally true for OF nodes but is a dependency worth preserving.
- Strap writes are hazardous. The file deliberately permits writes to passthrough and SPI1 mode strap bits and adds the AST2500 clear-through-`HW_REVISION_ID` behavior; descriptor mask mistakes in these areas can alter boot-selected behavior.
- A requested state can remain impossible because a read-only strap descriptor is skipped. The setter detects this through post-write evaluation and returns `-EPERM`, but board-level pinctrl failures may still be difficult to diagnose.
- `aspeed_g5_sig_expr_set()` stores the acquired regmap in a local `map` variable but performs writes through `ctx->maps[desc->ip]`. This depends on `aspeed_g5_acquire_regmap()` caching every successful non-SCU acquisition, which it does.
- Function/group names are ABI for device tree. Renames or removals can break board files.
- Pinconf ranges are broad bank-level ranges. Wrong endpoints or non-contiguous assumptions can make generic pinconf operations affect unrelated pins.
- As with G4, passthrough debounce support is incomplete because enable bits live in pinctrl while debounce period configuration lives in the GPIO controller.
- Many pins have DASH, video, GPIO, and peripheral alternatives sharing condition bits such as `COND1`, `COND2`, `VPI_24_RSVD_DESC`, and CRT DVO descriptors. Small expression changes can have multi-function side effects.

## Test And Validation Signals

- Build tests should compile the AST2500 driver with warnings enabled. The macro pattern catches many duplicate and missing symbol mistakes at compile time.
- Device-tree tests should validate `aspeed,ast2500-pinctrl`, legacy compatible behavior if needed, and `aspeed,external-nodes` phandles for GFX/LPC-backed functions.
- Boot tests should inspect `/sys/kernel/debug/pinctrl/*aspeed-g5-pinctrl*/` for expected pin, group, function, and mux state visibility.
- Regmap validation should verify SCU writes for common I2C, SD, SPI, Ethernet, GPIO, and UART functions; GFX writes for VPO/CRT DVO; and LPC writes for `LPCHC`.
- Negative tests should request an unavailable GFX or LPC-backed function without the corresponding external node and confirm a clear error path.
- Strap tests should cover GPID/GPIE passthrough disable, SPI1 mode fixup, and strap-blocked functions that should return `-EPERM`.
- Ethernet tests should validate RMII/RGMII groups, including SCU48 RMII clock descriptors and RGMII drive-strength pinconf values.
- GPIO tests should request GPIO on pins with higher-priority video, LPC, passthrough, and DASH functions to ensure the priority-walk disabling logic exposes pin-specific GPIO.
- Pinconf tests should set and read pull-down, bias-disable, drive-strength, and debounce parameters on supported pins, plus unsupported pins to confirm `-ENOTSUPP`.
- Hardware smoke tests should cover eSPI/LPC, PNOR, VPO, USB mode switching, SGPIO, and ADC pins because those areas combine several descriptors and may depend on board straps.
