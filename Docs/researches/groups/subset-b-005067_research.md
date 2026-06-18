# Research Report: subset-b-005067

This grouped report covers the requested Nuvoton and NXP pinctrl files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-npcm7xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-npcm7xx.c

Purpose: Implements the Nuvoton NPCM7xx pinctrl and GPIO driver for BMC SoCs such as NPCM750. It exposes the SoC pin groups, alternate functions, GPIO banks, generic pin configuration, and per-bank GPIO interrupt handling to the Linux pinctrl and gpiolib frameworks.

Important APIs, types, and functions: `struct npcm7xx_pinctrl` holds the device, GCR syscon regmap, registered pinctrl device, GPIO banks, and bank count. `struct npcm7xx_gpio` wraps `gpio_generic_chip` with bank MMIO base, IRQ metadata, pinctrl range id, and saved gpio-mmio callbacks. The large `npcm7xx_pins`, `npcm7xx_groups`, `npcm7xx_funcs`, and `pincfg` tables are the hardware contract. Core helper paths are `npcm7xx_setfunc()`, `npcm7xx_get/set_slew_rate()`, `npcm7xx_get/set_drive_strength()`, `npcm7xx_config_get()`, `npcm7xx_config_set_one()`, `npcm7xx_gpio_of()`, `npcm7xx_gpio_register()`, and `npcm7xx_pinctrl_probe()`.

Control flow: `arch_initcall(npcm7xx_pinctrl_register)` registers the platform driver early. Probe allocates state, resolves the `nuvoton,npcm750-gcr` syscon regmap, parses child GPIO nodes with `for_each_gpiochip_node()`, maps each GPIO bank, initializes `gpio_generic_chip`, reads `gpio-ranges`, captures bank IRQs, registers the pinctrl descriptor, then registers each GPIO chip and chained IRQ domain. Pinctrl DT state conversion uses `pinconf_generic_dt_node_to_map_all()`. Mux selection calls `npcm7xx_setfunc()` for each pin in a group, which toggles up to three GCR selector bits per pin. GPIO request forces mux mode to `fn_gpio`; GPIO direction callbacks coordinate pinctrl state before delegating to gpio-mmio direction helpers.

State and persistence: Runtime state is devm-managed except for MMIO register contents. GCR MFSEL/I2CSEGSEL/FLOCKR/SRCNT bits persist hardware mux choices; GPIO registers persist direction, input enable, pull-up/down, open drain, debounce enable, event polarity/type, and drive/slew settings until reset or reconfiguration. The driver does not implement suspend/resume save/restore, so persistence depends on SoC power-domain retention and later pinctrl reapplication.

Dependencies and integration points: Depends on platform driver matching `nuvoton,npcm750-pinctrl`, syscon for GCR access, child GPIO firmware nodes with MMIO resources, `gpio-ranges`, and IRQs. It integrates with pinctrl core through `pinctrl_desc`, `pinctrl_ops`, `pinmux_ops`, and `pinconf_ops`; with gpiolib through `gpio_generic_chip`; and with irqchip through immutable GPIO IRQ chip callbacks.

Risks: The pin/function tables are tightly coupled by enum order. `npcm7xx_pinmux_set_mux()` passes `group` as the mux mode to `npcm7xx_setfunc()` rather than the `function` selector, which works only if group and function numbering stay aligned; table edits can silently program the wrong GCR bits. `pincfg` is sparse and indexed by absolute pin number, so any out-of-range pin id from tables or DT would be unsafe. Pinconf get returns `-EINVAL` when a queried boolean state is false, making "not enabled" indistinguishable from unsupported for some callers. IRQ masking/unmasking and GPIO register read-modify-write rely on gpio generic locking around bank registers but do not add a broader pinctrl-level lock.

Test signals: Build coverage for `CONFIG_PINCTRL_NPCM7XX`, OF probe on an NPCM750 device tree, successful lookup of `nuvoton,npcm750-gcr`, registration of all GPIO child banks, correct `gpio-ranges`, pinmux state application for SMB/I2C, UART, LPC/eSPI, SPI, MMC, RGMII/RMII, watchdog, and clock pins, pinconf reads/writes for bias/open-drain/debounce/drive-strength/slew, GPIO input/output direction changes, and per-bank edge/level IRQ delivery are the main validation signals. Debugfs GPIO dumps should show expected DIN/DOUT/IEM/OE/PU/PD/EV* state after configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-npcm7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-npcm8xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-npcm8xx.c

