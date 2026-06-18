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
