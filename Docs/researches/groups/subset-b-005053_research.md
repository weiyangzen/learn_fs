# Research Report: subset-b-005053

This grouped report covers Intel Sunrisepoint/Tangier/Tiger Lake pinctrl files and MediaTek/Airoha pinctrl, GPIO, and external interrupt support files. Each section is delimited for reconciliation into the requested source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-sunrisepoint.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-sunrisepoint.c

Purpose: Provides the Intel Sunrisepoint PCH pinctrl/GPIO SoC descriptions for Sunrisepoint-LP and Sunrisepoint-H. The file is mostly immutable platform data consumed by the shared Intel pinctrl core, with ACPI IDs selecting the correct SoC table at probe.

Important APIs/types/functions: The main data objects are `sptlp_pins`, `sptlp_groups`, `sptlp_functions`, `sptlp_communities`, `sptlp_soc_data`, and the corresponding `spth_*` tables. `SPT_H_COMMUNITY()` and `SPT_LP_COMMUNITY()` wrap Intel community macros with Sunrisepoint register offsets for ownership, pad locks, host/software ownership, interrupt status, and interrupt enable. The platform driver uses `intel_pinctrl_probe_by_hid`, `intel_pinctrl_pm_ops`, `subsys_initcall(spt_pinctrl_init)`, and `module_exit`.

Control flow: ACPI matches `INT344B` to LP data and `INT3451`/`INT345D` to H data. Probe is delegated entirely to the shared Intel driver, which interprets the pin descriptors, groups, functions, and communities to register pinctrl/GPIO/IRQ services. Runtime muxing and GPIO access happen in `pinctrl-intel.c`, not here.

State and persistence: This file owns no mutable runtime state. Register offsets and pin/community topology become persistent hardware state only when the shared Intel core programs pad configuration, ownership, interrupt, or wake registers. Suspend/resume state handling is delegated through `intel_pinctrl_pm_ops`.

Dependencies and integration points: Depends on Linux platform, ACPI match, PM, and pinctrl APIs plus local `pinctrl-intel.h`. It integrates with ACPI-enumerated PCH devices and the Intel pinctrl namespace imported as `PINCTRL_INTEL`.

Risks: Most defects are table defects: wrong pin numbers, group membership, mux mode values, GPIO base mapping, or community pad ranges silently misroute GPIOs or interrupts. There are suspicious copied group mappings where `sptlp_spi1_groups` and `spth_spi1_groups` point at `"spi0_grp"`, and UART2 pin arrays repeat pin 71 instead of including pin 70; those may be inherited quirks but are test-worthy. Community ranges must match hardware register layout because the core derives MMIO offsets from them.

Test signals: Build with Sunrisepoint support, ACPI probe on LP and H systems, `debugfs` pinctrl enumeration, GPIO line naming/counts, SPI/I2C/UART/eMMC/SD mux selection, GPIO interrupt delivery, wake from suspend, and suspend/resume register restoration through the shared Intel PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-sunrisepoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tangier.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tangier.c

Purpose: Implements the common Intel Tangier pinctrl driver used by Tangier-family platform data. Unlike the Sunrisepoint/Tiger Lake files, this file contains active pinctrl, pinmux, pinconf, and probe logic for a family-based MMIO layout.

Important APIs/types/functions: Public entry is `devm_tng_pinctrl_probe()`, exported in namespace `PINCTRL_TANGIER`. Helper functions include `tng_get_family()`, `tng_buf_available()`, `tng_get_bufcfg()`, `tng_read_bufcfg()`, and `tng_update_bufcfg()`. Pinctrl callbacks are collected in `tng_pinctrl_ops`; pinmux callbacks in `tng_pinmux_ops`; pinconf callbacks in `tng_pinconf_ops`. BUFCFG bit definitions cover pin mode, pull enable/value, slew, input/output override, and open drain.

Control flow: Probe reads `device_get_match_data()`, duplicates static `struct tng_pinctrl` and family tables, maps BAR 0 once, splices each family to `regs + barno * TNG_FAMILY_LEN`, builds a `pinctrl_desc`, and registers with `devm_pinctrl_register()`. Pinctrl core callbacks then enumerate groups/functions, set mux modes by writing `BUFCFG_PINMODE_MASK`, force GPIO mode from `gpio_request_enable`, and get/set pin or group configs.

