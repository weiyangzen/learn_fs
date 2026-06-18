# subset-b-005075 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-single.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-single.c

## Purpose
`pinctrl-single.c` is a generic Open Firmware platform driver for "one register per pin" and "bit-per-mux" pin controllers, especially TI OMAP/DRA/AM padconf blocks and compatible simple padconf devices. It exposes muxing, optional generic pin configuration, optional GPIO-function mux switching, wake IRQ routing, and noirq suspend/resume context handling through the Linux pinctrl, pinmux, pinconf, irqdomain, and platform-driver APIs.

## Important APIs, Types, and Functions
The central state is `struct pcs_device`, which owns the MMIO base, register width, function mask/shift, pin table, GPIO function ranges, IRQ domain/list, SoC flags, raw spinlock, mutex, and function pointers for 8/16/32-bit register access. `struct pcs_soc_data` supplies compatible-specific flags and interrupt masks. `struct pcs_function` stores one dynamically parsed DT function, including `struct pcs_func_vals` register/value/mask entries and optional `struct pcs_conf_vals` pinconf metadata.

The pinctrl/pinmux entry points are `pcs_pinctrl_ops`, `pcs_pinmux_ops`, and, when enabled, `pcs_pinconf_ops`. `pcs_dt_node_to_map()` dispatches to `pcs_parse_one_pinctrl_entry()` for `pinctrl-single,pins` or `pcs_parse_bits_in_pinctrl_entry()` for `pinctrl-single,bits`. `pcs_set_mux()` applies mux values with raw spinlock protection. `pcs_request_gpio()` searches parsed `pinctrl-single,gpio-range` entries and writes the GPIO mux value. Pin configuration is parsed by `pcs_parse_pinconf()` and applied/read by `pcs_pinconf_set()`, `pcs_pinconf_get()`, and group variants.

IRQ support is centered on `pcs_irq_init_chained_handler()`, `pcs_irqdomain_map()`, `pcs_irq_handle()`, and `pcs_irq_set()`. Power management is handled by `pinctrl_single_suspend_noirq()`, `pinctrl_single_resume_noirq()`, `pcs_save_context()`, and `pcs_restore_context()`.

## Control Flow
`pcs_probe()` obtains compatible data, reads `pinctrl-single,register-width`, optional function mask/off values, and the bit-per-mux flag, patches legacy missing `#pinctrl-cells` when built in, maps the MMIO region, selects width-specific accessors, allocates one pin descriptor per register or bit slice, registers and enables pinctrl, parses GPIO function ranges, and optionally installs an IRQ domain and chained/shared parent handler. DT child nodes are parsed lazily through pinctrl core mapping callbacks when consumers request states; each node becomes a one-group, one-function mapping plus a config mapping if pinconf properties are present.

Mux setting loops over every parsed register/value entry, masks either the per-entry bit field or global function mask, writes the new value, and leaves other bits unchanged. Pinconf get/set first resolves the active pin mux setting back to the parsed function data, then interprets two-cell value/mask or four-cell value/enable/disable/mask DT properties as generic pinconf parameters.

## State and Persistence
Runtime state is mostly in MMIO registers and devm-owned structures. Parsed functions/groups are added dynamically to generic pinctrl registries and remain for the device lifetime. `pcs->gpiofuncs` and `pcs->irqs` are protected by the device mutex when updated. Register accesses that modify shared hardware state use `pcs->lock`. Compatible data may set `PCS_CONTEXT_LOSS_OFF`; in that case noirq suspend snapshots every mux register into `saved_vals`, then resume restores all registers before forcing the default pinctrl state. Interrupt enable state is held in hardware registers and rearmed through an optional platform callback.

## Dependencies and Integration Points
This driver depends on OF pinctrl helpers, generic pinctrl/pinmux registries, generic pinconf encodings, MMIO accessors, platform resources, optional platform data for OMAP PRM wake rearm, and irqdomain/chained IRQ APIs. Compatible strings select plain pinctrl, pinconf-capable pinctrl, shared wake IRQ variants, and context-loss variants. Consumer-facing integration is through device tree states using `pinctrl-single,pins`, `pinctrl-single,bits`, optional `pinctrl-single,gpio-range`, generic pinconf-like vendor properties, and standard pinctrl consumer state selection.

