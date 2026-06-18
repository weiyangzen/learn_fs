# subset-b-005119 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra210.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra210.c

## Purpose

This file is the Tegra210 SoC-specific pin controller description. It contains no board policy and almost no custom runtime logic; it maps Tegra210 package pins, GPIO-numbered pads, always-on/system pads, mux functions, pad groups, drive groups, register offsets, and bit positions into `struct tegra_pinctrl_soc_data`. The shared Tegra pinctrl core consumes this data to implement pin muxing, GPIO integration, pull-up/down, tristate, input enable, open-drain, lock, receive-select/high-voltage, high-speed mode, Schmitt, drive type, low-power drive, drive strength, and slew-rate controls.

## Important APIs, Types, and Data

The file defines `_GPIO()`, `_PIN()`, `NUM_GPIOS`, Tegra210 pin IDs, `tegra210_pins[]`, one-pin arrays such as `uart1_tx_pu0_pins[]`, drive grouping arrays such as `drive_sdmmc1_pins[]`, `enum tegra_mux`, `tegra210_functions[]`, `PINGROUP`, `DRV_PINGROUP`, `tegra210_groups[]`, and `tegra210_pinctrl`. `tegra210_pins[]` has 162 `PINCTRL_PIN()` entries. `tegra210_groups[]` has 187 entries, combining normal pin groups and dedicated drive-only groups. `tegra210_pinctrl_probe()` calls the common `tegra_pinctrl_probe()`, and the platform driver binds to `nvidia,tegra210-pinmux` with `pm_sleep_ptr(&tegra_pinctrl_pm)`.

## Control Flow

At `arch_initcall`, `tegra210_pinctrl_init()` registers `tegra210_pinctrl_driver`. Device Tree matching invokes `tegra210_pinctrl_probe()`, which passes the static `tegra210_pinctrl` table to the common Tegra pinctrl driver. Subsequent runtime pinctrl operations are handled by the common core by indexing the `pins`, `functions`, and `groups` arrays and by writing the bank/register/bit fields expanded by the group macros.

## State and Persistence

All state in this file is static, const SoC description data. Persistent effects are hardware register writes performed later by the common core, not by this file directly. The SoC data advertises `ngpios = NUM_GPIOS` and `gpio_compatible = "nvidia,tegra210-gpio"`, allowing the common pinctrl layer to coordinate pin ownership with the Tegra GPIO controller.

## Dependencies and Integration Points

It depends on the shared Tegra pinctrl structures and helpers declared in the local Tegra pinctrl headers and implemented by the common Tegra pinctrl driver. It integrates with platform-driver matching, OF compatible strings, Linux pinctrl/pinmux/pinconf consumers, GPIO ranges, and system sleep through `tegra_pinctrl_pm`. Board Device Trees select groups/functions by names generated from the static arrays.

## Risks

The main risk is table correctness. A wrong pin number, group name, function ordinal, register offset, bank, or bit field can silently program the wrong pad, break GPIO muxing, or damage electrical behavior through bad drive-strength or high-voltage settings. Several groups use `-1` for unsupported fields; the common driver must honor those sentinels. Function enum order must stay aligned with `tegra210_functions[]`, because group entries store enum constants rather than strings.

## Test Signals

Useful checks are build coverage for `CONFIG_PINCTRL_TEGRA210`, boot probing on a Tegra210 board with `nvidia,tegra210-pinmux`, pinctrl debugfs inspection of pin/group/function names, DT pin state application for SDMMC/I2C/UART/SPI/PCIe/display pins, suspend/resume checks for saved pin state, and GPIO handoff tests against `nvidia,tegra210-gpio`. Table changes should be reviewed against the Tegra210 TRM and binding examples rather than relying only on compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra234.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra234.c

## Purpose

This file describes Tegra234 pinmux hardware for the common Tegra pinctrl core. Unlike older single-instance Tegra tables, it provides separate SoC data for the main pinmux block and the always-on pinmux block. It maps Tegra234 pins, mux functions, normal groups, AON groups, register offsets, and supported electrical-control bits into `struct tegra_pinctrl_soc_data` records.

