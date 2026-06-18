# Research: subset-b-005074

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rk805.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rk805.c

## Purpose
This driver exposes the GPIO-capable pins on Rockchip RK805, RK806, and RK816 PMICs as both a `gpio_chip` and a pinctrl provider. It is a child platform driver of the RK808-family MFD device and uses the parent PMIC regmap to switch pin mux functions, read/write GPIO values, and control direction where the PMIC variant supports it. The hardware surface is small: RK805 has two output-only GPIOs, RK806 has three sleep/power-control pins with multiple function selections, and RK816 has one pin that can be thermistor or GPIO.

## Important APIs, Types, And Functions
`struct rk805_pctrl_info` is the central state object, holding the parent `struct rk808`, device, registered `pinctrl_dev`, embedded `gpio_chip`, copied `pinctrl_desc`, and variant-selected pin/function/group/config tables. `struct rk805_pin_config` maps each logical pin to the PMIC register and masks for function, direction, and value bits. Static tables define pin descriptors, groups, and functions for RK805/RK806/RK816.

Gpiolib callbacks are `rk805_gpio_get()`, `rk805_gpio_set()`, `rk805_gpio_direction_output()`, and `rk805_gpio_get_direction()`. Pinctrl callbacks are the simple group/function enumerators plus `rk805_pinctrl_set_mux()`, `rk805_pinctrl_gpio_request_enable()`, and `rk805_pmx_gpio_set_direction()`. Pinconf support is limited to `PIN_CONFIG_LEVEL` and `PIN_CONFIG_INPUT_ENABLE` through `rk805_pinconf_get()` and `rk805_pinconf_set()`.

## Control Flow
Probe attaches the child device firmware node to the parent MFD node, allocates state, copies the template gpio and pinctrl descriptors, then switches on `rk808->variant` to select the correct pin tables and `pin_cfg` array. It registers the GPIO chip first, then the pinctrl device, and finally adds a one-to-one GPIO pin range.

GPIO reads and writes are direct `regmap_read()` and `regmap_update_bits()` operations against the parent PMIC. Direction output sets the requested value first, then asks pinctrl to program output mode. GPIO request-enable selects the GPIO mux value for RK805 and RK816, but uses RK806 function 5 as the GPIO function. Pinconf level configuration similarly writes the value and forces output direction, while input-enable is accepted only for non-RK805 variants with a nonzero argument.

## State And Persistence
The driver has no persistent storage and no PM callbacks of its own. Software state is the variant-selected static table set plus gpiolib/pinctrl registration state. Pin value, mux, and direction persist in PMIC registers until changed by firmware, reset, suspend policy, or another PMIC user. RK805 pins intentionally behave as output-only because their `dir_msk` and `fun_msk` fields are absent.

## Dependencies And Integration Points
It depends on the RK808 MFD core for `struct rk808`, variant IDs, register definitions, and the regmap. It integrates with platform-device child creation from the MFD, gpiolib, pinctrl, pinmux, generic pinconf DT parsing via `pinconf_generic_dt_node_to_map_pin()`, and `gpiochip_add_pin_range()`. Device-tree consumers see the parent PMIC firmware node rather than a separate child node because probe calls `device_set_node()`.

## Risks And Test Signals
Risk is concentrated in variant-specific masks: a wrong `fun_msk`, `dir_msk`, or `val_msk` writes PMIC power/sleep control bits rather than ordinary GPIO state. `_rk805_pinctrl_set_mux()` logs regmap failures but returns 0, so mux write failures can be hidden from pinctrl consumers. RK805 input-enable is intentionally unsupported, and RK806 GPIO selection depends on function 5 rather than a function named `gpio`. Test signals include successful probe for all three variants, correct gpio count and pin names, output-only behavior on RK805, RK816 thermistor/GPIO mux switching, RK806 function selection across all three pins, pinconf `level` writes, input-enable rejection/acceptance by variant, and regmap error injection for value/direction paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rk805.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rockchip.c

## Purpose
This is the main Rockchip SoC pinctrl driver. It registers a pin controller for many Rockchip SoCs, parses Rockchip-specific pin groups from device tree, applies mux and pin configuration settings through GRF/PMU/IOC regmaps, and then populates child GPIO-bank devices that use the shared data structures from `pinctrl-rockchip.h`. It covers old 2-bit IOMUX controllers through modern RK3588-style split IOC layouts, with per-SoC register calculators for mux, pull, drive strength, and Schmitt trigger settings.

