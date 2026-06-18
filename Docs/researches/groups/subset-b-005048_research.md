# subset-b-005048 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns2-mux.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns2-mux.c

Purpose: Broadcom Northstar2 IOMUX pinctrl driver for group-based muxing plus per-pin generic pinconf for pins with pad configuration registers. It registers the `brcm,ns2-pinmux` platform driver at `arch_initcall`.

Important APIs/types/functions: `struct ns2_pinctrl`, `ns2_pin`, `ns2_pin_group`, `ns2_pin_function`, and `ns2_mux_log` describe controller state, pins, groups, functions, and conflict tracking. `ns2_pinctrl_ops`, `ns2_pinmux_ops`, and `ns2_pinconf_ops` implement Linux pinctrl, pinmux, and generic pinconf callbacks. `ns2_pinmux_set()` performs masked register updates; `ns2_pin_config_get/set()` handle bias, drive strength, slew rate, and input-enable.

Control flow: probe maps three MMIO resources, initializes the mux log, builds pin descriptors with `drv_data`, binds static group/function tables, then registers the pinctrl device. Device-tree maps use `pinconf_generic_dt_node_to_map_pin`. Mux selection validates selectors, rejects conflicting reuse of the same mux field, selects base0/base1, then updates the target offset under a spinlock.

State and persistence: state lives in hardware mux/pad registers plus an in-memory `mux_log` used only for the running instance. Pinconf persists in MMIO until hardware reset; devm allocations are released on device teardown. Pins 0-62 have `base == -1`, so pinconf operations return `-ENOTSUPP`.

Dependencies/integration: depends on platform resources, OF compatible data, Linux pinctrl core, generic pinconf helpers, and `pinctrl-utils`. Integrates with downstream NAND/NOR/PCIe/UART/PWM consumers through DT pin states.

Risks: static table/register-field mistakes can silently mux the wrong shared pins. Conflict tracking prevents divergent runtime selections but does not reconcile bootloader state. `pinctrl_register()` is non-devm while no remove path unregisters, acceptable for arch-init built-in style but worth checking if modularized.

Test signals: boot with `brcm,ns2-pinmux`, inspect pinctrl debugfs group/function listings, apply DT states for each mux group, verify unsupported pinconf on mfio pins, and scope/register-check pad configuration changes for pins 63-118.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-ns2-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-nsp-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-nsp-gpio.c

Purpose: Broadcom Northstar Plus chipCommonA GPIO driver with optional GPIO IRQ support and a local pinctrl device for GPIO-only pinconf settings.

Important APIs/types/functions: `struct nsp_gpio` carries MMIO bases, `gpio_chip`, pinctrl descriptor, and `raw_spinlock_t`. GPIO callbacks include `nsp_gpio_direction_input/output`, `nsp_gpio_get_direction`, `nsp_gpio_get`, and `nsp_gpio_set`. IRQ callbacks are bundled in immutable `nsp_gpio_irq_chip`. Pinconf callbacks support bias, drive strength, and slew through `nsp_pin_config_get/set()`.

Control flow: probe requires `ngpios`, maps GPIO and IO-control resources, initializes the gpiochip, optionally enables the shared parent interrupt and installs `nsp_gpio_irq_handler()`, registers the gpiochip, then registers a one-to-one pinctrl device. The IRQ handler checks chipCommonA status, combines level and edge sources, and dispatches set bits through the gpio IRQ domain.

State and persistence: output enable/data, interrupt masks/polarity/events, pull, slew, and drive strength live in MMIO registers. Driver state is devm-managed and protected by raw spinlocks for GPIO/IRQ paths. Drive strength is encoded across three adjacent IO-control registers.

Dependencies/integration: uses gpiolib, irqdomain/generic IRQ handling, platform OF (`brcm,nsp-gpio-a`), generic pinconf parsing, and pinctrl range helpers. It pairs with the NSP mux driver because pins must be muxed to GPIO before GPIO pinconf is meaningful.

Risks: only one GPIO group is exposed, so group pinconf get/set are stubs. Invalid drive strengths outside even 2-16 mA return `-ENOTSUPP`. Edge interrupt ack only clears event IRQs, while level IRQ behavior relies on input level/polarity and masking. Missing `ngpios` fails probe.

