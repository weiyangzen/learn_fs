# subset-b-005076 Research

Grouped research for the listed Ceph-client pinctrl files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-upboard.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-upboard.c

## Purpose
Implements the UP Board HAT pin controller for FPGA-backed header pins on UP and UP Squared boards. It exposes pinctrl/pinmux state for board functions such as I2C, SPI, UART, I2S, PWM, and ADC, and also registers a sparse GPIO forwarder so header pins can be requested as Linux GPIOs backed by an external GPIO provider.

## Important APIs, Types, And Functions
Key types are `enum upboard_pin_mode`, `struct upboard_pin`, `struct upboard_pingroup`, `struct upboard_pinctrl_data`, and `struct upboard_pinctrl`. Static UP and UP2 tables define pin descriptors, header pin order, pin groups, per-pin GPIO direction modes, and `struct pinfunction` entries. Runtime operations include `upboard_pinctrl_set_mux()`, `upboard_pinctrl_pin_get_mode()`, `upboard_gpio_request()`, `upboard_gpio_direction_input()`, `upboard_gpio_direction_output()`, and `upboard_pinctrl_probe()`.

## Control Flow
Probe obtains the parent `upboard_fpga`, selects UP or UP2 tables from `fpga_data->type`, rejects unsupported DMI boards, allocates one `regmap_field` set per pin for function-enable, GPIO-enable, and direction bits, registers pinctrl, adds generic groups/functions, registers DMI-provided default mappings, selects the default state, enables the pinctrl device, and finally registers the GPIO forwarder plus sparse pin range. Pinmux selection iterates group pins, switches function-capable pins through `funcbit`, otherwise enables GPIO mode and sets the expected direction.

## State And Persistence
State persists in FPGA registers accessed through the parent regmap: function-enable bits, GPIO-enable bits, and GPIO direction bits. Driver-owned state is devm-managed and includes pin tables, generic group/function registrations, pin range metadata, and GPIO forwarder descriptors added on request.

## Dependencies And Integration Points
Depends on the UP board MFD FPGA driver, regmap, DMI matching, generic pinctrl/pinmux helpers, `gpio/forwarder`, and gpiolib consumer/provider APIs. The DMI mapping currently targets `AAEON` `UP-APL01` and maps default states onto Intel ACPI devices such as `INT3452:*`.

## Risks
Board support is gated by DMI data, so new UP variants need explicit mappings. Function-mode pins without `funcbit` reject function selection with `-EPERM`. Default mappings include an `ssp0` group/function name that is not defined in the local UP/UP2 tables, so validation depends on whether that mapping is ever selected for a supported board. GPIO forwarder request failures must release pinctrl ownership, which this driver handles but remains a key error path.

## Test Signals
Useful signals are probe success on UP and UP2 hardware, default-state selection without unresolved groups/functions, debugfs pin mode output, GPIO request/free/direction round trips through the forwarder, and register traces showing `funcbit`, `enbit`, and `dirbit` updates for each mux mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-upboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-utils.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-utils.c

## Purpose
Provides small exported helper routines used by pinctrl drivers when building dynamic `struct pinctrl_map` arrays and config arrays from firmware or device-tree parsing.

## Important APIs, Types, And Functions
Exports `pinctrl_utils_reserve_map()`, `pinctrl_utils_add_map_mux()`, `pinctrl_utils_add_map_configs()`, `pinctrl_utils_add_config()`, and `pinctrl_utils_free_map()`. The functions operate on `struct pinctrl_map`, `enum pinctrl_map_type`, and packed pinconf config arrays.

## Control Flow
`pinctrl_utils_reserve_map()` grows a map allocation with `krealloc_array()` when the requested reserve exceeds the current capacity and zeroes new slots. Add helpers append mux or config entries and increment `num_maps`. Config map insertion duplicates the config array with `kmemdup_array()`. `pinctrl_utils_add_config()` appends one packed config to a resizable `unsigned long` array. `pinctrl_utils_free_map()` walks map entries and frees duplicated config arrays for group or pin config maps before freeing the map itself.