State and persistence: Runtime state is `struct tng_pinctrl`: device pointer, raw spinlock, registered pinctrl device, and copied family records with MMIO pointers. Hardware state persists in BUFCFG registers. Protected families are treated as unavailable and return `-EBUSY`/`-ENOTSUPP`, leaving firmware-owned pins untouched.

Dependencies and integration points: Uses generic pinctrl, pinmux, and pinconf APIs, `pinctrl-intel.h` data structures, local `pinctrl-tangier.h`, and platform resources. The source is a reusable implementation; SoC-specific Tangier files provide match data, pins, groups, functions, and family descriptors.

Risks: `tng_read_bufcfg()` assumes `tng_get_bufcfg()` succeeds after `tng_buf_available()`; keeping family data coherent is therefore required. The driver serializes read-modify-write register updates with a raw spinlock, but availability checks happen before the lock and depend on static family protection state. Pinconf supports only bias disable/up/down, push-pull/open-drain, and slew rate; unsupported generic properties must be rejected by tests. Pull strength accepts only 910, 2000, 20000/default, and 50000 ohms.

Test signals: Compile/link users of `devm_tng_pinctrl_probe`, platform probe with valid match data, debugfs pin dumps, protected-family access returning busy/unsupported, mux switching for every group, GPIO request forcing mode 0, pinconf get/set for supported pull/open-drain/slew cases, and group config propagation across all pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tangier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tangier.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tangier.h

Purpose: Defines the public data contract for Intel Tangier pinctrl platform data and declares the reusable probe entry implemented in `pinctrl-tangier.c`.

Important APIs/types/functions: Defines `TNG_FAMILY_NR`, `TNG_FAMILY_LEN`, `struct tng_family`, `TNG_FAMILY()`, `TNG_FAMILY_PROTECTED()`, `struct tng_pinctrl`, and `devm_tng_pinctrl_probe()`. `struct tng_family` maps pin ranges to MMIO family slots and can mark a family protected. `struct tng_pinctrl` packages the pinctrl descriptor, functions, groups, pins, and family list consumed by the probe helper.

Control flow: The header has no executable path. SoC-specific files instantiate const `struct tng_pinctrl` objects and expose them as match data. `devm_tng_pinctrl_probe()` duplicates that data, fills runtime MMIO fields, and registers the pin controller.

State and persistence: No direct mutable state exists in the header. Its structures define which state the implementation persists at runtime: copied family records with `regs`, a raw spinlock, and the registered `pinctrl_dev`. The protected bit is part of the persistent platform policy for inaccessible pin families.

Dependencies and integration points: Includes pinctrl core types and Intel shared group/function definitions from `pinctrl-intel.h`. It is the boundary between Tangier SoC data files and the common Tangier implementation.

Risks: The constants encode the MMIO family stride; an incorrect `TNG_FAMILY_LEN` or `barno` in users would make all register accesses land in the wrong window. Family ranges must be non-overlapping and cover every advertised pin that can be touched by groups. Protected families must be set for firmware-owned banks or the driver can attempt illegal MMIO operations.

Test signals: Build all Tangier SoC users, inspect match data for family coverage, probe on hardware or emulation, and verify protected families are reported as unavailable through debugfs and pinconf/pinmux operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tangier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tigerlake.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tigerlake.c

Purpose: Supplies Intel Tiger Lake-LP and Tiger Lake-H PCH pinctrl/GPIO topology to the shared Intel pinctrl core. It maps ACPI IDs to SoC data containing pin descriptors and GPIO community/pad-group layouts.

Important APIs/types/functions: Main objects are `tgllp_pins`, `tgllp_communities`, `tgllp_soc_data`, `tglh_pins`, `tglh_communities`, and `tglh_soc_data`. `TGL_LP_COMMUNITY()` and `TGL_H_COMMUNITY()` bind per-generation register offsets for pad ownership, pad config locks, host/software ownership, GPI status, and GPI enable. The platform driver is registered via `module_platform_driver(tgl_pinctrl_driver)`.

