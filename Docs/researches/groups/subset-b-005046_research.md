# subset-b-005046 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g6.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g6.c

## Purpose
This file is the AST2600, also called Aspeed generation 6, pinctrl driver data and registration unit. It binds the generic Aspeed pinctrl and pinmux helpers to AST2600-specific pins, groups, functions, register offsets, pin configuration capabilities, and a generation-specific expression setter. The bulk of the file is static SoC description data generated through the macro layer in `pinmux-aspeed.h`.

## Important APIs, types, and functions
The source defines SCU register offsets for AST2600 multi-function control, strap, pull-down, drive strength, and USB/PCIe related registers. `ASPEED_G6_NR_PINS` declares 258 pin slots, and the `#define <ball> <number>` blocks describe each physical ball or logical pin index. `SIG_EXPR_LIST_DECL_*`, `PIN_DECL_*`, `FUNC_GROUP_DECL`, `GROUP_DECL`, and `FUNC_DECL_*` create the per-pin priority expression data, group pin arrays, and function-to-group arrays consumed by the common Aspeed code. `aspeed_g6_pins`, `aspeed_g6_groups`, and `aspeed_g6_functions` are the exported data tables for the Linux pinctrl core. `aspeed_g6_configs` maps supported generic pinconf parameters to SCU bitfields. `aspeed_g6_sig_expr_set()` is the AST2600 write path for mux expressions, including special handling for hardware strap registers. `aspeed_g6_pinctrl_probe()` fixes pin descriptor numbers to array indices and calls `aspeed_pinctrl_probe()`. `arch_initcall(aspeed_g6_pinctrl_init)` registers the platform driver early.

## Control flow
At boot, `aspeed_g6_pinctrl_init()` registers the platform driver matching `aspeed,ast2600-pinctrl`. Probe iterates through `aspeed_g6_pins` and normalizes each descriptor number to its array index, then delegates registration to the common Aspeed probe. Once registered, Linux pinctrl operations call common helpers in `pinctrl-aspeed.c`, which use the tables in this file. A mux request selects a function and group, walks every pin in that group, disables higher-priority expressions, and enables the matching expression by calling `aspeed_g6_sig_expr_set()`. Pin configuration requests are routed through the common Aspeed pinconf helpers, which look up entries in `aspeed_g6_configs` and write the configured SCU bitfields using the `aspeed_g6_pin_config_map`.

## State and persistence behavior
The driver has no file-backed or heap-persistent state beyond static kernel tables and the shared `aspeed_g6_pinctrl_data` instance. Effective state lives in AST2600 SCU registers and persists according to hardware reset domains, strap behavior, and platform firmware policy. `aspeed_g6_sig_expr_set()` writes normal SCU mux bits with `regmap_update_bits()`. For `SCU500` and `SCU510` strap descriptors, it also uses paired write-1-clear registers at `SCU504` and `SCU514` before updating the strap value, relying on platform write-protection masks if firmware wants strap values immutable. Pinconf state is likewise SCU register state for pull enables, drive strength, and power source.

## Dependencies and integration points
This file depends on the Aspeed helper types and macros in `pinctrl-aspeed.h` and `pinmux-aspeed.h`, the common helper implementation in `pinctrl-aspeed.c`, and the generic Linux pinctrl, pinmux, pinconf, platform driver, regmap, and device tree infrastructure. It integrates with the AST2600 syscon parent through the common probe, which supplies the SCU regmap. Device tree consumers use the exposed function and group names in pinctrl nodes, while GPIO consumers use `gpio_request_enable` through common Aspeed code. Subsystems affected by this table include MDIO/MAC, RMII/RGMII/NCSI, SD/eMMC, LPC/eSPI, SPI/QSPI/FW SPI, I2C/I3C, UART, PWM/TACH, ADC, USB, PCIe reset, JTAG, FSI, and pass-through GPIO.