## State And Persistence
The helpers only manage caller-owned heap allocations. They do not persist state outside the returned map/config pointers and updated counters.

## Dependencies And Integration Points
Used by driver `.dt_free_map` callbacks and custom DT parsers. It depends on core pinctrl map types, `pinctrl_dev` only for device-scoped error logging, and slab allocation helpers.

## Risks
Callers must keep `reserved_maps`, `num_maps`, and ownership conventions consistent. `pinctrl_utils_add_map_mux()` stores group/function pointers without duplicating strings, so their lifetime must exceed map use. Only config maps get deep-freed by `pinctrl_utils_free_map()`.

## Test Signals
Compile coverage with drivers using dynamic map construction, DT parsing tests that allocate mux plus config maps, allocation-failure injection, and leak checking around `dt_free_map` paths are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-utils.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-utils.h

## Purpose
Declares the shared pinctrl map/config construction helpers implemented in `pinctrl-utils.c`.

## Important APIs, Types, And Functions
The header exposes prototypes for reserving map capacity, adding mux maps, adding group/pin config maps, appending single packed configs, and freeing generated maps. It includes `<linux/pinctrl/machine.h>` for `struct pinctrl_map` and `enum pinctrl_map_type`, and forward declares `struct pinctrl_dev`.

## Control Flow
There is no runtime control flow in the header. It defines a compile-time interface consumed by pinctrl drivers and DT parsers.

## State And Persistence
No state is stored here. The API contract describes caller-owned allocation state passed through pointer parameters.

## Dependencies And Integration Points
Integrated with pinctrl core map registration and with drivers that use `pinconf_generic_dt_node_to_map_all()` or custom map assembly. The include guard is `__PINCTRL_UTILS_H__`.

## Risks
Because the API is pointer-counter based, misuse can compile cleanly but corrupt map accounting at runtime. Any signature change affects many platform pinctrl drivers.