Control flow: ACPI IDs `INT34C5` and `INTC1055` select Tiger Lake-LP data; `INT34C6` selects Tiger Lake-H data. Probe is delegated to `intel_pinctrl_probe_by_hid`, which uses the selected community definitions to register pinctrl, GPIO, interrupt, and PM behavior.

State and persistence: The file is static data only. Hardware state is managed by the shared Intel core: pad mux/config, GPIO ownership, interrupt masks/status, and wake state. The HVCMOS, JTAG, and SPI pad groups with `INTEL_GPIO_BASE_NOMAP` are intentionally not exported as normal GPIO ranges.

Dependencies and integration points: Depends on Linux module/platform/PM/pinctrl APIs and `pinctrl-intel.h`. Integrates with ACPI-enumerated Intel PCH devices and imports `PINCTRL_INTEL`.

Risks: This file has no active logic, so correctness depends on exact pin numbering and pad-group GPIO bases. LP and H variants have different group ordering and community splits; an off-by-one range or wrong GPIO base can break interrupt routing or expose non-GPIO pads. Virtual GPIO and non-mapped pad groups need careful validation because the shared core treats them differently.

Test signals: Kernel build, ACPI probe for all listed IDs, `debugfs` pinctrl pin/group listings, GPIO line count and names, GPIO interrupt and wake tests, suspend/resume state preservation, and real board validation for LP and H pin banks including non-mapped HVCMOS/JTAG/SPI groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tigerlake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/Kconfig

Purpose: Defines the MediaTek, Airoha, and legacy Ralink pinctrl Kconfig menu. It selects the correct common pinctrl framework layers, GPIO support, external interrupt support, and SoC-specific drivers.

Important APIs/types/functions: Key symbols include `EINT_MTK`, `PINCTRL_MTK`, `PINCTRL_MTK_V2`, `PINCTRL_MTK_MTMIPS`, `PINCTRL_MTK_MOORE`, `PINCTRL_MTK_PARIS`, `PINCTRL_AIROHA`, many SoC options such as `PINCTRL_MT2701`, `PINCTRL_MT2712`, `PINCTRL_MT7988`, `PINCTRL_MT8196`, and PMIC `PINCTRL_MT6397`. `select` lines wire shared support such as `PINMUX`, `GENERIC_PINCONF`, `GPIOLIB`, `IRQ_DOMAIN`, `GPIOLIB_IRQCHIP`, and `REGMAP_MMIO`.

Control flow: Kconfig resolution determines which objects the Makefile builds. Older ARMv7/PMIC drivers select `PINCTRL_MTK`; Moore binding drivers select `PINCTRL_MTK_MOORE`; newer Paris binding drivers select `PINCTRL_MTK_PARIS`; MIPS/Ralink drivers select `PINCTRL_MTK_MTMIPS`; Airoha builds a standalone tristate driver.

State and persistence: No runtime state. It persists build-time dependency policy and default enablement, such as defaulting many ARM64 MediaTek SoC drivers when `ARCH_MEDIATEK` is enabled and defaulting PMIC pinctrl with `MFD_MT6397`.

Dependencies and integration points: Sourced by the parent pinctrl Kconfig. It must remain synchronized with `drivers/pinctrl/mediatek/Makefile`, SoC driver filenames, and common helper availability.

Risks: Incorrect `select` relationships cause build failures or missing runtime capabilities such as GPIO-to-IRQ translation. Broad `COMPILE_TEST` paths must still select all helper libraries. `EINT_MTK` defaults differ for `PINCTRL_MTK_PARIS` versus older bool symbols; regressions here can silently remove debounce/wake IRQ support.

Test signals: `allyesconfig`, `allmodconfig`, MediaTek ARM/ARM64 defconfigs, Ralink configs, PMIC configs, and targeted `COMPILE_TEST` builds for each family. Validate generated `.config` includes expected common helpers when a SoC driver is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/Makefile

