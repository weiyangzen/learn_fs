# Research: subset-b-005120 UniPhier pinctrl files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-core.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-core.c

## Purpose

This file is the shared UniPhier pin controller implementation used by the SoC-specific UniPhier pin table drivers. It translates `struct uniphier_pinctrl_socdata` tables into Linux pinctrl, pinmux, and generic pinconf operations, accesses the controller through a syscon-backed regmap, and saves/restores the pin controller register ranges across system sleep.

## Important APIs, Types, And Functions

The central runtime object is `struct uniphier_pinctrl_priv`, which owns the `pinctrl_desc`, registered `pinctrl_dev`, syscon `regmap`, SoC data pointer, and a sleep-save list of `struct uniphier_pinctrl_reg_region`. Register bases are fixed around pinmux, load-pinmux, drive strength, pull, and input-enable blocks: `UNIPHIER_PINCTRL_PINMUX_BASE`, `UNIPHIER_PINCTRL_LOAD_PINMUX`, `UNIPHIER_PINCTRL_DRVCTRL_BASE`, `UNIPHIER_PINCTRL_DRV2CTRL_BASE`, `UNIPHIER_PINCTRL_DRV3CTRL_BASE`, `UNIPHIER_PINCTRL_PUPDCTRL_BASE`, and `UNIPHIER_PINCTRL_IECTRL_BASE`.

Pinctrl group callbacks (`uniphier_pctl_get_groups_count()`, `uniphier_pctl_get_group_name()`, `uniphier_pctl_get_group_pins()`) expose SoC groups from `socdata`. Debugfs `uniphier_pctl_pin_dbg_show()` decodes packed per-pin drive and pull metadata. Pinconf helpers handle bias, drive strength, and input enable: `uniphier_conf_get_drvctrl_data()`, `uniphier_conf_pin_bias_get()`, `uniphier_conf_pin_drive_get()`, `uniphier_conf_pin_input_enable_get()`, `uniphier_conf_pin_bias_set()`, `uniphier_conf_pin_drive_set()`, `uniphier_conf_pin_input_enable()`, plus the per-pin and per-group config entry points. Pinmux helpers expose functions and groups and program selections through `uniphier_pmx_set_one_mux()`, `uniphier_pmx_set_mux()`, and `uniphier_pmx_gpio_request_enable()`. `uniphier_pinctrl_probe()` is the exported shared probe used by each SoC driver.

## Control Flow

A SoC-specific platform driver calls `uniphier_pinctrl_probe(pdev, socdata)`. The probe validates that the SoC data has pins, groups, functions, and counts; allocates `priv`; obtains the parent node's syscon regmap with `syscon_node_to_regmap()`; fills the `pinctrl_desc`; initializes suspend-save metadata with `uniphier_pinctrl_pm_init()`; registers the pinctrl device with `devm_pinctrl_register()`; and stores the driver data.

Device-tree pinctrl state parsing is delegated to `pinconf_generic_dt_node_to_map_all()`, so generic `bias-*`, `drive-strength`, and `input-enable` properties are translated into generic pinconf configs. `uniphier_conf_pin_config_set()` walks each requested config and dispatches to bias, drive, or input-enable setters. Group config is just a loop over every pin in the group and stops on the first failing pin.

Pinmux selection flows from `uniphier_pmx_set_mux()` to `uniphier_pmx_set_one_mux()` for each pin in the selected group. Each pin is first input-enabled when possible. A negative mux value means a dedicated pin and no pinmux register write. Otherwise the function computes register, shift, width, and stride from SoC capability flags. Normal layouts use 8 mux bits per pin with separate normal/debug offsets; `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE` uses 4 normal bits plus 4 debug bits in the same register word and writes `UNIPHIER_PINCTRL_LOAD_PINMUX` afterward.

GPIO request muxing uses the selected `pinctrl_gpio_range`, converts the pin to a GPIO offset, calls the SoC `get_gpio_muxval()` callback, and then reuses the one-pin mux setter. The pinmux ops set `.strict = true`, so GPIO and mux ownership conflicts are prevented by the pinctrl core.

## State And Persistence

All SoC pin, group, and function descriptions are immutable static data supplied by companion files. Runtime mutable state is the devm-allocated `uniphier_pinctrl_priv`, the pinctrl core state, and hardware registers reached through regmap. Bias, drive, input-enable, GPIO, and mux changes persist as hardware register state until overwritten, reset, or power loss.