## Test Signals
Build all pinctrl drivers that include this header, especially DT-enabled drivers using `.dt_free_map = pinctrl_utils_free_map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-xway.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-xway.c

## Purpose
Implements the Lantiq XWAY-family pinctrl, pinmux, pinconf, and GPIO driver for ASE, Danube, xRX100, xRX200, and xRX300 SoCs. Large static tables describe each SoC's multifunction pins, groups, functions, and external interrupt pin mapping; shared MMIO code applies mux, GPIO, and pinconf changes.

## Important APIs, Types, And Functions
Important data includes `enum xway_mux`, `struct pinctrl_xway_soc`, per-SoC `ltq_mfp_pin` arrays, `ltq_pin_group` arrays, and `ltq_pmx_func` arrays. Runtime functions include `xway_mux_apply()`, `xway_pinconf_get()`, `xway_pinconf_set()`, `xway_pinconf_group_set()`, GPIO callbacks `xway_gpio_get/set/dir_in/dir_out/to_irq()`, and `pinmux_xway_probe()`.

## Control Flow
Probe maps the MMIO resource, selects SoC data from OF match data with Danube fallback, creates one pin descriptor per GPIO, fills the generic Lantiq `ltq_pinmux_info`, registers with `ltq_pinctrl_register()`, registers a GPIO chip, and adds a pinctrl GPIO range for older DTs lacking `gpio-ranges`. Mux application writes two alternate-function bits per pin through `GPIO_ALT0` and `GPIO_ALT1`, with special port-3 register offsets. Pinconf get/set reads or mutates open-drain, pull, and output direction registers.

## State And Persistence
Runtime state is mostly MMIO register state: ALT0/ALT1 mux bits, output, input, direction, open-drain, pull-enable, and pull-select registers. Driver metadata is stored in the global `xway_info`, `xway_pctrl_desc`, and `xway_chip` structures filled at probe time.

## Dependencies And Integration Points
Depends on the shared Lantiq pinctrl layer from `pinctrl-lantiq.h`, `lantiq_soc.h` register helpers, gpiolib, OF matching, and the Lantiq external interrupt helper `ltq_eiu_get_irq()`. It integrates with DT compatible strings `lantiq,ase-pinctrl`, `lantiq,danube-pinctrl`, `lantiq,xrx100-pinctrl`, `lantiq,xrx200-pinctrl`, and `lantiq,xrx300-pinctrl`.

## Risks
The driver uses global mutable state, so it assumes one active controller instance. Port-3 special-case offsets are easy to break when changing register definitions. Table accuracy is critical because the generic Lantiq layer trusts group/function mux values. GPIO `to_irq()` returns `-1` rather than a standard negative errno when no EXIN mapping exists.

## Test Signals
Signals include per-compatible probe, pinmux selection for representative functions on each SoC family, pinconf readback for open-drain and pulls, GPIO direction/value tests across ports including port 3, `gpio-ranges` and legacy range paths, and external IRQ mapping for every EXIN entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-xway.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-zynq.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-zynq.c

## Purpose
Implements the classic Xilinx Zynq pinctrl, pinmux, and pinconf driver for 54 MIO pins plus EMIO SD card-detect/write-protect pseudo pins. Static tables model all supported groups and functions, while register access goes through a syscon regmap.

## Important APIs, Types, And Functions
Core types are `struct zynq_pinctrl`, `struct zynq_pctrl_group`, and `struct zynq_pinmux_function`. Important functions include `zynq_pinmux_set_mux()`, `zynq_pinconf_cfg_get()`, `zynq_pinconf_cfg_set()`, `zynq_pinconf_group_set()`, and `zynq_pinctrl_probe()`. The driver defines custom `PIN_CONFIG_IOSTANDARD` plus generic pinconf parameters for bias, slew, power source, and low-power receiver disable.

## Control Flow
Probe looks up a `syscon` phandle, uses the platform memory resource start as the pinctrl register offset, assigns static group/function tables, and registers the pinctrl descriptor. Pinmux maps a requested function/group either by writing per-pin mux bits in each MIO register or, for SDIO CD/WP functions, by writing dedicated selector fields. Pinconf get/set reads the target MIO register, interprets or updates tristate, pull-up, speed, IO standard, power source, and receiver-disable bits, then writes the register back.

## State And Persistence
Hardware state persists in the syscon register block. Driver state is devm-managed `struct zynq_pinctrl` with pointers to static group and function tables. EMIO pins are present for SDIO CD/WP mux selection but normal pinconf rejects pins beyond `ZYNQ_NUM_MIOS`.

## Dependencies And Integration Points
Integrates with DT compatible `xlnx,pinctrl-zynq`, the syscon provider, generic DT pinconf parsing through `pinconf_generic_dt_node_to_map_all`, and `pinctrl_utils_free_map`. It participates in the kernel pinctrl, pinmux, and generic pinconf APIs.

## Risks
The large static tables must match Zynq silicon mux encodings exactly. Group names with SDIO card-detect/write-protect pseudo pins have special register behavior unlike normal mux groups. Invalid IO-standard warnings print the parameter value rather than the invalid argument, reducing diagnostics. Register read/write errors are collapsed to `-EIO` in pinconf paths.

## Test Signals
Use DT states for representative Ethernet, USB, SDIO, SPI, UART, I2C, GPIO, and SDIO CD/WP functions; verify syscon register writes; test pinconf readback for supported parameters; and run compile tests with `CONFIG_PINCTRL_ZYNQ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-zynq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-zynqmp.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-zynqmp.c

## Purpose
Implements the Xilinx ZynqMP and Versal pinctrl driver using firmware platform-management APIs instead of direct MMIO. It discovers pins, functions, groups, and group membership from firmware, then services mux and config requests by calling firmware pinctrl operations.