Purpose: Maps MediaTek/Airoha/Ralink pinctrl Kconfig symbols to object files. It is the build glue between the Kconfig menu and the individual common or SoC-specific driver sources.

Important APIs/types/functions: Core objects are `mtk-eint.o`, `pinctrl-mtk-common.o`, `pinctrl-mtk-common-v2.o`, `pinctrl-mtmips.o`, `pinctrl-moore.o`, and `pinctrl-paris.o`. SoC objects include `pinctrl-airoha.o`, legacy Ralink/MT762x files, ARMv7 files such as `pinctrl-mt2701.o`, ARM64 files such as `pinctrl-mt2712.o`, `pinctrl-mt8189.o`, `pinctrl-mt8196.o`, and PMIC `pinctrl-mt6397.o`.

Control flow: Kbuild evaluates `obj-$(CONFIG_...)` assignments and links selected objects built-in or as modules according to the symbol type. Common framework objects are selected by Kconfig and built before SoC objects that reference their exported helpers.

State and persistence: No runtime state. The file persists build membership and must reflect every Kconfig option and source filename.

Dependencies and integration points: Tightly coupled to `Kconfig`, common headers, and SoC source files. If a driver selects `PINCTRL_MTK_MOORE`, both `pinctrl-moore.o` and `pinctrl-mtk-common-v2.o` must be present for symbols to resolve.

Risks: Missing or misspelled object entries cause selected drivers to disappear or fail link. Tristate/common-helper combinations are especially sensitive because helpers may need to be linked in the same module/built-in mode as users. Formatting drift, such as the spaced `PINCTRL_MT8189` line, is low risk but worth normalizing only in separate cleanup.

Test signals: `make drivers/pinctrl/mediatek/`, `modpost` symbol checks, build matrix for built-in and module variants, and comparing Kconfig symbols against Makefile object entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/mtk-eint.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/mtk-eint.c

Purpose: Implements the reusable MediaTek external interrupt controller library used by multiple pinctrl drivers. It creates an irqdomain for EINT lines, translates EINTs to GPIOs through pinctrl callbacks, handles masking/type/wake/debounce, and dispatches chained parent IRQs.

Important APIs/types/functions: Public exports are `mtk_eint_do_init()`, `mtk_eint_do_suspend()`, `mtk_eint_do_resume()`, `mtk_eint_set_debounce()`, `mtk_eint_find_irq()`, and debounce tables for several SoCs. Core internals include `mtk_eint_irq_chip`, `mtk_eint_irq_handler()`, `mtk_eint_set_type()`, `mtk_eint_flip_edge()`, `mtk_eint_chip_write_mask()`, and `mtk_eint_hw_init()`.

Control flow: Initialization fills default register offsets, allocates per-instance pin lists plus wake/current masks, creates a linear irqdomain, initializes hardware by enabling AP domain and masking all EINTs, maps each EINT to a Linux IRQ, installs `handle_level_irq`, and attaches a chained parent handler. IRQ handling walks each instance and port status register, maps the status bit back to an EINT number, optionally masks wake-only lines, dispatches `generic_handle_domain_irq()`, emulates dual-edge by flipping polarity and raising a software interrupt if a transition was missed, and resets debounce counters.

State and persistence: Runtime state lives in `struct mtk_eint`: MMIO bases, pin metadata, irqdomain, parent IRQ, per-instance `pin_list`, `wake_mask`, `cur_mask`, debounce table count, register layout, and GPIO translation hooks. Suspend writes wake masks into hardware; resume restores current masks. Debounce configuration persists in EINT debounce registers.

Dependencies and integration points: Uses Linux irqdomain/chained IRQ/GPIO APIs and `struct mtk_eint_xt` callbacks supplied by pinctrl implementations. SoC drivers provide `mtk_eint_hw` sizing and optional explicit `mtk_eint_pin` maps.

Risks: Dual-edge emulation depends on stable GPIO reads while polarity is flipped. `mtk_eint_set_debounce()` assumes an existing IRQ mapping and valid irq_data; invalid EINT numbers or unmapped lines can be hazardous. Wake/current mask semantics are inverted through `mask_set`/`mask_clr`, so regressions easily break suspend wake. The optional explicit pin map must not exceed `nbase` and must have indexes that fit allocated `pin_list` arrays.

