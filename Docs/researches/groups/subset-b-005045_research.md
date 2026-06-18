# Research: subset-b-005045

Grouped research for:

- `sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g4.c`
- `sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g5.c`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g4.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g4.c

## Purpose

`pinctrl-aspeed-g4.c` is the AST2400, or Aspeed generation 4, SoC-specific pin controller description. It binds the generic Aspeed pinctrl and pinmux engine to AST2400 silicon by declaring the available package balls, GPIO numbers, alternate signal expressions, function groups, generic pin configuration ranges, and the platform driver used for `aspeed,ast2400-pinctrl`.

Most of the file is declarative. The per-pin macro declarations describe which signal can appear at each priority level on each package ball and which SCU register bits or strap states make that signal active. The final registration block exposes those tables through Linux pinctrl, pinmux, and pinconf operations. The only significant AST2400-specific runtime behavior is `aspeed_g4_sig_expr_set()`, which writes signal descriptor bits while treating most hardware strap registers as read-only.

## Important APIs, Types, And Data

- Register mnemonics such as `SCU80`, `SCU84`, `SCU88`, `SCU8C`, `SCU90`, `SCU94`, `SCUA0`, `SCUA4`, `SCUA8`, `SCUAC`, `HW_STRAP1`, and `HW_STRAP2` encode AST2400 System Control Unit offsets used by signal descriptors. The source keeps the datasheet names so table entries can be cross-checked against the "Multi-function Pins Mapping and Control" table.
- `SIG_EXPR_DECL_SINGLE()`, `SIG_EXPR_LIST_DECL_SINGLE`, and `SIG_EXPR_LIST_DECL_DUAL` wrap shared `pinmux-aspeed.h` macros. They generate `struct aspeed_sig_desc`, `struct aspeed_sig_expr`, and expression-list symbols tagged by signal and function name.
- `SSSF_PIN_DECL()`, `GPIO_PIN_DECL()`, `PIN_DECL_1()`, `PIN_DECL_2()`, and `PIN_DECL_()` generate `struct aspeed_pin_desc` objects for each package ball. These descriptors are reached through `pinctrl_pin_desc.drv_data`.
- `FUNC_GROUP_DECL()` declares function-to-pin group membership, and later `ASPEED_PINCTRL_GROUP()` and `ASPEED_PINCTRL_FUNC()` populate the exported `aspeed_g4_groups[]` and `aspeed_g4_functions[]` tables.
- `aspeed_g4_pins[]` is the AST2400 pin descriptor array with `ASPEED_G4_NR_PINS` set to 224. It includes invalid GPIOY4-GPIOY7 placeholders in the numbering model and four non-GPIO USB pins, matching the comment that 216 GPIO-capable pins become 220 plus USB pins.
- `aspeed_g4_configs[]` maps pinconf parameters to SCU bit ranges. It supports pull-down/disable controls for GPIO banks, drive strength for RGMII transmit pins, ADC pull-down controls, and input debounce bits for GPIO D/E passthrough mode.
- `aspeed_g4_pin_config_map[]` maps generic pinconf requests to register bit values: pull-down enabled/disabled, bias disabled, and 8 mA or 16 mA drive strength.
- `aspeed_g4_ops` supplies the SoC-specific `struct aspeed_pinmux_ops` `.set` callback. It does not provide a custom `.eval`, so shared expression evaluation handles AST2400.
- `aspeed_g4_pinctrl_data` aggregates pins, groups, functions, configs, and pinconf maps for `aspeed_pinctrl_probe()`.
- `aspeed_g4_pinmux_ops`, `aspeed_g4_pinctrl_ops`, and `aspeed_g4_conf_ops` are Linux framework operation tables using shared Aspeed helpers from `pinctrl-aspeed.c`.
- `aspeed_g4_pinctrl_desc` is the Linux `struct pinctrl_desc` registered under the name `aspeed-g4-pinctrl`.
- `aspeed_g4_pinctrl_driver` is an `arch_initcall()` platform driver matching `aspeed,ast2400-pinctrl` and legacy `aspeed,g4-pinctrl`.

## Functional Coverage

The AST2400 tables cover a broad SoC multiplexing surface:

