# Research Report: subset-b-005066

This grouped report covers the requested Nomadik and Nuvoton pinctrl files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik-db8500.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik-db8500.c

## Purpose
This file is the DB8500 SoC data provider for the common Nomadik pinctrl driver. It enumerates the routed DB8500 GPIO-capable pads, names each pad by GPIO number and package ball, defines pin groups for alternate-function columns A, B, C, and extended ALT-C1 through ALT-C4 selections, groups those pin groups into named pinmux functions, and supplies the DB8500 PRCM GPIOCR metadata needed for ALT-Cx selections.

## Important APIs, types, and functions
The main output is `nmk_pinctrl_db8500_init()`, which stores the address of static `nmk_db8500_soc` in the caller-provided `const struct nmk_pinctrl_soc_data **`. `nmk_db8500_soc` points at `nmk_db8500_pins`, `nmk_db8500_groups`, `nmk_db8500_functions`, `db8500_altcx_pins`, and `db8500_prcm_gpiocr_regs`. The table uses `PINCTRL_PIN()`, `NMK_PIN_GROUP()`, local `DB8500_FUNC_GROUPS()`, local `FUNCTION()`, and `PRCM_GPIOCR_ALTCX()` macros from the pinctrl and gpio-nomadik contracts.

## Control flow
There is no active runtime control flow beyond `nmk_pinctrl_db8500_init()`. During `pinctrl-nomadik.c` probe, the compatible string `stericsson,db8500-pinctrl` causes the core driver to call this init function. Later, pinctrl core callbacks index the provided arrays: group callbacks expose `nmk_db8500_groups`, mux callbacks choose a group's `altsetting`, and DB8500 ALT-Cx mux requests also pass through the PRCM GPIOCR metadata so the common driver can set or clear the selected extended alternate function.

## State and persistence behavior
All data in this file is immutable static SoC description. Persistent hardware state is created only when the common driver consumes the tables and writes GPIO AFSLA/AFSLB and PRCM GPIOCR registers. The pin list intentionally contains GPIO-number holes; consumers must treat `npins` as descriptor count, not as a dense maximum GPIO number.

## Dependencies and integration points
The file depends on Linux pinctrl descriptors and `linux/gpio/gpio-nomadik.h` for Nomadik group/function/SoC structures and PRCM ALT-Cx macros. It integrates directly with `pinctrl-nomadik.c`, which owns registration and register writes. The group names are device-tree visible through the common driver's `groups` and `function` properties, so board DTS files rely on these exact strings.

## Risks
This is data-heavy and typo-sensitive. A group name typo can break a function's group list at runtime even though the file compiles; notable examples to audit are function strings that must exactly match `NMK_PIN_GROUP()` names. Wrong ALT-Cx PRCM register indices or control bits can select unrelated debug, memory, modem, or RF functions. Pin holes and ball-name mappings should be checked against the datasheet because an incorrect GPIO number silently programs the wrong pad.

## Test signals
Useful checks include build coverage for `CONFIG_PINCTRL_NOMADIK`, probe on a DB8500 device tree with a valid `prcm` phandle, pinctrl debugfs group/function enumeration, mux requests for plain ALT-A/B/C and ALT-C1..C4 groups, and board-level smoke tests for UART, MMC, LCD, I2C, SPI, USB, and debug functions named in this table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik-db8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik-stn8815.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik-stn8815.c

## Purpose
This file is the STN8815 SoC data provider for the common Nomadik pinctrl driver. It lists 124 routed GPIO-capable pins, maps each one to a `GPIO<number>_<ball>` pinctrl descriptor, defines the STN8815 alternate-function groups, and declares the function-to-group relationships for UART, MMC/SD, I2C, CLCD, and USB pinmuxing.

## Important APIs, types, and functions
The only exported entry point is `nmk_pinctrl_stn8815_init()`, which assigns `nmk_stn8815_soc` to the common driver's SoC pointer. `nmk_stn8815_soc` references `nmk_stn8815_pins`, `nmk_stn8815_groups`, and `nmk_stn8815_functions`. The group table uses `NMK_PIN_GROUP()` with `NMK_GPIO_ALT_A`, `NMK_GPIO_ALT_B`, and `NMK_GPIO_ALT_C`; the function table is built with local `STN8815_FUNC_GROUPS()` and `FUNCTION()` macros.