Test signals: GPIO-to-IRQ conversion, rising/falling/both-edge interrupts, level-high/low interrupts, wake from suspend, debounce programming with each SoC table, invalid type rejection, wake-only interrupt masking, and stress tests around fast edge changes that exercise software re-triggering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/mtk-eint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/mtk-eint.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/mtk-eint.h

Purpose: Defines the public MediaTek EINT data structures, SoC hardware descriptors, pin maps, pinctrl callback interface, exported debounce tables, and optional stubs when `CONFIG_EINT_MTK` is disabled.

Important APIs/types/functions: Important types are `struct mtk_eint_regs`, `struct mtk_eint_hw`, `struct mtk_eint_pin`, `struct mtk_eint_xt`, and `struct mtk_eint`. Function prototypes mirror the implementation exports: initialization, suspend/resume, debounce setting, and IRQ lookup. When EINT support is disabled, inline stubs return `-EOPNOTSUPP`.

Control flow: The header itself has none. Pinctrl drivers allocate/fill `struct mtk_eint`, attach `gpio_xlate` callbacks, provide register bases and hardware metadata, then call `mtk_eint_do_init()`. GPIO chips later call `mtk_eint_find_irq()` and `mtk_eint_set_debounce()`.

State and persistence: Declares all persistent EINT state: base pointers, per-base pin counts, irqdomain, wake/current masks, dual-edge flags, pin list lookup arrays, register layout, SoC debounce timings, and callback linkage to the pinctrl instance.

Dependencies and integration points: Depends on `linux/irqdomain.h` and GPIO/pinctrl consumers through opaque callback signatures. Integrated by old common MediaTek pinctrl, Moore/Paris variants, and SoC drivers that expose GPIO interrupt support.

Risks: Structure layout is a cross-file contract. `u16` pin numbers and base counts must be large enough for SoC descriptors. Callback correctness is critical: `get_gpio_n`, `get_gpio_state`, and `set_gpio_as_eint` are invoked while requesting IRQ resources and during dual-edge handling. Stub behavior means drivers must tolerate absent EINT support.

Test signals: Compile with `CONFIG_EINT_MTK=y/m/n`, build all users, validate callbacks are populated before init, and run GPIO IRQ/debounce/wake tests on drivers that include EINT hardware data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/mtk-eint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-airoha.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-airoha.c

Purpose: Implements a standalone Airoha EN7581/AN7583 pinctrl, pinmux, pinconf, GPIO, and GPIO IRQ driver. It combines SoC-specific pin/group/function/config tables with regmap-backed runtime operations.

Important APIs/types/functions: Key structures include `airoha_pinctrl`, `airoha_pinctrl_match_data`, `airoha_pinctrl_func`, `airoha_pinctrl_func_group`, `airoha_pinctrl_gpiochip`, and `airoha_pinctrl_conf`. Runtime entry points include `airoha_pinctrl_probe()`, `airoha_pinctrl_add_gpiochip()`, `airoha_pinmux_set_mux()`, `airoha_pinmux_set_direction()`, `airoha_pinconf_get()`, `airoha_pinconf_set()`, `airoha_irq_unmask()`, `airoha_irq_mask()`, `airoha_irq_type()`, and `airoha_irq_handler()`.

Control flow: Probe obtains the parent MMIO regmap, looks up the chip SCU syscon, registers pinctrl, adds all SoC groups/functions, stores config tables, enables pinctrl, and registers a gpiochip with IRQ support. Pinmux selects a matching function/group descriptor and writes one or two register updates, using the GPIO regmap for PWM mode registers and the chip SCU regmap for regular mux/LED maps. GPIO direction updates output-enable and two-bit direction registers. IRQ setup requests the parent IRQ, stores per-line type, programs edge/level registers when unmasked, reads status banks in the handler, dispatches mapped child IRQs, and clears status bits.