Purpose: Implements the Nuvoton NPCM8xx pinctrl and GPIO driver, extending the NPCM7xx-style model for newer NPCM845-class BMCs. It provides richer alternate-function tables, GPIO bank registration, configurable debounce timing slots, GPIO IRQ handling, and pin configuration for bias, drive mode, drive strength, slew rate, debounce, and level/input state.

Important APIs, types, and functions: `struct npcm8xx_pinctrl` owns the pinctrl device, GCR regmap, and eight potential GPIO banks. `struct npcm8xx_gpio` embeds `gpio_generic_chip`, bank MMIO base, per-bank debounce slot cache, IRQ metadata, per-bank IRQ chip copy, pinctrl range id, and saved gpio-mmio callbacks. `struct debounce_time` caches up to four hardware debounce timings per bank. Key functions include `npcm8xx_setfunc()`, `npcm8xx_get/set_slew_rate()`, `npcm8xx_get/set_drive_strength()`, `npcm8xx_gpio_request_enable()`, `debounce_timing_setting()`, `npcm_set_debounce()`, `npcm8xx_config_get()`, `npcm8xx_config_set_one()`, `npcm8xx_gpio_fw()`, `npcm8xx_gpio_register()`, and `npcm8xx_pinctrl_probe()`.

Control flow: `arch_initcall(npcm8xx_pinctrl_register)` registers the platform driver. Probe allocates state, retrieves the GCR regmap from the `nuvoton,sysgcr` phandle, parses GPIO child nodes, maps each bank, initializes gpio-mmio, reads `gpio-ranges` and a parent IRQ, stores saved callbacks, initializes debounce slot bookkeeping, registers the pinctrl descriptor, then registers each GPIO chip with a chained IRQ parent. Mux setting writes up to five selector bits per pin through `npcm8xx_setfunc()`. GPIO request normally selects `fn_gpio`, but pins 35, 36, and 183-189 are forced to their first function instead of generic GPIO mode. Pinconf writes manipulate GPIO bank registers and GCR SRCNT for LPC/eSPI slew.

State and persistence: Driver state is devm-managed, while hardware state lives in GCR MFSEL/I2CSEGSEL/FLOCKR/SRCNT registers and GPIO bank registers. Per-bank debounce timing slot allocation persists in `bank->debounce` so later GPIOs can reuse one of four programmed timing values. Debounce enable bits, selected debounce timing registers, pulls, open drain, output level/direction, interrupt type/polarity, drive strength, and slew settings persist in hardware until reset or reconfiguration. There is no explicit suspend/resume save/restore in this file; the IRQ chip uses `IRQCHIP_MASK_ON_SUSPEND`.

Dependencies and integration points: Depends on compatible `nuvoton,npcm845-pinctrl`, a `nuvoton,sysgcr` phandle, child GPIO firmware nodes with MMIO resources, `gpio-ranges`, and IRQs. It integrates with generic pinconf DT parsing through `pinconf_generic_dt_node_to_map()`, pinctrl through static pin/group/function descriptors, gpiolib through `gpio_generic_chip`, and irqchip through per-bank chained interrupt callbacks.

Risks: Like the 7xx driver, `npcm8xx_pinmux_set_mux()` passes `group` to `npcm8xx_setfunc()` as the selected mode rather than the `function` argument, so group/function table ordering is a hidden correctness dependency. The large sparse `pincfg` table is indexed directly by absolute pin id. Debounce timing allocation has only four slots per bank and returns `-ENOTSUPP` once all slots are consumed; it also uses set-only operations on the debounce selector register, so changing a pin from one timing slot to another may leave stale selector bits unless hardware encoding and prior state make that benign. `npcm8xx_pinctrl_probe()` logs GPIO registration failure but returns success unconditionally, which can mask GPIO registration failures after pinctrl registration. IRQ mask/unmask do not call `gpiochip_disable_irq()`/`gpiochip_enable_irq()` unlike the 7xx driver.