## Risks
The DT parser is permissive in some partial-failure paths: several loops break after invalid rows but still add functions/groups using the `found` count, so malformed DT may produce partial mappings. Pinconf get/set depends on a pin already having a mux setting; unconfigured pins return `-ENOTSUPP`. The width switch lacks an explicit error for unsupported widths, so a bad `register-width` can leave read/write callbacks unset. IRQ handling assumes one wake/status bit per mux register and uses register offsets as hwirqs, which is simple but narrow. Legacy property patching only works for built-in configurations. Context save uses `GFP_ATOMIC` and supports only 16/32/64-bit cases even though probe allows 8-bit accessors.

## Test Signals
Useful tests include DT binding probes for 8/16/32-bit register widths, one-register and bit-per-mux maps, invalid offsets, pinconf two-cell/four-cell properties, GPIO range request switching, shared and chained wake IRQ paths, suspend/resume with context-loss compatibles, and debugfs pin display. Kernel test signals are successful `devm_pinctrl_register_and_init()`, `pinctrl_enable()`, expected register writes under `pcs_set_mux()`, correct irqdomain mapping through `irq_create_of_mapping()`, and absence of partial groups when DT input is invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-single.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-st.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-st.c

## Purpose
`pinctrl-st.c` implements the STMicroelectronics STi pin controller and GPIO bank driver. It models eight-pin PIO banks, syscfg-backed mux/config fields, optional retiming controls, GPIO direction/data registers, and GPIO IRQ handling for STiH407-related compatibles. It registers pinctrl, pinmux, pinconf, and gpiochip interfaces from one platform device.

## Important APIs, Types, and Functions
`struct st_pinctrl` is the top-level device state with the pinctrl device, bank array, parsed functions/groups, syscon regmap, SoC data, and optional irqmux base. `struct st_gpio_bank` embeds a `gpio_chip`, `pinctrl_gpio_range`, MMIO PIO base, `struct st_pio_control`, software edge-IRQ state, and a spinlock. `struct st_pctl_data` describes compatible-specific syscfg register offsets and retiming style. `struct st_pctl_group`, `struct st_pmx_func`, and `struct st_pinconf` hold DT-derived functions, groups, per-pin configs, and alt function numbers.

Key paths include `st_pctl_probe_dt()` for DT discovery, `st_gpiolib_register_bank()` for each GPIO bank, `st_parse_syscfgs()` for regmap-field setup, `st_pctl_parse_functions()` and `st_pctl_dt_parse_groups()` for ST `st,pins` parsing, `st_pmx_set_mux()` for mux writes, `st_pinconf_set()`/`st_pinconf_get()` for opaque ST pinconf words, and `__gpio_irq_handler()` plus parent chained handlers for IRQ dispatch.

## Control Flow
Probe validates OF, counts child nodes into GPIO banks and function groups, allocates arrays, resolves the `st,syscfg` syscon regmap, selects compatible data, optionally maps an `irqmux` resource and installs an irqmux chained parent handler, creates pin descriptors, then iterates children. GPIO-controller children become gpiochips with pin ranges, optional parent IRQs, and syscfg field mappings. Non-GPIO children become functions with child groups; each group parses properties under a `st,pins` subnode where each property encodes bank phandle, offset, mux, direction, and optional retime fields.

Pinmux state application is direct: for every pin in the selected group, `st_pmx_set_mux()` finds the bank control and writes a four-bit alternate function field in the bank's `alt` regmap field. GPIO direction requests force function zero and write PIO PC0/PC1/PC2 set/clear registers. Pinconf writes update output-enable, pull-up, open-drain, and retime fields depending on packed or dedicated style.

## State and Persistence
The hardware state lives in syscfg regmap fields and PIO MMIO registers. Parsed function/group arrays are devm lifetime allocations. There is no suspend/resume context save in this file; persistence relies on hardware retention or system-level restore. IRQ edge mode is software state in `bank->irq_edge_conf`, protected by `bank->lock`, because hardware supports level comparisons rather than true edge IRQs. GPIO line ownership is managed by gpiochip and pinctrl range integration, while mux/config writes are not globally serialized beyond the regmap/PIO operations and IRQ-edge spinlock.