When `CONFIG_PM_SLEEP` is enabled, `uniphier_pinctrl_pm_init()` scans all pins to find the highest drive, pull, and input-enable register indices actually described by the SoC data, creates register-region save buffers, and registers late system sleep callbacks through `uniphier_pinctrl_pm_ops`. Suspend bulk-reads each range; resume bulk-writes the saved values and reloads pinmux for debug-mux-separate SoCs. There is no on-disk persistence.

## Dependencies And Integration Points

The file integrates with Linux pinctrl, pinmux, pinconf-generic, pinctrl-utils, platform-driver, OF, regmap, syscon, debugfs/seq_file, and device PM infrastructure. It depends heavily on `pinctrl-uniphier.h` for packed per-pin metadata accessors, SoC data structures, capability flags, and group/function macros. SoC files provide `get_gpio_muxval()` policy and OF-compatible platform drivers.

## Risks

The shared code assumes SoC tables are internally consistent: group pin arrays must align with mux value arrays, packed drive/pull/input indices must fit the hardware register layout, and GPIO range IDs must match SoC GPIO numbering. Fixed-drive pins are represented with a zero-width mask and rely on callers accepting only the fixed value bucket. Drive setting rounds down to the greatest supported strength not exceeding the requested value, rejecting only values below the minimum, so callers expecting exact drive strength may observe a lower effective value.

Input-enable handling is capability-sensitive. Without `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`, disabling a single pin is rejected because one bit may be shared by multiple pins; with the capability, the pin number overrides the packed `iectrl` field. A wrong capability flag can therefore make input-disable either impossible or incorrectly per-pin. Pinmux register calculation also changes with `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE`; mislabeling that flag can write the wrong mux halves or omit the required load strobe.

Suspend-save sizing is derived from the maximum indices in pin descriptors, not from raw hardware manuals. If a SoC table omits a controllable pin or uses a too-small index, that register may not be restored after sleep. Conversely, a too-large index expands save/restore traffic to registers that may not exist.

## Test Signals

Useful signals include a successful build with UniPhier pinctrl drivers enabled, probe success for each SoC compatible, no "pinctrl socdata lacks necessary members" or "failed to get regmap" logs, pinctrl state application from DT, debugfs pin metadata matching expected pull/drive classes, GPIO request/mux tests across normal and XIRQ GPIO ranges, bias and drive-strength get/set tests for 1-bit, 2-bit, 3-bit, fixed, and unsupported pins, input-enable tests on per-pin and shared-controller SoCs, and suspend/resume tests verifying pinmux, pull, drive, and input-enable register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld11.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld11.c

## Purpose

This file supplies the UniPhier LD11 SoC-specific pin controller data and platform-driver binding. It is table-driven data for the shared UniPhier core rather than an independent pinctrl algorithm implementation.

## Important APIs, Types, And Functions

The file defines `uniphier_ld11_pins` with 149 `UNIPHIER_PINCTRL_PIN()` descriptors, 41 mux groups, 6 GPIO-only groups, and 27 pinmux functions. The peripheral groups cover audio input/output and IEC variants, eMMC, RMII Ethernet, HSC input/output variants, I2C, NAND, SPI, system bus, UARTs with optional CTS/RTS and modem pins, and USB VBUS/overcurrent pins.

`uniphier_ld11_get_gpio_muxval()` maps GPIO requests to UniPhier mux values: GPIO offsets 132 and 135, representing XIRQ12 and XIRQ15, use mux value 13; GPIO offsets 120 through 143 use mux value 14; all other GPIOs use mux value 15. `uniphier_ld11_pindata` packages the pins, groups, functions, GPIO mux callback, and `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`. `uniphier_ld11_pinctrl_probe()` forwards that data to the shared `uniphier_pinctrl_probe()`. The OF compatible is `socionext,uniphier-ld11-pinctrl`, registered by a built-in platform driver named `uniphier-ld11-pinctrl`.

## Control Flow