Test signals: Build coverage for `CONFIG_PINCTRL_NPCM8XX`, probe on NPCM845 DT with valid `nuvoton,sysgcr`, all GPIO banks appearing with pin ranges, pinmux application for I3C, SMB, HSI/UART, SPI, flash media, RMII/RGMII, eSPI/LPC, PWM, fan, and test-port functions, pinconf for bias/open-drain/drive-strength/slew, debounce values spanning fixed and calculated ranges, GPIO direction and value IO, and edge/level GPIO IRQ delivery. Tests should explicitly cover GPIO registration error handling and the limited debounce-slot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-npcm8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-wpcm450.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-wpcm450.c

Purpose: Implements pinctrl, GPIO, pinconf debounce, and GPIO interrupt support for the Nuvoton WPCM450 BMC. It maps WPCM450 GCR MFSEL mux bits and banked GPIO/event registers into Linux pinctrl and gpiolib interfaces.

Important APIs, types, and functions: `struct wpcm450_pinctrl` stores the pinctrl device, GCR syscon regmap, GPIO MMIO base, eight bank objects, shared both-edge emulation bitmap, and a raw spinlock. `struct wpcm450_gpio` wraps a `gpio_generic_chip` with parent pinctrl and bank metadata. `struct wpcm450_bank` describes each bank's GPIO range, register offsets, and central event-register IRQ bit mapping. Important functions include `wpcm450_setfunc()`, `wpcm450_update_mfsel()`, `wpcm450_pinmux_set_mux()`, `wpcm450_config_get/set_one()`, `wpcm450_gpio_register()`, `wpcm450_gpio_irqhandler()`, `wpcm450_gpio_set_irq_type()`, and `wpcm450_pinctrl_probe()`.

Control flow: `module_platform_driver()` registers the platform driver for `nuvoton,wpcm450-pinctrl`. Probe allocates state, initializes the raw spinlock, resolves the `nuvoton,wpcm450-gcr` syscon, registers the static pinctrl descriptor, maps the GPIO/event controller resource, then iterates child GPIO nodes. Each child `reg` selects one of eight static bank descriptions; the driver initializes a gpio-mmio chip, assigns pin ranges, configures optional output support, collects up to four parent IRQs, and registers the chip. Mux selection walks group pins and toggles per-pin MFSEL1/MFSEL2 bits, including inverted selector bits. IRQ handling reads central event status and enable registers, filters bits belonging to the bank, adjusts polarity for emulated both-edge lines, then dispatches child IRQs through the GPIO IRQ domain.

State and persistence: Hardware state is in GCR MFSEL registers and the GPIO/event MMIO block. The driver tracks `both_edges` in memory for emulated dual-edge interrupts. Debounce enable is controlled centrally through `WPCM450_GPEVDBNC` and only supports GPIOs 0-15. Pinmux, debounce, output, direction, event type, polarity, and enable bits persist until reconfigured or reset. There is no suspend/resume context save.

Dependencies and integration points: Depends on compatible `nuvoton,wpcm450-pinctrl`, the `nuvoton,wpcm450-gcr` syscon, a GPIO controller resource, and child GPIO nodes with `reg` and optional parent IRQs. It integrates with pinctrl through static pin/group/function descriptors and `pinconf_generic_dt_node_to_map_all()`, with gpio-mmio through `gpio_generic_chip_init()`, and with IRQ core through immutable `wpcm450_gpio_irqchip`.

Risks: The central GPIO event block maps only 18 IRQ-capable GPIOs across banks 0 and 1; unsupported-bank interrupts must be represented accurately in DT. `wpcm450_irq_bitnum_to_gpio()` uses `>` rather than `>=` in the range check, so the first bit after a bank's valid IRQ range may not be rejected before conversion. Both-edge emulation relies on reading the current level and switching polarity in a loop; rapidly toggling lines can stress this logic. Some groups have empty or overlapping pin arrays, and MFSEL bit inversion must be maintained carefully for scs3/kbcc-like functions. Only debounce for GPIOs 0-15 is supported.