- Basic link and reset signals such as `MAC1LINK`, `MAC2LINK`, `LPCRST`, `LPCPD`, `LPCSMI`, `LPCPME`, `EXTRST`, `SPICS1`, `BMCINT`, `FLACK`, `FLBUSY`, `FLWP`, watchdog reset outputs, and oscillator or USB clock inputs.
- SD and I2C interfaces: `SD1`, `SD2`, and I2C buses 3 through 14 where supported by the pin map.
- MDIO interfaces `MDIO1` and `MDIO2`.
- UART-style individual modem/control/data signals, including `UART6` as a grouped function and several standalone UART signal functions.
- GPIO D/E passthrough groups such as `GPID`, `GPID0`, `GPID2`, `GPID4`, `GPID6`, `GPIE0`, `GPIE2`, `GPIE4`, and `GPIE6`.
- SPI and boot flash modes: `SPI1`, `SPI1DEBUG`, `SPI1PASSTHRU`, `ROM8`, `ROM16`, ROM chip selects, and VGA BIOS ROM signals.
- Video input and output modes: `VPI18`, `VPI24`, `VPI30`, `VPO12`, and `VPO24`, with compound expressions for width/mode selection.
- Ethernet modes `RMII1`, `RMII2`, `RGMII1`, and `RGMII2`, including strap-dependent RMII selection and separate GPIO expressions for the same pins.
- ADC channels `ADC0` through `ADC15`.
- USB host/device pin pairs: `USB11H2`, `USB11D1`, `USB2H1`, and `USB2D1`; the file also defines but intentionally does not export USB port 4 function/group capability because the datasheet evidence is weak.

## Control Flow

Initialization is short and deterministic:

1. `arch_initcall(aspeed_g4_pinctrl_init)` registers `aspeed_g4_pinctrl_driver`.
2. The platform bus matches a device-tree node with `aspeed,ast2400-pinctrl` or legacy `aspeed,g4-pinctrl`.
3. `aspeed_g4_pinctrl_probe()` iterates `aspeed_g4_pins[]` and assigns each `pinctrl_pin_desc.number` to its array index. This repairs the designated initializer index into the Linux-visible pin number.
4. Probe calls `aspeed_pinctrl_probe(pdev, &aspeed_g4_pinctrl_desc, &aspeed_g4_pinctrl_data)`.
5. The shared probe finds the parent syscon regmap, stores it as `pdata->scu`, places it in `pdata->pinmux.maps[ASPEED_IP_SCU]`, registers the pinctrl device, and stores driver data on the platform device.

Mux selection flows through the shared `aspeed_pinmux_set_mux()`:

1. Linux pinctrl supplies a function selector and group selector.
2. The shared code finds the requested `aspeed_pin_function` and `aspeed_pin_group`.
3. For each pin in the group, it walks the pin descriptor's priority lists.
4. Priority levels above the requested function are disabled with `aspeed_disable_sig()`, which disables every expression in that priority level.
5. The matching expression for the requested function is enabled through `aspeed_sig_expr_enable()`.
6. Enabling or disabling ultimately calls `aspeed_g4_sig_expr_set()` for AST2400-specific writes.

GPIO request flow uses `aspeed_gpio_request_enable()` from the shared driver. It disables higher-priority non-GPIO expressions until it finds a pin-specific `GPI*` expression whose signal and function names match, intentionally distinguishing normal GPIO from GPID/GPIE passthrough functions.

Pin configuration flow uses shared `aspeed_pin_config_get()`, `aspeed_pin_config_set()`, `aspeed_pin_config_group_get()`, and `aspeed_pin_config_group_set()`. The AST2400 file supplies only the config ranges and value maps; the shared implementation finds the matching range, converts generic pinconf arguments into bit values, and calls `regmap_update_bits()` on the SCU regmap.

## AST2400 Signal Setter Behavior

`aspeed_g4_sig_expr_set()` is the key local function. For each descriptor in an expression:

- It derives `pattern` from `desc->enable` or `desc->disable`.
- It shifts the pattern into position with `__ffs(desc->mask)`.
- It fails with `-ENODEV` if the descriptor references a missing regmap.
- It skips most `HW_STRAP1` descriptors and all `HW_STRAP2` descriptors because strap registers are configured by hardware or early firmware and are treated as read-only.
- It allows exceptions for `HW_STRAP1` bits 22, 21, 13, and 12. Bits 22 and 21 are GPID/GPIE passthrough mode bits; bits 13 and 12 select SPI1 operating mode. The comment explains that passthrough mode often must be disabled after BMC boot and that some systems strap SPI1 incorrectly.
- It applies writable bits with `regmap_update_bits()`.
- After all descriptor writes, it calls `aspeed_sig_expr_eval(ctx, expr, enable)`. If evaluation fails, it returns the negative error. If evaluation says the requested state is still not true, it returns `-EPERM`.

The post-write evaluation is important because skipped strap descriptors can make deconfiguration or configuration impossible. The caller receives a hard failure rather than assuming a write to non-strap bits was sufficient.

## State And Persistence

The file owns no heap state and no persistent storage. Runtime state is hardware state in SCU registers and, indirectly, Linux pinctrl registration state:

- `aspeed_g4_pins[]` is static data. Probe mutates only the `.number` field for each entry before registration.
- `aspeed_g4_pinctrl_data` is static data shared with the registered pinctrl device. During shared probe, its `scu` regmap and `pinmux.maps[ASPEED_IP_SCU]` are populated.
- Pinmux and pinconf operations persist by changing SCU register bits through regmap. Those changes remain until firmware, reset, another driver, or later pinctrl operations change them.
- Strap bits are mostly treated as immutable. The driver may observe them during expression evaluation but generally does not attempt to rewrite them.
- The driver has no remove path and is registered at `arch_initcall`, which is normal for early SoC pinctrl needed before many child devices bind.