## Dependencies and Integration Points
The driver integrates with syscon/regmap for mux and retiming controls, platform MMIO resources for PIO banks, OF aliases for bank numbering, OF IRQ resources for bank interrupts, optional top-level irqmux, gpiochip irq helpers, and pinctrl consumer maps. It uses `arch_initcall`, so ordering matters for early platform users. The DT contract is ST-specific: child GPIO nodes, `st,syscfg`, `st,bank-name`, optional `st,retime-pin-mask`, function/group child nodes, and `st,pins` property lists.

## Risks
The ST pinconf format is a driver-private packed `unsigned long`; it is not generic pinconf and requires exact DT macro values. `st_pctl_dt_calculate_pin()` depends on GPIO banks being registered before function parsing and on OF phandles matching bank fwnodes. Software edge emulation repeatedly flips comparison polarity and may lose transitions under high frequency or bouncing inputs. Several regmap-field setup failures are collapsed to `-EINVAL`, reducing diagnostics. GPIO bank base numbers are derived from `gpio` aliases and can collide if aliases are wrong. There is no explicit rollback for a top-level irqmux chained handler if a later probe step fails.

## Test Signals
Test with representative STiH407 DTs containing multiple GPIO banks, syscfg phandles, function groups, and retime masks. Validate mux register fields through regmap reads after selecting states, GPIO direction through PIO PC registers, pinconf debugfs formatting, packed/dedicated/no retime compatibles, level IRQs, rising/falling/both software edge IRQs, and irqmux fan-in. Failure tests should cover missing `st,syscfg`, missing GPIO banks, malformed `st,pins`, invalid IRQ resources, and inconsistent GPIO aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-stmfx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-stmfx.c

## Purpose
`pinctrl-stmfx.c` is the pinctrl, GPIO, pinconf, IRQ, and PM driver for the STMicroelectronics STMFX MFD GPIO expander. It exposes up to 24 GPIO/alternate-GPIO pins over the parent STMFX regmap and enables only the GPIO functions that are represented by `gpio-ranges`.

## Important APIs, Types, and Functions
`struct stmfx_pinctrl` holds the parent `struct stmfx`, pinctrl and gpiochip instances, a mutex used as IRQ bus lock, a valid GPIO mask, cached IRQ source/type/event/toggle arrays, and PM backup arrays. GPIO callbacks are `stmfx_gpio_get()`, `stmfx_gpio_set()`, direction get/input/output helpers, all operating on three banks of eight bits. Pinconf helpers map generic parameters to STMFX `GPIO_TYPE` and `GPIO_PUPD` semantics: `stmfx_pinconf_get()`, `stmfx_pinconf_set()`, and debug display. IRQ behavior is defined by `stmfx_pinctrl_irq_chip`, `stmfx_pinctrl_irq_set_type()`, `stmfx_pinctrl_irq_bus_sync_unlock()`, `stmfx_pinctrl_irq_thread_fn()`, and `stmfx_pinctrl_irq_toggle_trigger()`.

## Control Flow
Probe obtains the parent STMFX device, requires `gpio-ranges`, gets the platform IRQ, registers pinctrl with generic per-pin DT config mapping, enables pinctrl, registers a sleeping gpiochip with a threaded nested IRQ domain, enables STMFX GPIO/ALTGPIO functions according to available ranges, then requests the parent threaded IRQ. GPIO reads and writes use `GPIO_STATE`, `GPO_SET`, `GPO_CLR`, and `GPIO_DIR` registers. Pinconf get derives generic bias/drive/level answers from direction, type, pull, and output state.

IRQ type changes update cached arrays while holding the irq bus lock. Sync unlock writes event, type, and source arrays in bulk. For both-edge IRQs, the driver defers current-level sampling to sync-unlock because set-type may be atomic, then toggles the hardware edge polarity after each nested interrupt.

## State and Persistence
Hardware state is in STMFX registers accessed through the parent regmap. IRQ configuration is cached in `irq_gpi_src`, `irq_gpi_type`, `irq_gpi_evt`, and `irq_toggle_edge` so atomic irqchip callbacks avoid I2C/register accesses until bus sync. Suspend backs up GPIO state, direction, type, and pull registers; resume restores direction/type/pull/output state and IRQ event/type/source registers. Remove disables GPIO and alternate GPIO functions through the parent MFD function API.