Test signals: Build/probe for `CONFIG_PINCTRL_WPCM450`, successful GCR syscon lookup, all declared GPIO banks registering with correct input/output capability, pinmux transitions for SMB, serial, RMII, SDIO, SPI, PWM, flash interface, and HGPIO groups, debounce set/get on GPIOs 0-15 and rejection elsewhere, GPIO direction/value behavior on output-capable and input-only banks, and IRQ tests for level, rising, falling, and emulated both-edge events. Register dumps of MFSEL1/MFSEL2 and GPEV* should match requested states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-wpcm450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/Kconfig

Purpose: Defines the Kconfig entries for the NXP S32 Common Chassis pinctrl core and the S32G2 SIUL2 pinctrl driver.

Important APIs, types, and symbols: `PINCTRL_S32CC` is a hidden boolean selected by SoC-specific drivers. It depends on `ARCH_S32 && OF` and selects `GENERIC_PINCTRL_GROUPS`, `GENERIC_PINMUX_FUNCTIONS`, `GENERIC_PINCONF`, and `REGMAP_MMIO`. `PINCTRL_S32G2` is the visible option labeled "NXP S32G2 pinctrl driver"; it depends on `ARCH_S32 && OF`, selects `PINCTRL_S32CC`, and has help text for S32G2 family SoCs.

Control flow: There is no runtime control flow. Configuration flow is that enabling the visible S32G2 driver pulls in the common S32CC implementation and its generic pinctrl/pinmux/pinconf/regmap dependencies.

State and persistence: No runtime state. Build configuration persists in the kernel `.config` and determines whether `pinctrl-s32cc.o` and `pinctrl-s32g2.o` are compiled.

Dependencies and integration points: Integrates with the parent pinctrl Kconfig menu and Linux build system. It constrains these drivers to Open Firmware-enabled S32 architectures and ensures the common core can use generic pinctrl helpers and MMIO regmaps.

Risks: `PINCTRL_S32CC` is not user-visible, so any future SoC driver must select it or the common core will not build. `PINCTRL_S32G2` is a `bool`, not a tristate, matching the built-in registration pattern; changing module semantics would require driver and Makefile review.

Test signals: `make olddefconfig`/`menuconfig` visibility on `ARCH_S32`, expected symbol selection in `.config`, compile coverage with `CONFIG_PINCTRL_S32G2=y`, and absence of the option when `ARCH_S32` or `OF` is disabled validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/Makefile

Purpose: Connects NXP pinctrl Kconfig symbols to the objects built by kbuild.

Important APIs, types, and symbols: `obj-$(CONFIG_PINCTRL_S32CC) += pinctrl-s32cc.o` builds the common S32 pinctrl core, and `obj-$(CONFIG_PINCTRL_S32G2) += pinctrl-s32g2.o` builds the S32G2 SoC data and platform driver.

Control flow: There is no runtime control flow. Build-time control follows kbuild expansion of `obj-y` entries based on selected Kconfig symbols.

State and persistence: No runtime state. The selected `.config` controls whether these object files become part of the kernel image.

Dependencies and integration points: Integrates with `drivers/pinctrl/Makefile`, the local `Kconfig`, and the split between reusable S32CC core code and S32G2-specific data/driver registration.

Risks: Because `pinctrl-s32g2.c` calls `s32_pinctrl_probe()` from `pinctrl-s32cc.c`, selecting or building the SoC object without the common object would fail linking. The Kconfig currently prevents that by selecting `PINCTRL_S32CC`.