## Dependencies And Integration Points

- Linux pinctrl core: `struct pinctrl_desc`, `pinctrl_register()`, `pinctrl_ops`, `pinmux_ops`, `pinconf_ops`, and device-tree map parsing through `pinconf_generic_dt_node_to_map_all`.
- Linux pinconf generic parameters: `PIN_CONFIG_BIAS_PULL_DOWN`, `PIN_CONFIG_BIAS_DISABLE`, `PIN_CONFIG_DRIVE_STRENGTH`, and `PIN_CONFIG_INPUT_DEBOUNCE`.
- Regmap and syscon: all hardware access is via the parent SCU syscon regmap acquired by the shared Aspeed probe.
- Shared Aspeed code: `pinctrl-aspeed.c` supplies group/function enumeration, mux selection, GPIO request muxing, pinconf handling, and shared expression helpers. `pinmux-aspeed.h` supplies the macro language and core signal expression data model.
- Device tree bindings: consumers refer to function and group names declared in `aspeed_g4_functions[]` and `aspeed_g4_groups[]`; the pinctrl node must match `aspeed,ast2400-pinctrl` or the legacy compatible.
- Other subsystems indirectly depend on the names and groups here: Ethernet MACs, SD/MMC, I2C, SPI/flash, LPC, video, USB, ADC, GPIO, and watchdog/reset devices will request pin states through pinctrl.

## Risks And Edge Cases

- The tables are large and macro-generated. A wrong register, bit, function tag, or group membership can compile cleanly while selecting the wrong physical signal at runtime. The macro scheme catches some duplicate-symbol and designated-initializer mistakes, but it cannot prove datasheet transcription correctness.
- Function and group names are device-tree ABI. Renaming or removing entries can break existing board files or overlays.
- Strap-dependent functions may be impossible to enable or disable from Linux. `aspeed_g4_sig_expr_set()` reports `-EPERM` when evaluation fails after skipped strap writes, but the board-level symptom may be a pinctrl probe or device probe failure.
- The passthrough and SPI1 strap exceptions deliberately write selected strap bits. A wrong mask in a descriptor could affect early-boot-selected behavior.
- Pin ordering matters. Numeric macros such as `D6 0`, `B5 1`, and so on encode GPIO numbering, while `aspeed_g4_pins[]` is sorted alphabetically. Probe corrects `.number` to array index, so missing or duplicate entries can produce subtle pin number mismatches.
- Several pins have "Other" functions that are not GPIO. Consumers assuming that freeing/disabling a function always returns the pin to GPIO would be wrong; the shared Aspeed priority model handles this if the tables are accurate.
- The USB port 4 comment documents intentionally unexported capability. Adding groups without hardware validation may expose nonfunctional pins.
- Pinconf ranges use numeric low/high pin IDs and assume contiguous GPIO bank numbering. A wrong endpoint can apply pull-down, drive-strength, or debounce controls to the wrong bank.
- Input debounce support for D/E passthrough is explicitly incomplete because debounce period lives in the GPIO controller while mux debounce enable lives in SCU.

## Test And Validation Signals

- Build coverage: compile this driver with the Aspeed pinctrl sources. The macro-heavy table design should catch duplicate generated symbols, missing symbols, and many initializer mistakes.
- Device-tree binding coverage: boot an AST2400 board with `aspeed,ast2400-pinctrl` and representative pinctrl states for I2C, SD, Ethernet, LPC, SPI1, and GPIO.
- Runtime debugfs checks: inspect `/sys/kernel/debug/pinctrl/*aspeed-g4-pinctrl*/` for expected pins, groups, functions, and active mux state.
- Regmap checks: compare SCU bit changes for selected functions against the AST2400 datasheet, especially `SCU80` through `SCUAC`, `HW_STRAP1`, and `HW_STRAP2`-dependent expressions.
- Negative tests: request a function blocked by read-only strap state and verify `-EPERM` propagates rather than silently reporting success.
- GPIO tests: request GPIO on pins with higher-priority alternate functions and on GPID/GPIE passthrough-capable pins; verify the driver disables passthrough/alternate expressions and exposes pin-specific GPIO.
- Pinconf tests: set and read back pull-down, bias-disable, and RGMII drive-strength values; verify unsupported arguments return `-EINVAL` or `-ENOTSUPP`.
- Board tests: validate Ethernet RMII/RGMII selection, SPI1 strap fixup, LPC reset behavior, and front-panel passthrough behavior on real hardware because those paths involve strap exceptions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g5.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g5.c -->