## Important APIs, Types, And Functions
Key types are `struct zynqmp_pinctrl`, `struct zynqmp_pmux_function`, and `struct zynqmp_pctrl_group`. Important paths include `zynqmp_pinmux_request_pin()`, `zynqmp_pinmux_set_mux()`, `zynqmp_pinmux_release_pin()`, `zynqmp_pinconf_cfg_get()`, `zynqmp_pinconf_cfg_set()`, `zynqmp_pinctrl_prepare_pin_desc()`, `versal_pinctrl_prepare_pin_desc()`, `zynqmp_pinctrl_prepare_function_info()`, and `zynqmp_pinctrl_probe()`.

## Control Flow
Probe queries the SoC family, prepares pin descriptors differently for ZynqMP and Versal, discovers the number of functions, each function name, each function's group count, group-to-pin membership, and function-to-group names, then registers the pinctrl device. Mux request/release and set_mux call `zynqmp_pm_pinctrl_request()`, `zynqmp_pm_pinctrl_release()`, and `zynqmp_pm_pinctrl_set_function()`. Pinconf get/set translates generic pinconf parameters to PM firmware config IDs and drive-strength encodings.

## State And Persistence
Persistent hardware state lives in platform firmware and pin controller registers managed by firmware. Driver state is dynamically allocated arrays of pin descriptors, function descriptors, and group descriptors. `family_code` and the global `zynqmp_desc` hold family-dependent descriptor state.

## Dependencies And Integration Points
Depends on `<linux/firmware/xlnx-zynqmp.h>`, PM query IDs, DT compatibles `xlnx,zynqmp-pinctrl` and `xlnx,versal-pinctrl`, generic DT pinconf parsing, and `pinctrl_utils_free_map`. Versal also requires firmware support for `PM_QID_PINCTRL_GET_ATTRIBUTES`.

## Risks
Firmware response correctness is critical; group IDs index directly into allocated arrays. `MAX_GROUP_PIN`, `MAX_PIN_GROUPS`, and response chunk sizes bound discovery. Versal pin numbers use firmware attributes and non-ZynqMP code adjusts pin bitmap indexes by subtracting one, which is a subtle family-specific path. `zynqmp_pinconf_cfg_set()` logs failures per config but returns 0 after the loop, so callers may not see firmware set failures.

## Test Signals
Probe on ZynqMP and Versal firmware, PM query failure injection, mux request/set/release traces, DT pinconf application for pull, slew, Schmitt, drive strength, tristate, and output enable, and validation that discovered group/function names match firmware expectations are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-zynqmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinmux.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinmux.c

## Purpose
Provides the core pinmux implementation used by the pinctrl subsystem. It validates pinmux ops and maps, arbitrates ownership between mux users and GPIO users, enables/disables mux settings, exposes debugfs views, and implements generic pin function storage when `CONFIG_GENERIC_PINMUX_FUNCTIONS` is enabled.

## Important APIs, Types, And Functions
Important exported or internal APIs include `pinmux_check_ops()`, `pinmux_validate_map()`, `pinmux_can_be_used_for_gpio()`, `pinmux_request_gpio()`, `pinmux_free_gpio()`, `pinmux_gpio_direction()`, `pinmux_map_to_setting()`, `pinmux_enable_setting()`, `pinmux_disable_setting()`, `pinmux_init_device_debugfs()`, and generic function helpers such as `pinmux_generic_add_function()` and `pinmux_generic_get_function_groups()`.

## Control Flow
Map-to-setting resolves a function name to a selector, validates the requested group against that function's group list, and stores function/group selectors in the setting. Enabling a setting obtains group pins, requests each pin, records `desc->mux_setting`, and calls the driver's `set_mux()`. Error paths release already requested pins. Disabling a setting frees only pins whose current mux setting still matches the setting being disabled. GPIO request/free paths allocate an owner string, update `gpio_owner`, and call optional driver GPIO hooks.

## State And Persistence
State lives in each `struct pin_desc`: `mux_owner`, `gpio_owner`, `mux_usecount`, and `mux_setting`, protected by `desc->mux_lock`. Module references are held while pins are requested. Generic functions are stored in `pctldev->pin_function_tree` and counted in `pctldev->num_functions`.