## Important APIs, Types, And Functions
The file is built around `struct rockchip_pinctrl`, `struct rockchip_pin_ctrl`, and `struct rockchip_pin_bank` from the companion header. Bank macros such as `PIN_BANK*` and `RK3588_PIN_BANK_FLAGS()` define each SoC's bank layout, mux width/source flags, pull types, drive types, and explicit offsets. Per-SoC `*_pin_ctrl` objects select the bank list, register offset bases, route/recalculation tables, and calculator callbacks.

Core pinctrl ops are `rockchip_get_groups_count()`, `rockchip_get_group_name()`, `rockchip_get_group_pins()`, and `rockchip_dt_node_to_map()`. Mux operations are `rockchip_get_mux()`, `rockchip_verify_mux()`, `rockchip_set_mux()`, `rockchip_pmx_set()`, and `rockchip_pmx_gpio_request_enable()`. Pin configuration flows through `rockchip_get_pull()`, `rockchip_set_pull()`, `rockchip_get_drive_perpin()`, `rockchip_set_drive_perpin()`, `rockchip_get_schmitt()`, `rockchip_set_schmitt()`, `rockchip_pinconf_set()`, and `rockchip_pinconf_get()`. Probe is split between `rockchip_pinctrl_get_soc_data()`, `rockchip_pinctrl_register()`, `rockchip_pinctrl_parse_dt()`, and `rockchip_pinctrl_probe()`.

## Control Flow
Probe matches the SoC compatible to a `rockchip_pin_ctrl`, computes cumulative pin bases and per-bank register offsets, and builds `recalced_mask` and `route_mask` bitmaps from SoC tables. It obtains the primary GRF regmap from `rockchip,grf` or maps the controller MMIO resource for older bindings, optionally obtains `rockchip,pmu` and `rockchip,ioc1`, registers the pinctrl device, stores driver data, and calls `of_platform_populate()` so GPIO-bank child devices can bind.

Device-tree parsing counts function nodes excluding GPIO-bank nodes. Each function child owns one or more group nodes, and each group provides `rockchip,pins` entries in `<bank pin mux config-phandle>` tuples. The driver converts these into pinctrl mux maps and per-pin config maps. Selecting a function iterates all pins in the group and calls `rockchip_set_mux()` with rollback to GPIO on partial failure.

Mux programming selects PMU, base GRF, or special IOC regmaps from bank flags and SoC quirks. It handles 2-, 3-, and 4-bit mux fields, recalculated pin positions, route registers for alternate IO paths, RK3576 bank-0 high offsets, and RK3588 PMU2/BUS IOC split behavior for GPIO0 and other banks. Pull, drive, and Schmitt programming dispatch to the selected SoC calculator, translates generic pinconf values to hardware encodings, and writes Rockchip high-word write-enable masks through regmap.

## State And Persistence
Runtime software state includes parsed functions/groups, per-bank pin bases, computed register offsets, route/recalculated masks, deferred pin configuration lists, and the registered pinctrl descriptor. Hardware state persists in GRF/PMU/IOC registers until reset or later pinctrl changes. `rockchip_pinconf_set()` defers `PIN_CONFIG_LEVEL` and `PIN_CONFIG_INPUT_ENABLE` when the GPIO child has not probed yet; `rockchip_pinctrl_remove()` frees any deferred entries. System suspend forces the sleep pinctrl state and, for RK3288, snapshots GPIO6_C6 IOMUX because mask ROM may modify it on resume; resume restores that register and forces the default pinctrl state.

## Dependencies And Integration Points
The driver depends on OF platform probing, syscon/regmap, the generic pinctrl/pinmux/pinconf core, Rockchip DT bindings, and the separate Rockchip GPIO-bank driver that consumes `struct rockchip_pin_bank`. It is registered with `postcore_initcall()` so pinctrl and GPIO infrastructure is available early. Compatible strings cover PX30, RV1103B, RV1108, RV1126, RK2928, RK3036, RK3066A/B, RK3128, RK3188, RK3228, RK3288, RK3308, RK3328, RK3368, RK3399, RK3506, RK3528, RK3562, RK3568, RK3576, and RK3588.