## Risks
The largest risk is table correctness: a wrong pin number, group membership, priority ordering, strap bit, or function name silently routes board pins incorrectly. Hardware strap descriptors are especially sensitive because writes can affect boot-mode or interface-selection semantics and may fail under write protection. Several expressions combine normal mux bits with strap bits, so request ordering and verification matter. There is an explicit FIXME around I3C3/I3C4 and FSI priority and bit confirmation for four pins, marking an unresolved hardware interpretation risk. The array is sorted by symbol name for readability while pin numbers are reset during probe, so accidental omissions or duplicate macro symbols can be compile-time or runtime defects. `aspeed_g6_sig_expr_set()` assumes `desc->ip` is SCU and only warns otherwise, so adding non-SCU descriptors would require careful extension.

## Test signals
Useful tests include building with `CONFIG_PINCTRL_ASPEED_G6` and warnings enabled to catch duplicate macro symbols, unused aliases, and missing group/function declarations. Runtime validation should boot an AST2600 or emulator with representative device tree pinctrl states and confirm `/sys/kernel/debug/pinctrl` group/function listings, GPIO muxing, and pinconf application. Hardware smoke tests should cover at least RGMII/RMII selection, I2C/I3C pins, LPC/eSPI selection, SD/eMMC width groups, SPI/QSPI, UART alternate groups, and strap-protected paths. Negative tests should request unsupported configs and invalid group/function combinations and expect `-ENXIO`, `-ENOTSUPP`, `-EINVAL`, or `-EPERM` as appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed-g6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed.c

## Purpose
This is the common implementation for Aspeed pinctrl, pinmux, GPIO mux enable, probe, and generic pin configuration handling. SoC-specific files supply tables and optional pinmux operations, while this file implements the Linux pinctrl callbacks that interpret those tables.

## Important APIs, types, and functions
Group callbacks are `aspeed_pinctrl_get_groups_count()`, `aspeed_pinctrl_get_group_name()`, `aspeed_pinctrl_get_group_pins()`, and `aspeed_pinctrl_pin_dbg_show()`. Function callbacks are `aspeed_pinmux_get_fn_count()`, `aspeed_pinmux_get_fn_name()`, and `aspeed_pinmux_get_fn_groups()`. Mux control is implemented by `aspeed_pinmux_set_mux()`, with helpers `aspeed_sig_expr_enable()`, `aspeed_sig_expr_disable()`, `aspeed_disable_sig()`, and `aspeed_find_expr_by_name()`. GPIO routing is handled by `aspeed_gpio_request_enable()`, `aspeed_expr_is_gpio()`, and `aspeed_gpio_in_exprs()`. Registration is handled by `aspeed_pinctrl_probe()`. Pin configuration is implemented by `aspeed_pin_config_get()`, `aspeed_pin_config_set()`, `aspeed_pin_config_group_get()`, and `aspeed_pin_config_group_set()`, with lookup helpers for config ranges and config maps.

## Control flow
The pinctrl core calls group and function accessors directly into static SoC data through `struct aspeed_pinctrl_data`. For a mux request, `aspeed_pinmux_set_mux()` walks each pin in the selected group. For each pin it scans priority levels in order. Until it finds an expression whose `function` matches the selected function, it disables every expression in higher-priority levels. When it finds the matching expression, it enables it and continues to the next pin. If no expression is found, it constructs debug strings listing available signals and functions and returns `-ENXIO`. GPIO requests follow a similar priority walk but search for a pin-specific GPIO expression by name convention. Pinconf get/set first find a pin range and parameter entry, then translate between generic pinconf arguments and hardware bitfield values through `confmaps`.

## State and persistence behavior
This file does not allocate long-lived domain state except transient diagnostic strings in error paths. Persistent state is held in the SoC regmap registers supplied by the parent syscon and in the platform driver's `aspeed_pinctrl_data`. `aspeed_pinctrl_probe()` obtains the SCU regmap via `syscon_node_to_regmap()`, stores it in `pdata->scu`, and installs it into `pdata->pinmux.maps[ASPEED_IP_SCU]`. Pinmux and pinconf changes persist in hardware registers until reset or later writes. Group configuration applies per-pin writes and stops on the first failure, so partial configuration can remain if earlier pins succeeded.