State and persistence: Persistent runtime state includes two regmaps, registered pinctrl device, selected SoC tables, gpiochip, and per-GPIO `irq_type`. Hardware state persists in SCU mux/config registers, GPIO data/OE/direction registers, IRQ edge/level/status registers, pull-up/down bits, drive E2/E4 bits, and PCIe reset open-drain bits.

Dependencies and integration points: Uses generic pinctrl/pinmux/pinconf helpers, GPIO library, IRQ domain support through `gpio_irq_chip`, `syscon_regmap_lookup_by_compatible("airoha,en7581-chip-scu")`, and DT compatibles `airoha,en7581-pinctrl` and `airoha,an7583-pinctrl`. Kconfig selects `REGMAP_MMIO`, `GPIOLIB_IRQCHIP`, and generic pinctrl helpers.

Risks: SoC tables are large and sparse; group names must match function group names exactly or mux selection returns `-EINVAL`. `gpio_chip.ngpio` is fixed at 64 while pin descriptors are sparse and SoC-specific, so gpio-ranges and pin offsets need hardware validation. The pinconf bias get logic appears suspicious: after a valid pull-up or pull-down state passes the matching check, the trailing `else if (pull_up || pull_down)` still rejects it, which can make `PIN_CONFIG_BIAS_PULL_UP` and `PIN_CONFIG_BIAS_PULL_DOWN` reads fail. Config setters ignore return values from individual SCU updates in several cases, so a missing pin config entry can be hidden. IRQ masking uses edge/level enable clearing, but `irq_mask_ack` only masks and does not explicitly clear status.

Test signals: Probe both compatibles, verify syscon lookup and parent regmap availability, enumerate groups/functions in debugfs, mux UART/I2C/SPI/PCM/eMMC/PNAND/PWM/LED/PCIe reset functions, validate pull/drive/open-drain get and set per pin, GPIO input/output for both 32-pin banks, IRQ rising/falling/both/level operation, shared parent IRQ behavior, and DT gpio-ranges for sparse pin numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-airoha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-moore.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-moore.c

Purpose: Implements the MediaTek "Moore" generic DeviceTree binding pinctrl framework. It registers generic pin groups/functions from SoC tables, provides mux and pinconf operations, builds a GPIO chip, and optionally attaches the common MediaTek EINT library.

Important APIs/types/functions: Public entry is `mtk_moore_pinctrl_probe()`. Runtime callbacks include `mtk_pinmux_set_mux()`, `mtk_pinmux_gpio_request_enable()`, `mtk_pinmux_gpio_set_direction()`, `mtk_pinconf_get()`, `mtk_pinconf_set()`, group config helpers, `mtk_gpio_get()`, `mtk_gpio_set()`, `mtk_gpio_to_irq()`, and `mtk_gpio_set_config()`. Custom DT pinconf parameters are `mediatek,tdsel`, `mediatek,rdsel`, `mediatek,pull-up-adv`, and `mediatek,pull-down-adv`.

Control flow: Probe maps all named register bases from `soc->base_names`, copies pin descriptors, registers pinctrl without enabling it, adds generic groups/functions from SoC data, enables pinctrl so hogs can be claimed, tries to build EINT support, then registers the gpiochip. Mux setting iterates pins in a group and writes per-pin modes from group data. Pinconf get/set dispatches to common-v2 helpers and SoC callbacks for bias, drive strength, advanced pull, TDSEL/RDSEL, direction, level, and Schmitt input.

State and persistence: Runtime state lives in `struct mtk_pinctrl`: mapped bases, SoC data, spinlock, pinctrl device, optional EINT state, and gpiochip. Hardware state persists in SoC register fields reached through `mtk_hw_get_value()`/`mtk_hw_set_value()` and SoC-specific callbacks.

Dependencies and integration points: Depends on `pinctrl-mtk-common-v2.h`, `mtk-eint.h`, generic pinctrl/pinmux functions, GPIO library, and DT pinconf parsing. Moore SoC files provide `struct mtk_pin_soc` tables with pins, groups, functions, register calculators, and EINT metadata.