## Dependencies and Integration Points
The driver depends on the STMFX MFD core (`stmfx_function_enable/disable`, `struct stmfx`, register definitions), regmap, platform IRQs, pinctrl utils, generic pinconf DT per-pin mapping, gpiochip nested threaded IRQ support, and PM sleep callbacks. Consumers use normal GPIO descriptors and pinctrl pin configuration; pin availability is governed by `gpio-ranges` rather than all 24 pins being blindly usable.

## Risks
The `IRQ_TYPE_EDGE_BOTH` non-toggle branch in `stmfx_pinctrl_irq_set_type()` clears `irq_toggle_edge[reg]` with `&= mask`, which preserves only the current bit instead of clearing it; this is suspicious and worth review. Both-edge support depends on reading GPIO state and rewriting trigger polarity after handling, so fast transitions can be missed. `stmfx_pinctrl_irq_thread_fn()` temporarily clears IRQ source enables by writing zeros, which reduces reentry but creates a window controlled by the parent interrupt behavior. Probe requires `gpio-ranges`, so missing DT range data is fatal. Restore writes backed-up `GPIO_STATE` through `GPO_SET`, which restores high outputs but does not explicitly clear low outputs unless prior direction/type state makes that harmless for the hardware.

## Test Signals
Test probe with 16-pin and 24-pin `gpio-ranges`, GPIO get/set/direction over all three register banks, generic pinconf bias/drive/level operations, nested IRQ mask/unmask/type programming, both-edge toggle behavior from both initial levels, suspend/resume register restoration, and function disable on remove. Fault injection should cover regmap bulk read/write failures, missing `gpio-ranges`, unavailable IRQ, and parent STMFX function enable errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-stmfx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-sx150x.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-sx150x.c

## Purpose
`pinctrl-sx150x.c` supports Semtech SX1501-SX1509 I2C GPIO expanders as combined pinctrl, GPIO, pinconf, and optional IRQ controllers. It hides multiple chip register layouts behind a custom regmap and supports 4, 8, and 16 GPIO variants plus the oscillator output pin on SX1507/8/9 devices.

## Important APIs, Types, and Functions
`struct sx150x_device_data` describes each chip model's register offsets, GPIO count, pin descriptors, and model-specific private registers. `struct sx150x_pinctrl` owns the I2C client, regmap, pinctrl device, gpiochip, IRQ cached mask/sense state, mutex, and selected device data. GPIO callbacks implement direction/data access and special OSCIO handling. Pinconf callbacks support pull-up/down, open-drain/push-pull where available, and output level. IRQ callbacks maintain cached edge sense and mask values and dispatch nested interrupts from the IRQ source register.

The custom regmap is the most important abstraction. `sx150x_regmap_reg_width()`, `sx150x_maybe_swizzle()`, `sx150x_regmap_reg_read()`, and `sx150x_regmap_reg_write()` make one logical 32-bit regmap value represent one or more SMBus bytes, including two-bit-per-line `RegSense` and byte-swizzled 16-pin SX1503/SX1506 layouts.

## Control Flow
`sx150x_probe()` checks SMBus functionality, selects OF/I2C match data, initializes the custom cached regmap, initializes hardware, registers pinctrl, configures and registers the gpiochip, optionally configures nested threaded IRQ support if `client->irq` is present, enables pinctrl after gpiochip registration, and adds a pin range. Hardware initialization optionally resets SX1507/8/9 when `semtech,probe-reset` is present, programs miscellaneous/autoclear behavior, and sets pins to normal mode by clearing polarity or PLD mode.

GPIO direction and data access write the logical direction/data registers through regmap. IRQ set-type rejects level IRQs and encodes rising/falling bits into the cached `sense` field; bus sync writes mask and sense registers. The IRQ thread reads and acknowledges the source register, then calls nested IRQ handlers for each active GPIO.

## State and Persistence
The persistent hardware state includes direction, data, pull, drain, polarity/PLD, IRQ mask/source/sense, and oscillator clock registers. Runtime-only cached state includes `pctl->irq.masked` and `pctl->irq.sense`, protected by `pctl->lock` in irq bus lock/unlock. Regmap uses `REGCACHE_MAPLE`, with IRQ source and data marked volatile. There is no suspend/resume path in this file, so restore behavior depends on regmap cache and parent I2C/device power behavior outside this driver.