## Dependencies And Integration Points
Integrated with pinctrl core internals in `core.h`, driver `pinmux_ops`, driver `pinctrl_ops`, gpiolib pin ranges, debugfs, radix trees, and module reference counting. Debugfs exposes `pinmux-functions`, `pinmux-pins`, and writable `pinmux-select`.

## Risks
Strict controllers rely on correct ownership checks to prevent unsafe GPIO/mux overlap. The debugfs `pinmux-select` path calls driver `set_mux()` directly and does not update normal pin ownership state. Generic function removal decrements `num_functions`, which can leave sparse selector indexes if removals are not last-in-order. Callers must not free pins more times than requested.

## Test Signals
Core test signals include map validation failures, concurrent mux/GPIO request arbitration on strict and non-strict controllers, error unwinding from `set_mux()`, debugfs output consistency, generic function add/remove lookup behavior, and lockdep coverage around `mux_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinmux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinmux.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pinmux.h

## Purpose
Defines the private interface between pinctrl core and the pinmux implementation, including no-op stubs when pinmux or debugfs support is disabled and optional generic function helper declarations.

## Important APIs, Types, And Functions
Declares core pinmux helpers for operation validation, map validation, GPIO request/free/direction, map-to-setting conversion, setting enable/disable, debugfs display, and generic function management. Defines `struct function_desc` under `CONFIG_GENERIC_PINMUX_FUNCTIONS`.

## Control Flow
The header has no runtime flow, but preprocessor branches decide whether callers invoke real pinmux functions or inline stubs. With `CONFIG_PINMUX=n`, most operations return success or permissive defaults. With debugfs disabled, debug display hooks compile away.

## State And Persistence
No direct state is stored here. The generic `function_desc` type describes entries stored in a pinctrl device radix tree by `pinmux.c`.

## Dependencies And Integration Points
Consumed by pinctrl core and drivers that use internal generic function helpers. Depends on pinctrl core types, `struct dentry`, `struct seq_file`, and public `struct pinfunction` definitions.

## Risks
Stubbed behavior can mask missing pinmux support in builds where `CONFIG_PINMUX` is disabled. Any prototype mismatch with `pinmux.c` breaks core compilation. The generic helper declarations are only available when the corresponding Kconfig symbol is enabled.

## Test Signals
Build matrices with `CONFIG_PINMUX`, `CONFIG_DEBUG_FS`, and `CONFIG_GENERIC_PINMUX_FUNCTIONS` enabled and disabled provide the main signal, along with compile coverage of drivers using generic pinmux helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pinmux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/Kconfig

## Purpose
Defines Kconfig symbols for Marvell PXA2xx pinctrl support and chip-specific PXA25x/PXA27x drivers.

## Important APIs, Types, And Functions
Symbols are `PINCTRL_PXA`, `PINCTRL_PXA25X`, and `PINCTRL_PXA27X`. The common symbol selects `PINMUX`, `PINCONF`, and `GENERIC_PINCONF`; chip symbols select the common symbol and default to `y` on matching platform symbols.

## Control Flow
The menu is visible only when `ARCH_PXA` or `COMPILE_TEST` is set. Selecting a chip driver pulls in common PXA pinctrl support and controls Makefile object inclusion.

## State And Persistence
State is build-time configuration persisted in `.config`; no runtime state is created by this file.

## Dependencies And Integration Points
Works with `drivers/pinctrl/pxa/Makefile` and the PXA platform Kconfig symbols `PXA25x` and `PXA27x`.

## Risks
Because `PINCTRL_PXA` is hidden and selected, common driver coverage depends on at least one chip symbol. Missing dependencies on OF or platform resources would surface at build/probe time rather than menu visibility.

## Test Signals
`olddefconfig` on PXA platforms, `COMPILE_TEST` builds, and verifying object inclusion for both chip symbols are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/Makefile

## Purpose
Builds the Marvell PXA pinctrl objects selected by Kconfig.

## Important APIs, Types, And Functions
`CONFIG_PINCTRL_PXA25X` builds `pinctrl-pxa2xx.o` plus `pinctrl-pxa25x.o`; `CONFIG_PINCTRL_PXA27X` builds `pinctrl-pxa2xx.o` plus `pinctrl-pxa27x.o`.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` assignments and links the common implementation with the selected chip-specific table/probe file.