## Control flow
The file is passive table data. The common Nomadik probe path selects it when device-tree match data identifies `PINCTRL_NMK_STN8815`. Pinctrl group callbacks expose the pin arrays, function callbacks expose the `u0`, `mmcsd`, `u1`, `i2c1`, `i2c0`, `i2cusb`, `clcd`, and `usb` functions, and the common mux callback writes the selected alternate function into the corresponding GPIO bank registers.

## State and persistence behavior
The tables are immutable and do not allocate or mutate state. Hardware persistence occurs later through `pinctrl-nomadik.c` when muxing or pin configuration is applied. Unlike DB8500, this SoC data has no ALT-Cx PRCM GPIOCR extension table, so the common driver treats absent PRCM data as acceptable for STN8815 and falls back to ordinary ALT-C handling.

## Dependencies and integration points
The file depends on pinctrl core descriptors and Nomadik structures from `linux/gpio/gpio-nomadik.h`. It integrates with the common Nomadik pinctrl driver and with device trees that reference the exact function and group names, such as `u0txrx_a_1`, `mmcsd_a_1`, `usbfs_b_1`, and `usbhs_c_1`.

## Risks
The file's main risks are table accuracy and string consistency. Function group strings are not compiler-validated against group definitions. The STN8815 pin list notes that GPIOs 124-127 are not routed; tests and board descriptions must not assume a full 128-pin contiguous external pad set. Since the common driver may operate without PRCM on STN8815, accidental addition of ALT-Cx-style requirements would need corresponding core-driver and SoC-data updates.

## Test signals
Compile coverage for the Nomadik driver, STN8815 probe without a PRCM base, pinctrl debugfs enumeration, and board-level mux tests for UART0 modem pins, MMC/SD split groups, I2C, CLCD high data pins, USB FS, and USB HS are the strongest validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik-stn8815.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik.c

## Purpose
This is the common pinctrl, pinmux, and pinconf implementation for Nomadik-family pin controllers. SoC-specific files provide pins, groups, functions, and optional PRCM ALT-Cx metadata; this file registers the Linux pinctrl device, parses device-tree mux/config nodes, maps global pin numbers to `gpio-nomadik` banks, programs GPIO alternate-function and pin configuration registers, and coordinates low-power and glitch-avoidance behavior.

## Important APIs, types, and functions
Key state is `struct nmk_pinctrl`, containing the device, pinctrl device, selected SoC data, and optional PRCM base. Global integration points are `nmk_gpio_chips[]` and `nmk_gpio_slpm_lock`, shared with gpio-nomadik. Muxing is handled by `nmk_pmx_set()`, `__nmk_gpio_set_mode()`, `__nmk_gpio_set_mode_safe()`, `nmk_prcm_altcx_set_mode()`, and `nmk_prcm_gpiocr_get_mode()`. Pin configuration is handled by `nmk_pin_config_set()` and helpers for pull, direction, low-EMI, and sleep mode. Device-tree parsing is implemented by `nmk_pinctrl_dt_node_to_map()` and `nmk_pinctrl_dt_subnode_to_map()`.

## Control flow
`core_initcall(nmk_pinctrl_init)` registers a platform driver. Probe selects STN8815 or DB8500 SoC data from OF match data, follows `nomadik-gpio-chips` references to populate GPIO bank structures, maps optional `prcm`, fills the global pinctrl descriptor, and calls `devm_pinctrl_register()`. Runtime pinctrl calls then enumerate groups/functions from SoC data. A mux request validates the group's alternate setting, optionally enters the ALT-C glitch-avoidance sequence, enables each GPIO bank clock, lazily masks disabled IRQs, writes AFSLA/AFSLB, updates PRCM ALT-Cx bits when needed, and restores sleep registers.