## Dependencies and Integration Points
The driver integrates with I2C/SMBus byte data, regmap custom bus callbacks, OF/I2C device matching, pinctrl generic per-pin config DT helpers, gpiochip generic config, nested threaded GPIO IRQ support, and subsystem init ordering via `subsys_initcall`. Device tree compatibles choose exact register maps and whether OSCIO is exposed as an extra pin.

## Risks
The source comments state that 4-bit chips are untested. The custom regmap is layout-sensitive; any wrong width or swizzle corrupts multi-byte registers. `sx150x_pinconf_get()` appears to test `if (!ret)` after masking `data` for pull-up/down cases, but `ret` is the successful return code rather than the masked data value; that path likely fails to reject disabled pulls as intended. `sx150x_gpio_set_multiple()` is disabled for SX150X_789 because OSCIO lives in a separate register, but other multi-register edge cases depend on the logical regmap width being correct. IRQ handling supports edge-only IRQs and acknowledges by writing the source value; parent polarity is hard-coded as falling for the requested threaded IRQ.

## Test Signals
Test every compatible's register width calculation, especially SX1503/SX1506 `RegSense` swizzling, GPIO direction/data over 4/8/16-bit devices, OSCIO level behavior, pull-up/down and drain pinconf, optional probe reset, IRQ mask/type/source acknowledgment, and pin range registration. Regression tests should include pull get semantics when the pull bit is disabled, absent IRQ operation, and I2C error propagation from custom regmap reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-sx150x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-tb10x.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-tb10x.c

## Purpose
`pinctrl-tb10x.c` is the Abilis TB10x SoC I/O mux driver. It exposes static pin descriptors and static mux groups, parses simple device-tree function declarations, and arbitrates shared two-bit port mux registers between peripheral functions and GPIO usage.

## Important APIs, Types, and Functions
The static data is extensive: `tb10x_pins[]` lists SoC pins, many `*_pins[]` arrays define groups, and `tb10x_pingroups[]` maps each group to a port, mode, and GPIO/non-GPIO flag. `struct tb10x_port` tracks the current mode and active function reference count per mux port. `struct tb10x_pinctrl` stores the MMIO base, pinctrl device, static group table, dynamic OF function table, mutex, port states, and a bitmap of pins currently requested as GPIOs.

Pinctrl callbacks expose static groups and parse DT nodes through `tb10x_dt_node_to_map()`, which requires `abilis,function`. Pinmux callbacks expose one group per parsed function, request GPIO mode through `tb10x_gpio_request_enable()`, release GPIOs through `tb10x_gpio_disable_free()`, and select muxes through `tb10x_pctl_set_mux()`.

## Control Flow
Probe maps the single mux register resource, initializes the mutex, points at the static group table, snapshots current hardware mode for all nine ports, scans child nodes with `abilis,function` into the flexible `pinfuncs[]` array, and registers pinctrl. When a consumer selects a state, `tb10x_dt_node_to_map()` creates one mux map from child node name to the requested function/group string. `tb10x_pctl_set_mux()` rejects incompatible port modes or pins already requested as GPIO, writes the port mode if no user is active, and increments the port count. GPIO request scans all groups to find whether the pin belongs to a GPIO-capable mux group, checks conflicts against active non-GPIO functions, records the pin in the GPIO bitmap, and writes the GPIO mode if needed.

## State and Persistence
Hardware mux state is a compact MMIO register with two bits per port. The driver snapshots initial modes but does not restore them on remove or suspend. Runtime arbitration state is in `ports[].mode`, `ports[].count`, and `gpios`; it is protected by `state->mutex`. Function reference counts are incremented in `set_mux()` but there is no corresponding function disable callback to decrement them, so selected peripheral functions effectively remain counted for the driver lifetime.

## Dependencies and Integration Points
This driver uses platform MMIO resources, OF child nodes with `abilis,function`, pinctrl utils for map allocation, and the pinmux GPIO request hooks used by external GPIO controllers/ranges. It does not register a gpiochip itself; it only arbitrates muxing for GPIO-capable pins. Integration depends on exact static group names matching the strings referenced in device tree.