## Dependencies and integration points
The implementation depends on Linux pinctrl, pinmux, pinconf generic helpers, platform devices, syscon/regmap, and the Aspeed table definitions. It is used by generation-specific Aspeed drivers such as the AST2600 driver. It integrates with device tree through the SoC pinctrl descriptors, with GPIO through `.gpio_request_enable`, and with debugfs through `.pin_dbg_show` and debug logging.

## Risks
Mux correctness depends on priority list ordering supplied by SoC data. If a GPIO expression does not follow the expected `GPI*` name and signal/function equality convention, `aspeed_gpio_request_enable()` can reject or misidentify it. The GPIO path assumes that if GPIO is not the lowest priority signal type there is only one expression to enable. The pinconf map lookup accepts wildcard `arg == -1`, so ordering in `confmaps` matters for ambiguous parameters. `aspeed_pin_config_group_set()` applies pins one at a time without rollback. Diagnostic string construction uses `krealloc()` and can fail, turning a reporting path into `NULL` strings but still returns the mux error.

## Test signals
Compile tests should cover all Aspeed SoC drivers that include these helpers. Runtime tests should verify pinmux requests where the target function is high priority, lower priority, and absent. GPIO tests should include normal `GPIO*`, input-only `GPI*`, and pass-through GPIO-like names. Pinconf tests should exercise pull-up, pull-down, bias disable, drive strength, and group operations, including unsupported parameters and invalid arguments. Debugfs pinctrl listings and dynamic debug messages provide useful observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed.h

## Purpose
This header defines the common Aspeed pinctrl data model shared between SoC-specific pin table files and the common implementation. It bridges Linux pinctrl descriptors, Aspeed pinmux expressions, SCU regmap access, and generic pinconf support.

## Important APIs, types, and functions
`struct aspeed_pin_config` describes one pinconf-capable hardware bitfield for a parameter, pin range, register, and mask. `struct aspeed_pin_config_map` maps generic pinconf parameter/argument pairs to hardware values and masks. `struct aspeed_pinctrl_data` is the central per-SoC data carrier: SCU regmap, pin descriptors, pin config entries, pinmux data, and config maps. Macros `ASPEED_PINCTRL_PIN`, `ASPEED_SB_PINCONF`, `ASPEED_PULL_DOWN_PINCONF`, and `ASPEED_PULL_UP_PINCONF` reduce boilerplate in SoC files. The header prototypes all common Aspeed group, function, mux, GPIO, probe, and pinconf operations.

## Control flow
SoC files include this header to construct static `aspeed_pinctrl_data` instances and pin descriptor arrays. During probe, those instances are passed to `aspeed_pinctrl_probe()`. After registration, Linux pinctrl callback tables in the SoC file call the functions declared here, which read back the same data structures through `pinctrl_dev_get_drvdata()`.

## State and persistence behavior
The header itself stores no state. It defines how state is represented: hardware state is reached through `struct regmap *scu`, static SoC capabilities are represented by const arrays, and mux state is represented by `struct aspeed_pinmux_data`. Pinconf map entries are immutable lookup tables. The macros create static data whose lifetime is the kernel image lifetime.

## Dependencies and integration points
The header depends on Linux `pinctrl`, `pinmux`, `pinconf`, generic pinconf, `regmap`, and the Aspeed pinmux header. It is included by common Aspeed implementation files and SoC-specific drivers. Its function prototypes are the integration contract used when constructing `struct pinctrl_ops`, `struct pinmux_ops`, and `struct pinconf_ops`.