## State and persistence behavior
The driver mutates hardware GPIO registers for mux, pull, direction, output, low-EMI, and sleep behavior. It also mutates shadow fields in `struct nmk_gpio_chip`, including `pull_up`, `lowemi`, and interrupt masks. PRCM GPIOCR writes persist outside the GPIO bank block. Suspend/resume delegates to `pinctrl_force_sleep()` and `pinctrl_force_default()`. The static pinctrl descriptor is reused across probes, so its `pins` and `npins` fields are filled during probe from the selected SoC data.

## Dependencies and integration points
The file depends on Linux pinctrl, pinmux, pinconf, GPIO, IRQ, OF/fwnode, clock, I/O, and platform-driver APIs. Its closest integration is `gpio-nomadik`, which provides bank clocks, register bases, IRQ domains, output helpers, sleep helpers, and bank population. Device-tree bindings use `function`, `groups`, `pins`, `ste,config`, and `ste,*` pin configuration properties.

## Risks
This driver is concurrency and hardware-sequence sensitive. ALT-C transitions temporarily alter sleep-mode state across all banks under `nmk_gpio_slpm_lock`; failure paths must restore clocks and SLPM registers correctly. `find_nmk_gpio_from_pin()` assumes bank-ordered GPIO numbering and can mis-map pins if bank descriptors are sparse or not populated as expected. Device-tree parsing does not reject out-of-range config values strongly; absent `pins`/`groups` properties surface as parse failures. `nmk_pin_config_get()` is unimplemented, so readback through generic pinconf is limited.

## Test signals
Signals include probe ordering with GPIO banks both pre-existing and populated through phandles, pinctrl debugfs group/function listings, muxing plain ALT-A/B/C and DB8500 ALT-Cx groups, GPIO request/free, lazy IRQ masking during mux-to-peripheral, suspend/resume default/sleep states, and dynamic-debug traces around PRCM GPIOCR changes and glitch-safe switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-nomadik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/Kconfig

## Purpose
This Kconfig file declares build-time configuration symbols for Nuvoton pinctrl/GPIO drivers: WPCM450, NPCM7XX, NPCM8XX, the MA35 common core, and MA35D1. It encodes architecture or compile-test constraints and selects the pinctrl, pinmux, pinconf, GPIO, IRQ, and syscon dependencies required by each driver family.

## Important APIs, types, and functions
The relevant symbols are `PINCTRL_WPCM450`, `PINCTRL_NPCM7XX`, `PINCTRL_NPCM8XX`, hidden `PINCTRL_MA35`, and user-visible `PINCTRL_MA35D1`. `PINCTRL_MA35D1` selects `PINCTRL_MA35`, which in turn selects generic pinctrl groups/functions/config, gpiolib, generic GPIO, irqchip support, and `MFD_SYSCON`.

## Control flow
Kconfig has no runtime flow. During configuration, visible symbols are offered when their `depends on` expressions are satisfied. Enabling `PINCTRL_MA35D1` causes the hidden common MA35 symbol to be selected, so the Makefile builds both `pinctrl-ma35.o` and `pinctrl-ma35d1.o`.

## State and persistence behavior
The persistent state is the kernel `.config`. These symbols determine whether driver objects are built in, built as modules where supported, or omitted. `PINCTRL_NPCM7XX`, `PINCTRL_MA35`, and `PINCTRL_MA35D1` are `bool`, so their objects are built-in when enabled; WPCM450 and NPCM8XX are `tristate`.

## Dependencies and integration points
The file integrates with `drivers/pinctrl/nuvoton/Makefile` via `obj-$(CONFIG_...)` entries. It depends on architecture symbols such as `ARCH_WPCM450`, `ARCH_NPCM7XX`, `ARCH_NPCM`, and `ARCH_MA35`, while allowing broader compile coverage through `COMPILE_TEST`. All entries require OF.

## Risks
Incorrect `select` lines can produce link failures or drivers without required framework support. The hidden `PINCTRL_MA35` split is important: enabling only the SoC wrapper without the common core would fail to link `ma35_pinctrl_probe()` and PM helpers. Bool-only choices prevent module builds for some drivers, so changing symbol type affects initialization timing and module ABI.