At built-in platform-driver registration, a matching DT node invokes `uniphier_ld11_pinctrl_probe()`, which calls the shared core with `uniphier_ld11_pindata`. The core registers pinctrl operations, exposes all LD11 groups and functions, parses generic pinconf properties, and uses LD11's packed pin descriptors for drive, pull, and input-enable register addressing. Runtime mux changes select each group's pin list and LD11-specific mux values; GPIO requests call `uniphier_ld11_get_gpio_muxval()` before programming the mux.

## State And Persistence

The LD11 file owns no mutable state. Its pin, group, function, and match tables are `static const`. Runtime state lives in the shared UniPhier core and hardware registers. Because the SoC data advertises per-pin input-enable control, the core treats input-enable bits as keyed by pin number for configuration and suspend/resume sizing.

## Dependencies And Integration Points

This source depends on `pinctrl-uniphier.h`, Linux platform-driver and OF match infrastructure, and the shared UniPhier core. It integrates with board device trees through the LD11 compatible string and through pinctrl state names matching the function and group names declared here.

## Risks

Most risk is descriptor accuracy. The file mixes ordinary peripheral groups, optional width extensions such as `emmc_dat8`, GPIO-only ranges, and overlapping alternate functions. A wrong pin number or mux value can silently route a board peripheral to another pad. The XIRQ-specific GPIO mux exceptions must match the GPIO controller's range IDs; if a range ID changes, `gpio_offset`-based selection can choose the wrong mux value. Per-pin input-enable capability must remain aligned with LD11 hardware because the shared core ignores packed `iectrl` values when that flag is set.

## Test Signals

Good validation includes DT probe with `socionext,uniphier-ld11-pinctrl`, successful application of eMMC, NAND, RMII, UART, SPI, I2C, USB, audio, and system-bus pin states, GPIO tests through every declared GPIO range, XIRQ GPIO tests for offsets 120-143 and the special offsets 132/135, bias and drive tests on 1-bit, 2-bit, fixed4, and fixed5 pins, and suspend/resume checks that per-pin input-enable settings survive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld20.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld20.c

## Purpose

This file provides the UniPhier LD20 pin controller description. It lists LD20 pins, pin groups, mux values, functions, GPIO-only ranges, capability flags, and the platform-driver binding consumed by the shared UniPhier core.

## Important APIs, Types, And Functions

`uniphier_ld20_pins` contains 176 packed pin descriptors. The file defines 58 mux groups plus 3 GPIO-only groups and 38 pinmux functions. Compared with LD11, LD20 has broader audio coverage (`ain1`, `ain2`, `ain3`, `aout1`, `aout1b`, `aout2`, `aout3`, `aout4`), both RGMII and RMII Ethernet groups, more HSC input variants, SD, four SPI controllers, and USB0-USB3 groups.

`uniphier_ld20_get_gpio_muxval()` matches the LD11 GPIO policy: XIRQ12 and XIRQ15 use mux value 13, XIRQ offsets 120-143 use mux value 14, and all other GPIOs use mux value 15. `uniphier_ld20_pindata` sets `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`, so input-enable is interpreted per pin. The OF compatible is `socionext,uniphier-ld20-pinctrl`, registered through the built-in `uniphier-ld20-pinctrl` platform driver.

## Control Flow

Probe is a thin wrapper around `uniphier_pinctrl_probe(pdev, &uniphier_ld20_pindata)`. The shared core validates and registers the LD20 arrays, then all runtime operations are table-driven: function selection applies a group's mux values pin by pin; GPIO requests compute a GPIO mux value through LD20's callback; bias, drive, and input-enable operations decode the packed metadata in `uniphier_ld20_pins`.

## State And Persistence

The LD20 source is immutable static data and has no local state machine. Hardware pin state is mutable through the shared regmap. Per-pin input-enable capability affects both runtime config and the set of input-enable registers saved by the shared PM code.

## Dependencies And Integration Points

The file integrates with the platform bus, OF compatible matching, Linux pinctrl via the shared core, and board pinctrl states that refer to the group/function names. It depends on `pinctrl-uniphier.h` for metadata packing and array macros.

## Risks

LD20 contains many overlapping media/audio and serial alternatives with high mux values such as 26 and 27 for some audio input groups. Any group/mux mismatch can be difficult to diagnose because the shared core trusts the arrays and only validates array lengths through macros. The SD group comment notes no `SDVOLC`, which is a board-integration risk if device trees assume voltage-control routing. GPIO XIRQ handling shares the same offset-sensitive risks as LD11. Per-pin input-enable must match the hardware register model.