## Important APIs, Types, and Data

The file starts with pin-number enums for the main and AON domains, then defines `tegra234_pins[]`, many one-pin arrays, `enum tegra_mux_dt`, `tegra234_functions[]`, macro helpers for optional pin and drive register entries, `tegra234_groups[]`, `tegra234_pinctrl`, `tegra234_aon_pins[]`, `tegra234_aon_groups[]`, and `tegra234_pinctrl_aon`. The source contains 199 `PINCTRL_PIN()` entries across both domains and 199 `PINGROUP()` table entries. `DRV_PINGROUP_ENTRY_Y()` and `DRV_PINGROUP_ENTRY_N()` model whether a pad has drive controls; `PIN_PINGROUP_ENTRY_Y()` and `PIN_PINGROUP_ENTRY_N()` model whether normal mux/pull/tristate/input-related fields exist.

## Control Flow

`tegra234_pinctrl_init()` registers a platform driver at `arch_initcall`. `tegra234_pinctrl_probe()` reads match data with `device_get_match_data(&pdev->dev)` and passes either `tegra234_pinctrl` or `tegra234_pinctrl_aon` to `tegra_pinctrl_probe()`. The OF table distinguishes `nvidia,tegra234-pinmux` from `nvidia,tegra234-pinmux-aon`; both use the same platform driver and common Tegra pinctrl implementation after match selection.

## State and Persistence

The file provides static SoC metadata only. Hardware state is persistent in MMIO pinmux registers written by the shared Tegra core in response to pinctrl consumers. The main and AON data sets intentionally do not set `ngpios` or `gpio_compatible` in this file, so GPIO coupling differs from Tegra30/Tegra210 and is expected to be handled by the broader Tegra234 GPIO/pinctrl integration.

## Dependencies and Integration Points

It depends on the common Tegra pinctrl data model, platform driver core, OF match data, and Linux pinctrl consumers. The table exposes `schmitt_in_mux`, `drvtype_in_mux`, and `sfsel_in_mux`, while leaving `hsm_in_mux` false. It integrates with Device Tree through names such as `nvidia,tegra234-pinmux`, `nvidia,tegra234-pinmux-aon`, group names, and function strings including PCIe, EQOS, QSPI, SDMMC1, UFS, CAN, UART, I2C, SPI, audio, display, and AON control signals.

## Risks

This is register-description-heavy code. The main risks are mismatched main/AON domains, incorrect match data, wrong register bank or offset, and optional-field sentinels that do not match hardware reality. Some groups intentionally have no drive entry, for example EQOS/QSPI compatibility groups with `DRV_PINGROUP_ENTRY_N`; enabling unsupported drive fields would cause common-core writes to invalid registers. Function enum/string order must remain synchronized. Because the AON block has separate pins but shares `tegra234_functions[]`, name collisions and incomplete group coverage are review targets.

## Test Signals

Compile with Tegra234 pinctrl enabled and verify `MODULE_DEVICE_TABLE(of, ...)` exposes both compatibles. On hardware or emulation, confirm both main and AON platform devices probe, pinctrl debugfs shows expected main/AON groups, and DT states for SDMMC1, QSPI, EQOS, PCIe reset/clkreq, UFS, CAN, UART, and I2C apply without invalid register accesses. Regression tests should include suspend/resume-sensitive AON pads and a check that groups with no drive entry reject or ignore drive settings through the common core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra234.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra30.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra30.c

## Purpose

This file is the Tegra30 SoC-specific pinctrl table. It enumerates GPIO-backed pins and non-GPIO system pins, declares pin groups, function names, mux options, drive groups, and register bit layouts for the common Tegra pinctrl core. It supports the older Tegra30 register model where mux/pull/tristate/input/open-drain/ioreset fields live in pinmux bank registers and drive controls live in a separate drive bank.