## State And Persistence
This is build-time state only. It does not persist runtime data.

## Dependencies And Integration Points
Integrates with `pxa/Kconfig`, the common exported `pxa2xx_pinctrl_init()` symbol, and the chip-specific platform drivers.

## Risks
If both chip drivers are built into the same linked object scope, `pinctrl-pxa2xx.o` appears in both object lists; Kbuild normally handles duplicate object references, but changes should preserve one common implementation for both variants.

## Test Signals
Build `CONFIG_PINCTRL_PXA25X=m`, `CONFIG_PINCTRL_PXA27X=m`, and both enabled together to verify object selection and symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa25x.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa25x.c

## Purpose
Provides the PXA25x-specific pin descriptor table and platform probe wrapper for the common PXA2xx pinctrl implementation.

## Important APIs, Types, And Functions
The file defines `pxa25x_pins[]` using `PXA_GPIO_ONLY_PIN`, `PXA_GPIO_PIN`, `PXA_PINCTRL_PIN`, and `PXA_FUNCTION` macros from `pinctrl-pxa2xx.h`. Runtime code is `pxa25x_pinctrl_probe()`, the OF match table for `marvell,pxa25x-pinctrl`, and a `platform_driver`.

## Control Flow
Probe maps alternate-function, direction, and sleep-state register resources, derives per-bank pointers, then calls `pxa2xx_pinctrl_init()` with the PXA25x table. The common code builds one group per pin and unique function lists from the table.

## State And Persistence
Persistent hardware state is in PXA GPIO alternate-function, direction, and sleep registers. This file contributes static pin/function metadata; allocated pinctrl state is owned by the common driver.

## Dependencies And Integration Points
Depends on platform resources in the order expected by probe and on the common PXA2xx implementation exported from `pinctrl-pxa2xx.c`. It integrates with OF through `marvell,pxa25x-pinctrl`.

## Risks
The table is the source of truth for every PXA25x mux option, so duplicate or incorrect function names change generated function groups. Register pointer arithmetic uses `sizeof(base_af[0])`, the pointer size, as a stride, which assumes the mapped resources are laid out as expected by the original register bank model.

## Test Signals
Probe with a PXA25x DT node, function list/group generation, muxing representative UART/MMC/LCD/PCMCIA pins, GPIO direction changes, and sleep-state pinconf updates are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa25x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa27x.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa27x.c

## Purpose
Provides the PXA27x-specific pin/function table and platform driver wrapper for the shared PXA2xx pinctrl implementation.

## Important APIs, Types, And Functions
The main data is `pxa27x_pins[]`, a large table of GPIO-capable pins and alternate functions covering UART, SSP, USB, camera, keypad, LCD, AC97/I2S, MMC, memory, and other PXA27x blocks. Runtime code is `pxa27x_pinctrl_probe()`, the OF match table `marvell,pxa27x-pinctrl`, and the module platform driver.

## Control Flow
Probe maps the same register resource layout as PXA25x, computes bank base arrays, and calls `pxa2xx_pinctrl_init()` with PXA27x descriptors. The common implementation derives groups and functions dynamically from the descriptor table and handles all mux/pinconf operations.

## State And Persistence
The file itself is static metadata. Hardware persistence is in PXA27x GAFR, GPDR, and PGSR registers accessed by the common implementation.

## Dependencies And Integration Points
Depends on `pinctrl-pxa2xx.h` macros and `pxa2xx_pinctrl_init()`. It is selected by `CONFIG_PINCTRL_PXA27X` and matched by OF compatible `marvell,pxa27x-pinctrl`.