Test signals: exercise libgpiod direction/value paths, configure pull and drive strength from DT, trigger rising/falling/high/low IRQs, verify shared IRQ returns `IRQ_NONE` with no pending bits, and confirm pinctrl debugfs shows the local `gpio_grp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-nsp-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-nsp-mux.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-nsp-mux.c

Purpose: Broadcom Northstar Plus IOMUX pinctrl driver for group-based muxing and GPIO request/free handoff on muxable NSP pins.

Important APIs/types/functions: `struct nsp_pinctrl`, `nsp_pin`, `nsp_pin_group`, `nsp_pin_function`, and `nsp_mux_log` model controller data. `nsp_pinmux_set()` performs conflict-checked masked register writes. `nsp_gpio_request_enable()` and `nsp_gpio_disable_free()` switch individual mux bits for gpiolib users.

Control flow: probe maps three register resources, initializes mux logs from static group descriptors, creates pin descriptors with `gpio_select` in `drv_data`, binds static groups/functions, and registers `nsp-pinmux`. DT states map at group granularity via `pinconf_generic_dt_node_to_map_group`. `set_mux` validates selectors, logs first use of a mux field, rejects incompatible double configuration, and writes base0/base1/base2 under spinlock.

State and persistence: mux state is persisted in hardware registers. `mux_log` is runtime-only and initialized as unconfigured, so bootloader-configured mux state is not considered. GPIO request/free toggles base0 bits using each pin's `gpio_select` value.

Dependencies/integration: integrates with Linux pinctrl and pinmux cores, Broadcom NSP DT compatible `brcm,nsp-pinmux`, and the companion NSP GPIO driver. Functions cover SPI, I2C, MDIO, PWM, GPIO_B, UART, SATA LEDs, SDIO, switch LEDs, NAND, and eMMC.

Risks: shared PWM/GPIO_B fields require DT to request paired groups correctly. Double-configuration detection is per running driver instance and cannot protect against external firmware changes. Base1 mapping uses `devm_ioremap()` from a resource instead of `devm_platform_ioremap_resource()`, so resource validation differs.

Test signals: list functions/groups in debugfs, apply conflicting mux states to confirm `-EINVAL`, request GPIOs through gpiolib and verify base0 changes, and validate NAND/eMMC mutual exclusion on the shared base2 field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-nsp-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/Kconfig

Purpose: Kconfig menu for Marvell Berlin and Synaptics AS370 pinctrl support, active only when `ARCH_BERLIN` or `COMPILE_TEST` is enabled.

Important APIs/types/functions: defines hidden common `PINCTRL_BERLIN`, user/build selectable `PINCTRL_AS370`, `PINCTRL_BERLIN_BG4CT`, and SoC-default `PINCTRL_BERLIN_BG2`, `PINCTRL_BERLIN_BG2CD`, `PINCTRL_BERLIN_BG2Q`.

Control flow: selecting a SoC-specific symbol selects the common `PINCTRL_BERLIN` core. BG2/BG2CD/BG2Q use `def_bool MACH_*`; AS370 and BG4CT are explicit bool prompts. All public SoC entries depend on OF.

State and persistence: no runtime state; it controls compile-time inclusion and dependency closure.

Dependencies/integration: common core selects `PINMUX` and `REGMAP_MMIO`. The Makefile consumes these symbols to build `berlin.o` and the selected SoC table drivers.

Risks: because `PINCTRL_BERLIN` is `bool`, these drivers are built-in under the selected configs. Missing OF dependency would break DT-only probe paths, but all SoC symbols require OF.

Test signals: run Kconfig resolution for ARCH_BERLIN and COMPILE_TEST builds, confirm `berlin.o` is linked when any SoC symbol is enabled, and verify `MACH_BERLIN_*` defaults select expected drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/Makefile

Purpose: Build rules for the Berlin pinctrl core and per-SoC descriptor drivers.

Important APIs/types/functions: unconditional `obj-y += berlin.o` builds the common core whenever the directory is included; conditional objects build BG2, BG2CD, BG2Q, BG4CT, and AS370 drivers from their Kconfig symbols.

Control flow: Kbuild links `berlin.o` before selected SoC files. SoC objects call the common exported probe helpers in `berlin.c`.

State and persistence: compile-time only; no runtime state.

Dependencies/integration: paired with `drivers/pinctrl/berlin/Kconfig`; relies on all selected per-SoC objects sharing `berlin.h`.

Risks: unconditional common object means the directory inclusion must remain gated by Kconfig. Missing object entry for a new SoC would produce a config that cannot probe despite descriptor code existing.

Test signals: inspect built-in object list for each config and run allmodconfig/allyesconfig style compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2.c

Purpose: Marvell Berlin BG2 pinctrl descriptor driver for SoC and system-manager pinmux blocks.

Important APIs/types/functions: static `berlin2_soc_pinctrl_groups` and `berlin2_sysmgr_pinctrl_groups` describe register offsets, bit widths, LSB positions, and legal mux functions. `berlin2_pinctrl_match` maps `marvell,berlin2-soc-pinctrl` and `marvell,berlin2-system-pinctrl` to descriptor data. Probe delegates to `berlin_pinctrl_probe()`.

Control flow: the builtin platform driver matches DT, retrieves `device_get_match_data()`, and lets the shared Berlin core build function/group state and use the parent syscon regmap.

State and persistence: all mux state is in syscon registers addressed by the descriptor offsets. This file owns no mutable runtime state beyond constants.

Dependencies/integration: depends on the Berlin core, OF match data, platform bus, and parent syscon regmap. Functions span GPIO, SPI, USB debug, SATA, SD, UART, TWSI, HDMI, I2S, PDM, NAND/eMMC, Ethernet, LEDs, and AV output signals.

Risks: duplicate mux values intentionally expose one hardware mode under multiple function names for DT composition; edits must preserve those aliases. Register bit-width/LSB errors can affect unrelated pins in the same syscon word.

Test signals: boot BG2 DTs for both compatible strings, inspect generated function groups in debugfs, and verify representative mux writes in the parent syscon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2cd.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2cd.c

Purpose: Berlin BG2CD descriptor driver for SoC and system-manager pinmux blocks.

Important APIs/types/functions: `berlin2cd_soc_pinctrl_groups`, `berlin2cd_sysmgr_pinctrl_groups`, `berlin2cd_pinctrl_match`, and `berlin2cd_pinctrl_probe()` provide BG2CD-specific data to the shared Berlin core.

Control flow: builtin platform driver matches `marvell,berlin2cd-soc-pinctrl` or `marvell,berlin2cd-system-pinctrl`; probe passes the selected descriptor to `berlin_pinctrl_probe()`, which obtains the parent syscon regmap and registers pinctrl.

State and persistence: descriptor-only source; mux selections persist in syscon registers. Unknown groups are represented with empty function descriptors and therefore are not exposed as selectable functions.

Dependencies/integration: Linux OF/platform/property helpers and `berlin.h`. Exposes groups for JTAG, GPIO, SD0, USB debug, front-end, PLL, PWM, UART, EDDC, TWSI, SPI, NAND, and other BG2CD muxes.

Risks: many system-manager groups are unknown placeholders; attempting to use them from DT will not resolve a function. Common core function synthesis depends on null-terminated function arrays emitted by macros.

Test signals: compile with `MACH_BERLIN_BG2CD`, verify both compatibles bind, check unknown groups do not create bogus functions, and use debugfs to confirm G/GSM group names and function membership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2cd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2q.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2q.c

Purpose: Berlin BG2Q descriptor driver for SoC and system-manager pinmux blocks.

Important APIs/types/functions: `berlin2q_soc_pinctrl_groups` and `berlin2q_sysmgr_pinctrl_groups` list large G/GAV/GSM mux tables. `berlin2q_pinctrl_match` binds `marvell,berlin2q-soc-pinctrl` and `marvell,berlin2q-system-pinctrl`; probe delegates to the shared Berlin core.

Control flow: platform match chooses descriptor data; common core builds unique functions from all group functions, maps function-to-groups, parses DT `function` and `groups`, and writes register fields through regmap.

State and persistence: this file is immutable descriptor data. Hardware syscon registers retain mux values across driver calls until reset or later writes.

Dependencies/integration: integrates media/audio/storage/network peripherals through DT pin states, including NAND/MMC, LVDS, RGMII, JTAG, TWSI, SPI, SATA, I2S, PDM, camera, demod, AVIF, smartcard, SD, HDMI, LEDs, UART, and EDDC.

Risks: BG2Q has many overlapping debug and peripheral functions sharing mux values; careless DT grouping can request incompatible muxes for adjacent fields. Since the Berlin core has no conflict log, later states can overwrite earlier selections.

Test signals: build with `MACH_BERLIN_BG2Q`, enumerate debugfs groups/functions, apply representative audio/video/storage pin states, and verify regmap writes use correct offsets from 0x18 through 0x40 ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg2q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg4ct.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg4ct.c

Purpose: Berlin4CT descriptor driver for SoC, AVIO, and system pinctrl MMIO blocks.

Important APIs/types/functions: `berlin4ct_soc_pinctrl_groups`, `berlin4ct_avio_pinctrl_groups`, and `berlin4ct_sysmgr_pinctrl_groups` define mux tables. Unlike older BG2 drivers, `berlin4ct_pinctrl_probe()` maps its own MMIO resource and creates a regmap with 32-bit registers and stride 4 before calling `berlin_pinctrl_probe_regmap()`.

Control flow: match data selects one descriptor for `marvell,berlin4ct-soc-pinctrl`, `marvell,berlin4ct-avio-pinctrl`, or `marvell,berlin4ct-system-pinctrl`. Probe maps resource 0, initializes regmap, and hands both to the common core.

State and persistence: mux state is MMIO register state in each block. Runtime state is common-core allocation only; this file has static descriptors.

Dependencies/integration: depends on OF, platform MMIO resources, regmap-mmio, and Berlin core. Functions cover NAND, RGMII, SD, STS, smartcard, SPI, USB VBUS, TWI, AVIO audio/HDMI/PDM, system UART/JTAG/SPI/LED/HDMI pins.

Risks: resource-size-based `max_register` must match hardware register span. Some groups use high mux values for debug functions; bad DT can route board-critical storage/network pins incorrectly.

Test signals: boot each of the three compatible blocks, verify regmap creation, use debugfs to confirm group counts, and observe register changes for NAND/RGMII and AVIO I2S pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin-bg4ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin.c

Purpose: Shared Marvell Berlin pinctrl core that turns static per-SoC group/function descriptors into a Linux pinctrl/pinmux device.

Important APIs/types/functions: `struct berlin_pinctrl` stores regmap, descriptor, generated `struct pinfunction` array, and `pinctrl_dev`. `berlin_pinctrl_probe()` obtains a parent syscon regmap; `berlin_pinctrl_probe_regmap()` accepts a caller-supplied regmap. `berlin_pinctrl_build_state()` builds unique functions and group membership. `berlin_pinmux_set()` writes selected mux values.

Control flow: DT parsing requires `function` and `groups` properties, reserves maps, and adds one mux map per group. During probe, the core allocates state, stores match descriptor, synthesizes function tables, registers the pinctrl device, and then services pinmux requests by finding the function in the selected group and updating a masked regmap field.

State and persistence: generated function tables are heap/devm allocated for the device lifetime. Hardware state persists in regmap-backed syscon/MMIO registers. No separate conflict tracking or pinconf state exists.

Dependencies/integration: relies on Linux pinctrl, pinmux, pinctrl-utils, regmap, OF, syscon parent nodes, and per-SoC descriptors from `berlin.h`.

Risks: `max_functions += 1 << (bit_width + 1)` is an over-allocation heuristic; very large bit widths would waste memory but tables use small widths. `krealloc(... nfunctions * sizeof(...))` with zero functions would be fragile, though descriptors contain valid functions. No get_group_pins callback is implemented, matching group-name-only Berlin binding style.

Test signals: unit-style DT parsing with missing properties should return `-EINVAL`; boot any Berlin SoC and validate generated function counts, function-to-group lists, and regmap bit updates for a sample group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin.h

Purpose: Shared descriptor interface for Berlin-family pinctrl table drivers.

Important APIs/types/functions: defines `struct berlin_desc_function`, `struct berlin_desc_group`, and `struct berlin_pinctrl_desc`. Macros `BERLIN_PINCTRL_GROUP`, `BERLIN_PINCTRL_FUNCTION`, and `BERLIN_PINCTRL_FUNCTION_UNKNOWN` build null-terminated compound-literal function arrays. Declares `berlin_pinctrl_probe()` and `berlin_pinctrl_probe_regmap()`.

Control flow: per-SoC C files use macros to create descriptor arrays; the common core reads those descriptors to build runtime pinctrl function/group mappings and to compute regmap masks.

State and persistence: no runtime state in the header. Descriptor objects are static constants in each SoC file.

Dependencies/integration: requires platform_device and regmap types via included users; it is included by Berlin core and descriptor drivers.

Risks: compound literal lifetime is safe for file-scope static initializers, but moving macro use into block scope would create invalid dangling pointers. `u8` offset/bit fields cap descriptor values; current hardware tables fit.

Test signals: compile all Berlin descriptor users, check unknown groups terminate properly, and verify each `BERLIN_PINCTRL_GROUP` has at least the sentinel function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/pinctrl-as370.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/pinctrl-as370.c

Purpose: Synaptics AS370 pinctrl descriptor driver using the Berlin common core with a direct MMIO regmap.

Important APIs/types/functions: `as370_soc_pinctrl_groups` describes AS370 mux groups, mostly audio, PDM, NAND/eMMC, SPI, USB, TWI, JTAG, PWM, UART, and SD0 pins. `as370_pinctrl_probe()` maps resource 0, creates a 32-bit regmap, and delegates to `berlin_pinctrl_probe_regmap()`.

Control flow: platform driver matches `syna,as370-soc-pinctrl`, retrieves descriptor data, initializes regmap-mmio from the pinctrl resource, then registers via the Berlin core.

State and persistence: mux state resides in MMIO registers; file-local state is static descriptor data only.

Dependencies/integration: OF/platform/regmap and Berlin core. Consumers request named functions through DT `function`/`groups` properties.

Risks: AS370 uses several mux values for reset, PLL, and debug outputs; bad pin states can disrupt boot-critical rails or clocks. Regmap `max_register` is set to resource size, so hardware descriptions must expose the correct span.

Test signals: compile with `PINCTRL_AS370`, boot an AS370 DT, validate debugfs group/function membership, and verify representative I2S, NAND/eMMC, and SD0 mux register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/pinctrl-as370.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/Kconfig

Purpose: Kconfig entries for Cirrus Logic CS42L43, Lochnagar, and Madera-family pinctrl drivers.

Important APIs/types/functions: defines visible tristate `PINCTRL_CS42L43` and `PINCTRL_LOCHNAGAR`, hidden tristate `PINCTRL_MADERA`, and hidden bool chip-table selectors `PINCTRL_CS47L15`, `PINCTRL_CS47L35`, `PINCTRL_CS47L85`, `PINCTRL_CS47L90`, `PINCTRL_CS47L92`.

Control flow: CS42L43 depends on `MFD_CS42L43` and selects GPIOLIB, PINMUX, PINCONF, and GENERIC_PINCONF. Lochnagar depends on `MFD_LOCHNAGAR && !MIPS`, avoiding a symbol clash. Madera is selected by MFD options and selects PINMUX/GENERIC_PINCONF.

State and persistence: compile-time only.

Dependencies/integration: paired with the Cirrus Makefile, MFD parent drivers, gpiolib, pinctrl, and generic pinconf infrastructure.

Risks: hidden chip selectors must be selected by Madera MFD Kconfig; otherwise the common Madera driver probes but no chip table is available and returns `-ENODEV`. The `!MIPS` guard is necessary due to `RST` naming conflicts.

Test signals: Kconfig dependency resolution for MFD-enabled builds, module/built-in combinations for CS42L43 and Lochnagar, and compile coverage for each hidden Madera chip selector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/Makefile

Purpose: Kbuild rules for Cirrus pinctrl drivers.

Important APIs/types/functions: builds standalone `pinctrl-cs42l43.o` and `pinctrl-lochnagar.o`; builds composite `pinctrl-madera.o` from `pinctrl-madera-core.o` plus conditionally included CS47Lxx table objects.

Control flow: `ifeq` blocks append chip-specific table objects only when hidden bool symbols are `y`; the final composite object is linked when `CONFIG_PINCTRL_MADERA` is enabled.

State and persistence: compile-time only.

Dependencies/integration: must stay synchronized with `pinctrl-madera.h` extern declarations and Madera Kconfig chip selectors.

Risks: if a chip table is omitted from `pinctrl-madera-objs`, the common core can reference an extern not linked under corresponding `IS_ENABLED()` paths or fail to support that codec.

Test signals: inspect `pinctrl-madera.o` composition for each Madera codec config and run compile tests for standalone CS42L43/Lochnagar modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs42l43.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs42l43.c

Purpose: Cirrus CS42L43 combined pinctrl and GPIO driver for codec pins, GPIO function selection, shutter routing, drive strength, and input debounce.

Important APIs/types/functions: `struct cs42l43_pin` holds gpiochip, regmap, device, and shutter lock state. Static pin/group/function tables define 15 pins and GPIO/ASP/PDM/I2C/SPI groups. `cs42l43_pin_set_mux()`, GPIO callbacks, and pinconf callbacks implement muxing and config.

Control flow: probe gets the parent MFD `cs42l43`, assigns regmap and `hw_lock`, configures gpiochip callbacks, optionally uses a child `pinctrl` fwnode, enables runtime PM, registers pinctrl, then registers the gpiochip. GPIO operations resume the device, access regmap, and release runtime PM.

State and persistence: mux, drive strength, debounce, GPIO direction/value/status, and shutter configuration live in codec registers. `shutters_locked` is immutable after probe and prevents shutter register writes when hardware lock is active.

Dependencies/integration: depends on `MFD_CS42L43`, cs42l43 register definitions, regmap, runtime PM, gpiolib, pinctrl, and generic pinconf. GPIOLIB pin ranges map the first three pins to GPIOs.

Risks: `cs42l43_gpio_set()` returns immediately on regmap update failure without `pm_runtime_put()`, risking a runtime-PM reference leak on that error path. Debounce semantics are coarse: any nonzero request maps to about 85 us. Shutter muxing is denied when locked.

Test signals: probe under MFD parent, validate GPIO get/set/direction with runtime PM tracing, set every supported drive strength, test debounce 0/nonzero, verify locked shutter requests return `-EPERM`, and inspect pinctrl debugfs groups/functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs42l43.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l15.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l15.c

Purpose: CS47L15 chip-specific Madera pin-group table.

Important APIs/types/functions: static pin arrays define `aif1`, `aif2`, `aif3`, and `pdmspk1` groups. Exported `const struct madera_pin_chip cs47l15_pin_chip` reports `CS47L15_NUM_GPIOS`, group pointer, and group count.

Control flow: no probe here; `pinctrl-madera-core.c` selects this exported table when the Madera parent type is `CS47L15` and `CONFIG_PINCTRL_CS47L15` is enabled.

State and persistence: immutable table data only; runtime mux/pinconf state is managed by the Madera core in codec registers.

Dependencies/integration: includes Madera core header for chip constants and `pinctrl-madera.h` for shared table structures. Function names intentionally match group names for alternate functions.

Risks: pin numbers are zero-indexed relative to datasheet numbering; off-by-one edits would misroute codec audio pins. Missing hidden Kconfig selection causes the common core to reject CS47L15 with `-ENODEV`.

Test signals: compile with CS47L15 support, probe Madera pinctrl on a CS47L15 parent, and verify debugfs exposes 15 pins plus the four alternate groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l35.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l35.c

Purpose: CS47L35 chip-specific group table for the shared Madera pinctrl driver.

Important APIs/types/functions: defines pin arrays for `aif1`, `aif2`, `aif3`, `mif1`, and `pdmspk1`, then exports `cs47l35_pin_chip` with `CS47L35_NUM_GPIOS`.

Control flow: selected by Madera core during probe when parent type is `CS47L35` and hidden config support is enabled. The core combines these alternate groups with generated single-GPIO groups and shared functions.

State and persistence: static descriptor state only.

Dependencies/integration: Madera MFD constants, `pinctrl-madera.h`, and common Madera core.

Risks: `mif1` spans non-contiguous pins 6 and 15, so tests must not assume each group is contiguous. Zero-indexed datasheet conversion is a common maintenance hazard.

Test signals: build with CS47L35 table linked, verify group membership for non-contiguous `mif1`, and apply an `aif`/`pdmspk1` alternate function through DT or pdata mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l85.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l85.c

Purpose: CS47L85/WM1840 group table for the Madera pinctrl core.

Important APIs/types/functions: defines MIF1-3, AIF1-4, DMIC4-6, and PDM speaker groups. `cs47l85_pin_chip` exports `CS47L85_NUM_GPIOS` and the group table.

Control flow: Madera core chooses this table for parent types `CS47L85` and `WM1840` when `CONFIG_PINCTRL_CS47L85` is enabled.

State and persistence: immutable group data only; common core writes hardware registers.

Dependencies/integration: Madera MFD chip constants and common pinctrl structures.

Risks: speaker groups use interleaved pins (`pdmspk1` 36/38 and `pdmspk2` 37/39), so group ordering is deliberate. Any mismatch with codec GPIO count truncates common pin descriptors.

Test signals: probe CS47L85/WM1840, inspect all 12 alternate groups, and apply AIF, MIF, DMIC, and speaker mux states to ensure common core handles high GPIO indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l85.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l90.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l90.c

Purpose: CS47L90/CS47L91 group table for the shared Madera pinctrl driver.

Important APIs/types/functions: defines MIF1-3, AIF1-4, DMIC3-5, and `pdmspk1` groups, exported as `cs47l90_pin_chip` with `CS47L90_NUM_GPIOS`.

Control flow: selected by Madera core for parent types `CS47L90` and `CS47L91`.

State and persistence: descriptor constants only.

Dependencies/integration: Madera MFD headers and `pinctrl-madera.h`.

Risks: CS47L90 differs from CS47L85 in DMIC and speaker coverage; copying tables across codecs can expose invalid groups. Hidden config must be selected by the parent MFD option.

Test signals: compile with CS47L90 support, verify debugfs group list lacks DMIC6 and PDM speaker 2, and exercise MIF/AIF/DMIC mux states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l90.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l92.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l92.c

Purpose: CS42L92/CS47L92/CS47L93 group table for the shared Madera pinctrl driver.

Important APIs/types/functions: defines `pdmspk1`, `aif1`, `aif2`, and `aif3` pin arrays, exported through `cs47l92_pin_chip` with `CS47L92_NUM_GPIOS`.

Control flow: Madera core selects this table for parent types `CS42L92`, `CS47L92`, and `CS47L93` when `CONFIG_PINCTRL_CS47L92` is enabled.

State and persistence: static table only.

Dependencies/integration: Madera MFD chip constants and the common pinctrl core.

Risks: this family has fewer alternate groups than larger Madera codecs; DT/pdata copied from CS47L85/90 may request nonexistent MIF/DMIC groups and fail. Pin numbering is zero-indexed.

Test signals: probe each supported parent type, inspect four alternate groups, and validate AIF plus PDM speaker muxing through pinctrl state application.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l92.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-lochnagar.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-lochnagar.c

Purpose: Cirrus Lochnagar board pinctrl/GPIO driver supporting Lochnagar1 and Lochnagar2 pin muxes, AIF routing, and output-only GPIO controls.

Important APIs/types/functions: macro-generated pin, AIF, function, and group tables feed `struct lochnagar_pin_priv`. `lochnagar_set_mux()`, `lochnagar_pin_set_mux()`, `lochnagar_aif_set_mux()`, and `lochnagar_conf_group_set()` implement mux and AIF master/slave config. A `gpio_chip` exposes board-control GPIO outputs.

Control flow: probe identifies parent MFD type, selects Lochnagar1/2 tables, builds function-to-group arrays, registers pinctrl, and registers gpiochip. Pin muxing dispatches by function type: pin functions write mux registers, while AIF functions set source/enable bits and for Lochnagar2 force associated mux pins to AIF. GPIO set either routes mux pins through Lochnagar2 GPIO channels or toggles direct GPIO bits.

State and persistence: register writes persist in Lochnagar MFD regmap. Lochnagar2 dynamically allocates up to 16 GPIO channel source registers, reusing existing matching channels or first free channel. The driver itself stores only table pointers and generated group lists.

Dependencies/integration: MFD Lochnagar regmaps and type IDs, DT binding constants, gpiolib, pinctrl, generic pinconf, and pinctrl-utils. Supports `cirrus,lochnagar-pinctrl`.

Risks: `lochnagar_pin_set_mux()` logs regmap write errors but returns 0 at the end, which can hide failed pin mux writes. GPIOs support output only; input direction returns `-EINVAL`. Lochnagar2 GPIO channel exhaustion returns `-ENOSPC`.

Test signals: probe both board revisions, verify function-group membership, route AIF groups and master/slave config, exhaust or reuse Lochnagar2 GPIO channels in tests, and check direct reset GPIO inversion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-lochnagar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-madera-core.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-madera-core.c

Purpose: Shared pinctrl core for Cirrus Madera codecs, combining generated single-pin GPIO groups, chip-specific alternate groups, common mux functions, and generic pinconf.

Important APIs/types/functions: `madera_pins`, `madera_mux_funcs`, and chip tables from `pinctrl-madera.h` drive the pinctrl device. Core callbacks include group enumeration, debug display, `madera_mux_set_mux()`, GPIO request/direction/free hooks, and `madera_pin_conf_get/set/group_set()`. `madera_pin_probe()` selects the chip descriptor by MFD type.

Control flow: probe inherits the parent fwnode, selects a chip table for CS47L15/35/85/90/92 families, sizes the descriptor to the chip GPIO count, registers and initializes pinctrl, optionally registers pdata mappings, enables pinctrl, and stores driver data. Muxing writes function codes into `MADERA_GPIOx_CTRL_1`; alt functions use function value 0 across chip-specific pin groups, while other functions target generated one-pin groups.

State and persistence: mux and pinconf state live in Madera codec registers. Driver state is devm-managed. Pinconf writes are batched as masks for two adjacent registers per pin.

Dependencies/integration: Madera MFD core/register headers, regmap, pinctrl, generic pinconf, pdata mappings, and chip-specific table objects.

Risks: `madera_pin_desc` is a static descriptor whose `npins` is mutated per probe, which would be risky if multiple Madera instances with different GPIO counts probed concurrently. Drive strength accepts only 4 and 8 mA; unsupported values warn and encode as 4 mA rather than returning an error. Input enable get checks CTRL_1 direction mask while set writes CTRL_2, worth hardware-register verification.

Test signals: probe each supported Madera type, check pdata mapping application, inspect debugfs pin states, test every pinconf parameter, verify strict GPIO/function exclusivity, and validate unsupported drive-strength behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-madera-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-madera.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-madera.h

Purpose: Shared declarations for the Madera pinctrl core and chip-specific group tables.

Important APIs/types/functions: `struct madera_pin_groups` describes an alternate function group; `struct madera_pin_chip` describes chip GPIO count and group table; `struct madera_pin_private` is the runtime core state. Extern declarations expose CS47L15/35/85/90/92 chip tables.

Control flow: chip-specific C files instantiate `madera_pin_chip`; the common core selects one by MFD type and stores it in `madera_pin_private`.

State and persistence: no state here; runtime state is allocated in the core and hardware state is in codec registers.

Dependencies/integration: used by all Cirrus Madera pinctrl sources and depends on the Madera MFD type declarations being visible in including C files.

Risks: extern declarations and Makefile object inclusion must remain aligned. Adding a new codec requires updating this header, Kconfig, Makefile, and core type switch together.

Test signals: compile all chip selector combinations and verify no unresolved externs or missing switch cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-madera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/Kconfig

Purpose: Kconfig entries for Cix Sky1 pinctrl support.

Important APIs/types/functions: hidden `PINCTRL_SKY1_BASE` selects generic pinctrl group/function/conf and regmap support; visible `PINCTRL_SKY1` depends on `ARCH_CIX || COMPILE_TEST` and `HAS_IOMEM`, and selects the base.

Control flow: enabling the Sky1 SoC driver pulls in the reusable base driver compiled from this subset and the SoC-specific `pinctrl-sky1.o`.

State and persistence: compile-time only.

Dependencies/integration: Kbuild consumes both symbols; base driver exports `sky1_base_pinctrl_probe()` for SoC-specific code.

Risks: base is tristate, so module linkage between base and SoC driver must be consistent. Missing `HAS_IOMEM` would break MMIO access, so the dependency is required.

Test signals: Kconfig resolution for ARCH_CIX and COMPILE_TEST, module build coverage, and confirmation that selecting `PINCTRL_SKY1` links both base and SoC object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/Makefile

Purpose: Kbuild rules for Cix Sky1 pinctrl drivers.

Important APIs/types/functions: builds `pinctrl-sky1-base.o` for `CONFIG_PINCTRL_SKY1_BASE` and `pinctrl-sky1.o` for `CONFIG_PINCTRL_SKY1`.

Control flow: the SoC-specific driver depends on the base helper object exported from `pinctrl-sky1-base.c`.

State and persistence: compile-time only.

Dependencies/integration: paired with Cix Kconfig and the shared header `pinctrl-sky1.h`.

Risks: if a future SoC uses the base without selecting the base symbol, exported probe linkage fails. Object order is simple but both pieces must agree on structure definitions.

Test signals: build with `PINCTRL_SKY1=m/y`, inspect linked objects, and run modpost for exported symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1-base.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1-base.c

Purpose: Reusable Cix Sky1 pinctrl base driver that parses DT pinmux/config data, creates one group per pin, writes mux/pull/drive fields, and exports `sky1_base_pinctrl_probe()`.

Important APIs/types/functions: uses SoC-provided `struct sky1_pinctrl_soc_info` and `sky1_pin_desc` from `pinctrl-sky1.h`. Core callbacks are `sky1_pctrl_dt_node_to_map()`, `sky1_pmx_set_mux()`, `sky1_pconf_group_set/get()`, and `sky1_pctrl_build_state()`. Register field macros cover mux bits, pull bits, and drive-strength bits.

Control flow: exported probe validates SoC info, maps MMIO resource 0, allocates a dynamic pinctrl descriptor and pin list, builds one-pin groups, registers and enables pinctrl, and calls `pinctrl_provide_dummies()` to make default/sleep state transitions work across separate controllers. DT parsing walks child nodes, reads packed `pinmux` cells, validates pin/function numbers, adds mux maps, and optionally adds group config maps.

State and persistence: hardware state is per-pin MMIO registers at `base + pin * 4`. Group `config` stores the last config value for group get but is not a full hardware readback. Driver state is devm-managed.

Dependencies/integration: Linux OF, pinctrl, pinmux, generic pinconf, MMIO accessors, and SoC-specific Sky1 data. Functions are generic names `func0` through `func3`; valid function count is per pin.

Risks: `sky1_pconf_parse_conf()` declares the config argument as `enum pin_config_param`, though it carries a numeric argument; this is type-confusing but works as integer C. Unsupported drive strengths silently map to default table index 4 rather than erroring. No locks protect MMIO read-modify-write operations, so concurrent pinctrl changes could race.

Test signals: parse DT nodes with valid/invalid packed pinmux cells, verify one group per pin in debugfs, set pull-up/down/disable and drive strengths, confirm default/sleep dummy behavior during suspend transitions, and validate exported symbol use by the SoC driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1-base.c -->