## Test signals
Validation is mostly build-matrix based: compile with each architecture symbol, with `COMPILE_TEST`, and with combinations of built-in/tristate drivers. For MA35D1, confirm that selecting `PINCTRL_MA35D1` also builds the common MA35 object and satisfies syscon, generic pinconf, gpiolib, and irqchip dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/Makefile

## Purpose
This Makefile maps Nuvoton pinctrl Kconfig symbols to their corresponding object files. It is the build glue that includes family-specific and common pinctrl drivers in the kernel build.

## Important APIs, types, and functions
The key entries are `obj-$(CONFIG_PINCTRL_WPCM450) += pinctrl-wpcm450.o`, `obj-$(CONFIG_PINCTRL_NPCM7XX) += pinctrl-npcm7xx.o`, `obj-$(CONFIG_PINCTRL_NPCM8XX) += pinctrl-npcm8xx.o`, `obj-$(CONFIG_PINCTRL_MA35) += pinctrl-ma35.o`, and `obj-$(CONFIG_PINCTRL_MA35D1) += pinctrl-ma35d1.o`.

## Control flow
There is no runtime control flow. Kbuild expands each `obj-$(CONFIG_...)` according to the configured symbol value. For MA35D1, the Kconfig relationship causes both the common `pinctrl-ma35.o` and SoC-specific `pinctrl-ma35d1.o` objects to be included when MA35D1 support is enabled.

## State and persistence behavior
The Makefile does not store runtime state. Its persistent effect is in build artifacts: enabled objects become built-in or module objects according to their Kconfig symbol type and value. Since `PINCTRL_MA35` and `PINCTRL_MA35D1` are bools, the MA35 objects are built-in rather than modules.

## Dependencies and integration points
This file integrates with the local Kconfig and with the wider Linux Kbuild system. The object names correspond directly to source files in the same directory. It is especially coupled to the MA35 split, where `pinctrl-ma35d1.c` calls functions implemented in `pinctrl-ma35.c`.

## Risks
The main risk is symbol/object drift. If Kconfig selects a symbol but the Makefile omits the object, probe entry points or common helpers will be missing. If an object is tied to the wrong symbol, unrelated platforms may build unused code or fail when dependencies are absent. The MA35 common object must stay tied to the hidden common symbol rather than only the MA35D1 wrapper if additional MA35 variants are added.

## Test signals
Run Kbuild with each Nuvoton config enabled and disabled. For MA35D1, link validation should prove that `ma35_pinctrl_probe()`, `ma35_pinctrl_suspend()`, and `ma35_pinctrl_resume()` resolve from `pinctrl-ma35.o` when `pinctrl-ma35d1.o` is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35.c

## Purpose
This is the common MA35 pinctrl, pinmux, pinconf, GPIO, and GPIO-IRQ implementation. SoC-specific files provide pin descriptors and an MFP offset/shift to pin-number decoder; this file parses device-tree function/group nodes, programs shared multi-function pin registers through a syscon regmap, registers per-bank GPIO chips, and implements generic pin configuration for pulls, drive strength, Schmitt trigger, slew rate, output enable, and power source.

## Important APIs, types, and functions
The exported entry points are `ma35_pinctrl_probe()`, `ma35_pinctrl_suspend()`, and `ma35_pinctrl_resume()`. Important internal types are `struct ma35_pinctrl`, `struct ma35_pin_ctrl`, `struct ma35_pin_bank`, and `struct ma35_pin_setting`. Key callbacks include `ma35_pinctrl_dt_node_to_map_func()`, `ma35_pinmux_set_mux()`, GPIO direction/get/set/request helpers, IRQ helpers `ma35_irq_gpio_ack/mask/unmask/irqtype()` and `ma35_irq_demux_intgroup()`, and pinconf helpers for pull, drive, Schmitt, slew, output, and power source.

