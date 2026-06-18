# Research Report: subset-b-005068

This grouped report covers the requested pinctrl core, AMD, Apple, Axis ARTPEC-6, AS3722, and Atmel/Microchip AT91 pin control sources. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf-generic.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf-generic.c

Purpose: Implements the generic pin configuration helpers shared by pinctrl drivers that opt into generic pinconf. It covers debugfs decoding of generic and custom parameters, firmware/DT parsing of generic pinconf properties, packed `pinmux` decoding, and translation of DT subnodes into pinctrl maps.

Important APIs and functions: `pinconf_generic_dump_pins()` and `pinconf_generic_dump_config()` expose readable debug output for `struct pin_config_item` definitions. `parse_fw_cfg()` is the internal firmware-property parser. Exported DT helpers are `pinconf_generic_parse_dt_pinmux()`, `pinconf_generic_parse_dt_config()`, `pinconf_generic_dt_subnode_to_map()`, `pinconf_generic_dt_node_to_map()`, and `pinconf_generic_dt_free_map()`. The `dt_params[]` table maps standard property names such as `bias-pull-up`, `drive-strength`, `input-debounce`, `output-high`, `slew-rate`, and skew/voltage properties to `enum pin_config_param` values.

Control flow: DT map creation starts at `pinconf_generic_dt_node_to_map()`, tries the parent node, then each available child. Each subnode selects either a `"pins"` or `"groups"` target list, optionally parses `"function"`, calls `pinconf_generic_parse_dt_config()`, reserves map entries, then emits mux and config maps per string target. Config parsing allocates a temporary max-sized array, parses generic parameters, then driver custom parameters if present, and shrinks to an exact `kmemdup()` result. Debug dumping probes each possible parameter by calling pin or group get callbacks and prints only supported values.

State and persistence: The file keeps no persistent runtime state. It allocates transient config arrays and bitmaps while parsing, then hands immutable packed config arrays to pinctrl map structures. Persistence occurs in consumer drivers when the pinctrl core applies these packed configs to hardware.

Dependencies and integration points: Integrates with firmware node APIs, OF helpers, `pinconf_to_config_packed()`, pinctrl map utilities, generic pinctrl descriptors, custom params/items in `struct pinctrl_desc`, and core pin/group getters from `pinconf.c`.

Risks: `parse_fw_cfg()` returns `-ENOENT` for an unmatched string-valued property, which can abort parsing rather than ignore it. Conflict checks log drive/bias/drive-mode conflicts but only duplicate exact parameters return `-EINVAL`. `par->param <= count` is used to distinguish generic from custom params and depends on enum/table assumptions. Map ownership is subtle because config arrays are freed after `pinctrl_utils_add_map_configs()` duplicates them.