## Risks
Macro-generated `drv_data` points at `PIN_SYM(name_)`, so every pin descriptor must have a matching pin declaration symbol. Pin range entries in `aspeed_pin_config` are inclusive and rely on numeric pin ordering matching hardware banks. Config map wildcard entries can make lookup order significant. Because this header exposes internal helper prototypes rather than an opaque interface, SoC files can accidentally couple to assumptions in the common implementation.

## Test signals
Build coverage is the main signal: missing pin symbols, bad macro use, type mismatches, or duplicate declarations should fail compilation. Runtime tests come through SoC drivers using these helpers and should verify that pin descriptor `drv_data` resolves to the expected `aspeed_pin_desc` and that pinconf ranges map to the intended pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinctrl-aspeed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinmux-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinmux-aspeed.c

## Purpose
This file implements reusable Aspeed pinmux expression evaluation. It lets common or SoC-specific mux code ask whether a signal descriptor or full signal expression is currently enabled or disabled in hardware.

## Important APIs, types, and functions
`aspeed_sig_desc_eval()` reads a descriptor bitfield from the selected IP regmap and compares it against either the descriptor's enable or disable value. `aspeed_sig_expr_eval()` evaluates all descriptors in an expression, unless the SoC provides a custom `ctx->ops->eval`. `aspeed_sig_desc_print_val()` is a debug helper showing desired and actual register state. `aspeed_pinmux_ips` maps IP indices to debug names for SCU, GFX, and LPC.

## Control flow
Expression evaluation starts in callers such as `aspeed_sig_expr_enable()`, `aspeed_sig_expr_disable()`, or SoC-specific post-write verification. If a custom eval op exists, `aspeed_sig_expr_eval()` delegates to it. Otherwise it loops through every descriptor in the expression and calls `aspeed_sig_desc_eval()` against `ctx->maps[desc->ip]`. The expression returns true only if every descriptor matches the requested enabled or disabled state. A zero result stops evaluation early as false; a negative result propagates regmap or missing-map errors.

## State and persistence behavior
This file does not mutate hardware and has no persistent state. It reads regmap-backed hardware registers and interprets their current values. Debug messages expose register values but do not affect state.

## Dependencies and integration points
It depends on `pinmux-aspeed.h`, Linux regmap, bit operations such as `__ffs()`, and kernel debug logging. It is called by `pinctrl-aspeed.c` for enable/disable decisions and by AST2600 code to verify writes. It supports multiple register-map domains through `ASPEED_IP_SCU`, `ASPEED_IP_GFX`, and `ASPEED_IP_LPC`.

## Risks
The code assumes descriptor masks are nonzero because it calls `__ffs(desc->mask)`. Missing regmaps return `-ENODEV`, which can break muxing for descriptors targeting IP domains not installed by a SoC driver. Multi-bit descriptor semantics require explicit enable and disable values; a field value that is neither returns false for both states and can leave callers needing additional handling. Debug indexing assumes `desc->ip` is in range of `aspeed_pinmux_ips`.

## Test signals
Unit-style tests can exercise descriptor comparison on fake regmaps for single-bit, multi-bit, enabled, disabled, and neither-state values. Runtime validation comes from successful muxing paths and from dynamic debug traces showing expected register fields. Negative tests should cover missing maps and invalid or protected register access failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinmux-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinmux-aspeed.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinmux-aspeed.h

## Purpose
This header defines the Aspeed data-driven pinmux model and the macro system used by SoC files to describe complex pin priority, signal, group, and function relationships. It captures why Aspeed muxing cannot be represented as a simple one-bit-per-function model.

## Important APIs, types, and functions
Core types are `struct aspeed_sig_desc`, `struct aspeed_sig_expr`, `struct aspeed_pin_desc`, `struct aspeed_pin_group`, `struct aspeed_pin_function`, `struct aspeed_pinmux_ops`, and `struct aspeed_pinmux_data`. IP IDs `ASPEED_IP_SCU`, `ASPEED_IP_GFX`, and `ASPEED_IP_LPC` index the regmap array. Descriptor macros include `SIG_DESC_IP_BIT`, `SIG_DESC_BIT`, `SIG_DESC_SET`, `SIG_DESC_CLEAR`, and list/expression declaration macros. Pin macros such as `PIN_DECL_1`, `PIN_DECL_2`, `PIN_DECL_3`, `PIN_DECL_4`, `SSSF_PIN_DECL`, and `GPIO_PIN_DECL` build priority arrays. Group/function macros build arrays consumed by pinctrl callbacks. `aspeed_sig_expr_set()` is an inline wrapper around the SoC `set` operation.