## Risks And Test Signals
The highest risk is SoC-specific register math: mux widths, PMU-vs-GRF source flags, explicit offsets, recalculated bits, and route registers must match the TRM exactly. RK3588 and RK3576 special cases are particularly sensitive because one logical bank may span multiple IOC regions. Deferred GPIO-related pinconf depends on ordering with the GPIO driver and correct locking. `rockchip_pinctrl_parse_groups()` trusts each config phandle to parse as generic pinconf, so DT errors surface at probe. Test signals include probe and pin enumeration on each compatible, DT group parsing failures for malformed `rockchip,pins`, mux set/get for PMU and GRF banks, route table programming for alternate functions, pull/drive/Schmitt get/set at bank boundaries, RK3568 GPIO0 D3-D6 pull-up remap, RK3288 suspend/resume restoration, deferred level/input-enable application after GPIO-bank probe, and child GPIO-bank population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rockchip.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rockchip.h

## Purpose
This header is the shared contract between the Rockchip pinctrl driver and the Rockchip GPIO-bank driver. It defines logical pin numbers, SoC type identifiers, GPIO register layout descriptions, per-bank pinctrl metadata, mux route/recalculation tables, parsed DT group/function structures, and the top-level controller state. It lets `pinctrl-rockchip.c` own mux/pinconf parsing while `gpio-rockchip.c` owns GPIO and IRQ-bank registration against the same `rockchip_pin_bank` instances.

## Important APIs, Types, And Functions
The first section defines stable logical pin numbers for GPIO banks 0 through 4, each with A/B/C/D groups of eight pins. `enum rockchip_pinctrl_type` names every SoC variant handled by the driver. `struct rockchip_gpio_regs` describes GPIO register offsets for different GPIO IP versions.

`struct rockchip_iomux` records IOMUX flags and offsets. `enum rockchip_pin_drv_type` and `enum rockchip_pin_pull_type` describe hardware encoding families. `struct rockchip_drv` stores per-eight-pin drive metadata. `struct rockchip_pin_bank` is the central per-bank object: it holds MMIO/regmap/clock/IRQ handles, pin numbering, mux/drive/pull descriptors, GPIO-chip and pinctrl-range instances, IRQ-domain state, locks, register-layout pointer, SoC quirk masks, and deferred pinconf entries.

`struct rockchip_pin_ctrl` describes one SoC family, including the bank array, base offsets, route/recalculated mux tables, and calculator callbacks. `struct rockchip_pin_config`, `struct rockchip_pin_group`, and `struct rockchip_pmx_func` represent parsed device-tree pin groups and functions. `struct rockchip_pinctrl` holds the controller-wide regmaps, registered pinctrl descriptor, parsed groups/functions, and the selected SoC control data.

## Control Flow
There is no runtime code in the header, but the data flow is explicit. `pinctrl-rockchip.c` fills `rockchip_pin_ctrl` static instances with `rockchip_pin_bank` arrays. During probe it computes `pin_base`, register offsets, route masks, and recalculation masks inside each bank, then registers pinctrl groups/functions. `gpio-rockchip.c` later finds the same bank objects, maps each bank's GPIO MMIO, registers gpiolib/IRQ state, and drains deferred pin configuration lists stored in `rockchip_pin_bank`.

## State And Persistence
The header defines in-memory state layouts rather than persistence mechanisms. `rockchip_pin_bank` carries both static SoC description fields and mutable runtime fields such as `saved_masks`, `toggle_edge_mode`, `domain`, `gpio_chip`, `grange`, and `deferred_pins`. Hardware persistence is represented indirectly through regmap/MMIO handles and register offsets; suspend state for GPIO IRQ masks lives in fields defined here but is acted on by implementation files.

## Dependencies And Integration Points
The types intentionally bind pinctrl, gpiolib, irqdomain, clock, regmap, and device-tree code. Because the GPIO driver includes this header, field changes in `rockchip_pin_bank` or `rockchip_pinctrl` are cross-driver ABI changes within the kernel tree. The header also encodes assumptions about Rockchip GPIO register naming and about the bank size grouping used by the pinctrl driver, especially the four IOMUX/drive/pull descriptors per bank.

## Risks And Test Signals
The main risk is structural coupling: adding a SoC or altering a field can break either pinctrl or GPIO-bank code. `nr_pins`, `pin_base`, and `nr_banks` must remain consistent or pin-to-bank lookup and GPIO ranges become wrong. Deferred pin configuration requires the list and mutex fields to be initialized before GPIO-bank probe. Test signals include building both Rockchip pinctrl and GPIO drivers together, probing with old and new GPIO register layouts, validating pin numbers and ranges against DT bindings, exercising deferred pinconf handoff, and checking suspend/resume IRQ-mask fields through the GPIO driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rockchip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rp1.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rp1.c