Test signals: DT parsing tests should cover missing/empty `pinmux`, parent and child subnodes, `"pins"` versus `"groups"`, mux-only nodes, config-only nodes, duplicate/conflicting properties, custom parameters, and debugfs output on drivers with `.is_generic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf.c

Purpose: Provides the core pin configuration glue between pinctrl maps/settings and controller driver `pinconf_ops`. It validates maps, converts map names to numeric pin or group selectors, applies settings, exposes direct pin config setting, and creates debugfs views for per-pin and per-group configuration.

Important APIs and functions: `pinconf_check_ops()` validates that a controller can set either pin or group configs. `pinconf_validate_map()` checks map integrity. `pin_config_get_for_pin()` and `pin_config_group_get()` are the core read paths used by generic debug dumping. `pinconf_map_to_setting()`, `pinconf_apply_setting()`, and `pinconf_set_config()` form the set/apply path. Debugfs helpers include `pinconf_show_map()`, `pinconf_show_setting()`, `pinconf_init_device_debugfs()`, `pinconf_pins_show()`, and `pinconf_groups_show()`.

Control flow: Registration validation rejects config-capable controllers that cannot set configs. When a map is converted, `PIN_MAP_TYPE_CONFIGS_PIN` resolves a pin name with `pin_get_from_name()`, while `PIN_MAP_TYPE_CONFIGS_GROUP` resolves a group selector with `pinctrl_get_group_selector()`. Applying the setting dispatches to `pin_config_set()` or `pin_config_group_set()` and logs failures with the numeric selector. Group reads acquire the target pinctrl device by dev name, lock `pctldev->mutex`, resolve the group selector, call the driver's group getter, and unlock.

State and persistence: The file does not own hardware state. It stores selector/config pointers in `struct pinctrl_setting` and relies on map lifetimes owned by the pinctrl core. Hardware persistence is entirely driver-defined after `pinconf_apply_setting()` invokes callbacks.

Dependencies and integration points: Depends on `core.h` lookup helpers, pin descriptors, pinctrl map/settings types, debugfs/seq_file, and optional generic pinconf debug dumping from `pinconf-generic.c`. It is central to all drivers that provide `struct pinconf_ops`.

Risks: `pinconf_map_to_setting()` copies config pointers rather than duplicating arrays, so map lifetime must outlive settings. `pinconf_apply_setting()` requires exact callback presence for the chosen setting type, so a map type mismatch becomes runtime `-EINVAL`. Debugfs paths assume descriptors and group callbacks are stable under `pctldev->mutex`; driver-specific callbacks must avoid unsafe sleeping or lock inversions.

Test signals: Useful tests include invalid map registration, pin-name and group-name lookup failures, pin and group config application, direct `pinconf_set_config()`, debugfs `pinconf-pins`/`pinconf-groups` rendering, and drivers that implement only pin or only group callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf.h

Purpose: Defines the internal pin configuration interface used between the pinctrl core, generic pinconf code, and controller drivers. It supplies real declarations when relevant Kconfig options are enabled and no-op or `-ENOTSUPP` stubs otherwise.

Important APIs and types: Declares `struct pinctrl_dev`, `struct pinctrl_map`, `struct pinctrl_setting`, and the core functions from `pinconf.c`: operation checking, map validation, setting conversion/free/apply, direct pin config set, and pin/group config get. It also declares debugfs functions, generic pinconf dump helpers, DT parsing helpers, and generic pins-function DT mapping when their config options are enabled.

Control flow: The header has no runtime control flow, but compile-time conditionals determine whether callers are linked to real implementations or stubs. `CONFIG_PINCONF` gates core pinconf behavior; `CONFIG_DEBUG_FS` gates debug display; `CONFIG_GENERIC_PINCONF && CONFIG_OF` gates generic DT config and pinmux parsing.

State and persistence: No state is stored here. The main persistence implication is build-time: when pinconf is disabled, callers can still compile but configuration requests resolve to no-ops or unsupported errors, preventing accidental hardware mutation.

Dependencies and integration points: Includes `linux/errno.h` and participates in nearly every pinconf-related source file in this directory. It is consumed by core pinctrl code and by drivers that need internal helpers beyond public `<linux/pinctrl/pinconf.h>`.

Risks: Stub behavior must match caller expectations. Several disabled paths return success for validation/apply/free-style helpers, so code compiled without `CONFIG_PINCONF` may skip behavior silently. There is no non-`CONFIG_PINCONF` stub for `pin_config_group_get()`, consistent with current callers but a trap for new code if used outside the guarded build.

Test signals: Build matrix coverage is the main signal: `CONFIG_PINCONF=n`, `CONFIG_GENERIC_PINCONF=n`, `CONFIG_OF=n`, and `CONFIG_DEBUG_FS=n` should all compile. Runtime validation belongs to the implementation files selected by these guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinconf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amd.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amd.c

Purpose: Implements the AMD GPIO/pinctrl driver for ACPI-described AMD GPIO controllers. It provides GPIO direction/value operations, generic pin configuration, optional IOMUX pinmux selection, IRQ handling with wake status processing, ACPI s2idle wake checks, and suspend/hibernate save/restore.

Important APIs and functions: GPIO methods are `amd_gpio_get_direction()`, direction input/output, get/set value, and `amd_gpio_set_config()`. Pinconf methods are `amd_pinconf_get()`, `amd_pinconf_set()`, and group wrappers. IRQ methods include enable/disable, mask/unmask, `amd_gpio_irq_set_wake()`, `amd_gpio_irq_set_type()`, `amd_gpio_irq_eoi()`, and `do_amd_gpio_irq_handler()`. PM paths are `amd_gpio_suspend_hibernate_common()`, `amd_gpio_suspend()`, `amd_gpio_hibernate()`, and `amd_gpio_resume()`. Probe/remove are `amd_gpio_probe()` and `amd_gpio_remove()`.

Control flow: Probe maps the MMIO resource, fetches the shared parent IRQ, allocates suspend state, fills `gpio_chip`, registers pinctrl using tables from `pinctrl-amd.h`, clears wake bits, wires a GPIO IRQ chip without a parent handler, adds the gpiochip and pin range, requests the shared IRQ, and registers ACPI wake/s2idle hooks. IRQ handling reads wake status registers, expands each status bit to four pins, dispatches pending unmasked GPIO IRQs through the gpio irq domain, masks spurious non-IRQ lines, and writes EOI. Pinmux, when the optional `"iomux"` resource exists, writes a 2-bit selection byte and verifies readback.

State and persistence: `struct amd_gpio` owns MMIO bases, the gpiochip, pinctrl device, groups, lock, IRQ, and suspend `saved_regs`. Register changes persist in GPIO/IOMUX hardware. Suspend saves only pins with mux/gpio owners or IRQ use, masks non-wake interrupts, clears debounce for wake reliability, and restores saved config while preserving pending IRQ/wake status bits.

Dependencies and integration points: Integrates with ACPI IDs `AMD0030`, `AMDI0030`, `AMDI0031`, and `AMDI0033`, gpiolib, pinctrl, pinmux, generic pinconf, IRQ core, suspend/ACPI LPS0 wake checks, and static data in `pinctrl-amd.h`.

Risks: Register bit semantics are delicate: `INTERRUPT_MASK_OFF` uses inverted naming relative to mask/unmask intent, and type changes busy-wait with the raw spinlock held until hardware reports interrupt enable. `amd_gpio_irq_set_wake()` logs enable/disable IRQ wake errors but returns 0. Optional IOMUX support mutates the global `amd_pinctrl_desc.pmxops` to NULL when absent, which is safe for one platform device but would be risky if multiple variants with different resources coexisted. Debugfs output contains non-ASCII glyphs and is unsuitable as a stable parser target.

Test signals: Probe on each ACPI ID, GPIO direction/value operations, debounce boundary values, bias and drive-strength pinconf, IRQ rising/falling/both/level modes, wake from s2idle/S3/S4, spurious interrupt masking, suspend/resume with GPIO owners, and optional IOMUX DT/ACPI resource validation are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amd.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amd.h

Purpose: Supplies the AMD GPIO driver's register layout, bit definitions, runtime state structures, pin descriptors, group descriptors, and optional IOMUX function table. It is a data-heavy companion to `pinctrl-amd.c`.

Important APIs and types: Defines register offsets such as `WAKE_INT_MASTER_REG`, `WAKE_INT_STATUS_REG0/1`, debounce, interrupt, wake, pull, output, and drive-strength bit offsets/masks. `struct amd_gpio` stores the driver's lock, GPIO and IOMUX MMIO bases, pinctrl/gpio objects, group table, saved registers, platform device, and IRQ. `struct amd_function` describes IOMUX function names, four selectable groups, group count, and register index. Static tables include `kerncz_pins[]`, `kerncz_groups[]`, and `pmx_functions[]`.

Control flow: No executable logic is defined, but macros generate large sets of one-pin groups named `IMX_F{0..3}_GPIO<n>` and functions named `iomux_gpio_<n>`. Runtime code indexes these arrays in `amd_get_groups_count()`, `amd_set_mux()`, and pinctrl descriptor registration.

State and persistence: The header itself is immutable data. Its bit definitions determine which hardware register fields are read, saved, restored, or modified by the driver. `saved_regs` is declared in `struct amd_gpio` but allocated and maintained in the C file.

Dependencies and integration points: Depends on pinctrl generic descriptors and `struct pingroup`. It encodes the Kerncz-era AMD GPIO numbering where GPIO 63 is absent, GPIOs 0-62 and 64-183 are described, and extra groups exist for I2C and UART functions.

Risks: The table data is a contract with hardware. Incorrect bit offsets can break IRQ, wake, debounce, and GPIO output behavior across the whole driver. The group enum and generated group table must remain aligned; gaps such as missing GPIO63 must be reflected consistently in pins, groups, and functions. `NSELECTS` assumes exactly four IOMUX choices per GPIO.

Test signals: Compile-time array alignment, successful pinctrl registration with the expected pin and group counts, debugfs group enumeration, IOMUX selection readback for valid GPIOs, and suspend register save/restore across all described pin numbers validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amdisp.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amdisp.c

Purpose: Implements a small AMD ISP display/sensor-control pinctrl and GPIO driver exposing three output-only GPIO-style controls. It registers pinctrl groups from `pinctrl-amdisp.h` and a gpiochip that toggles a fixed control bit in three MMIO registers.

Important APIs and functions: Pinctrl callbacks are `amdisp_get_groups_count()`, `amdisp_get_group_name()`, and `amdisp_get_group_pins()`. GPIO callbacks are `amdisp_gpio_get_direction()`, `amdisp_gpio_direction_input()`, `amdisp_gpio_direction_output()`, `amdisp_gpio_get()`, and `amdisp_gpio_set()`. Setup paths are `amdisp_gpiochip_add()` and `amdisp_pinctrl_probe()`.

Control flow: Probe allocates `struct amdisp_pinctrl`, sets the platform device init name, maps the single MMIO resource, registers and enables pinctrl, then registers a gpiochip and a pinctrl GPIO range. GPIO get/set chooses an offset from `gpio_offset[]` indexed by GPIO number, reads or writes bit `GPIO_CONTROL_PIN`, and protects the read-modify-write with a raw spinlock.

State and persistence: Runtime state is held in `struct amdisp_pinctrl`: device, pinctrl descriptor/device, gpio range/chip, static data pointer, MMIO base, and raw spinlock. Hardware state is only the output bit in registers at offsets `0x0`, `0x4`, and `0x50`; no suspend/resume or software shadow is maintained.

Dependencies and integration points: Integrates with platform-device probing by name `amdisp-pinctrl`, gpiolib, pinctrl core, and static pin/group/function data in `pinctrl-amdisp.h`.

Risks: The driver reports output-only operation; input direction is unsupported and direction output is a no-op, so consumers must set values explicitly. There is no bounds check in `amdisp_gpio_get()`/`set()` beyond gpiolib's `ngpio` validation. `pdev->dev.init_name` is changed during probe, which is unusual and may affect device naming assumptions.

Test signals: Platform probe with one MEM resource, pinctrl group enumeration for gpio0-2, gpiochip registration with named lines, get/set of all three GPIOs, rejection of input direction, and concurrent set operations validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amdisp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amdisp.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amdisp.h

Purpose: Defines the static data used by the AMD ISP pinctrl driver: three pins, three one-pin groups, GPIO range pins/names, and one GPIO function descriptor.

Important APIs and types: `amdisp_pins[]` declares `GPIO_0`, `GPIO_1`, and `GPIO_2` with comments identifying sensor control roles. `amdisp_range_pins[]` and `amdisp_range_pins_name[]` describe the gpiochip range. `enum amdisp_functions`, `struct amdisp_function`, `amdisp_functions[]`, `struct amdisp_pingroup`, and `amdisp_groups[]` provide the pinctrl group/function data consumed by `pinctrl-amdisp.c`.

Control flow: The header has no executable flow. Macros `AMDISP_GPIO_PINS()`, `FUNCTION()`, and `PINGROUP()` generate the static arrays that probe wires into the pinctrl descriptor and gpio range.

State and persistence: All data is immutable. Hardware persistence is controlled by the C file after a consumer sets one of the GPIO lines.

Dependencies and integration points: Relies on pinctrl descriptor types and `ARRAY_SIZE()` from kernel headers included by the C file. It is intentionally local and not guarded by include guards because only `pinctrl-amdisp.c` includes it.

Risks: `struct amdisp_pingroup.funcs` is typed as `unsigned int *` but initialized with an `(int[])` compound literal; this works in practice for static data but is unnecessarily loose. Function data is not used by a `pinmux_ops` implementation in the C file, so the function table is descriptive rather than active.

Test signals: Build coverage, pinctrl debugfs group listing, gpio line names `gpio0`-`gpio2`, and matching `ngpio`/range sizes validate the header tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-amdisp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-apple-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-apple-gpio.c

Purpose: Implements Apple SoC pinctrl, GPIO, pinmux, and external IRQ support. It dynamically creates one group per pin and four functions (`gpio`, `periph1`, `periph2`, `periph3`) using the `apple,npins` DT property.

Important APIs and functions: Register helpers are `apple_gpio_set_reg()` and `apple_gpio_get_reg()` over a flat regmap. DT map parsing is `apple_gpio_dt_node_to_map()`. Pinmux uses `apple_gpio_pinmux_func_is_gpio()` and `apple_gpio_pinmux_set()`. GPIO methods handle direction, get, set, input, and output. IRQ methods are ack, mask, unmask, startup, type selection, and chained `apple_gpio_irq_handler()`. Probe and registration are `apple_gpio_pinctrl_probe()` and `apple_gpio_register()`.

Control flow: Probe reads interrupt-controller status and parent IRQ count, allocates flexible-array driver state, reads `apple,npins`, builds pin descriptors/names/numbers, maps MMIO, initializes regmap, registers pinctrl, adds generic one-pin groups and functions, then registers gpiochip and optional hierarchical parent IRQ data. DT pinmux parsing reads each packed `pinmux` cell, extracts `APPLE_PIN()` and `APPLE_FUNC()`, validates function index, and emits mux maps. IRQ handling receives a parent group pointer, recovers the controller via the `irqgrps` flexible array, reads pending bits per 32-pin block for that group, and dispatches child IRQs.

State and persistence: `struct apple_gpio_pinctrl` owns the MMIO base, regmap cache, pinctrl descriptor, gpiochip, and IRQ group mapping. Register fields persist mode, data, peripheral selection, input enable, pull, drive, Schmitt, group, and lock status. No suspend state is explicitly saved in this file.

Dependencies and integration points: Uses `dt-bindings/pinctrl/apple.h`, OF, regmap MMIO, generic pinctrl/pinmux helper registries, gpiolib, and IRQ core. Compatible strings are `apple,t8103-pinctrl` and `apple,pinctrl`.

Risks: `apple_gpio_get_reg()` returns 0 on regmap read failure, which can look like a valid low/input state. `apple_gpio_register()` allocates parent IRQ arrays manually, passes them to `devm_gpiochip_add_data()`, then frees them; this relies on gpiolib copying needed data during registration. The IRQ group recovery pointer arithmetic is compact and depends on `irqgrps[i] == i`.

Test signals: DT pinmux parsing for valid/invalid functions, GPIO direction/value changes, input reads using uncached MMIO, IRQ startup/type/mask/unmask for all trigger types, multiple parent IRQ groups, and probe without interrupt-controller validate the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-apple-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-artpec6.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-artpec6.c

Purpose: Implements the Axis ARTPEC-6 pin controller. It provides static pin/group/function tables, mux selection for peripheral groups, and generic pinconf support for bias and drive strength.

Important APIs and functions: `artpec6_pmx_reg_offset()` maps pin numbers across register holes. Pinctrl callbacks expose groups. Pinmux callbacks are `artpec6_pmx_get_functions_count()`, `artpec6_pmx_get_fname()`, `artpec6_pmx_get_fgroups()`, `artpec6_pmx_set()`, and `artpec6_pmx_request_gpio()`. Pinconf callbacks are `artpec6_pconf_get()`, `artpec6_pconf_set()`, and `artpec6_pconf_group_set()`. Probe/reset paths are `artpec6_pmx_reset()`, `artpec6_pmx_probe()`, and `artpec6_pmx_remove()`.

Control flow: Probe maps MMIO, resets every pin drive field to 8 mA, fills driver data from static tables, and registers the pinctrl descriptor. DT mapping is delegated to `pinconf_generic_dt_node_to_map_all()`. Setting a mux iterates the selected group's pins, skips pins above `ARTPEC6_MAX_MUXABLE` because they lack a select field, computes config 0 for GPIO or the group's configured alternate value, updates the `SEL` field, and leaves nonmuxable pins unchanged. Pinconf get/set reads the per-pin register and manipulates `UDC0/UDC1` for pull-up/down/disable and `DRV` for 4/6/8/9 mA.

State and persistence: Runtime state is `struct artpec6_pmx`, holding device, pinctrl device, MMIO base, and static table pointers/counts. Hardware state is held in per-pin registers and persists until reset or later pinctrl operations. There is no explicit PM save/restore path.

Dependencies and integration points: Integrates with OF compatible `axis,artpec6-pinctrl`, pinctrl core, pinmux, generic pinconf DT parsing, and pinctrl utility map freeing. The driver is registered with `arch_initcall()`.

Risks: `artpec6_pconf_get()` checks `pin >= pmx->num_pins` but then logs `pmx->pins[pin].name`, which would be out of bounds on invalid input. Several function group arrays mention names not present in `artpec6_pin_groups` (`uart4grp1`) or use unusual naming (`uart5nocts`), so table consistency matters. There is no locking around MMIO read-modify-write operations.

Test signals: Probe on matching DT, mux selection for GPIO and each peripheral group, pinconf bias disable/pull-up/pull-down, drive strength 4/6/8/9 mA and invalid values, nonmuxable pin handling, and debugfs generic pinconf output are useful validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-artpec6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-as3722.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-as3722.c

Purpose: Implements pinctrl, pinmux, pinconf, GPIO, and IRQ translation for the ams AS3722 PMIC's eight GPIO pins. It bridges Linux pinctrl/gpiolib operations to the parent AS3722 MFD register and IRQ helpers.

Important APIs and functions: Pinctrl exposes eight one-pin groups. Pinmux methods include function count/name/groups, `as3722_pinctrl_set()`, `as3722_pinctrl_gpio_request_enable()`, and `as3722_pinctrl_gpio_set_direction()`. Pinconf methods are `as3722_pinconf_get()` and `as3722_pinconf_set()`. GPIO methods are `as3722_gpio_get()`, `as3722_gpio_set()`, `as3722_gpio_direction_output()`, and `as3722_gpio_to_irq()`. Probe is `as3722_pinctrl_probe()`.

Control flow: Probe inherits the parent firmware node, obtains the parent `struct as3722`, registers pinctrl, registers a sleeping gpiochip, and adds a pin range. DT maps are handled by `pinconf_generic_dt_node_to_map_pin()`. Setting a mux writes the `IOSF` field in `AS3722_GPIOn_CONTROL_REG(group)`, records the active function, and forces output mode for output-like alternate functions. GPIO direction uses saved pinconf mode bits to compute an AS3722 GPIO mode. GPIO get chooses signal input or output register based on current hardware mode and applies inversion. GPIO set reads inversion state and updates `GPIO_SIGNAL_OUT_REG`.

State and persistence: `struct as3722_pctrl_info` stores the parent device pointer, pinctrl/gpio objects, current mux option per pin, and software pinconf mode properties in `gpio_control[]`. Hardware state persists in AS3722 control and signal registers. Pinconf set mostly updates the software shadow; the hardware mode is applied when GPIO direction is set.

Dependencies and integration points: Depends on the AS3722 MFD API (`as3722_read()`, `as3722_update_bits()`, `as3722_irq_get_virq()`), platform device children, generic pinconf DT utilities, gpiolib, and pinctrl. Compatible string is `ams,as3722-pinctrl`.

Risks: Pinconf state is partly deferred; changing bias/open-drain/high-impedance does not immediately rewrite hardware unless a direction operation occurs. `as3722_pinctrl_gpio_request_enable()` rejects GPIO use when `io_function` is nonzero, so stale function tracking would block GPIO. Unsupported high-impedance direction combinations return `-EINVAL`. All GPIO operations can sleep due to parent register access.

Test signals: Probe under the AS3722 MFD, DT function selection for all mux options, GPIO request rejection while alternate functions are active, pinconf get/set for bias/open-drain/high-impedance, input/output direction mode writes, inverted GPIO get/set, and `to_irq()` mapping are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-as3722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91-pio4.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91-pio4.c

Purpose: Implements the newer Atmel/Microchip PIO4 pinctrl plus GPIO controller for SAMA5D2 and SAMA7 variants. It models each pin as one group, supports mux functions GPIO/A-G, generic and custom pinconf, gpiochip operations, IRQ domains, wake sources, and suspend/resume restore.

Important APIs and functions: Low-level register access uses `atmel_gpio_read()`, `atmel_gpio_write()`, `atmel_pin_config_read()`, and `atmel_pin_config_write()`. GPIO paths include direction/get/set/multiple and `atmel_gpio_to_irq()`. IRQ paths include set type, mask/unmask, wake, and `atmel_gpio_irq_handler()`. DT mapping is handled by `atmel_pctl_dt_node_to_map()` and helpers. Pinconf methods are `atmel_conf_pin_config_group_get()`, `atmel_conf_pin_config_group_set()`, pin wrappers, and debug show. Probe is `atmel_pinctrl_probe()`.

Control flow: Probe selects SoC data from OF match, calculates total pins and last-bank size, maps MMIO, enables the clock, allocates pin/group/name arrays, initializes one group per pin, creates gpiochip and wake/backup/IRQ arrays, chains each bank IRQ, creates a linear IRQ domain and mappings, registers pinctrl, adds gpiochip, and links the pin range. DT parsing reads packed `pinmux` cells, extracts pin/function/ioset, records pin metadata, emits mux maps, and optionally emits group config maps. Pin config access must write `MSKR` and use a write memory barrier before reading/writing `CFGR`.

State and persistence: `struct atmel_pioctrl` stores MMIO base, clock, bank/pin metadata, pinctrl device, gpiochip, irq domain, parent IRQs, wake-source bitmaps, and per-bank suspend backups of `IMR`, `ODSR`, and each pin `CFGR`. Hardware register state persists and is explicitly saved/restored over system sleep.

Dependencies and integration points: Uses `dt-bindings/pinctrl/at91.h`, generic pinconf parsing with custom `atmel,drive-strength`, gpiolib, IRQ domains, clocks, OF match data, and platform driver binding for `atmel,sama5d2-pinctrl`, `microchip,sama7d65-pinctrl`, and `microchip,sama7g5-pinctrl`.

Risks: `atmel_conf_pin_config_set()` and get wrappers pass `grp->pin` as a group selector, which works only because group index equals pin id in the one-pin-per-group model. `atmel_gpio_set_multiple()` shifts caller-provided masks/bits in place on platforms where bank width differs from `BITS_PER_LONG`, which is surprising. Pin config reads/writes rely on correct `MSKR` sequencing and can affect the wrong pin if reordered.

Test signals: DT pinmux/config parsing, all mux functions A-G, GPIO get/set/multiple across banks and partial last bank, IRQ type/mask/wake behavior per bank, custom drive-strength and slew-rate support by SoC, suspend/resume state restoration, and invalid pin/function cells should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91-pio4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91.c

Purpose: Implements the legacy AT91 pinctrl and GPIO stack for AT91RM9200, AT91SAM9x5, SAMA5D3, and SAM9X60-class PIO controllers. The file contains both a GPIO platform driver for PIO banks and a pinctrl platform driver that depends on those GPIO banks having probed first.

Important APIs and functions: Pinctrl parsing and mapping are handled by `at91_pinctrl_probe_dt()`, `at91_pinctrl_mux_mask()`, `at91_pinctrl_parse_functions()`, `at91_pinctrl_parse_groups()`, and `at91_dt_node_to_map()`. Mux operations use SoC-specific `struct at91_pinctrl_mux_ops` callbacks and `at91_pmx_set()`. Pinconf uses packed driver-local bits through `at91_pinconf_get()` and `at91_pinconf_set()`. GPIO operations include direction/get/set/multiple and debug show. IRQ handling includes `gpio_irq_type()`, `alt_gpio_irq_type()`, mask/unmask/wake, `gpio_irq_handler()`, and `at91_gpio_of_irq_setup()`.

Control flow: GPIO bank probes run first via `arch_initcall()` registration, use DT aliases to place banks in global `gpio_chips[]`, map bank MMIO, enable clocks, configure IRQ chips, add gpiochips, and update `gpio_banks`. Pinctrl probe counts active banks/functions/groups in the controller DT node, defers until all active GPIO banks are present, reads `atmel,mux-mask`, parses function/group child nodes with `atmel,pins = <bank pin mux config>`, creates pin descriptors, registers pinctrl, and links GPIO ranges. Applying a mux validates each pin against bank availability and mux masks, disables interrupts, writes peripheral select registers, and disables GPIO mode for peripheral pins.

State and persistence: Global `gpio_chips[]` and `gpio_banks` coordinate separate platform drivers. Each bank stores MMIO, clock, wakeup mask, suspend backup mask, optional shared-IRQ linked-list pointer, and gpio range. Pinctrl state stores parsed function/group tables and mux masks. Hardware register state persists in PIO registers; GPIO suspend disables non-wakeup interrupts and may gate the bank clock, then restores interrupt masks on resume.

Dependencies and integration points: Depends on `pinctrl-at91.h` register definitions, OF child-node bindings, DT aliases, clocks, gpiolib, pinctrl, IRQ core, and SoC-specific mux ops for classic, PIO3, SAMA5D3, and SAM9X60 behavior.

Risks: Probe ordering is fragile and intentionally uses `-EPROBE_DEFER` until GPIO banks are ready. The static `grp_index` in `at91_pinctrl_parse_functions()` persists across calls and would be unsafe for multiple controller instances. Driver-local pinconf bits are not generic packed `PIN_CONFIG_*` values. Shared parent IRQ handling chains up to three banks and depends on `next` list setup. `BUG_ON(alias_idx >= ARRAY_SIZE(gpio_chips))` can crash on invalid DT aliases.

Test signals: Multi-bank DT probe ordering, mux-mask validation, all supported mux modes A-D by SoC, GPIO bank aliases and `#gpio-lines`, GPIO IRQ edge/level modes, shared parent IRQ dispatch, wakeup suspend/resume, pinconf flags for pull-up/down, multidrive, debounce, Schmitt, drive strength and slew rate, and invalid `atmel,pins` data are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-at91.c -->