Risks: Group `data` must be an array of pin modes matching group pin count. Several operations return `-ENOTSUPP` when SoC callbacks are absent, so tables must advertise only supported properties. EINT failure is warning-only, leaving pinctrl/GPIO working but `to_irq` and debounce unavailable. The static `mtk_desc` is mutated at probe time; concurrent probes of multiple Moore instances would need scrutiny.

Test signals: Build all Moore SoC users, probe with and without `gpio-ranges`, DT mux group selection, GPIO direction/value, custom pinconf parsing, drive/bias/Schmitt/TDSEL/RDSEL get-set, EINT to_irq and debounce, and behavior when EINT init fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-moore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-moore.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-moore.h

Purpose: Declares helper macros and the probe API for MediaTek Moore-binding SoC pinctrl drivers.

Important APIs/types/functions: Defines `MTK_RANGE()`, `MTK_PIN()`, `PINCTRL_PIN_GROUP()`, `PINCTRL_PIN_FUNCTION()`, and `mtk_moore_pinctrl_probe()`. `MTK_PIN()` creates `struct mtk_pin_desc` entries with EINT and drive group metadata. Group/function macros bridge SoC table naming conventions to generic pinctrl descriptors.

Control flow: No executable logic. SoC drivers include this header to define pins, groups, functions, register ranges, and then call `mtk_moore_pinctrl_probe()` from their platform probe.

State and persistence: No direct state. The macros determine static SoC table contents that later control muxing, GPIO, EINT, and pinconf behavior.

Dependencies and integration points: Includes core pinctrl, pinmux, pinconf, OF/platform headers, MediaTek EINT, and common-v2 definitions. It is the SoC-data contract consumed by `pinctrl-moore.c`.

Risks: Macro-generated names require strict table naming consistency. Incorrect EINT metadata in `MTK_PIN()` breaks GPIO-to-IRQ translation. Since `funcs` is initialized to `NULL`, SoC files must provide separate group/function mode data where the Moore core expects it.

Test signals: Compile Moore SoC files, inspect generated group/function arrays, probe a Moore SoC, and verify mux modes plus EINT mappings match DeviceTree binding examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-moore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt2701.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt2701.c

Purpose: Provides MT2701/MT7623 pinctrl SoC data for the older MediaTek common pinctrl framework. It supplies drive groups, per-pin drive mappings, special pull-up/down registers, input-enable/Schmitt ranges, special mux bits, register offsets, and EINT hardware sizing.

Important APIs/types/functions: Main data includes `mt2701_drv_grp`, `mt2701_pin_drv`, `mt2701_spec_pupd`, `mt2701_ies_set`, `mt2701_smt_set`, `mt2701_spec_pinmux`, and `mt2701_pinctrl_data`. Local helpers `mt2701_spec_pinmux_set()` and `mt2701_spec_dir_set()` handle extra mux flag bits and direction register addressing for high pins.

Control flow: The platform driver matches `mediatek,mt2701-pinctrl` or `mediatek,mt7623-pinctrl`, passes `mt2701_pinctrl_data` to `mtk_pctrl_common_probe`, and registers at `arch_initcall`. The common framework uses the tables to service pinmux, GPIO, pinconf, EINT, and PM operations.

State and persistence: This file is static data plus two stateless helper callbacks. Hardware state persists in pinmux, direction, pull, drive, IES/SMT, data, and EINT registers as programmed by the common framework.

Dependencies and integration points: Includes `pinctrl-mtk-common.h`, generated `pinctrl-mtk-mt2701.h`, `regmap`, DT binding constants, and MediaTek EINT PM ops. EINT uses `debounce_time_mt2701`, `ap_num=169`, and `db_cnt=16`.

Risks: The per-pin drive and special pull tables are long and hardware-specific; bad offsets or bit positions can damage signal integrity or boot media behavior. `mt2701_spec_pinmux_set()` derives `spec_flag` from mode bit 3 and inverts the register bit when the flag is clear, so mux mode encodings must match hardware expectations. `mt2701_spec_dir_set()` shifts direction registers for pins above 175, which is easy to break with table changes.