## Risks
The missing function-free/decrement path means port `count` can only increase, which is acceptable for static board muxing but risky for dynamic state changes or unload/reload expectations. Because each parsed function exposes only one group string, DT mistakes are caught late by pinctrl matching. Conflict detection scans static groups and relies on group metadata being complete. GPIO-only groups with `port < 0` are always mapped and skip register writes. There is no pinconf, IRQ, or PM handling.

## Test Signals
Test DT parsing with valid and missing `abilis,function`, initial hardware mode snapshots, selecting multiple compatible functions on the same port, rejecting incompatible modes with `-EBUSY`, GPIO request conflicts against active functions, function conflicts against requested GPIOs, and static group/pin enumeration. A useful stress test is repeated state selection/freeing to document the monotonic `ports[].count` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-tb10x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-th1520.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-th1520.c

## Purpose
`pinctrl-th1520.c` is the T-Head TH1520 SoC pinctrl driver. It supports three pad groups, per-pin mux selection, generic pin configuration for padcfg-capable pins, GPIO mux requests, and GPIO input-enable direction control over MMIO registers.

## Important APIs, Types, and Functions
`struct th1520_pad_group` describes one compatible pad bank with a name and static pin descriptor table. `struct th1520_pinctrl` owns the pinctrl descriptor, mutex for dynamically adding functions, raw spinlock for register read/modify/write, base MMIO address, and pinctrl device. Pin descriptors encode possible mux functions and flags in `drv_data` through `TH1520_PAD()`, with `TH1520_PAD_NO_PADCFG` marking pads that cannot be configured.

DT mapping is handled by `th1520_pinctrl_dt_node_to_map()`, which parses child `pins`, optional `function`, and generic pinconf properties. Pinconf is implemented by `th1520_pinconf_get()`, `th1520_pinconf_set()`, and group variants. Muxing is implemented by `th1520_pinmux_set()`, `th1520_pinmux_set_mux()`, and `th1520_gpio_request_enable()`.

## Control Flow
Probe maps MMIO, enables the clock, reads `thead,pad-group`, chooses one of the three static pin groups, initializes the pinctrl descriptor and locks, registers pinctrl, and enables it. For each pinctrl DT state, the map callback counts selected pins, allocates maps, parses generic configs once per child node, validates pin names against the selected pad group, optionally creates per-pin config maps, and, if a function is present, dynamically registers a unique function named from the parent and child node and maps each selected pin group to it.

When a mux is selected, the stored function data is the desired `enum th1520_muxtype`; `th1520_pinmux_set()` scans the pin's encoded mux alternatives to find the selector value and writes four bits in the MUXCFG register. Pinconf set accumulates a 10-bit padcfg mask/value and does one locked RMW of the halfword associated with the pin. GPIO direction only toggles the input-enable bit; output behavior is presumably handled by the separate GPIO controller.

## State and Persistence
Hardware state lives in PADCFG registers, two pins per 32-bit word, and MUXCFG registers, eight pins per 32-bit word. Register updates are serialized by `raw_spinlock_t lock`. Dynamic functions and group names are devm allocations or generic pinmux registrations protected by `mutex`. There is no suspend/resume context save; state persistence depends on SoC retention or pinctrl consumers reapplying states after resume.

## Dependencies and Integration Points
The driver depends on platform resources, clocks, OF properties, generic pinctrl/pinmux/pinconf frameworks, dynamic generic function registration, and optional debugfs hooks. Its DT integration requires `thead,pad-group` and state child nodes with `pins`, optional `function` strings from the driver's mux string table, and standard generic pinconf properties. GPIO integration uses pinmux hooks only; it does not register a gpiochip.

## Risks
`th1520_drive_strength_from_ma()` loops while `ds < TH1520_PADCFG_DS`, where `TH1520_PADCFG_DS` is a bitmask value rather than the array length; this works only because the mask is 15 and the table has 16 entries, but it is fragile. Dynamic functions are added during DT map creation and are not explicitly removed on map free, so repeated mapping of many unique child nodes could accumulate generic functions for device lifetime. Pins marked no-padcfg reject pinconf, which DT authors must handle. The code does not validate that requested generic configs are electrically meaningful together, for example strong pull-up versus regular pull-up selection beyond fixed resistance constants.

