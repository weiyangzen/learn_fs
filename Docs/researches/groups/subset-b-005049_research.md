# Research Report: subset-b-005049

This grouped report covers the requested CIX Sky1, Linux pinctrl core/device-tree, and Freescale/NXP i.MX pinctrl files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1.c

Purpose: Defines the CIX Sky1 pin controller pad/function tables and registers a platform driver for the normal and S5 pinmux domains. It is mostly SoC data: two compatible strings select either the 66-pin S5 pad table or the 138-pin main pad table.

Important APIs and types: Uses `SKY_PINFUNCTION()` entries over `struct sky1_pin_desc`, packages them as `sky1_pinctrl_soc_info`, and calls the shared `sky1_base_pinctrl_probe()`. Runtime PM hooks use `pinctrl_force_sleep()` and `pinctrl_force_default()`. The `of_device_id` table binds `cix,sky1-pinctrl-s5` and `cix,sky1-pinctrl`.

Control flow: `arch_initcall()` registers the platform driver. Probe retrieves match data with `device_get_match_data()` and delegates all controller setup to the shared base driver. Suspend/resume look up `struct sky1_pinctrl` from driver data and force hog sleep/default states through the pinctrl core.

State and persistence: The file stores immutable pad/function arrays. Runtime state is in the base driver allocation and in hardware registers managed by that base implementation. Selected pin states persist in controller registers until later state changes, suspend/resume, or reset.

Dependencies and integration points: Depends on the generic pinctrl core, OF platform matching, and `pinctrl-sky1.h`. It integrates with board DT pinctrl references, CIX GPIO/peripheral consumers, and the shared Sky1 base implementation not shown here.

Risks: Pad data is table-driven and easy to misalign with hardware numbering. Several pins intentionally expose empty function lists for fixed/system signals, so DT must not request alternate functions there. The source as read contains duplicate-looking table entries in the main domain; build and runtime pin-list inspection should catch unintended duplication or numbering drift.

Test signals: Build the Sky1 pinctrl driver, boot with both compatible strings, inspect `/sys/kernel/debug/pinctrl`, select default and sleep states, and exercise I2C/I3C, SPI, UART, I2S/HDA, GMAC, USB, and GPIO pins from DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1.h

Purpose: Provides the private data model for the CIX Sky1 pinctrl implementation. It describes per-pin function lists, SoC-level pin tables, and the controller runtime state passed between the SoC table file and the shared base probe.

Important APIs and types: `struct sky1_pinctrl_group` names one pin group and its config; `struct sky1_pin_desc` wraps a `pinctrl_pin_desc` plus a function-name array; `struct sky1_pinctrl_soc_info` points at the SoC pin table; `struct sky1_pinctrl` stores device, `pinctrl_dev`, MMIO base, SoC info, generated groups, and group names. `SKY_PINFUNCTION()` is the table-construction macro. `sky1_base_pinctrl_probe()` is the exported probe boundary.

Control flow: No executable code runs in this header. Its types define the flow used by `pinctrl-sky1.c`: static pin descriptions are passed to `sky1_base_pinctrl_probe()`, which is expected to allocate groups and register a pinctrl device.

State and persistence: The header defines state containers but owns no state itself. `struct sky1_pinctrl` fields persist for the device lifetime under devres or platform-driver ownership; register state persists in MMIO hardware.

Dependencies and integration points: Requires Linux pinctrl and platform-device types from includers. It is tightly coupled to the shared Sky1 base driver and the SoC data file.

Risks: The macro assumes every `_func` has a matching `_func_group` array in scope. If `nfunc` and group names do not match hardware mux values used by the base driver, pin selections can silently program the wrong mode. Header changes affect both Sky1 domains.

Test signals: Compile coverage, probe of both Sky1 compatibles, debugfs group/function counts matching table sizes, and DT state selection through the base driver validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/core.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/core.c

Purpose: Implements the Linux pinctrl core: controller registration, pin descriptor storage, per-consumer pinctrl handles, mapping registration, device-tree map ingestion, state lookup/selection, GPIO range mediation, hog handling, power-management state forcing, and debugfs views.