## Control flow
`ma35_pinctrl_probe()` validates SoC info, allocates controller state and a pinctrl descriptor, obtains the system-controller regmap from the `nuvoton,sys` phandle, discovers GPIO child nodes, parses non-GPIO child nodes into functions and groups, registers and enables pinctrl, then registers each valid GPIO bank. A mux request walks the selected group's `ma35_pin_setting` entries and writes each 4-bit MFP field. A GPIO request clears that pin's MFP field to GPIO mode. IRQ flow reads a bank `INTSRC`, dispatches set bits through the gpio irq domain, and acknowledges by writing the source bit.

## State and persistence behavior
Runtime state includes parsed group/function arrays, per-bank register bases, clocks, IRQ numbers, irq type/enable shadows, and the shared syscon regmap. Hardware state persists in MFP registers, GPIO mode/output/pull/drive/slew/Schmitt/power registers, and GPIO interrupt registers. Clocks are prepared and enabled for valid banks during discovery and remain enabled for GPIO/pinctrl operation. Suspend/resume forces pinctrl sleep/default states.

## Dependencies and integration points
The driver depends on Linux pinctrl/pinmux/pinconf, generic pinconf DT parsing, gpiolib, gpio irqchip helpers, IRQ core, clocks, OF/fwnode, syscon/regmap, and MMIO. Device tree supplies GPIO bank child nodes and function/group nodes with `nuvoton,pins` triples of MFP register index, port shift, and mux value. It integrates with SoC data through `struct ma35_pinctrl_soc_info`.

## Risks
There are several correctness risks. `ma35_pinctrl_parse_functions()` uses a static `grp_index`, which is safe for a single probe path but would be fragile if multiple MA35 controllers probed in one boot. `ma35_pinctrl_dt_node_to_map_func()` can leak the parent reference on the `of_get_parent()` error path after allocating maps. GPIO child discovery increments `id` without checking against `MA35_GPIO_BANK_MAX`. Pinconf helpers assume valid bank register bases derived from global pin numbers. IRQ type handling maps level-high/level-low to `handle_edge_irq`, which deserves hardware validation.

## Test signals
Test with MA35D1 device trees that define GPIO children and multiple function nodes. Verify pinctrl debugfs functions/groups, mux writes to syscon MFP registers, GPIO request fallback to mux value 0, GPIO direction/output/input paths, interrupt rising/falling/both behavior, generic pinconf read/write for pulls, drive strengths at 1.8 V and 3.3 V, Schmitt, slew, power source, and suspend/resume state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35.h

## Purpose
This header defines the small contract between MA35 SoC-specific pin-table files and the common MA35 pinctrl implementation. It provides data structures and macros for declaring pins, their MFP register location, and their possible mux values, plus prototypes for the shared probe and PM helpers.

## Important APIs, types, and functions
`struct ma35_mux_desc` names one mux value. `struct ma35_pin_data` records the MFP register `offset`, field `shift`, and a null-terminated array of mux descriptors for one pin. `struct ma35_pinctrl_soc_info` carries a SoC pin table, pin count, and `get_pin_num()` callback. `MA35_PIN()` builds a `struct pinctrl_pin_desc` with compound-literal driver data, and `MA35_MUX()` builds one mux descriptor. The declared functions are `ma35_pinctrl_probe()`, `ma35_pinctrl_suspend()`, and `ma35_pinctrl_resume()`.

## Control flow
The header has no executable flow. At compile time, `MA35_PIN()` expands SoC data into pinctrl descriptors. At runtime, the common driver receives a `ma35_pinctrl_soc_info`, publishes the descriptors to pinctrl core, and uses the SoC `get_pin_num()` callback to translate device-tree MFP offset/shift triples back to pin numbers.

## State and persistence behavior
The macro-created pin and mux descriptors are static immutable SoC data. The `drv_data` field points at compound-literal `struct ma35_pin_data` storage associated with each descriptor. Persistent hardware state is not changed by the header itself; register writes happen in `pinctrl-ma35.c`.

## Dependencies and integration points
It includes generic pinconf, pinmux, and platform-device headers. It is included by `pinctrl-ma35.c` and `pinctrl-ma35d1.c`. The macro format is coupled to the common driver's expectation that each pin has a register offset, bit shift, and mux metadata, even though current mux programming is driven by device-tree triples rather than by searching the per-pin mux list.