## Test Signals
Test all three `thead,pad-group` values, invalid pad group, clock failure, DT mapping with multiple child nodes and repeated pins, unknown pin and unknown function failures, mux writes for every function slot position, GPIO request selecting GPIO mux, generic pinconf for bias, drive strength, input enable, Schmitt, and slew, plus no-padcfg rejection. Debugfs output should show correct PADCFG/MUXCFG addresses and values for selected pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-th1520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-tps6594.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-tps6594.c

## Purpose
`pinctrl-tps6594.c` is the pinmux and GPIO-regmap driver for TI TPS6594-family PMICs, including TPS6593, TPS6594, LP8764, TPS65224, and TPS652G1 variants. It exposes PMIC GPIO pins as pinctrl groups, maps named alternate functions to GPIO configuration register mux values, and registers GPIO access through `gpio-regmap`.

## Important APIs, Types, and Functions
Function tables are built from `struct tps6594_pinctrl_function`, which combines a `struct pinfunction` with a mux value. Variant templates (`tps6594_template_pinctrl`, `tps65224_template_pinctrl`, `tps652g1_template_pinctrl`) select pins, functions, mux mask, remap table, and counts. `struct muxval_remap` handles pins whose mux value differs from the common function value. `struct tps6594_pinctrl` stores the parent MFD pointer, gpio-regmap device, pinctrl device, selected tables, mux mask, and remap metadata.

Pinctrl callbacks enumerate one group per pin and use `pinconf_generic_dt_node_to_map_group()` for DT maps. Pinmux callbacks enumerate functions, return legal groups from the static pinfunction definitions, set muxes with `tps6594_pmx_set_mux()`, and force GPIO muxing from `tps6594_pmx_gpio_set_direction()`. GPIO register translation is handled by `tps6594_gpio_regmap_xlate()`.

## Control Flow
Probe obtains the parent `struct tps6594`, allocates a pinctrl descriptor and state, switches on `tps->chip_id`, copies the relevant template, fills `gpio_regmap_config`, registers pinctrl, then registers gpio-regmap. The mux path gets the selected function's default mux value, applies any group-specific remap, and writes the mux select bits in `TPS6594_REG_GPIOX_CONF(pin)` with `regmap_update_bits()`. GPIO-regmap translates direction, input, and output base registers into the correct PMIC register and bit mask; GPIO direction output uses the direction bit in each GPIO configuration register.

## State and Persistence
State is entirely in the PMIC regmap registers plus static per-variant tables copied at probe. There is no local locking in this file; regmap and gpio-regmap provide the access serialization. There is no suspend/resume handling here, so persistence depends on PMIC retention and parent MFD/regmap behavior. No pinconf operations are implemented beyond group DT mapping; this file is mux and GPIO only.

## Dependencies and Integration Points
The driver depends on the TPS6594 MFD core for chip ID, register definitions, and regmap; pinctrl/pinmux core; generic pinconf group DT map helpers; platform device matching from the MFD; and `gpio-regmap` for GPIO operations. Consumers select named functions such as `nsleep1`, `wkup`, `clk32kout`, `scl_i2c2_cs_spi`, or variant-specific names on named groups `GPIO0`...`GPIO10` or `GPIO0`...`GPIO5`.

## Risks
The default switch case in probe leaves the descriptor and template largely empty but still proceeds, so an unsupported `chip_id` from the parent could register a broken zero-pin controller instead of failing. Remap tables are essential for special pins; missing entries silently write the common mux value. `tps6594_pmx_gpio_set_direction()` ignores the `input` argument and only selects GPIO mux, leaving actual direction to gpio-regmap. No explicit IRQ or pinconf support is provided here, so expectations must be met by other PMIC blocks or not advertised. Static template structs are copied then patched with `tps`, which is fine, but future mutable fields should avoid sharing through template pointers.

## Test Signals
Test probe for every supported chip ID, group/function enumeration counts, DT mux selection for every function's legal group list, remapped mux values on TPS6594 GPIO8/GPIO9 and TPS65224 GPIO5, GPIO input/output register translation across one-register and two-register layouts, unsupported chip ID behavior, and regmap error propagation from mux writes and gpio-regmap registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-tps6594.c -->