Important APIs and functions: Exported entry points include `pinctrl_get()`, `pinctrl_put()`, `pinctrl_lookup_state()`, `pinctrl_select_state()`, devm variants, `pinctrl_register()`, `pinctrl_register_and_init()`, `pinctrl_enable()`, `pinctrl_unregister()`, `pinctrl_register_mappings()`, GPIO helpers such as `pinctrl_gpio_request()`, and PM helpers `pinctrl_force_sleep()`/`pinctrl_force_default()`. Core globals are `pinctrldev_list`, `pinctrl_list`, and `pinctrl_maps` with dedicated mutexes.

Control flow: Controller drivers register descriptors; pins are inserted into a radix tree and hog states are claimed when enabled. Consumers call `pinctrl_get()`, which parses DT maps, scans registered maps for the device, creates `pinctrl_state` objects, and attaches mux/config settings. `pinctrl_select_state()` disables old mux ownership, applies all new mux settings first, then config settings, links consumers to controllers, and partially rolls back mux ownership on errors.

State and persistence: Software state lives in global lists, radix trees, `kref`-counted `struct pinctrl`, current `p->state`, map chunks, GPIO ranges, and per-pin mux/GPIO ownership fields in `struct pin_desc`. Hardware state persists through driver callbacks in pinmux/pinconf layers and is not fully restorable if config application fails after mux changes.

Dependencies and integration points: Integrates with OF parsing (`devicetree.c`), pinmux/pinconf validators and appliers, gpiolib ranges, device links, debugfs, PM state names, and all controller drivers.

Risks: Lifetime and locking are central risks: maps retain caller-owned arrays, DT map chunks must unregister and free driver-allocated map data, and controller unregister races with active consumers are only partially guarded. Rollback after failed state selection can disable mux ownership but cannot generally restore prior hardware config. GPIO range readiness is heuristic when a GPIO line has no backing pin controller.

Test signals: Kernel pinctrl selftests if available, compile with `CONFIG_PINMUX`, `CONFIG_PINCONF`, `CONFIG_OF`, `CONFIG_GPIOLIB`, and `CONFIG_DEBUG_FS`; probe/remove controllers, request/free GPIOs, select default/init/sleep/idle states, exercise hogs, inspect debugfs, and inject invalid maps for error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/core.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/core.h

Purpose: Defines private data structures and internal helper prototypes shared by the pinctrl core, DT parser, pinmux, pinconf, and generic group/function helpers.

Important APIs and types: Key structures are `struct pinctrl_dev`, `struct pinctrl`, `struct pinctrl_state`, `struct pinctrl_setting`, `struct pin_desc`, `struct pinctrl_maps`, and generic `struct group_desc`. It declares lookup helpers, group helpers, pin name helpers, GPIO range lookup, forced PM state helpers, and the global `pinctrl_maps` list/mutex.

Control flow: The header contains only declarations and the inline `pin_desc_get()` radix-tree lookup. It defines the private object graph used by `core.c`: controllers own pin descriptors, consumers own states, states own settings, and settings point back to the controller that applies mux/config operations.

State and persistence: No state is allocated here, but fields define lifetime rules. `struct pinctrl_dev` persists for controller lifetime, `struct pinctrl` is kref-counted per consumer, DT maps are linked to a consumer handle, and `pin_desc` tracks runtime mux/GPIO ownership.

Dependencies and integration points: Depends on Linux list, radix-tree, mutex, kref, and `linux/pinctrl/machine.h`. It is not a public driver ABI; external drivers generally use public pinctrl headers instead.

Risks: Because this is a private header, structure changes require synchronized updates across core, pinmux, pinconf, devicetree, and generic helper files. Conditional fields under `CONFIG_GENERIC_PINCTRL_GROUPS`, `CONFIG_GENERIC_PINMUX_FUNCTIONS`, `CONFIG_DEBUG_FS`, and `CONFIG_PINMUX` can hide build-only bugs.

Test signals: Matrix builds across pinmux/pinconf/generic-group/debugfs configs, controller registration, debugfs rendering, GPIO request paths, and DT map free paths validate structure layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/devicetree.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/devicetree.c

Purpose: Converts generic pinctrl device-tree properties into runtime pinctrl mapping tables and provides helpers for bindings that use indexed pinctrl argument arrays.