## Risks
Macro misuse is the main risk. The `MA35_PIN()` compound literals must remain valid for static descriptor lifetime; using the macro in automatic storage would be unsafe. The `get_pin_num()` callback must match the SoC's MFP register layout, or parsed groups will refer to the wrong pinctrl pin numbers. Mux descriptor names are useful documentation and potential debug data, but they do not independently validate device-tree mux values.

## Test signals
Build tests catch prototype and macro syntax drift. Runtime pinctrl debugfs output should show the SoC pin names from `MA35_PIN()`. Device-tree group parsing that maps MFP offset/shift triples to expected pin names validates the `ma35_pinctrl_soc_info` contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35d1.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35d1.c

## Purpose
This file is the MA35D1 SoC-specific pin table and platform-driver wrapper for the common MA35 pinctrl implementation. It enumerates 224 pin descriptors from PA0 through PN15-style ports, records each pin's MFP register offset and bit shift, documents available mux values, supplies the MA35D1 MFP-to-pin-number decoder, and registers the `nuvoton,ma35d1-pinctrl` platform driver.

## Important APIs, types, and functions
The central data is `ma35d1_pins[]`, built with `MA35_PIN()` and `MA35_MUX()` entries. `ma35d1_get_pin_num()` converts an MFP register offset and shift to a linear pin number using `(offset - 0x80) * 2 + shift / 4`. `ma35d1_pinctrl_info` packages the pin table and decoder for the common driver. `ma35d1_pinctrl_probe()` calls `ma35_pinctrl_probe()`. The platform driver uses `ma35d1_pinctrl_of_match`, `DEFINE_NOIRQ_DEV_PM_OPS()`, and `arch_initcall()`.

## Control flow
At architecture init time, `ma35d1_pinctrl_init()` registers the platform driver. OF matching on `nuvoton,ma35d1-pinctrl` calls `ma35d1_pinctrl_probe()`, which delegates all real setup to the common MA35 driver with `ma35d1_pinctrl_info`. Runtime muxing and GPIO handling are then controlled by `pinctrl-ma35.c`; this file only supplies descriptor data and PM callback wiring.

## State and persistence behavior
The SoC pin table and mux descriptors are immutable. The platform driver's runtime state is allocated by the common probe. Hardware persistence happens when common code writes MFP and GPIO registers. The file's initcall choice makes the driver built-in and registered early, consistent with `PINCTRL_MA35D1` being a bool symbol.

## Dependencies and integration points
The file depends on platform-driver, module metadata, PM, pinctrl descriptors, and the local MA35 header. It integrates with device-tree binding data and the common MA35 parser: `nuvoton,pins` triples must use offsets and shifts compatible with `ma35d1_get_pin_num()`. The descriptors cover GPIO, UART, I2C, CAN, SPI/QSPI, SD/eMMC, EBI, LCM, RGMII/RMII, CCAP, PWM, timers, smartcard, JTAG, tamper, USB host, trace, and interrupt functions.

## Risks
The table is large and hardware-sensitive. Wrong offsets, shifts, mux values, or duplicate/conflicting pin numbers can silently mux the wrong pad. The PN entries include repeated names and offsets across linear pin numbers, reflecting package or function variants; that area deserves datasheet cross-checking. Because device-tree mux values are not validated against the `MA35_MUX()` list in common code, an invalid but in-range value could still be written. The decoder formula assumes the MA35D1 MFP block remains a simple 8-byte-per-bank, 4-bit-per-pin layout from base `0x80`.

## Test signals
Build and link with `CONFIG_PINCTRL_MA35D1`, confirm `arch_initcall` registration and OF probe, inspect pinctrl debugfs for all expected pin names, validate representative mux groups across every port bank, test GPIO fallback on each bank, exercise high-value peripherals such as UART0, SD/eMMC, Ethernet RGMII/RMII, LCM, and QSPI, and compare register writes against the MA35D1 datasheet for selected pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/nuvoton/pinctrl-ma35d1.c -->