## Important APIs, Types, and Data

The file defines `_GPIO()`, `_PIN()`, `NUM_GPIOS`, Tegra30 pin IDs, `tegra30_pins[]`, one-pin arrays for each group, large drive grouping arrays such as `drive_lcd2_pins[]`, `enum tegra_mux`, `tegra30_functions[]`, `PINGROUP`, `DRV_PINGROUP`, `tegra30_groups[]`, and `tegra30_pinctrl`. The source contains 260 `PINCTRL_PIN()` entries and 290 `PINGROUP()`/`DRV_PINGROUP()` entries. `PINGROUP()` captures mux functions, register offset, open-drain support, and IO reset support. `DRV_PINGROUP()` captures high-speed mode, Schmitt, low-power mode, drive-down/up fields, and slew-rate fields for drive groups.

## Control Flow

The driver is registered from `tegra30_pinctrl_init()` at `arch_initcall`. Platform matching on `nvidia,tegra30-pinmux` calls `tegra30_pinctrl_probe()`, which passes `tegra30_pinctrl` into `tegra_pinctrl_probe()`. After that, the common Tegra pinctrl code performs all pinctrl operations by resolving pin/group/function names into these tables and writing the described MMIO fields.

## State and Persistence

The file has no mutable runtime state other than static registration of a platform driver. Pin configuration state persists in Tegra30 pinmux/drive registers through the common core. `tegra30_pinctrl` sets `ngpios = NUM_GPIOS` and `gpio_compatible = "nvidia,tegra30-gpio"`, so the common core can expose or coordinate GPIO-capable pads with the Tegra30 GPIO controller.

## Dependencies and Integration Points

It integrates with the common Tegra pinctrl driver, platform bus, Device Tree, Linux pinctrl/pinmux/pinconf APIs, and the Tegra30 GPIO driver. Its group and function names are the ABI consumed by DTS pinctrl states for peripherals such as display, GMI/NAND, SDMMC, UART, I2C, SPI, ULPI, HDMI/CEC, PCIe, audio, keyboard controller, and camera/VI. The SoC flags set `hsm_in_mux = false`, `schmitt_in_mux = false`, and `drvtype_in_mux = false`, meaning those electrical controls are not represented as mux-register fields.

## Risks

The file is highly table-driven and sensitive to numeric accuracy. Incorrect register offsets or bit positions can cause wrong pads to be muxed or electrically misconfigured. Drive group membership is especially risky because a single drive group spans multiple pins; wrong membership affects a whole peripheral bus. `TEGRA_MUX_INVALID` and reserved function entries must stay in the correct function order. Unsupported fields use `-1`; the common core must avoid writes for those fields. Because this is older hardware, regressions may only be visible on real Tegra30 boards.

## Test Signals

Build with Tegra30 pinctrl enabled and boot a DT using `nvidia,tegra30-pinmux`. Verify debugfs pin/group/function inventories, GPIO range behavior against `nvidia,tegra30-gpio`, and live pinctrl state application for SDMMC, UART, I2C, SPI, display, and ULPI. Electrical tests should exercise open-drain I2C groups, IO reset capable VI/SDMMC4 groups, and drive-strength/slew-rate programming on representative drive groups. Review table edits against the Tegra30 TRM and board schematics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/ti/Kconfig

## Purpose

This Kconfig fragment declares `PINCTRL_TI_IODELAY`, the build-time option for the Texas Instruments IO delay pin configuration driver. It makes the DRA7 IO delay module available as a tristate driver and constrains normal builds to OF-enabled DRA7 SoCs while allowing compile-test coverage.

## Important APIs, Types, and Functions

The key symbol is `config PINCTRL_TI_IODELAY`. It is `tristate "TI IODelay Module pinconf driver"`, depends on `OF && (SOC_DRA7XX || COMPILE_TEST)`, and selects `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCONF`, and `REGMAP_MMIO`. There are no functions or runtime data structures in this file; its API is the Kconfig symbol consumed by the Makefile and kernel configuration system.