## Risks
The table contains many repeated function names with different direction and alternate-function values; grouping is name-based, so naming mistakes can merge or split function groups incorrectly. Like PXA25x, resource ordering and derived bank-pointer strides must match platform register layout.

## Test Signals
Compile with `CONFIG_PINCTRL_PXA27X`, probe on PXA27x hardware or emulation, inspect generated function groups, and verify mux programming for high-use blocks such as FFUART, MMC, LCD, camera, and USB pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa27x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa2xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa2xx.c

## Purpose
Implements the common Marvell PXA2xx pinctrl, pinmux, and pinconf logic used by PXA25x and PXA27x table drivers.

## Important APIs, Types, And Functions
Important operations include group callbacks `pxa2xx_pctrl_get_*`, mux callbacks `pxa2xx_pmx_set_mux()` and `pxa2xx_pmx_gpio_set_direction()`, pinconf callbacks `pxa2xx_pconf_group_get/set()`, state builders `pxa2xx_build_functions()`, `pxa2xx_build_groups()`, `pxa2xx_build_state()`, and exported initializer `pxa2xx_pinctrl_init()`.

## Control Flow
Initialization allocates driver state, copies register base arrays, builds one group per pin, derives a unique function list by scanning all chip-specific pin descriptors, builds each function's group list by matching names, and registers the pinctrl device. Mux selection finds the descriptor for the requested pin/function, writes alternate-function bits in the GAFR bank, and updates direction in GPDR. GPIO direction changes only update GPDR. Low-power pinconf reads/writes per-pin sleep-state bits in PGSR.

## State And Persistence
State persists in PXA hardware registers: GAFR for alternate functions, GPDR for direction, and PGSR for sleep GPIO state. Driver-built state includes devm-managed pin descriptors, groups, functions, group lists, base register arrays, and a spinlock protecting register updates.

## Dependencies And Integration Points
Integrates with pinctrl, pinmux, generic pinconf, optional OF DT parsing via `pinconf_generic_dt_node_to_map_all`, and chip-specific PXA25x/PXA27x wrappers. Exports `pxa2xx_pinctrl_init()` for those wrappers.

## Risks
Function identity is string-based and per-pin descriptors can include duplicate names with different mux values. Groups are single-pin only, so multi-pin peripheral states rely on selecting the same function on multiple pin groups. Register-bank array sizing uses `roundup(maxpin, 16/32)` as a count driver, which overallocates but relies on chip wrappers filling enough base pointers.

## Test Signals
Signals include generated function/group listings, mux writes to GAFR/GPDR for representative pins, GPIO direction calls, PGSR low-power config set/get, DT map parsing, and concurrent mux operations under spinlock/lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa2xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa2xx.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa2xx.h

## Purpose
Defines the shared PXA2xx pin descriptor DSL, driver data structures, and initializer prototype used by the PXA25x and PXA27x pinctrl drivers.

## Important APIs, Types, And Functions
Macros include `PXA_FUNCTION`, `PXA_PIN`, `PXA_GPIO_PIN`, `PXA_GPIO_ONLY_PIN`, and `PXA_PINCTRL_PIN`. Types include `struct pxa_desc_function`, `struct pxa_desc_pin`, and `struct pxa_pinctrl`. The header declares `pxa2xx_pinctrl_init()`.

## Control Flow
There is no executable flow. Chip-specific files use the macros to build static arrays that the common implementation later scans to derive pinctrl groups and pinmux functions.

## State And Persistence
No runtime state is allocated by the header. `struct pxa_pinctrl` describes runtime state stored by the common implementation, including MMIO bases, generated groups/functions, pinctrl descriptor, and spinlock.

## Dependencies And Integration Points
Depends on generic pinctrl types through included C files and is included by `pinctrl-pxa2xx.c`, `pinctrl-pxa25x.c`, and `pinctrl-pxa27x.c`.