## Test Signals

Test signals include successful DT probe, pinmux activation for RGMII and RMII Ethernet, eMMC plus `emmc_dat8`, SD without voltage-control expectations, all SPI and UART groups, USB0-USB3, audio groups with alternate `aout1b` and high mux values, GPIO tests over the three GPIO ranges, XIRQ-specific GPIO request tests, pinconf get/set on representative pull and drive classes, and suspend/resume retention of mux and input-enable registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld4.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld4.c

## Purpose

This file is the UniPhier LD4 SoC pinctrl data provider. It describes LD4 pins, mux groups, functions, GPIO mux value policy, and the platform-driver binding for the shared UniPhier pinctrl core.

## Important APIs, Types, And Functions

`uniphier_ld4_pins` defines 175 pin descriptors. The file declares 28 mux groups, one GPIO-only group, and 18 functions. Major functions include eMMC and `emmc_dat8`, MII and RMII Ethernet, I2C0-I2C3, NAND with chip-select extension, SD, SPI0, system bus with multiple chip-select groups, UART0 with flow/modem extensions, UART1 plus alternate `uart1b`, UART2, UART3, and USB0/USB1/USB2 plus `usb2b`.

`uniphier_ld4_get_gpio_muxval()` has a switch-based policy. PORT00-PORT26, XIRQ1-XIRQ11, and XIRQ14 use mux value 0; XIRQ0, XIRQ12, and XIRQ15 use mux value 14; all other GPIO offsets use mux value 15. `uniphier_ld4_pindata` sets `.caps = 0`, so the shared core uses packed input-enable indices and the non-debug-separate mux layout. The OF compatible is `socionext,uniphier-ld4-pinctrl`.

## Control Flow

The built-in platform driver probes on the LD4 compatible and calls `uniphier_pinctrl_probe()`. The shared core exposes the LD4 functions and groups, handles DT pinctrl maps, and programs mux, bias, drive, and input-enable registers using the LD4 tables. GPIO requests pass through the LD4-specific GPIO mux callback and then through the shared one-pin mux writer.

## State And Persistence

This file contains only static tables and no writable state. Runtime state is stored in the shared pinctrl device and hardware registers. With `.caps = 0`, input-enable controls may be shared across pins; the shared core rejects per-pin disabling in that model and sizes suspend/resume input-enable save ranges from packed `iectrl` values.

## Dependencies And Integration Points

Dependencies are the shared UniPhier header/core, Linux platform and OF support, and board DT pinctrl users. The group and function names are the public integration surface for device-tree pinctrl states.

## Risks

The LD4 groups include negative mux values for dedicated pins in system-bus-related groups, which relies on the shared core's "nothing to write" handling for mux value `< 0`. Several peripherals share pins through alternate groups such as `uart1`/`uart1b` and `usb2`/`usb2b`, so board states must pick mutually compatible groups. The GPIO mux switch is more nuanced than newer LD11/LD20 logic; range-ID or offset mistakes can make ordinary ports, XIRQ lines, and default GPIOs program different mux values than intended. Shared input-enable semantics make disabling individual pins risky or unsupported.

## Test Signals

Useful signals include successful probe with `socionext,uniphier-ld4-pinctrl`, pinctrl state tests for eMMC, NAND, SD, MII/RMII Ethernet, system bus chip selects, alternate UART/USB groups, GPIO request tests covering PORT00-PORT26 and XIRQ offsets, verification that dedicated negative-mux pins do not cause register errors, pinconf pull/drive tests, and suspend/resume checks for shared input-enable and mux retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld6b.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld6b.c

## Purpose

This source defines the UniPhier LD6b SoC pin controller tables and binding. It feeds LD6b-specific pin descriptors, peripheral mux groups, GPIO ranges, and capability flags into the shared UniPhier pinctrl implementation.

## Important APIs, Types, And Functions

`uniphier_ld6b_pins` contains 235 pin descriptors, the largest table in this subset except Pro4. The file defines 32 mux groups, 2 GPIO-only groups, and 20 pinmux functions. Notable groups include `adinter` for Achip-Dchip interconnect, eMMC plus 8-bit data extension, RGMII/RMII Ethernet, I2C0-I2C3, NAND plus chip select, SD, SPI0/SPI1, system bus with chip-select groups 1 through 5, UART variants including `uart0b`, `uart1b`, and `uart2b`, and USB0-USB3.