Test signals: Kernel build with `CONFIG_PINCTRL_S32G2=y` should compile and link both objects; build with only hidden common selected by another SoC should compile only `pinctrl-s32cc.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32.h

Purpose: Provides the shared internal interface and data structures for NXP S32 pinctrl drivers. It lets SoC-specific files describe pins and memory ranges while delegating parsing, muxing, pinconf, GPIO-mode handling, and PM save/restore to the S32 common core.

Important APIs and types: `struct s32_pin_group` pairs generic `struct pingroup` data with an array of SSS mux values. `struct s32_pin_range` defines inclusive pin id ranges per MMIO resource. `struct s32_pinctrl_soc_data` supplies the immutable SoC pin descriptors and memory-region ranges. `struct s32_pinctrl_soc_info` is the runtime parsed function/group state used by the common core. Macros `S32_PINCTRL_PIN()` and `S32_PIN_RANGE()` construct pin descriptors and ranges. Exported functions are `s32_pinctrl_probe()`, `s32_pinctrl_suspend()`, and `s32_pinctrl_resume()`.

Control flow: The header has no executable logic. SoC drivers provide `s32_pinctrl_soc_data` to `s32_pinctrl_probe()`, which then registers the pinctrl device and parses DT-defined functions/groups. PM callbacks in SoC drivers call the exported suspend/resume functions.

State and persistence: No state is stored by the header. It defines which SoC data is immutable and which runtime state is allocated and populated by the common core. The suspend/resume declarations expose the persistent pad save/restore contract under PM sleep.

Dependencies and integration points: Depends on pinctrl core types such as `struct pingroup`, `struct pinctrl_pin_desc`, and `struct pinfunction`, and forward-declares `struct platform_device`. It is included by both `pinctrl-s32cc.c` and `pinctrl-s32g2.c`.

Risks: This is an internal ABI between S32 common and SoC-specific files. Changing structure fields requires coordinated edits in the core parser, mux code, PM code, and every SoC data file. `S32_PIN_RANGE()` ranges must match platform resources exactly or common regmap offset calculations will target the wrong MMIO area.

Test signals: Compile coverage for common and S32G2 objects, successful probe using `s32_pinctrl_soc_data`, correct DT group parsing into `s32_pin_group`, and suspend/resume builds under `CONFIG_PM_SLEEP` validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32cc.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32cc.c

Purpose: Implements the common S32 Common Chassis/SIUL2 pinctrl core used by S32 SoC-specific data files. It parses DT pinmux groups, maps pin ids to MMIO resources, programs source signal select fields, applies generic pin configuration, supports GPIO ownership transitions, and saves/restores active pad registers across system sleep.

Important APIs, types, and functions: Public entry points are `s32_pinctrl_probe()`, `s32_pinctrl_suspend()`, and `s32_pinctrl_resume()`. Internal state is `struct s32_pinctrl`, which holds device, pinctrl device, mapped regions, parsed SoC info, saved GPIO configs, lock, and optional PM context. `struct s32_pinctrl_mem_region` maps a regmap to one pin range. Helpers include `s32_get_region()`, `s32_regmap_read/write/update()`, `s32_dt_group_node_to_map()`, `s32_pmx_set()`, `s32_pmx_gpio_request_enable()`, `s32_pmx_gpio_disable_free()`, `s32_pmx_gpio_set_direction()`, `s32_parse_pincfg()`, `s32_pinconf_mscr_write()`, `s32_pinctrl_parse_groups()`, `s32_pinctrl_parse_functions()`, and `s32_pinctrl_probe_dt()`.

Control flow: `s32_pinctrl_probe()` validates SoC data, allocates runtime state, initializes the saved GPIO config list and pinctrl descriptor, calls `s32_pinctrl_probe_dt()` to map each platform resource into a regmap and parse DT child nodes into functions/groups, registers the pinctrl device, and allocates PM save storage. DT flow expects top-level child nodes to represent functions and their children to represent groups with `pinmux` cells plus optional generic pinconf properties. Pinmux `set_mux` validates every pin in a group, then updates the `S32_MSCR_SSS_MASK` field for each MSCR pin. Pinconf set parses generic properties into MSCR masks and values; group pinconf overwrites all non-SSS bits, while per-pin pinconf only updates selected bits. GPIO request saves the current MSCR value in a list, clears SSS to select GPIO mode, and restores the value on GPIO free.

State and persistence: Runtime parsed functions/groups and region mappings are devm-owned. GPIO request state persists in the `gpio_configs` linked list until the GPIO is freed. Hardware pad configuration persists in SIUL2 MSCR/IMCR registers. Under `CONFIG_PM_SLEEP`, suspend saves only pins with `mux_owner` or `gpio_owner`, and resume writes those saved pad values back. Pins not currently owned are intentionally not restored.

Dependencies and integration points: Uses Linux pinctrl core, generic pinconf parser, pinctrl-utils mapping helpers, regmap-mmio, platform resources, and OF child-node parsing. SoC-specific files provide `struct s32_pinctrl_soc_data` with pins and inclusive memory ranges. GPIO integration uses pinctrl GPIO callbacks, not a gpiochip implemented in this file.

Risks: `s32_regmap_*()` computes register offset from inclusive pin ranges and regmap stride; bad SoC ranges or mismatched resources will corrupt the wrong register. GPIO config restoration writes MMIO while holding `gpio_configs_lock`, so regmap operations inside the spinlocked section should be reviewed for sleepability on the configured regmap backend. Multiple GPIO requests for the same pin can add multiple saved configs; free restores the first matching list entry. `s32_pinconf_get()` casts `unsigned long *` to `unsigned int *`, which assumes the generic caller accepts raw 32-bit MSCR state rather than packed pinconf. Group pinconf `S32_PINCONF_OVERWRITE` updates all non-SSS bits and can clear fields not represented by the requested properties because `config` starts at zero.

Test signals: Build with `CONFIG_PINCTRL_S32CC`, probe through `pinctrl-s32g2.c`, DT parsing failures for missing/empty `pinmux`, mux programming for multiple pins/functions, generic pinconf properties for pull-up/down/disable/high-impedance, open-drain/push-pull, input/output enable, slew rates 208/166/150/133/83 MHz, GPIO request/free restoring prior MSCR state, GPIO direction setting IBE/OBE, invalid pin range handling, and suspend/resume retaining owned pin state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32cc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32g2.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32g2.c

Purpose: Supplies NXP S32G2 SIUL2-specific pin identifiers, pin descriptors, MMIO pin ranges, OF match data, PM operations, and the built-in platform driver that binds the generic S32 common pinctrl core to S32G2 hardware.

Important APIs, types, and functions: `enum s32_pins` enumerates MSCR pad ids and IMCR input-select ids, including GPIO ports, QSPI, boot mode, I2C, LIN, USDHC, CAN, JTAG, Ethernet/GMAC/PFE EMAC, FlexRay, FlexTimer, DSPI, LLCE, USB, and SIUL external interrupt inputs. `s32_pinctrl_pads_siul2[]` lists the actual `pinctrl_pin_desc` entries exposed to the core. `s32_pin_ranges_siul2[]` maps sparse pin id ranges to six platform MMIO resources. `s32_pinctrl_data` packages those arrays for the common probe. `s32g_pinctrl_probe()` passes OF match data into `s32_pinctrl_probe()`.

Control flow: The driver is registered with `builtin_platform_driver()`, matching `nxp,s32g2-siul2-pinctrl`. Probe retrieves `s32_pinctrl_data` from the OF match table and delegates all substantive setup to the common S32 core. PM uses `LATE_SYSTEM_SLEEP_PM_OPS(s32_pinctrl_suspend, s32_pinctrl_resume)`, so suspend/resume sequencing is handled by the common code after most device suspend and before most resume actions.

State and persistence: This file itself is immutable SoC description plus platform-driver metadata. Hardware state and parsed DT runtime state live in `pinctrl-s32cc.c`. The memory ranges determine persistence/save-restore behavior because they decide which pin ids can be read or written through the common regmap helpers.

Dependencies and integration points: Depends on `pinctrl-s32.h`, the common S32CC object, OF/platform driver infrastructure, and a device tree node compatible with `nxp,s32g2-siul2-pinctrl` that provides one MMIO resource per `s32_pin_ranges_siul2` entry and child function/group nodes using the common `pinmux` format.

Risks: The enum values are sparse hardware register indices, not dense array offsets; the `s32_pinctrl_pads_siul2[]` contents and `s32_pin_ranges_siul2[]` must remain consistent with platform resources. Missing enum entries in the pins array make otherwise valid pinmux cells fail common range or descriptor checks. Incorrect range boundaries can cause common regmap offset calculation to target the wrong SIUL2 resource. Because the driver is built-in, Kconfig/Makefile changes must preserve built-in registration semantics.

Test signals: Build/link with `CONFIG_PINCTRL_S32G2=y`, OF probe for `nxp,s32g2-siul2-pinctrl`, successful mapping of six resources, pinctrl debug output listing MSCR and IMCR pins, DT muxing for representative peripherals from both SIUL2_0 and SIUL2_1 ranges, invalid-pin DT rejection, and system suspend/resume preserving owned pins through the common PM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32g2.c -->