Important APIs and functions: Exports `of_pinctrl_get()`, `pinctrl_dt_to_map()`, `pinctrl_dt_free_maps()`, `pinctrl_count_index_with_args()`, and `pinctrl_parse_index_with_args()`. Internally, `dt_to_map_one_config()` finds the owning controller node, calls the controller's `dt_node_to_map()`, and `dt_remember_or_free_map()` registers and tracks generated maps.

Control flow: `pinctrl_dt_to_map()` walks `pinctrl-0`, `pinctrl-1`, etc. on a consumer node, resolves optional names from `pinctrl-names`, follows each phandle to a config node, finds the parent pin controller, asks that controller to produce maps, and registers each map chunk. Empty states become `PIN_MAP_TYPE_DUMMY_STATE`. On any error, all DT-derived maps for that consumer are freed.

State and persistence: `struct pinctrl_dt_map` records each generated map chunk on `p->dt_maps`. Map entries get duplicated `dev_name` strings and borrow state-name strings from DT property storage after taking a node reference. Registered maps persist until `pinctrl_dt_free_maps()` unregisters them and calls controller `dt_free_map()`.

Dependencies and integration points: Depends on OF, `core.c` map registration, controller `pctlops->dt_node_to_map`, optional `dt_free_map`, module probe deferral, and `#pinctrl-cells` conventions for argument helpers.

Risks: Parent-walking defers probe unless `pinctrl-use-default` allows missing controllers, so DT hierarchy mistakes can become probe loops. Map memory ownership is split between this file and controller callbacks; leaks or double frees occur if callbacks do not match allocation strategy. Indexed argument helpers assume a parent or grandparent supplies `#pinctrl-cells`.

Test signals: DT overlays with named, unnamed, empty, invalid-phandle, missing-controller, hog, and `pinctrl-use-default` states; module deferral tests; and bindings using `pinctrl_parse_index_with_args()` cover the important paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/devicetree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/devicetree.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/devicetree.h

Purpose: Declares the internal interface between the pinctrl core and its device-tree parser, with no-op or `-ENODEV` stubs when `CONFIG_OF` is disabled.

Important APIs and types: Declares `pinctrl_dt_to_map()`, `pinctrl_dt_free_maps()`, `pinctrl_count_index_with_args()`, and `pinctrl_parse_index_with_args()`. Forward declarations cover `device_node`, `of_phandle_args`, `pinctrl`, and `pinctrl_dev`.

Control flow: With OF enabled, `core.c` calls these functions during handle creation and destruction. Without OF, parsing is skipped and indexed helper users get `-ENODEV`.

State and persistence: The header owns no state. It gates whether `struct pinctrl` instances may accumulate `dt_maps` from device-tree parsing.

Dependencies and integration points: Includes only `linux/errno.h` and is consumed by `core.c` plus other pinctrl internals needing indexed phandle parsing.

Risks: Stub behavior must match callers' expectations. A caller that treats `-ENODEV` as fatal under non-OF builds can regress platform-data users. Signature changes must stay synchronized with `devicetree.c`.

Test signals: Build and boot with `CONFIG_OF=y` and `CONFIG_OF=n`, plus compile coverage for consumers of the indexed parsing helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/devicetree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/Kconfig

Purpose: Defines build-time configuration for Freescale/NXP pinctrl drivers spanning common i.MX MMIO controllers, i.MX SCMI firmware-backed controllers, i.MX SCU controllers, legacy i.MX1/i.MX27 controllers, MXS i.MX23/i.MX28 controllers, Vybrid, i.MX8/9, and i.MXRT variants.

Important APIs and symbols: Core symbols include `PINCTRL_IMX`, `PINCTRL_IMX_SCMI`, `PINCTRL_IMX_SCU`, `PINCTRL_IMX1_CORE`, and `PINCTRL_MXS`. SoC symbols select the appropriate core, for example `PINCTRL_IMX25` and `PINCTRL_IMX35` select `PINCTRL_IMX`, `PINCTRL_IMX1`/`PINCTRL_IMX27` select `PINCTRL_IMX1_CORE`, and `PINCTRL_IMX23`/`PINCTRL_IMX28` select `PINCTRL_MXS`.

Control flow: Kconfig selection determines which common objects and SoC data files are compiled. Defaults are tied to matching SoC architecture symbols, with `COMPILE_TEST` enabling broader build coverage.