## Control flow
SoC files use the macros to create descriptor arrays, expression objects, expression pointer lists, per-pin priority arrays, group pin arrays, and function group lists. At runtime, common mux code walks `aspeed_pin_desc.prios` from highest to lowest priority, evaluates or disables expression lists, and then calls the SoC `set` op for the target expression. The model supports AND across descriptors in one expression, OR across expressions in one signal priority, and priority ordering across signals on the same pin.

## State and persistence behavior
The header creates static const data in including C files. Runtime mutable state is limited to `struct aspeed_pinmux_data`, especially installed regmaps and optional ops. Hardware state lives outside the header in the selected IP registers. Descriptors store enable and disable patterns, not current state.

## Dependencies and integration points
The header depends on Linux regmap and bit macros and is included by both shared Aspeed implementation files and SoC-specific pin table files. It integrates with the Linux pinctrl core indirectly through `pinctrl-aspeed.h`, whose data structures include `struct aspeed_pinmux_data`. It also encodes compile-time validation strategy through generated symbol names and aliases.

## Risks
The macro layer is dense and easy to misuse. Naming errors can either intentionally fail compilation through duplicate symbols or accidentally create wrong but valid function/group relationships. The model relies on correct priority order and complete higher-priority disable lists to make lower-priority signals and GPIO work. `SIG_DESC_CLEAR` sets both enable and disable to zero for clear-selected descriptors, which is appropriate only for hardware fields where zero is both selected state and safe disabled comparison. The header documents many hardware corner cases, so changes that simplify it risk breaking valid mux cases.

## Test signals
Compile-time coverage is important because symbol aliases and designated initializers catch many table mistakes. Runtime tests should target representative corner cases from the header comments: shared bits, multiple descriptors, multiple expressions for one signal, strap-influenced signals, non-GPIO "other" functions, and GPIO as non-default or input-only signals. Debug traces from `pinmux-aspeed.c` can confirm descriptor interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/pinmux-aspeed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/Kconfig

## Purpose
This Kconfig file declares Broadcom pinctrl driver configuration symbols and their build-time dependencies. It controls which Broadcom pinctrl, pinmux, pinconf, GPIO-integrated, and STB-related drivers are available for a kernel build.