## Control Flow

During Kconfig evaluation, the symbol appears only when dependencies are satisfied. If selected as built-in or module, the Makefile compiles `pinctrl-ti-iodelay.o`. The selected generic pinctrl and regmap features ensure that the C driver can use generic group helpers, generic pinconf handling, and MMIO regmap access without requiring the user to manually enable them.

## State and Persistence

The only persistent state is the generated kernel configuration value in `.config` and derived build artifacts. It does not persist hardware state.

## Dependencies and Integration Points

The file integrates the TI IO delay driver with Kconfig, architecture/SoC selection, Device Tree support, generic pinctrl infrastructure, and MMIO regmap support. It is paired directly with `drivers/pinctrl/ti/Makefile`.

## Risks

Dependency mistakes can hide the driver from valid DRA7 builds or enable it in unsupported environments. Missing `select` statements would turn into compile or link errors in `pinctrl-ti-iodelay.c`. Over-broad dependencies can increase build coverage but may expose assumptions about OF-only probing.

## Test Signals

Check `make olddefconfig` visibility for DRA7 and compile-test configurations. Build `PINCTRL_TI_IODELAY=y` and `m`, verify the object is included, and confirm `n` excludes it. A compile-test build is useful because the option is explicitly designed to support `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/ti/Makefile

## Purpose

This Makefile connects the `PINCTRL_TI_IODELAY` Kconfig symbol to the TI IO delay driver object. It is the build-system glue for the `drivers/pinctrl/ti` subdirectory.

## Important APIs, Types, and Functions

The only build rule is `obj-$(CONFIG_PINCTRL_TI_IODELAY) += pinctrl-ti-iodelay.o`. There are no C APIs, types, or functions in this file. The rule means built-in configuration produces a built-in object, module configuration produces a module object, and disabled configuration omits the driver.

## Control Flow

Kbuild expands `obj-y` or `obj-m` according to `CONFIG_PINCTRL_TI_IODELAY`. The compiled source is `pinctrl-ti-iodelay.c`, producing `pinctrl-ti-iodelay.o` and, for module builds, the corresponding loadable module.

## State and Persistence

Persistent effects are build artifacts under the kernel output tree. There is no runtime state.

## Dependencies and Integration Points

The rule depends on `drivers/pinctrl/ti/Kconfig` defining `PINCTRL_TI_IODELAY` and on the C source file having the expected basename. It integrates with top-level Kbuild traversal into the TI pinctrl directory.

## Risks

The risk surface is small: a symbol typo would prevent the driver from building, and an object-name typo would fail the build or silently omit the intended source. Because there is only one rule, any future TI pinctrl driver added to this directory must update both Kconfig and this Makefile.

## Test Signals

Build with `CONFIG_PINCTRL_TI_IODELAY=y` and verify `pinctrl-ti-iodelay.o` is linked into vmlinux. Build with `CONFIG_PINCTRL_TI_IODELAY=m` and verify a module is produced. Build with the symbol unset and verify no TI IO delay object is compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/ti/pinctrl-ti-iodelay.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/ti/pinctrl-ti-iodelay.c

## Purpose

This driver programs the Texas Instruments DRA7 IO Delay module through the Linux pinctrl pinconf path. It parses `pinctrl-pin-array` Device Tree entries containing register offsets plus agnostic and gnostic delay values, computes hardware coarse/fine delay fields from bootloader calibration registers, writes per-pin IO delay registers through regmap, and exposes debugfs details when enabled.

## Important APIs, Types, and Functions

Key data types are `struct ti_iodelay_reg_data` for SoC register layout and masks, `struct ti_iodelay_reg_values` for computed calibration values, `struct ti_iodelay_cfg` for one DT-provided pin delay tuple, `struct ti_iodelay_pingroup` for a generic pinctrl group plus its configurations, and `struct ti_iodelay_device` for device-local state. Important functions are `ti_iodelay_extract()`, `ti_iodelay_compute_dpe()`, `ti_iodelay_pinconf_init_dev()`, `ti_iodelay_pinconf_set()`, `ti_iodelay_dt_node_to_map()`, `ti_iodelay_node_iterator()`, `ti_iodelay_pinconf_group_set()`, `ti_iodelay_alloc_pins()`, and `ti_iodelay_probe()`. `dra7_iodelay_data` and `dra7_iodelay_regmap_config` provide the sole supported compatible, `ti,dra7-iodelay`.

## Control Flow

`module_platform_driver()` registers the platform driver. Probe requires an OF node, gets match data, maps the MMIO resource, initializes a regmap, unlocks the global IO delay block, registers a devm cleanup action that relocks it, reads reference/coarse/fine calibration registers, computes `cdpe` and `fdpe`, allocates synthetic pin descriptors from register-space geometry, registers the pinctrl device, and enables it.

When a consumer applies a pinctrl state, `ti_iodelay_dt_node_to_map()` counts rows in `pinctrl-pin-array`, allocates pins/config arrays, parses each row with `pinctrl_parse_index_with_args()`, converts the offset to a synthetic pin number, stores delay data in both the group and pin descriptor `drv_data`, registers a generic group, and returns one `PIN_MAP_TYPE_CONFIGS_GROUP` map. `ti_iodelay_pinconf_group_set()` accepts only one dummy config, `PIN_CONFIG_END`, and applies every `ti_iodelay_cfg` in the group through `ti_iodelay_pinconf_set()`.

## State and Persistence

Driver state is devm-managed and tied to the platform device lifetime: mapped base, regmap, pinctrl descriptor, pin descriptors, calibration values, and dynamically allocated groups/config arrays. Hardware state persists in IO delay registers after `regmap_update_bits()` writes. The driver deliberately leaves per-pin IO delay values unlocked to allow later mode changes such as MMC transitions, while the global block is relocked on device teardown through the devm cleanup action.

## Dependencies and Integration Points

It depends on OF, platform devices, `devm_platform_get_and_ioremap_resource()`, regmap MMIO, generic pinctrl groups, generic pinconf maps, and pinctrl devicetree helpers. It integrates with DRA7 Device Tree bindings using `pinctrl-pin-array`, with bootloader calibration because it reads recalibration values already programmed before Linux, and with debugfs via optional pin/group display callbacks.

## Risks

The delay math uses truncating integer division and assumes nonzero calibrated delay counts. Incorrect DT offsets can map to wrong synthetic pins, and `ti_iodelay_offset_to_pin()` checks only upper range, not that the offset is at or beyond `reg_start_offset` or aligned to a per-pin stride. `ti_iodelay_alloc_pins()` increments `phy_reg` but does not store names or physical addresses in descriptors, making debug names generic. `ti_iodelay_pinconf_group_set()` returns `-ENOTSUPP` for any per-pin write failure, losing the original regmap error. Leaving values unlocked is intentional but increases exposure to accidental padconf changes.

## Test Signals

Build under `PINCTRL_TI_IODELAY=y/m` and probe a `ti,dra7-iodelay` node with a valid MMIO resource. Runtime validation should cover valid and invalid `pinctrl-pin-array` rows, too few cells, out-of-range offsets, zero coarse/fine calibration counts, and representative MMC mode-change pinctrl states. Debugfs should show offsets, configured delays, and register values. Hardware tests should compare resulting coarse/fine fields against TRM calculations and confirm the global lock is restored on driver removal or probe-error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/ti/pinctrl-ti-iodelay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/Kconfig

## Purpose

This Kconfig fragment defines the UniPhier pinctrl driver family. It exposes a menu-level `PINCTRL_UNIPHIER` switch and individual boolean options for supported UniPhier SoCs, allowing architecture defaults to select the appropriate SoC-specific pinctrl table drivers.

## Important APIs, Types, and Functions

The menu symbol is `PINCTRL_UNIPHIER`, a bool depending on `ARCH_UNIPHIER || COMPILE_TEST` and `OF && MFD_SYSCON`, defaulting to `ARCH_UNIPHIER`. It selects `PINMUX` and `GENERIC_PINCONF`. Child symbols are `PINCTRL_UNIPHIER_LD4`, `PRO4`, `SLD8`, `PRO5`, `PXS2`, `LD6B`, `LD11`, `LD20`, `PXS3`, and `NX1`. ARM-generation SoCs default to `ARM`; later SoCs default to `ARM64`.

## Control Flow

Kconfig first determines whether the UniPhier menu is available. If enabled, child symbols can be selected and their defaults follow the target architecture. Kbuild then uses these symbols to include the common UniPhier core object and the selected SoC-specific objects from the Makefile.

## State and Persistence

The file persists only kernel configuration choices in `.config`. It does not own runtime state or hardware state.

## Dependencies and Integration Points

The dependency on OF and MFD_SYSCON reflects that UniPhier pinctrl drivers use Device Tree and syscon/regmap-backed SoC registers. `PINMUX` and `GENERIC_PINCONF` are selected for the shared core and SoC drivers. The child symbols integrate directly with `drivers/pinctrl/uniphier/Makefile`.

## Risks

Incorrect defaults can omit a needed SoC driver from common ARM/ARM64 UniPhier defconfigs. Missing `MFD_SYSCON` or generic pinconf dependencies would break builds or probing. Because all child symbols are bools under a bool menu, they are built-in when selected rather than separately modularized; that matches common pinctrl usage but affects footprint.

## Test Signals

Run configuration checks for UniPhier ARM and ARM64 defconfigs and compile-test builds. Verify menu visibility when `ARCH_UNIPHIER` is off but `COMPILE_TEST` is on. Build each child symbol and confirm the expected object file is selected by the Makefile together with `pinctrl-uniphier-core.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/Makefile