## Risks
The macro DSL hides compound-literal function arrays inside static pin tables, so descriptor lifetime depends on static storage usage in chip files. Direction and alternate-function encoding are packed into `muxval`; incorrect macro arguments directly program wrong hardware bits.

## Test Signals
Compile both chip drivers, inspect generated function/group state, and validate that macro-generated GPIO input/output functions are present on every GPIO-capable pin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa2xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/Kconfig

## Purpose
Defines the Qualcomm pinctrl Kconfig menu, including the TLMM core, PMIC GPIO/MPP drivers, LPASS LPI core, and LPASS LPI SoC variants.

## Important APIs, Types, And Functions
Primary symbols are `PINCTRL_MSM`, `PINCTRL_QCOM_SPMI_PMIC`, `PINCTRL_QCOM_SSBI_PMIC`, `PINCTRL_LPASS_LPI`, and LPASS variants such as `PINCTRL_MILOS_LPASS_LPI`, `PINCTRL_SC7280_LPASS_LPI`, `PINCTRL_SDM660_LPASS_LPI`, `PINCTRL_SM8250_LPASS_LPI`, `PINCTRL_SM8550_LPASS_LPI`, and `PINCTRL_SM8650_LPASS_LPI`. It also sources `drivers/pinctrl/qcom/Kconfig.msm` for many SoC TLMM symbols.

## Control Flow
The menu is visible under `ARCH_QCOM` or `COMPILE_TEST`. Selecting symbols pulls in required pinmux, pinconf, gpiolib, irqchip, regmap, SPMI, SSBI, OF, and Qualcomm SCM dependencies. Makefile object rules consume these symbols to build the matching drivers.

## State And Persistence
Only build-time `.config` state is persisted. Runtime state is created by the selected driver objects, not this file.

## Dependencies And Integration Points
Integrates Qualcomm pinctrl with OF, GPIOLIB, hierarchical IRQ domains, QCOM SCM, SPMI/SSBI PMIC buses, and the qcom Makefile. `PINCTRL_MSM` is the common TLMM core dependency for SoC-specific entries sourced from `Kconfig.msm`.

## Risks
Dependency mistakes can expose drivers without required bus or IRQ infrastructure. LPASS variants depend on the LPASS core symbol, so missed dependencies hide variants. The sourced `Kconfig.msm` file must stay aligned with Makefile object names.

## Test Signals
`allmodconfig`, `COMPILE_TEST`, Qualcomm defconfig builds, menu visibility checks, and dependency-cycle checks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/Makefile

## Purpose
Maps Qualcomm pinctrl Kconfig symbols to the corresponding driver objects.

## Important APIs, Types, And Functions
Build rules cover the common `pinctrl-msm.o`, many TLMM SoC drivers, PMIC SPMI/SSBI GPIO and MPP drivers, LPASS LPI core and variants, `tlmm-test.o`, and newer platform objects such as `pinctrl-qcs8300.o`, `pinctrl-milos.o`, and `pinctrl-sm8750.o`.

## Control Flow
Kbuild includes each object when its `CONFIG_PINCTRL_*` symbol is enabled. Shared symbols can build multiple objects, for example SPMI PMIC builds both GPIO and MPP drivers.

## State And Persistence
The file controls build artifacts only. It does not create runtime state directly.

## Dependencies And Integration Points
Must stay in sync with `qcom/Kconfig` and `qcom/Kconfig.msm`, source filenames, and module expectations. It integrates TLMM, PMIC, LPASS, and test drivers into the pinctrl subsystem build.

## Risks
Missing or stale object mappings produce configured-but-unbuilt drivers or build failures. Formatting inconsistencies are low risk but make new entries harder to audit. Shared Kconfig symbols that build multiple objects must preserve both pieces.

## Test Signals
Build with representative Qualcomm symbols enabled as modules and built-ins, run `allmodconfig`, and verify every Kconfig symbol has a matching object when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/Makefile -->