Test signals: Build MT2701/MT7623 configs, probe via DT, pinmux for boot media and special pins, pull/drive/IES/SMT get-set, GPIO direction/value for pins above and below 175, EINT mapping/debounce, and suspend/resume through `mtk_eint_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt2701.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt2712.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt2712.c

Purpose: Provides MT2712 pinctrl SoC data for the older MediaTek common framework. It defines special pull-up/down fields, IES/SMT ranges, drive-strength groups, register offsets, and EINT hardware parameters.

Important APIs/types/functions: Core data objects are `mt2712_spec_pupd`, `mt2712_smt_set`, `mt2712_ies_set`, `mt2712_drv_grp`, `mt2712_pin_drv`, and `mt2712_pinctrl_data`. The platform driver matches `mediatek,mt2712-pinctrl` and delegates to `mtk_pctrl_common_probe`.

Control flow: At `arch_initcall`, the platform driver registers. DT match data selects `mt2712_pinctrl_data`; the common framework uses its offsets and callbacks (`mtk_pctrl_spec_pull_set_samereg`, `mtk_pconf_spec_set_ies_smt_range`) to implement mux, GPIO, pinconf, and EINT operations.

State and persistence: The file holds immutable SoC tables. Persistent hardware state is written by the common framework into direction, pull enable/select, data out/in, pinmux, IES/SMT, drive, and EINT registers.

Dependencies and integration points: Depends on `pinctrl-mtk-common.h`, generated `pinctrl-mtk-mt2712.h`, regmap, generic pinconf constants, and `mtk_eint_pm_ops`. EINT metadata advertises `ap_num=229`, `db_cnt=40`, eight ports, and the MT2701 debounce timing table.

Risks: Because MT2712 has many range-based IES/SMT entries and special PUPD fields, overlapping or missing ranges can create subtle input and pull behavior errors. Drive group indexes must match `mt2712_drv_grp`. `type1_start`/`type1_end` and register offsets are global common-framework assumptions and should not be changed without auditing the register calculator.

Test signals: Build and DT probe on MT2712, verify all pins enumerate, run mux tests for representative peripherals, validate pull-up/down and drive strength for special and normal pins, test IES/SMT input behavior, EINT edge/level/debounce/wake, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt2712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6397.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6397.c

Purpose: Provides the MT6397 PMIC pinctrl driver data and probe wrapper. It reuses the older MediaTek common pinctrl framework with the parent PMIC regmap rather than MMIO resources.

Important APIs/types/functions: `mt6397_pinctrl_data` defines pins, register offsets under `MT6397_PIN_REG_BASE`, unsupported IES/SMT offsets, pull/data/mux offsets, port layout, and mux encoding. `mt6397_pinctrl_probe()` obtains the parent `struct mt6397_chip` and calls `mtk_pctrl_init()` with the PMIC regmap.

Control flow: The built-in platform driver matches `mediatek,mt6397-pinctrl`, gets parent driver data, and initializes common pinctrl directly against `mt6397->regmap`. No module init function is needed because `builtin_platform_driver()` registers it.

State and persistence: Runtime state is managed by the common framework and parent MFD regmap. Hardware state persists in PMIC register space for direction, pull enable/select, data out/in, and mux settings. IES and SMT are explicitly unsupported.

Dependencies and integration points: Depends on the MT6397 MFD core, `pinctrl-mtk-common.h`, generated `pinctrl-mtk-mt6397.h`, OF platform matching, and generic pinconf constants. Kconfig ties it to `MFD_MT6397` or `COMPILE_TEST`.

Risks: Parent driver data must be present and must contain a valid regmap. Register offsets are absolute PMIC offsets starting at `0xc000`; a base error affects every pin. Unsupported IES/SMT must be handled cleanly by common pinconf code. Since this is a PMIC pinctrl, probe ordering relative to the MFD parent matters.

Test signals: Build with MT6397 MFD, probe from a PMIC child node, enumerate PMIC pins, set GPIO direction/value through regmap, configure pull and mux modes, confirm IES/SMT return unsupported, and run suspend/resume scenarios that exercise parent regmap availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/mediatek/pinctrl-mt6397.c -->