`uniphier_ld6b_get_gpio_muxval()` returns mux value 14 for GPIO offsets 120-143, documented as XIRQ aliases of PORT150-177, and mux value 15 otherwise. `uniphier_ld6b_pindata` uses `.caps = 0`, so it relies on the default mux layout and shared or indexed input-enable semantics rather than per-pin override. The OF compatible is `socionext,uniphier-ld6b-pinctrl`.

## Control Flow

The LD6b built-in platform driver matches its OF compatible and calls `uniphier_pinctrl_probe()`. The shared probe registers the static tables. Runtime mux selection and GPIO request handling are table-driven: selected groups write the listed mux values, while GPIO requests derive a mux value from the LD6b callback. Generic pinconf operations operate on the packed LD6b drive, pull, and input-enable metadata.

## State And Persistence

LD6b state in this file is immutable. Mutable runtime state is owned by the shared core and by hardware registers. Since the capabilities field is zero, suspend/resume save ranges and input-enable behavior are based on the descriptor-encoded register indices, and the debug-mux-separate load strobe is not used.

## Dependencies And Integration Points

The file depends on `pinctrl-uniphier.h`, the common UniPhier core, and Linux platform/OF infrastructure. It exposes function and group names to board DT pinctrl states, and its GPIO mux callback integrates with GPIO ranges registered by the GPIO/pinctrl subsystem.

## Risks

The table has many high-numbered pads and overlapping alternate serial/system-bus chip selects. Wrong mux values on `system_bus_cs*`, UART alternates, or NAND/eMMC shared pads can break boot media or board buses. The XIRQ alias comment means GPIO offsets 120-143 are not independent raw pins; tests must validate the GPIO controller's offset mapping. With `.caps = 0`, individual input-disable requests should fail when controls are shared, so device-tree states must not assume per-pin input disable.

## Test Signals

Validation should cover successful probe, pinmux tests for `adinter`, boot media groups, RGMII/RMII, all system-bus chip selects, alternate UARTs, SPI, SD, and USB0-USB3, GPIO request tests for XIRQ aliases and ordinary GPIOs, pinconf tests on representative drive/pull classes, negative or unsupported input-disable behavior, and suspend/resume restoration of mux, drive, pull, and input-enable registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-ld6b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-nx1.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-nx1.c

## Purpose

This file provides the UniPhier NX1 SoC pinctrl description and platform-driver binding for the shared UniPhier pinctrl core.

## Important APIs, Types, And Functions

`uniphier_nx1_pins` defines 96 pin descriptors. The file declares 23 mux groups, 5 GPIO-only groups, and 19 functions. It covers eMMC with `emmc_dat8`, RGMII/RMII Ethernet, I2C0-I2C6, SD, SPI0/SPI1, UART0-UART3 with UART1 and UART2 flow-control extensions, and USB0/USB1. Some eMMC mux values are `-1`, indicating dedicated pins that the shared core input-enables but does not program through the pinmux registers.

`uniphier_nx1_get_gpio_muxval()` returns mux value 14 for GPIO offsets 120 and above, treated as XIRQ lines, and mux value 15 otherwise. `uniphier_nx1_pindata` enables `UNIPHIER_PINCTRL_CAPS_PERPIN_IECTRL`, so the shared core treats input-enable controls as per-pin. The OF compatible is `socionext,uniphier-nx1-pinctrl`.

## Control Flow

Probe is a wrapper that calls the shared `uniphier_pinctrl_probe()` with the NX1 data. After registration, DT pinctrl states select groups by name and the core writes each group's mux values. GPIO request handling uses the NX1 GPIO mux callback before the shared one-pin mux path. Generic pinconf get/set operations use the NX1 packed pin attributes.

## State And Persistence

The file owns only static const SoC metadata. Runtime state and persistence rules are inherited from the shared core and hardware registers. Per-pin input-enable capability means the core uses pin numbers for input-enable bits, including suspend/resume save sizing.

## Dependencies And Integration Points

NX1 integrates through the platform driver's OF match table, the shared UniPhier core, Linux pinctrl and GPIO range handling, and board DT pinctrl states that reference the declared group/function names.

## Risks