## Purpose
This driver supports the Raspberry Pi RP1 GPIO unit as a combined pinctrl, pinmux, pinconf, GPIO, and GPIO-IRQ provider. It exposes 54 GPIOs split across three RP1 IO banks, supports both modern generic pinctrl bindings and legacy Broadcom-style `brcm,pins` bindings, maps RP1 alternate functions to Linux pinctrl functions/groups, and programs GPIO, RIO, interrupt-enable, and pad-control register blocks through regmap fields.

## Important APIs, Types, And Functions
`struct rp1_pinctrl` is the controller state: three MMIO bases, parent IRQs, per-pin `struct rp1_pin_info`, registered `pinctrl_dev`, embedded `gpio_chip`, GPIO range, and one raw spinlock per IO bank. `struct rp1_pin_info` stores the logical GPIO number, bank, bank-local offset, current IRQ type, and arrays of `regmap_field` handles for GPIO control, RIO value/direction, interrupt enable, and pad controls. Static tables define pins, peripheral groups, functions, per-pin function-select mappings, legacy function maps, and the three IO-bank register-offset descriptions.

Core helpers are `rp1_get_fsel()`, `rp1_set_fsel()`, `rp1_get_dir()`, `rp1_set_dir()`, `rp1_get_value()`, and `rp1_set_value()`. GPIO callbacks wrap these helpers. IRQ support is implemented by `rp1_gpio_irq_handler()`, `rp1_gpio_irq_config()`, `rp1_irq_set_type()`, `rp1_gpio_irq_set_type()`, `rp1_gpio_irq_ack()`, and `rp1_gpio_irq_set_affinity()`. Pin parsing and muxing use `rp1_pctl_dt_node_to_map()`, `rp1_pctl_legacy_map_func()`, `rp1_pctl_legacy_map_pull()`, `rp1_pmx_set()`, and `rp1_pmx_free()`. Pinconf operations are `rp1_pinconf_set()`, `rp1_pinconf_get()`, and group wrappers.

## Control Flow
Probe maps GPIO, RIO, and PADS resources, creates regmaps with explicit readable/writable ranges, and for each bank/pin allocates the needed `regmap_field` objects with `rp1_gen_regfield()`. It registers the pinctrl device, configures the embedded `gpio_irq_chip` with up to three parent IRQs parsed from DT, registers the GPIO chip, and adds a pinctrl GPIO range.

GPIO direction output writes the value, sets RIO output enable, and selects GPIO function. Direction input clears output enable and selects GPIO function. `rp1_set_fsel()` enables pad input and output by default, selects peripheral output overrides for normal functions, disables output-enable override for `none`, and writes the hardware function-select value. Pinctrl muxing translates abstract function names back to the FSEL slot supported by each pin, then programs every pin in the selected group.

The IRQ parent handler determines which IO bank fired, reads the bank interrupt status register, clears the per-pin latched event, and dispatches mapped child IRQs. Type configuration clears all interrupt flags, sets the requested edge/level bits, records `pin->irq_type`, and installs edge or level handlers under the bank raw spinlock. Legacy DT parsing converts `brcm,function` and `brcm,pull` arrays into mux and config maps, with scalar-or-per-pin validation.

## State And Persistence
Software state includes allocated regmap fields, the parent IRQ array, per-pin IRQ type, and the module parameter `persist_gpio_outputs`. Pin mux, GPIO direction/value, interrupt type/enable, and pad configuration persist in RP1 registers. When a pin is freed, `rp1_pmx_free()` normally returns it to GPIO input; if `persist_gpio_outputs` is true and the pin is already GPIO, it leaves outputs in place. There are no explicit suspend/resume callbacks in this file.

## Dependencies And Integration Points
The driver depends on platform MMIO resources, OF IRQ parsing, regmap and regmap-field APIs, pinctrl/pinmux/pinconf core APIs, gpiolib with hierarchical parent IRQ support, and Raspberry Pi RP1 DT compatible `raspberrypi,rp1-gpio`. It integrates with both modern function/group-based pinctrl consumers and older Raspberry Pi/Broadcom overlays using `brcm,pins`, `brcm,function`, and `brcm,pull`.