## Purpose

This Makefile maps UniPhier pinctrl Kconfig symbols to Kbuild objects. It always builds the shared UniPhier pinctrl core when the directory is included, and conditionally builds one object per supported UniPhier SoC family.

## Important APIs, Types, and Functions

The key unconditional rule is `obj-y += pinctrl-uniphier-core.o`. Conditional rules map `CONFIG_PINCTRL_UNIPHIER_LD4`, `PRO4`, `SLD8`, `PRO5`, `PXS2`, `LD6B`, `LD11`, `LD20`, `PXS3`, and `NX1` to their corresponding `pinctrl-uniphier-*.o` objects. There are no C functions here; the file's interface is the Kbuild object list.

## Control Flow

When Kbuild descends into this directory, it compiles the core object and any SoC object whose Kconfig symbol expands to `y`. Because the Kconfig symbols are bools, this Makefile does not produce modules for UniPhier pinctrl; selected objects become built-in.

## State and Persistence

Persistent state is limited to kernel build artifacts. Runtime pinctrl state is owned by the compiled C drivers and hardware registers, not by this file.

## Dependencies and Integration Points

It depends on `drivers/pinctrl/uniphier/Kconfig` defining the listed symbols and on source files with matching names. It integrates with the top-level pinctrl build and with the shared UniPhier core that SoC-specific objects use for common registration and pinconf behavior.

## Risks

The unconditional `obj-y` core rule assumes directory inclusion is already gated by higher-level Kbuild/Kconfig. If a SoC symbol is added in Kconfig but not here, the option will not compile its driver. If a rule points at the wrong object, the build fails or probes for that SoC disappear. The lack of module rules is intentional but should be considered if future symbols become tristate.

## Test Signals

Build UniPhier configurations selecting each SoC option and confirm the matching object appears in the build log. Verify that the core object is present whenever any UniPhier pinctrl driver is built. Cross-check Kconfig and Makefile symbol lists whenever new UniPhier SoC support is added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/uniphier/Makefile -->