State and persistence: No runtime state. The file controls whether driver objects exist as built-in or modules and which generic pinctrl facilities are selected.

Dependencies and integration points: Integrates with architecture symbols such as `ARCH_MXC`, `SOC_IMX*`, `IMX_SCU`, `ARM_SCMI_PROTOCOL`, generic pinctrl group/function helpers, `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, and `REGMAP`.

Risks: Missing `select` lines cause link failures or runtime feature gaps in shared core files. Built-in-only legacy symbols affect init ordering; tristate newer symbols must align with exported symbols from common cores. The SCMI driver is platform-allowlisted, so Kconfig enablement alone is not enough for runtime probe.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, SoC defconfigs, and module/built-in combinations for common core plus individual SoC drivers validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/Makefile

Purpose: Maps Freescale/NXP pinctrl Kconfig symbols to the object files built under `drivers/pinctrl/freescale`.

Important APIs and symbols: Uses `obj-$(CONFIG_...) += ...` for common objects (`pinctrl-imx.o`, `pinctrl-scu.o`, `pinctrl-imx-scmi.o`, `pinctrl-imx1-core.o`, `pinctrl-mxs.o`) and SoC-specific data/probe files such as `pinctrl-imx1.o`, `pinctrl-imx23.o`, `pinctrl-imx25.o`, `pinctrl-imx27.o`, `pinctrl-imx28.o`, and `pinctrl-imx35.o`.

Control flow: Build system inclusion is controlled entirely by Kconfig. Shared cores are linked when selected by SoC symbols, and SoC files provide the platform/SCMI driver registration and pin tables.

State and persistence: No runtime state. It determines which probe functions, module aliases, and exported common symbols are available in the built kernel.

Dependencies and integration points: Must stay synchronized with `Kconfig` symbol names and source filenames. It also determines whether shared helper exports satisfy SoC object references.

Risks: Omitting a common object selected by a SoC symbol produces link errors; adding a SoC file without a matching Kconfig line leaves it unreachable. Duplicate object inclusion under different symbols can create duplicate registration if not designed for it.

Test signals: Incremental builds for each `CONFIG_PINCTRL_*` symbol, clean `make drivers/pinctrl/freescale/`, and defconfig builds for i.MX/MXS platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx-scmi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx-scmi.c

Purpose: Implements an i.MX pinctrl driver that delegates mux/config programming to SCMI firmware using the SCMI pinctrl protocol, currently allowlisted for i.MX94, i.MX95, and i.MX952.

Important APIs and functions: `struct scmi_pinctrl_imx` stores SCMI handles, protocol ops, and the pinctrl descriptor. `pinctrl_scmi_imx_dt_node_to_map()` converts `fsl,pins` cells into packed SCMI config maps. Pinconf callbacks call `settings_get_one()` and `settings_conf()`. `scmi_pinctrl_imx_get_pins()` queries firmware pin names, and `scmi_pinctrl_imx_probe()` registers/enables the controller.

Control flow: SCMI core matches `SCMI_PROTOCOL_PINCTRL`. Probe checks machine compatibility, obtains protocol ops, queries pin count/names, registers pinctrl, and enables hogs. DT map parsing emits one `PIN_MAP_TYPE_CONFIGS_PIN` per pin, combining mux, optional extended mux, pad config, and daisy selection into one firmware call. Pinmux `set_mux` intentionally does nothing because mux is applied through pinconf.

State and persistence: Driver state persists in the SCMI device allocation. Generated map configs are heap-copied arrays referenced by pinctrl maps; firmware-applied settings persist in platform firmware/hardware until changed or reset.

Dependencies and integration points: Depends on SCMI protocol APIs, OF machine compatibility, generic pinctrl groups/functions, generic pinconf packing, and i.MX `fsl,pins` binding cell layout.

Risks: Daisy offset is a static cached value derived from machine compatibility, so multi-SoC test environments need care. Map free only releases the map array, while per-pin copied config arrays need ownership scrutiny. The source as read also contains an apparent duplicate local declaration in `pinctrl_scmi_imx_pinconf_set()`, which build coverage should catch. Firmware error translation and maximum config count are critical.

Test signals: Build with `CONFIG_PINCTRL_IMX_SCMI`, probe on allowlisted i.MX9 boards, SCMI firmware pin count/name queries, DT states with mux/config/daisy/ext fields, suspend/resume consumers, and firmware error injection for unsupported settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx-scmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx.c

Purpose: Provides the shared MMIO/SCU-aware i.MX pinctrl implementation used by many NXP/Freescale SoC data files. It parses i.MX `fsl,pins`/`pinmux` bindings, registers generic groups/functions, applies muxes and pad configs, and supplies PM state forcing.

Important APIs and functions: Exported API is `imx_pinctrl_probe()` plus `imx_pmx_ops` and `imx_pinctrl_pm_ops`. Important internals include `imx_dt_node_to_map()`, `imx_pmx_set_one_pin_mmio()`, `imx_pinconf_get_mmio()`, `imx_pinconf_set_mmio()`, `imx_pinctrl_parse_pin_mmio()`, `imx_pinctrl_parse_groups()`, `imx_pinctrl_parse_functions()`, and `imx_pinctrl_probe_dt()`.

Control flow: SoC drivers pass `imx_pinctrl_soc_info` to `imx_pinctrl_probe()`. Probe maps registers, optionally maps an input-select block, registers the pinctrl device, parses DT into generic functions/groups, then enables hogs. State selection calls `imx_dt_node_to_map()` to create mux and config maps; mux setting writes mux registers and select-input registers, while config setting writes pad-control registers or delegates to SCU callbacks.

State and persistence: `struct imx_pinctrl` stores MMIO bases, parsed `pin_regs`, group index, and SoC info. Parsed group data is devm allocated. Hardware mux, select input, SION, and pad config values persist in IOMUXC registers or SCU firmware until reprogrammed.

Dependencies and integration points: Uses generic pinctrl group/function helpers, pinmux/pinconf core, OF parsing, syscon/regmap for optional GPR attachment, platform MMIO mapping, and SoC-specific data in files such as `pinctrl-imx25.c` and `pinctrl-imx35.c`.

Risks: DT cell-size handling differs for default, shared mux/conf, SCU, and generic `pinmux` formats; malformed bindings can misparse register offsets. `imx_pmx_ops.gpio_set_direction` is a global ops struct field overwritten during probe, which is risky with multiple controller variants. Shared mux/config registers require read-modify-write masking to preserve mux bits. Quirky select-input encoding uses packed width/shift/select fields.

Test signals: Probe on MMIO and SCU i.MX variants, DT parsing for flat and nested function layouts, pin state changes for mux/config/select-input/SION, GPIO direction callbacks, debugfs pinconf output, suspend/resume default/sleep states, and invalid `fsl,pins` sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx.h

Purpose: Defines the shared data contract for common i.MX pinctrl SoC drivers and the common `pinctrl-imx.c` implementation.

Important APIs and types: Defines `struct imx_pin_mmio`, `struct imx_pin_scu`, `struct imx_pin`, `struct imx_pin_reg`, `struct imx_pinctrl`, and `struct imx_pinctrl_soc_info`. Exports `imx_pinctrl_probe()`, `imx_pmx_ops`, `imx_pinctrl_pm_ops`, SCU helper prototypes, and macros such as `SHARE_MUX_CONF_REG`, `ZERO_OFFSET_VALID`, `IMX_USE_SCU`, `IMX_MUX_MASK`, and `IOMUXC_CONFIG_SION`.

Control flow: SoC data files fill `imx_pinctrl_soc_info` and call `imx_pinctrl_probe()`. The common driver uses flags and callbacks to decide whether to parse/apply MMIO cells or SCU firmware cells.

State and persistence: The header defines runtime state containers but owns no storage. `struct imx_pinctrl` persists per controller; register offsets and parsed pin configs persist for driver lifetime; hardware state is persisted by MMIO or SCU writes.

Dependencies and integration points: Includes public pinmux definitions and is used by all common i.MX pinctrl SoC files plus SCU support. Its flags encode binding and register-layout differences across SoCs.

Risks: `imx_pin_reg` uses signed 16-bit offsets with `-1` sentinel, so large register maps or zero-offset semantics depend on flags. Callback pointers must be present when `IMX_USE_SCU` is set. Macros such as `PAD_CTL_MASK()` assume modest bit widths.

Test signals: Build every `PINCTRL_IMX` SoC, compile SCU and non-SCU paths, parse representative DT bindings, and validate register offsets for SoCs with shared mux/config registers and zero-valid offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1-core.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1-core.c

Purpose: Implements the shared pinctrl core for legacy i.MX1/i.MX21/i.MX27-style controllers, whose muxing is organized by ports and bitfields rather than modern IOMUXC pad-control registers.

Important APIs and functions: Exported entry is `imx1_pinctrl_core_probe()`. Internal register helpers are `imx1_write_bit()`, `imx1_write_2bit()`, `imx1_read_bit()`, and `imx1_read_2bit()`. Pinctrl operations include group lookup, DT map generation, mux setting, function enumeration, pullup config get/set, and debug display.

Control flow: SoC files provide pad descriptors and call the core probe. Probe maps MMIO, parses DT child functions/groups from `fsl,pins = <PIN MUX_ID CONFIG>`, registers pinctrl, and populates child devices. State selection maps each group into one mux map plus per-pin config maps. `imx1_pmx_set()` decodes `mux_id` into function/GPIO/direction/output/input bits and writes the corresponding port registers.

State and persistence: `struct imx1_pinctrl` holds device, pinctrl device, MMIO base, and parsed SoC info. Parsed functions/groups and pin arrays are devm allocated into mutable SoC info. Hardware state persists in DDIR, OCR, ICONFA/B, GIUS, GPR, and PUEN registers.

Dependencies and integration points: Depends on OF platform parsing, common pinctrl/pinmux/pinconf APIs, and SoC data from `pinctrl-imx1.c`/`pinctrl-imx27.c`. It also calls `of_platform_populate()` for subdevices under the controller node.

Risks: A static `grp_index` in function parsing can retain value across probes unless only one legacy controller probes. The static `pinctrl_desc` is mutated per probe, which is another multi-instance risk. Register helpers rely on exact port/pin bitfield math. DT config only represents pullup enable.

Test signals: Boot i.MX1 and i.MX27 DTs, parse multiple functions/groups, inspect debugfs register-derived state, test GPIO-vs-function muxing, pullup config changes, and subdevice population under the IOMUXC node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1.c

Purpose: Supplies the i.MX1 pad enumeration and pin descriptor table, then registers a built-in platform driver for `fsl,imx1-iomuxc` using the legacy i.MX1 core.

Important APIs and types: Defines `PAD_ID()`, port constants, `enum imx1_pads`, `imx1_pinctrl_pads[]`, `imx1_pinctrl_info`, and `imx1_pinctrl_probe()`. Driver registration uses `builtin_platform_driver_probe()`.

Control flow: The platform bus matches `fsl,imx1-iomuxc`; the built-in probe passes static pad data to `imx1_pinctrl_core_probe()`, which handles DT parsing and hardware operations.

State and persistence: This file is immutable SoC data except for the `imx1_pinctrl_info` object that the core fills with parsed groups/functions. Hardware state is managed by `pinctrl-imx1-core.c`.

Dependencies and integration points: Depends on `pinctrl-imx1.h`, the legacy core object, OF matching, and board DT nodes using i.MX1 pad IDs.

Risks: Pad IDs are sparse by port, and the descriptor array must match valid hardware pads. Built-in-only registration affects init ordering. Since the common core mutates the SoC info, this table is not purely const.

Test signals: i.MX1 defconfig build, boot with `fsl,imx1-iomuxc`, DT group parsing, debugfs pin list matching expected pads, and peripheral bring-up for LCD, UART, SPI, SD, USB, and CSI pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1.h

Purpose: Defines the legacy i.MX1/i.MX27 pinctrl data structures shared between SoC table files and `pinctrl-imx1-core.c`.

Important APIs and types: `struct imx1_pin` carries pin ID, encoded mux ID, and config. `struct imx1_pin_group` stores group name, pin IDs, pin array, and count. `struct imx1_pmx_func` maps a function to group names. `struct imx1_pinctrl_soc_info` carries device pointer, static pins, parsed groups/functions, and counts. `IMX_PINCTRL_PIN()` wraps `PINCTRL_PIN()`, and `imx1_pinctrl_core_probe()` is the common probe entry.

Control flow: SoC files initialize static pins and call the core probe. The core fills mutable group/function arrays after parsing DT, then uses them in pinctrl and pinmux callbacks.

State and persistence: The header owns no state, but its structs define driver-lifetime parsed DT state. Hardware register persistence is managed by the core implementation.

Dependencies and integration points: Requires public pinctrl pin descriptor types from includers and platform device declarations. Used by i.MX1 and i.MX27 SoC drivers.

Risks: Encoded mux IDs are opaque bitfields decoded only by the core. Any binding change must preserve the `<PIN MUX_ID CONFIG>` layout or update parser and docs together. Mutable fields in `soc_info` make const-correctness impossible for current users.

Test signals: Build legacy SoC drivers, parse DT functions/groups, and exercise mux/config callbacks using representative mux ID encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx23.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx23.c

Purpose: Provides i.MX23 MXS-family pin numbers, pin descriptors, register offsets, and platform-driver registration for the shared MXS pinctrl core.

Important APIs and types: Defines `enum imx23_pin_enum`, `imx23_pins[]`, `imx23_regs` with `muxsel`, `drive`, and `pull` offsets, `imx23_pinctrl_data`, and a probe wrapper around `mxs_pinctrl_probe()`.

Control flow: `postcore_initcall()` registers the platform driver. OF match on `fsl,imx23-pinctrl` calls the probe wrapper, which delegates parsing and register programming to `pinctrl-mxs`.

State and persistence: This file stores immutable SoC data and one static `mxs_pinctrl_soc_data` instance. Runtime state and MMIO writes are owned by the MXS core. Selected mux/drive/pull values persist in MXS registers.

Dependencies and integration points: Depends on `pinctrl-mxs.h`, OF platform matching, and MXS DT bindings. It covers GPMI, LCD, PWM, SSP, I2C, AUART, rotary, and EMI pin banks.

Risks: `PINID(bank,pin)` numbering must match MXS hardware and DT bindings. Register offsets differ from i.MX28, so cross-copy mistakes can program drive or pull registers incorrectly.

Test signals: Build `CONFIG_PINCTRL_IMX23`, boot an i.MX23 board, inspect pin descriptors, select NAND/LCD/SSP/I2C/UART states, and verify drive/pull configuration through hardware behavior or debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx25.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx25.c

Purpose: Supplies i.MX25 pad IDs and pin descriptors for the common i.MX MMIO pinctrl driver, and registers the `fsl,imx25-iomuxc` platform driver.

Important APIs and types: Defines `enum imx25_pads`, `imx25_pinctrl_pads[]`, `imx25_pinctrl_info`, OF match table, `imx25_pinctrl_probe()`, and an `arch_initcall()` driver registration.

Control flow: Platform probe delegates directly to `imx_pinctrl_probe()`, which maps IOMUXC registers, parses DT functions/groups, registers the controller, and enables hog states.

State and persistence: The pad table and SoC info are immutable. Runtime parsed group/function data, register offsets, and current state are in the common i.MX driver. Hardware mux/pad values persist in IOMUXC registers.

Dependencies and integration points: Depends on `pinctrl-imx.h`, `CONFIG_PINCTRL_IMX`, OF bindings using i.MX25 register-offset cells, and consumers for external memory, LCD, CSI, I2C, CSPI, UART, SD, keypad, FEC, and boot/control pads.

Risks: The pad enum includes reserved pads and must align with register-offset-derived pin IDs in DT. Since this SoC info sets no special flags, the default six-cell `fsl,pins` MMIO format is expected. Bad DT offsets can select reserved descriptors.

Test signals: i.MX25 build/boot, valid `fsl,imx25-iomuxc` probe, default/sleep state selection, debugfs pad names, and peripheral tests for FEC, UART, SDHC, LCD, and NAND.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx27.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx27.c

Purpose: Supplies i.MX27 pad IDs and pin descriptors for the legacy i.MX1-style pinctrl core, and registers the `fsl,imx27-iomuxc` platform driver.

Important APIs and types: Defines port constants, `PAD_ID()`, `enum imx27_pads`, `imx27_pinctrl_pads[]`, `imx27_pinctrl_info`, OF match table, probe wrapper, and `arch_initcall()` registration.

Control flow: Platform probe calls `imx1_pinctrl_core_probe()`. The common legacy core parses DT functions/groups and programs port-based mux registers.

State and persistence: Static pad data lives here; parsed functions/groups are added to the mutable `imx27_pinctrl_info` by the core. Hardware state persists in legacy IOMUX registers through the core.

Dependencies and integration points: Depends on `pinctrl-imx1.h`, `CONFIG_PINCTRL_IMX1_CORE`, and DT bindings for i.MX27 mux ID/config triples. Covers LCD, SD, CSI, USB, I2C, SSI, ATA, CSPI, UART, NAND, PCMCIA, and clock/reset pads.

Risks: Sparse port-based pad IDs must match the legacy register layout. The shared legacy core has static descriptor/index state, so multiple instances would be risky even though SoC usage is normally single-instance. Mux IDs are opaque and easy to misencode in DT.

Test signals: i.MX27 build/boot, debugfs pin state reads, DT parsing for several functions, UART/USB/SD/FEC-equivalent peripheral pin selection, and pullup config tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx27.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx28.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx28.c

Purpose: Provides i.MX28 MXS-family pin descriptors and register offsets for the shared MXS pinctrl core.

Important APIs and types: Defines `enum imx28_pin_enum`, `imx28_pins[]`, `imx28_regs` with `muxsel = 0x100`, `drive = 0x300`, and `pull = 0x600`, `imx28_pinctrl_data`, probe wrapper, OF match table, and `postcore_initcall()` registration.

Control flow: OF match on `fsl,imx28-pinctrl` calls `mxs_pinctrl_probe()` with the i.MX28 data. The MXS core handles DT mapping, pinmux, pinconf, and MMIO writes.

State and persistence: Static SoC data is held here. Runtime controller state belongs to `pinctrl-mxs`. Mux, drive, and pull settings persist in MXS hardware registers.

Dependencies and integration points: Depends on `pinctrl-mxs.h`, `CONFIG_PINCTRL_MXS`, and i.MX28 DT bindings. It exposes pins for GPMI, LCD, SSP, AUART, PWM, SAIF, I2C, SPDIF, Ethernet, JTAG, and EMI.

Risks: i.MX28 has more banks and different drive/pull offsets than i.MX23, so shared-board assumptions can break. Missing enum entries for unavailable pins are intentional; DT must use valid `PINID()` values.

Test signals: Build `CONFIG_PINCTRL_IMX28`, boot i.MX28 hardware, inspect debugfs, and test NAND, LCD, MMC/SSP, UART, Ethernet, I2C, and drive-strength/pull states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx28.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx35.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx35.c

Purpose: Supplies the large i.MX35 pad descriptor table and platform-driver wrapper for the common i.MX MMIO pinctrl driver.

Important APIs and types: Defines `enum imx35_pads` with 485 entries including many reserved IDs, `imx35_pinctrl_pads[]`, `imx35_pinctrl_info`, OF match table for `fsl,imx35-iomuxc`, `imx35_pinctrl_probe()`, and `arch_initcall()` registration.

Control flow: Platform probe delegates to `imx_pinctrl_probe()`. All DT parsing, group/function registration, mux writes, pad config writes, and PM state forcing are handled by the common i.MX driver.

State and persistence: Static pad descriptors are immutable; parsed groups/functions and register-offset maps live in common-driver state. Hardware state persists in i.MX35 IOMUXC registers.

Dependencies and integration points: Depends on `pinctrl-imx.h`, `CONFIG_PINCTRL_IMX`, and i.MX35 DT bindings. The pad list spans external memory, CSI, I2C, SSI/ESAI-like audio, CSPI, UART, USB OTG, display, SD, ATA, MLB, FEC, boot/clock/reset, SDRAM, JTAG, and reserved register slots.

Risks: The table is large and reserve-heavy, so off-by-one enum changes can corrupt many DT-visible pin IDs. As with i.MX25, no special flags are set, so DT must use the default common i.MX cell format. Reserved pad descriptors may appear in debugfs but should not be selected by board pin states.

Test signals: i.MX35 build/boot, successful `fsl,imx35-iomuxc` probe, DT state selection for UART, FEC, SD, LCD, and NAND/ATA, debugfs pin count/name inspection, and suspend/resume default/sleep state checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/freescale/pinctrl-imx35.c -->