## Important APIs, types, and functions
The file defines symbols including `PINCTRL_BCM281XX`, `PINCTRL_BCM2835`, `PINCTRL_BCM4908`, the shared `PINCTRL_BCM63XX`, several BCM63xx variants, `PINCTRL_BRCMSTB`, `PINCTRL_IPROC_GPIO`, `PINCTRL_CYGNUS_MUX`, `PINCTRL_NS`, `PINCTRL_NSP_GPIO`, `PINCTRL_NS2_MUX`, and `PINCTRL_NSP_MUX`. It selects framework symbols such as `PINMUX`, `PINCONF`, `GENERIC_PINCONF`, `REGMAP_MMIO`, `GPIOLIB`, `GPIOLIB_IRQCHIP`, `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `REGMAP`, and `GPIO_REGMAP`. It also sources `drivers/pinctrl/bcm/Kconfig.stb`.

## Control flow
Kconfig evaluation exposes prompts when architecture or `COMPILE_TEST` dependencies are met. Selected symbols cause corresponding object rules in the BCM Makefile to compile drivers. Default expressions enable drivers automatically for matching Broadcom architectures. The shared `PINCTRL_BCM63XX` symbol is selected by the individual BCM63xx SoC entries rather than prompted directly.

## State and persistence behavior
The file contributes persistent build configuration state through the kernel `.config`. It has no runtime state. Choices here determine which driver code is built in or available as a module and which framework dependencies are force-enabled.

## Dependencies and integration points
It integrates with the top-level pinctrl Kconfig tree, architecture symbols such as `ARCH_BCM_MOBILE`, `ARCH_BCM2835`, `ARCH_BRCMSTB`, `ARCH_BCMBCA`, `BMIPS_GENERIC`, `ARCH_BCM_IPROC`, `ARCH_BCM_CYGNUS`, `ARCH_BCM_5301X`, and `ARCH_BCM_NSP`, and the local Makefile. The help text documents driver scope and GPIO separation or integration.

## Risks
Incorrect dependencies can hide a driver for valid platforms or expose it where required infrastructure is missing. Incorrect `select` usage can force framework code without all needed prerequisites. Defaults that are too broad increase kernel footprint, while defaults that are too narrow break expected platform support. The STB source line means local Kconfig validity also depends on `Kconfig.stb`.

## Test signals
Run Kconfig configuration tests for the supported Broadcom architectures and for `COMPILE_TEST`. Confirm `make olddefconfig`, `make allnoconfig`, and relevant defconfigs select expected symbols. Build tests should verify every enabled symbol maps to an object rule and has all framework dependencies available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/Makefile

## Purpose
This Makefile maps Broadcom pinctrl Kconfig symbols to the object files compiled into the kernel or modules. It is the build glue for the Broadcom pinctrl subdirectory.

## Important APIs, types, and functions
The file uses standard kernel `obj-$(CONFIG_...) += ...` assignments. Notable mappings include `CONFIG_PINCTRL_BCM281XX` to `pinctrl-bcm281xx.o`, `CONFIG_PINCTRL_BCM2835` to `pinctrl-bcm2835.o`, `CONFIG_PINCTRL_BCM4908` to `pinctrl-bcm4908.o`, shared and SoC-specific BCM63xx objects, `CONFIG_PINCTRL_BRCMSTB` to `pinctrl-brcmstb.o`, `CONFIG_PINCTRL_BCM2712` to `pinctrl-brcmstb-bcm2712.o`, and iProc, Cygnus, NS, NSP, and NS2 drivers.

## Control flow
During kernel build, Kbuild expands each `obj-y`, `obj-m`, or empty assignment based on the resolved `.config`. Enabled built-in symbols compile into the built-in object list; module symbols compile as modules when the symbol is tristate and set to `m`.

## State and persistence behavior
The Makefile stores no runtime state. Its effect is persistent only in build outputs and depends entirely on `.config`.

## Dependencies and integration points
It integrates with the local Kconfig symbols and the Linux Kbuild system. It assumes each referenced object has a matching source file in the same directory and that symbol type matches whether modular builds are possible.

## Risks
A missing or misspelled object mapping causes an enabled driver not to build. A stale mapping to a removed source breaks builds. Referencing `CONFIG_PINCTRL_BCM2712` here while its Kconfig may be sourced elsewhere requires the broader Kconfig tree to define it consistently. Ordering is mostly not semantically significant, but shared objects such as `pinctrl-bcm63xx.o` must be selected when dependent variants need common code.

## Test signals
Build tests with representative configs should confirm each Kconfig symbol produces the intended object. `make W=1` or allmodconfig-style builds can catch stale object references. Comparing this file against local Kconfig symbols is a useful static consistency check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm281xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm281xx.c

## Purpose
This file implements the Broadcom BCM281xx family pinctrl driver, with support for BCM11351-style BCM281xx devices and BCM21664 devices. It exposes each pin as a one-pin group, supports generic alternate mux functions, and implements pin configuration for standard, I2C, and HDMI pin register layouts.

## Important APIs, types, and functions
Register field definitions describe common function select bits and type-specific config bits for standard, I2C, and HDMI pin registers. `enum bcm281xx_pin_type` classifies pins as standard, I2C, HDMI, or unknown. `struct bcm281xx_pin_function` represents alternate functions. `enum bcm281xx_pinctrl_type`, `struct bcm281xx_pinctrl_info`, and `struct bcm281xx_pinctrl_data` distinguish device variants and runtime data. Large pin descriptor arrays define BCM281xx and BCM21664 pin names, numbers, and pin types. Function arrays define `alt1` through `alt4` for BCM281xx and `alt1` through `alt6` for BCM21664. Lock helpers `bcm21664_pinctrl_lock_all()` and `bcm21664_pinctrl_set_pin_lock()` handle BCM21664 write protection. Pinmux uses `bcm281xx_pinmux_set()`. Pinconf uses `bcm281xx_std_pin_update()`, `bcm281xx_i2c_pin_update()`, `bcm21664_i2c_pin_update()`, `bcm281xx_hdmi_pin_update()`, and `bcm281xx_pinctrl_pin_config_set()`.

## Control flow
`builtin_platform_driver_probe()` registers a built-in platform driver. Probe gets match data for the compatible string, maps the MMIO resource, creates a regmap, initializes the global pinctrl descriptor with variant-specific pins, and locks all BCM21664 pins by default. The pinctrl core sees one group per pin through `get_groups_count`, `get_group_name`, and `get_group_pins`. For muxing, `bcm281xx_pinmux_set()` optionally unlocks a BCM21664 pin, writes the function number into bits 10:8 of that pin's register, then relocks the pin. For pinconf, `bcm281xx_pinctrl_pin_config_set()` selects a type-specific updater, builds one value/mask pair for all requested configs, optionally unlocks the pin, writes the mask with `regmap_update_bits()`, and relocks. `pin_config_get` is intentionally unsupported.

## State and persistence behavior
Runtime state is in the static `bcm281xx_pinctrl_pdata` and variant info tables, plus the MMIO-backed regmap. Hardware mux and config state persists in per-pin PADCTRL registers until reset or later writes. BCM21664 adds access-lock register state: probe locks all lock banks, and each mux or pinconf write temporarily unlocks the target pin and relocks it. There is no rollback if relocking fails after a successful register update.

## Dependencies and integration points
The driver depends on Linux platform devices, OF match data, MMIO resource mapping, regmap-mmio, pinctrl, pinmux, pinconf generic parsing, and pinctrl utility DT map cleanup. It is selected by `PINCTRL_BCM281XX`, built by the BCM Makefile, and matches `brcm,bcm11351-pinctrl` and `brcm,bcm21664-pinctrl`. GPIO is explicitly provided by a separate driver; this driver only handles mux and electrical configuration.

## Risks
The group model says every pin supports every alternate function, so invalid hardware combinations may not be rejected by pinctrl and must be avoided by correct device tree data. Pin indices must match the PADCTRL register order exactly because offsets are computed as `4 * pin`. The global `bcm281xx_pinctrl_desc` and `bcm281xx_pinctrl_pdata` assume a single instance. `pin_config_get()` returns `-ENOTSUPP`, limiting readback tests and diagnostics. BCM21664 lock handling can leave a pin unlocked if relocking fails after a write path returns early. Type-specific config validation differs between BCM281xx I2C and BCM21664 I2C, so incorrect pin type tagging changes accepted properties.

## Test signals
Build tests should enable `PINCTRL_BCM281XX` for `ARCH_BCM_MOBILE` and `COMPILE_TEST`. Device tree validation should ensure pin names in groups match the arrays and compatible strings select the right variant. Runtime tests should verify mux writes for each alt function count, standard pin configs for bias, hysteresis, slew, input enable, and drive strength, I2C pull-up resistance validation, HDMI mode/input controls, and BCM21664 lock/unlock behavior. Negative tests should cover invalid drive strengths, unsupported I2C pull-up values, unsupported config parameters, unknown pin indices, and missing MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-bcm281xx.c -->