## Risks And Test Signals
Risk centers on table correctness and bank-local indexing. The parent IRQ handler reads a 32-bit bank status and iterates set bits as bank-local offsets, so mapping must match `rp1_iobanks`. Legacy mapping has strict array-length rules and can reject overlays with mismatched `brcm,function` or `brcm,pull` counts. The static `rp1_pinctrl_data` means the driver expects one controller instance. `rp1_pinconf_get()` relies on all pad drive encodings being known; invalid hardware values would leave `arg` undefined. Test signals include probe with one, two, and three parent IRQs, GPIO value/direction on all banks, mux selection for direct FSEL functions and named peripheral functions, legacy DT mappings, all IRQ trigger types and affinity delegation, pad pull/drive/slew/Schmitt get/set, `persist_gpio_outputs` free behavior, and invalid pin/function rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-scmi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-scmi.c

## Purpose
This driver exposes pins, groups, functions, muxing, and pin configuration supplied by firmware through the ARM SCMI pinctrl protocol as a Linux pinctrl provider. Instead of programming local MMIO registers, it delegates all enumeration, mux, request/free, and configuration operations to `struct scmi_pinctrl_proto_ops` obtained from the SCMI core.

## Important APIs, Types, And Functions
`struct scmi_pinctrl` stores the device, SCMI protocol handle, registered pinctrl device, descriptor, lazily populated function cache, and function count. Pinctrl operations call SCMI protocol methods: `count_get()`, `name_get()`, `group_pins_get()`, and `function_groups_get()`. Pinmux operations are `pinctrl_scmi_func_set_mux()`, `pinctrl_scmi_request()`, and `pinctrl_scmi_free()`.

Pinconf translation is centralized in `pinctrl_scmi_map_pinconf_type()`, with get/set wrappers mapping `PIN_CONFIG_LEVEL` to input or output value. `pinctrl_scmi_pinconf_get()` and group get call `settings_get_one()`. `pinctrl_scmi_pinconf_set()` and group set build arrays of SCMI config types/values and call `settings_conf()`. `pinctrl_scmi_get_pins()` builds the pin descriptor table from SCMI pin names. `scmi_pinctrl_probe()` obtains protocol ops, initializes the descriptor, allocates function cache storage, registers, and enables the pinctrl device.

## Control Flow
Probe first rejects devices without an SCMI handle and blocklists several NXP machine compatibles. It obtains the SCMI pinctrl protocol and protocol handle with `devm_protocol_get()`, allocates driver state, fills pinctrl/pinmux/pinconf ops, reads all pin names from firmware, registers the pinctrl provider with `devm_pinctrl_register_and_init()`, allocates one `struct pinfunction` entry per SCMI function, and calls `pinctrl_enable()`.

Group and function names are fetched on demand from firmware. Function-to-group lists are cached the first time `get_function_groups` is called: SCMI returns group IDs, the driver resolves each ID to a group name, stores the allocated name pointer array in `pmx->functions[selector]`, and reuses it thereafter. Pin and group configs are mapped from Linux generic pinconf parameters to SCMI config IDs. For more than four configs, temporary arrays are heap allocated; four or fewer use stack arrays. `PIN_CONFIG_PERSIST_STATE` is silently skipped for per-pin set.

## State And Persistence
The driver keeps minimal software state: pin descriptors allocated at probe and lazily populated function group arrays. Hardware or firmware state is external to Linux and persists according to platform SCMI firmware policy. There are no local MMIO registers, no GPIO chip, and no suspend/resume hooks. Names returned by SCMI are treated as firmware-owned memory.

## Dependencies And Integration Points
It depends on the SCMI core, `SCMI_PROTOCOL_PINCTRL`, generic pinctrl/pinmux/pinconf infrastructure, optional OF mapping via `pinconf_generic_dt_node_to_map_all()`, and the SCMI device table entry `{ SCMI_PROTOCOL_PINCTRL, "pinctrl" }`. It is a firmware-mediated integration point for platforms where the secure or system controller owns pin programming.

## Risks And Test Signals
Correctness depends on firmware faithfully reporting counts, names, group IDs, and supported configuration types. The file uses a global `pinctrl_ops` pointer, so multiple SCMI pinctrl devices would share the last protocol-ops pointer even though protocol operations are expected to be common. Per-pin set skips `PIN_CONFIG_PERSIST_STATE`, but group set does not special-case it. Heap allocation paths for large config lists need cleanup on mapping failures. Test signals include probe with nonzero pin/function/group counts, function group caching, mux set calls reaching firmware, request/free calls, all mapped generic pinconf get/set types, `PIN_CONFIG_LEVEL` input/output mapping, conversion of `-EOPNOTSUPP` to `-ENOTSUPP`, large config arrays beyond four entries, OF pinconf map parsing, and machine blocklist rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-scmi.c -->