Because NX1 is a smaller table with several dedicated eMMC pins, negative mux handling must be validated for boot-media paths. The broad `gpio_offset >= 120` XIRQ rule assumes the GPIO controller exposes XIRQ offsets at and above 120; a different range layout would choose mux value 14 for the wrong lines. Per-pin input-enable flag accuracy matters for both runtime input-enable and PM restore behavior. I2C4-I2C6 and UART flow-control groups share limited high pads, so board states must avoid incompatible simultaneous selections.

## Test Signals

Signals include successful probe with `socionext,uniphier-nx1-pinctrl`, eMMC and `emmc_dat8` state application with negative mux values, RGMII/RMII Ethernet tests, I2C0-I2C6 and UART flow-control mux tests, GPIO request tests on offsets below and above 120, pinconf bias/drive/input-enable tests, and suspend/resume validation on per-pin input-enable registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-nx1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pro4.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pro4.c

## Purpose

This source supplies the UniPhier Pro4 SoC pinctrl tables and platform-driver binding. It is the Pro4 data layer for the shared UniPhier core and includes the debug-mux-separate capability needed by this SoC's pinmux register layout.

## Important APIs, Types, And Functions

`uniphier_pro4_pins` contains 329 pin descriptors, the largest table in this item. It defines 36 mux groups, one GPIO-only group, and 23 functions. Major groups include eMMC and 8-bit data, Ethernet MII/RGMII/RMII plus alternate RMII-B, I2C0-I2C3 and I2C6, NAND plus chip select, SD and SD1, SPI0/SPI1, system bus plus chip-select groups 0 through 7, UART0-UART3 with UART3 flow/modem extensions, and USB0-USB3.

`uniphier_pro4_get_gpio_muxval()` returns mux value 2 for GPIO offsets 134-140, documented as XIRQ14-XIRQ20, and mux value 7 otherwise. `uniphier_pro4_pindata` sets `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE`, which changes the shared mux writer to a 4-bit normal/debug split and makes it write `UNIPHIER_PINCTRL_LOAD_PINMUX` after mux changes and after resume. The OF compatible is `socionext,uniphier-pro4-pinctrl`.

## Control Flow

The Pro4 platform driver probes through `uniphier_pro4_pinctrl_probe()` and passes `uniphier_pro4_pindata` to the shared core. Pinctrl state selection uses Pro4 group arrays and mux values. GPIO requests use the Pro4 callback and then the shared one-pin mux setter. Because debug mux is separate, mux writes follow the Pro4-specific register layout path and issue the load strobe.

## State And Persistence

The Pro4 tables are immutable static metadata. Runtime state lives in the shared pinctrl driver and hardware registers. Pro4 does not set per-pin input-enable capability, but does set debug-mux-separate; this affects both normal runtime mux writes and PM resume, where the shared core reloads pinmux after bulk-restoring saved registers.

## Dependencies And Integration Points

Dependencies include `pinctrl-uniphier.h`, the shared UniPhier core, Linux platform/OF infrastructure, syscon/regmap access through the parent node, and board DT pinctrl states. The Pro4 compatible string binds the SoC-specific data into the common implementation.

## Risks

The Pro4 table is large and has many high-numbered pins, system-bus chip selects, and overlapping storage/network interfaces. Descriptor or mux value mistakes can affect boot media, external bus chip selects, or Ethernet modes. `UNIPHIER_PINCTRL_CAPS_DBGMUX_SEPARATE` is critical: if omitted, the core would use the wrong mux stride and skip the load-pinmux register; if set incorrectly, other SoCs would be misprogrammed. The GPIO mux policy has a narrow XIRQ14-XIRQ20 exception, so GPIO range offset correctness is essential. Shared input-enable semantics still apply because the per-pin input-enable flag is not set.

## Test Signals

Useful validation includes successful probe with `socionext,uniphier-pro4-pinctrl`, pinmux state tests for eMMC/NAND/SD/SD1, MII/RGMII/RMII/RMII-B Ethernet, SPI, I2C, UART, USB, and every system-bus chip select, GPIO request tests around offsets 134-140 and ordinary offsets, verification that mux writes trigger load-pinmux behavior, pinconf tests across supported drive/pull classes, and suspend/resume tests that confirm mux state is restored and reloaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/pinctrl-uniphier-pro4.c -->
