# Research: subset-b-005109

This grouped report covers the ten source files assigned to work item `subset-b-005109`. Each section is delimited with the exact source path so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos-arm.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos-arm.c

## Purpose
This file is the ARMv7/S5P/Exynos SoC data layer for the shared Samsung pinctrl, pinmux, pinconf, GPIO, and external interrupt driver. It does not register a platform driver directly. Instead, it exports `samsung_pinctrl_of_match_data` instances consumed by `pinctrl-samsung.c` through the OF match table when `CONFIG_PINCTRL_EXYNOS_ARM` is enabled.

## Important APIs, Types, and Data
The central outputs are `s5pv210_of_data`, `exynos3250_of_data`, `exynos4210_of_data`, `exynos4x12_of_data`, `exynos5250_of_data`, `exynos5260_of_data`, `exynos5410_of_data`, and `exynos5420_of_data`. Each wraps an array of `struct samsung_pin_ctrl`, and each controller points at one or more arrays of `struct samsung_pin_bank_data`. The file uses common Exynos macros from `pinctrl-exynos.h`, especially `EXYNOS_PIN_BANK_EINTG`, `EXYNOS_PIN_BANK_EINTW`, and `EXYNOS_PIN_BANK_EINTN`, to describe GPIO interrupt banks, wakeup interrupt banks, and non-interrupt banks.

It defines two bank register layouts, `bank_type_off` and `bank_type_alive`, covering standard Exynos ARM register fields for function, data, pull, drive, and power-down configuration. S5PV210 is a special case: `s5pv210_pud_value_init()` overrides pull encoding values, and `s5pv210_retention_init()` maps the old clock controller node to provide retention release through `s5pv210_retention_disable()`.

## Control Flow
The source is declarative. At boot, `pinctrl-samsung.c` matches a compatible string such as `samsung,exynos4210-pinctrl`, retrieves the associated exported `*_of_data`, chooses a controller instance by the `pinctrl` OF alias, maps resources, copies bank data into runtime `samsung_pin_bank` objects, and invokes callbacks listed in each `samsung_pin_ctrl`. For controllers that set `.eint_gpio_init` or `.eint_wkup_init`, interrupt domains are initialized in `pinctrl-exynos.c`. For controllers that set `.suspend`, `.resume`, and `.retention_data`, suspend/resume and pad retention are coordinated by the common driver and Exynos callbacks.

## State and Persistence
The source-level state is static `__initconst` data. Runtime state is created by the common driver from these tables. Retention persistence is encoded through `struct samsung_retention_data` tables, including shared PMU refcounting through `exynos_shared_retention_refcnt` for Exynos3250/4/5420 style controllers. S5PV210 persists a mapped clock controller base in retention private data because retention control is not PMU-regmap based on that platform.

## Dependencies and Integration Points
This file depends on `pinctrl-samsung.h` for shared structures, `pinctrl-exynos.h` for Exynos bank macros and callback declarations, and Exynos PMU register definitions from `linux/soc/samsung/exynos-regs-pmu.h`. Integration is through exported `*_of_data` symbols referenced by the Samsung platform driver's OF match table. It also depends on device tree alias ordering: multi-controller SoCs rely on `of_alias_get_id(node, "pinctrl")` matching the order of `samsung_pin_ctrl` entries.

## Risks
The bank arrays often include comments that EINTG banks must start ordered by EINT group number. If a bank is moved out of service-register order, demuxed GPIO interrupts can be routed to the wrong bank. Retention register grouping is SoC-specific and shared across controllers; incorrect `retention_data` or refcount use can leave pads retained or released at the wrong time after suspend. S5PV210 direct clock-controller mapping has a resource lifetime risk because it is obtained outside normal platform resource management.

## Test Signals
Useful test signals are successful probe for each compatible, pinctrl states applying `samsung,pin-function` and config properties, GPIO request/direction/value operations across every bank, EINT GPIO IRQ delivery by service-register group, wakeup IRQ delivery from suspend, and suspend/resume preserving function/pull/drive registers. Device-tree binding checks should verify bank node names and `pinctrl` aliases for every listed controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos-arm64.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos-arm64.c

## Purpose
This file is the ARM64 Exynos-family SoC data layer for the Samsung pinctrl driver. It covers many controllers, including Exynos2200, Exynos5433, Exynos7, Exynos7870, Exynos7885, Exynos850, Exynos8890, Exynos8895, Exynos9610, Exynos9810, Exynos990, ExynosAuto v9/v920, Tesla FSD, Google GS101, and Axis ARTPEC8/9. Like the ARM file, it exports data only; registration and runtime behavior are handled by `pinctrl-samsung.c` and Exynos helper logic in `pinctrl-exynos.c`.

## Important APIs, Types, and Data
The exported symbols are `exynos2200_of_data`, `exynos5433_of_data`, `exynos7_of_data`, `exynos7870_of_data`, `exynos7885_of_data`, `exynos850_of_data`, `exynos8890_of_data`, `exynos8895_of_data`, `exynos9610_of_data`, `exynos9810_of_data`, `exynos990_of_data`, `exynosautov9_of_data`, `exynosautov920_of_data`, `fsd_of_data`, `gs101_of_data`, `artpec8_of_data`, and `artpec9_of_data`. The file defines several register-layout variants: standard `bank_type_off` and `bank_type_alive`, Exynos5433 drive-width variants, Exynos7870 alive layout, Exynos850 4-bit pull/drive layouts, Exynos8895 3-bit drive layouts, and ARTPEC layouts.

The data uses macros from `pinctrl-exynos.h`: generic Exynos macros, Exynos5433 external-resource macros, Exynos7870/850/8895 variants, ExynosAuto v920 macros with explicit EINT control/mask/pend offsets, GS101 macros with filter configuration offsets, and ARTPEC macros. `no_retention_data` intentionally initializes retention control with no registers so the shared Exynos PMU pathway can still provide PMU regmap storage for wakeup mask programming on GS101 and ExynosAuto v920.

## Control Flow
For any matching compatible, the common driver selects the controller by OF alias, maps the main plus any extra memory resources, copies the bank tables, and registers pinctrl/gpio chips. `.eint_gpio_init` creates GPIO interrupt domains; `.eint_wkup_init` creates wakeup interrupt domains. Controllers that set `.suspend` and `.resume` feed Exynos, GS101, or ExynosAuto v920 suspend/resume helpers. GS101 and Exynos9610 banks carry EINT filter offsets used by the Exynos helper when saving/restoring and switching filters.

## State and Persistence
Most data is immutable `__initconst`, but a few arrays are not marked initconst, reflecting data used beyond init on some platforms. Runtime state is copied into devm-managed `samsung_pin_bank` structures. Suspend persistence depends on bank type widths and callbacks in the common driver plus Exynos callbacks. For Exynos5433, retention is split into general, audio, and FSYS/MMC groups. GS101 and ExynosAuto v920 use `no_retention_data` so the Exynos retention initializer still obtains PMU regmap-backed private data for wakeup mask writes, even with no pad-retention registers to release.

## Dependencies and Integration Points
This file depends on the shared Samsung headers, Exynos PMU register definitions, and the OF match table in `pinctrl-samsung.c`. It integrates with device tree compatible strings for Samsung, Google, Tesla, and Axis controllers and assumes `pinctrl` aliases map onto each SoC's controller order. It also integrates with Exynos wakeup interrupt compatible strings handled in `pinctrl-exynos.c`, such as `google,gs101-wakeup-eint` and `samsung,exynosautov920-wakeup-eint`.

## Risks
The largest risk is table drift: bank names, resource indexes, EINT offsets, and alias order must match hardware manuals and device tree bindings. ExynosAuto v920 banks use per-bank EINT register offsets instead of global offsets; mixing those with normal Exynos macros would corrupt interrupt programming. GS101 filter offsets are another fragile integration point because suspend switches wakeup banks to analog filter mode and resume restores digital filtering. Empty retention data is intentional but non-obvious; removing it would break wakeup mask programming that depends on retention private PMU data.

## Test Signals
Strong signals include DT binding validation for all compatibles, boot probe with every `pinctrl` alias, GPIO line naming matching bank-node names, pinmux/pinconf register programming on each bank layout variant, GPIO EINT and wakeup EINT delivery, GS101 wakeup mask writes across three PMU wakeup-mask registers, ExynosAuto v920 IRQ mask/pend/con offset tests, and suspend/resume tests proving pad state and EINT filters are preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos-arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos.c

## Purpose
This file implements Exynos-specific external interrupt, wakeup interrupt, suspend/resume, filter, wakeup-mask, and retention behavior for the Samsung pinctrl driver. It is the active SoC logic used by the declarative ARM and ARM64 data files.

## Important APIs, Types, and Functions
`struct exynos_irq_chip` embeds a Linux `irq_chip` and stores EINT register offsets, wakeup-mask register metadata, and a `set_eint_wakeup_mask` callback. `exynos_eint_gpio_init()` initializes external GPIO interrupt handling for EINT GPIO banks. `exynos_eint_wkup_init()` initializes wakeup interrupt domains and chained handlers. `exynos_pinctrl_suspend()`, `exynos_pinctrl_resume()`, `gs101_pinctrl_suspend()`, `gs101_pinctrl_resume()`, `exynosautov920_pinctrl_suspend()`, and `exynosautov920_pinctrl_resume()` save and restore SoC-specific EINT registers. `exynos_retention_init()` creates PMU-backed retention control.

Core IRQ operations are `exynos_irq_mask()`, `exynos_irq_unmask()`, `exynos_irq_ack()`, `exynos_irq_set_type()`, `exynos_irq_request_resources()`, and `exynos_irq_release_resources()`. Wakeup-mask state is held in static `eint_wake_mask_values[MAX_WAKEUP_REG]` and updated by `exynos_wkup_irq_set_wake()` or `gs101_wkup_irq_set_wake()`.

## Control Flow
During probe, the common driver calls `exynos_eint_gpio_init()` for GPIO EINT-capable controllers. That requests the parent IRQ, creates one linear IRQ domain per GPIO EINT bank, duplicates the default `exynos_gpio_irq_chip`, and stores per-bank save state. When the parent IRQ fires, `exynos_eint_gpio_irq()` reads the Exynos service register, derives the bank group and pin number, then dispatches into the bank IRQ domain.

Wakeup initialization scans child nodes for a compatible wakeup EINT controller, clones the matching wakeup `exynos_irq_chip`, and creates domains for EINT wakeup banks. Banks with per-pin interrupts get chained handlers for EINT0-15 style lines; banks without their own `interrupts` property are collected into a muxed handler that reads pending/mask registers and demuxes all active pins.

IRQ resource request locks the GPIO as IRQ and programs the pin function to `EXYNOS_PIN_CON_FUNC_EINT`; release returns it to input. Set-type selects the hardware trigger encoding and switches the Linux IRQ flow handler between edge and level. Suspend writes wakeup masks and saves GPIO EINT registers; resume restores saved registers and, for GS101, toggles EINT filters between analog suspend mode and digital resume mode.

## State and Persistence
Persistent state includes global wakeup-mask values, per-bank `soc_priv` save data for GPIO EINT registers, runtime IRQ domains, and PMU regmap-backed retention control. Retention enable only increments an optional refcount; retention disable writes configured PMU registers when the final shared user resumes. `exynos_retention_init()` also writes retention release values during initialization so pads start in a usable state.

## Dependencies and Integration Points
The file integrates with gpiolib IRQ resource locking, irqdomain, chained IRQ handlers, the common Samsung bank model, Exynos PMU regmap helpers, and OF child nodes for wakeup EINT controllers. It depends on bank metadata such as `eint_offset`, `eint_con_offset`, `eint_mask_offset`, `eint_pend_offset`, `eint_fltcon_offset`, and `eint_num` supplied by SoC tables.

## Risks
Offset selection is subtle: normal Exynos banks use chip-wide EINT base offsets plus per-bank `eint_offset`, while ExynosAuto banks use per-bank offsets relative to `pctl_offset`. A wrong table entry can mask, ack, or configure the wrong interrupt. `eint_num` is static and accumulates during wakeup init, so multiple controller init order must be stable. Wakeup mask arrays are global; overlapping wakeup banks across controllers depend on correct bit numbering. Failing to call `gpiochip_unlock_as_irq()` on release would leave GPIO lines locked as IRQs.

## Test Signals
Tests should exercise IRQ type programming for all edge/level modes, GPIO-to-IRQ mapping, parent service-register dispatch, muxed wakeup IRQ demux, per-pin wakeup chained handlers, set-wake mask updates, suspend/resume of EINT con/filter/mask registers, GS101 three-register wake mask writes, and ExynosAuto v920 explicit-offset register paths. Runtime warnings about missing PMU syscon or missing IRQs are important failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos.h

## Purpose
This header defines Exynos-specific constants, bank-construction macros, wakeup IRQ data structures, and callback prototypes used by the Samsung pinctrl driver. It is the contract between the declarative Exynos SoC data files and the active Exynos logic in `pinctrl-exynos.c`.

## Important APIs, Types, and Macros
The header defines function and EINT register constants, including `EXYNOS_PIN_CON_FUNC_EINT`, GPIO EINT offsets, wakeup EINT offsets, Exynos7 wakeup offsets, service-register offsets, trigger encodings, EINT field widths, and filter configuration bit definitions. It provides bank construction macros for many SoC variants: `EXYNOS_PIN_BANK_EINTN/G/W`, `EXYNOS5433_PIN_BANK_*`, `EXYNOS7870_PIN_BANK_*`, `EXYNOS850_PIN_BANK_*`, `EXYNOS8895_PIN_BANK_EINTG`, `EXYNOSV920_PIN_BANK_*`, `GS101_PIN_BANK_*`, and `ARTPEC_PIN_BANK_EINTG`.

The two small data structures are `struct exynos_weint_data`, for per-pin wakeup interrupt chained handlers, and `struct exynos_muxed_weint_data`, for muxed wakeup interrupt banks behind one parent IRQ. Function declarations expose Exynos GPIO/wakeup initialization, suspend/resume variants, GS101 resume/suspend variants, ExynosAuto v920 variants, and `exynos_retention_init()`.

## Control Flow
There is no executable control flow in this header. Its macros initialize `struct samsung_pin_bank_data` with the fields the common Samsung probe and Exynos IRQ logic later consume. The key distinction encoded by the macros is EINT type: none, GPIO, wakeup, or variant-specific wakeup/GPIO with additional offsets.

## State and Persistence
The header stores no runtime state. It defines how state will be laid out in SoC data. Fields such as `pctl_res_idx`, `eint_con_offset`, `eint_mask_offset`, `eint_pend_offset`, and `eint_fltcon_offset` drive runtime persistence and suspend/resume behavior indirectly by telling `pinctrl-samsung.c` and `pinctrl-exynos.c` where each bank's registers live.

## Dependencies and Integration Points
It depends on `pinctrl-samsung.h` for `struct samsung_pin_bank_data`, `struct samsung_pin_bank`, and driver data types. It is included by `pinctrl-exynos.c`, `pinctrl-exynos-arm.c`, and `pinctrl-exynos-arm64.c`. The macro outputs must remain compatible with the shared Samsung probe's field-copy logic.

## Risks
Macros hide many hardware assumptions. Using a macro with the wrong bank type can silently select wrong pull/drive field widths. Using generic macros for ExynosAuto v920 or GS101 would omit explicit EINT or filter offsets. The `EXYNOS_EINT_NR_WKUP_EINT` define has no value in this snapshot and appears to be a placeholder; any code that tried to consume it as a numeric constant would fail.

## Test Signals
Compile coverage across `CONFIG_PINCTRL_EXYNOS_ARM` and `CONFIG_PINCTRL_EXYNOS_ARM64` is the first signal. Runtime test signals come from SoC bank tables generated by these macros: correct pin names, correct interrupt domains, correct suspend/resume register access, and no invalid memory-resource indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-exynos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-s3c64xx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-s3c64xx.c

## Purpose
This file provides S3C64xx-specific data and interrupt logic for the shared Samsung pinctrl driver. It handles legacy S3C64xx GPIO EINT groups and EINT0 wakeup interrupts, then exports `s3c64xx_of_data` for the common Samsung platform driver.

## Important APIs, Types, and Functions
The file defines several S3C64xx bank layouts: 4-bit, 4-bit-alive, 4-bit with alternate register spacing, 2-bit, and 2-bit-alive types. Bank macros such as `PIN_BANK_4BIT_EINTG`, `PIN_BANK_4BIT_EINTW`, `PIN_BANK_2BIT_EINTG`, and `PIN_BANK_2BIT_EINTW` set the bank type, EINT function number, EINT mask, and EINT offset.

Interrupt-specific data structures are `struct s3c64xx_eint0_data`, `struct s3c64xx_eint0_domain_data`, and `struct s3c64xx_eint_gpio_data`. Key functions include `s3c64xx_irq_get_trigger()`, `s3c64xx_irq_set_function()`, GPIO EINT mask/ack/type handlers, `s3c64xx_eint_gpio_init()`, EINT0 wakeup mask/ack/type handlers, `s3c64xx_irq_demux_eint()`, and `s3c64xx_eint_eint0_init()`.

## Control Flow
The common Samsung probe calls `s3c64xx_eint_gpio_init()` for GPIO EINT setup and `s3c64xx_eint_eint0_init()` for wakeup setup. GPIO EINT setup creates one IRQ domain per GPIO EINT bank, stores them in group order, and installs a chained parent handler. The handler repeatedly reads the service register, decodes group and pin, handles the special group-1 split between two banks, and dispatches the pin through the relevant IRQ domain.

Wakeup setup locates a `samsung,s3c64xx-wakeup-eint` child node, maps four parent IRQs for EINT0 ranges 0-3, 4-11, 12-19, and 20-27, then creates per-bank domains for wakeup banks. The demux handlers read EINT0 pending and mask registers, filter by range, and dispatch active bits using a global mapping from EINT number to bank domain and pin.

## State and Persistence
Runtime state is stored in devm-managed EINT data structures, per-bank IRQ domains, the common bank structures, and the hardware registers. This file does not implement suspend/resume retention callbacks. It initializes `drvdata->pud_val` with S3C64xx-specific pull encoding through `s3c64xx_pud_value_init()`.

## Dependencies and Integration Points
It integrates with the common Samsung pinctrl/gpiolib driver through `s3c64xx_pin_ctrl`, with irqdomain and chained IRQ APIs, and with device tree child nodes for wakeup EINT parent interrupts. It depends on `drvdata->virt_base`, a legacy single base mapping retained by the common driver specifically for platforms like S3C64xx.

## Risks
The service-register domain indexing assumes GPIO EINT bank domains are stored in group order and that group 1 is split exactly as coded. `BUG_ON(ret)` in interrupt dispatch can panic if a pending unmasked interrupt lacks a domain mapping. Some mask arrays use `fls(mask)` to size domains, so sparse masks must have `ddata->eints` and domain translations consistent with pin indexes. Clock gating is not explicit in this file, relying on legacy access assumptions through `virt_base`.

## Test Signals
Tests should cover GPIO EINT group dispatch, group-1 split behavior, EINT0 range demux, all trigger types, invalid trigger rejection, bank function switching to EINT, sparse wakeup masks, and DT failure paths for missing wakeup parent IRQs. GPIO pull configuration should be checked for S3C-specific pull disable/down/up encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-samsung.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-samsung.c

## Purpose
This is the common Samsung pinctrl, pinmux, pinconf, GPIO, platform-driver, and power-management implementation. SoC-specific files provide bank descriptions and callbacks; this file turns those descriptions into registered pinctrl devices and gpiochips.

## Important APIs, Types, and Functions
The driver implements `pinctrl_ops`, `pinmux_ops`, `pinconf_ops`, and `gpio_chip` callbacks. Device-tree parsing is handled by `samsung_dt_node_to_map()` and `samsung_dt_subnode_to_map()`, which convert `samsung,pins`, `samsung,pin-function`, and config properties into pinctrl maps. Pinmux programming is in `samsung_pinmux_setup()`. Pin configuration read/write is centralized in `samsung_pinconf_rw()`. GPIO operations include `samsung_gpio_set()`, `samsung_gpio_get()`, direction callbacks, `samsung_gpio_to_irq()`, and `samsung_gpio_set_config()`.

Probe-time helpers include `samsung_pinctrl_get_soc_data()`, `samsung_banks_node_get()`, `samsung_pinctrl_register()`, `samsung_pinctrl_parse_dt()`, `samsung_gpiolib_register()`, and `samsung_pinctrl_probe()`. PM helpers are `samsung_pinctrl_suspend()` and `samsung_pinctrl_resume()`.

## Control Flow
At `postcore_initcall`, the platform driver is registered. Probe allocates `samsung_pinctrl_drv_data`, selects SoC data by `pinctrl` OF alias, maps memory resources, copies static bank data into runtime banks, links bank fwnodes, obtains optional parent IRQ and optional prepared `pclk`, initializes retention control, registers pinctrl, initializes SoC EINT callbacks, initializes pull-value encoding, registers one gpiochip per bank, enables pinctrl, and stores drvdata.

During pinctrl state selection, DT nodes are converted into maps. If a node has no children it is treated as one pin configuration node; otherwise each child is parsed. Each listed `samsung,pins` entry may produce a mux map and a config map. Pinmux and pinconf accesses locate the bank with `pin_to_reg_bank()`, enable the clock, lock the bank raw spinlock, update register fields, unlock, and disable the clock.

Suspend enables the clock, saves supported registers for banks with power-down config, invokes SoC suspend callbacks per bank, disables the clock, then enables retention. Resume enables the clock, invokes SoC resume callbacks, restores saved registers, disables the clock, then disables retention.

## State and Persistence
The main runtime state is `struct samsung_pinctrl_drv_data`, including mapped register bases, pin descriptors, dynamic pin groups/functions, bank array, GPIO chips, optional parent IRQ, optional clock, pull encoding values, and retention control. Per-bank state includes pin base, fwnode, gpiochip, irq_domain, irq_chip, raw spinlock, and `pm_save`. Pinctrl maps and pin/function arrays are devm-managed or freed through pinctrl callbacks.

## Dependencies and Integration Points
The file integrates with the Linux pinctrl core, pinmux/pinconf, gpiolib, irqdomain through bank IRQ domains, OF/property APIs, clock framework, platform driver core, and SoC-specific data from ARM, ARM64, S3C64xx, and S5PV210/Exynos helpers. The OF match table conditionally references exported `*_of_data` symbols based on Kconfig.

## Risks
Pin-to-bank lookup assumes bank arrays are ordered by increasing pin ranges and the input pin is valid. `samsung_pinconf_group_set()` ignores return values from per-pin config writes, so a later pin failure can be hidden. DT parsing logs malformed optional config properties but continues, which can leave partially applied maps. Clock enable failures are propagated in most runtime paths but EINT callback return values from SoC init are not checked in probe. Bank fwnode matching relies on exact bank names or `<bank>-gpio-bank` child names.

## Test Signals
Important signals include successful probe for every compatible, correct generated pin names, pinctrl map parsing for flat and nested DT nodes, mux writes on banks with one and two CON registers, pinconf get/set across all supported config types, GPIO direction/value and bias config, gpio-to-IRQ mapping, suspend/resume register preservation, clock failure handling, and missing bank node warnings in invalid DTBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-samsung.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-samsung.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-samsung.h

## Purpose
This header defines the shared data model and constants used by the Samsung pinctrl family. It is the common contract for generic driver code, Exynos data and logic, and S3C64xx support.

## Important APIs, Types, and Macros
`enum pincfg_type` defines logical configuration fields: function, data, pull, drive, power-down function, and power-down pull. `PINCFG_PACK`, `PINCFG_UNPACK_TYPE`, and `PINCFG_UNPACK_VALUE` pack Samsung-specific config type/value pairs into pinconf words. Pull and GPIO function constants define common Exynos/S5P values for input/output and pull states.

Core types are `struct samsung_pin_bank_type` for bit widths and register offsets, `struct samsung_pin_bank_data` for static bank descriptions, `struct samsung_pin_bank` for runtime bank state, `struct samsung_retention_ctrl` and `struct samsung_retention_data` for pad retention, `struct samsung_pin_ctrl` for per-controller SoC data and callbacks, `struct samsung_pinctrl_drv_data` for driver runtime data, `struct samsung_pinctrl_of_match_data` for OF match payloads, `struct samsung_pin_group`, and `struct samsung_pmx_func`.

Macros `PIN_GROUP` and `PMX_FUNC` build static group/function descriptors, although this driver also dynamically creates one-pin groups and functions from DT. The header declares all SoC `*_of_data` symbols consumed by the common OF match table.

## Control Flow
The header itself has no execution. Its structures define how probe copies static SoC data into runtime banks, how pinctrl operations interpret register fields, how GPIO and IRQ code find per-bank state, and how suspend/resume callbacks are wired.

## State and Persistence
`struct samsung_pin_bank` is the key persistent runtime object. It stores register bases, offsets, EINT metadata, bank name, ID, pin base, fwnode, GPIO and IRQ objects, spinlock, and saved power-management register values. `struct samsung_pinctrl_drv_data` persists controller-wide arrays, clock, IRQ, registered pinctrl device, pin groups/functions, and retention control. `pm_save[PINCFG_TYPE_NUM + 1]` accounts for double CON registers on wide banks.

## Dependencies and Integration Points
The header depends on Linux pinctrl, pinmux, pinconf, consumer/machine, and GPIO driver definitions. It is included by the Samsung common driver and SoC-specific files. The extern declarations integrate Kconfig-selected SoC data with `pinctrl-samsung.c`.

## Risks
The packed config format uses only 8 bits for values, so new config fields needing larger values would require a different representation. `PIN_NAME_LENGTH` is fixed at 10; longer generated bank names could truncate pin names if not controlled. Structure comments and field names need to stay synchronized with SoC macro outputs; several features such as ExynosAuto explicit EINT offsets and GS101 filter offsets rely on optional fields being copied by probe.

## Test Signals
Compile coverage is the main header-level signal. Runtime signals include correct pin name generation, correct register bitfield programming for every `samsung_pin_bank_type`, successful IRQ domain association through `samsung_pin_bank`, and correct suspend/resume save slot usage on banks with more than 32 function bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-samsung.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/Kconfig

## Purpose
This Kconfig file defines build-time configuration for Sophgo pinctrl drivers. It separates the shared core from SoC-specific front-end drivers and from optional operation families for CV18xx and SG2042-style controllers.

## Important Symbols
`PINCTRL_SOPHGO_COMMON` is a tristate internal common driver that selects generic pinctrl groups, generic pinmux functions, and generic pinconf support. `PINCTRL_SOPHGO_CV18XX_OPS` and `PINCTRL_SOPHGO_SG2042_OPS` are boolean helper-operation selectors. User-visible tristate symbols include `PINCTRL_SOPHGO_CV1800B`, `PINCTRL_SOPHGO_CV1812H`, `PINCTRL_SOPHGO_SG2000`, `PINCTRL_SOPHGO_SG2002`, `PINCTRL_SOPHGO_SG2042`, and `PINCTRL_SOPHGO_SG2044`.

## Control Flow
Kconfig does not execute at runtime. Its dependency and select graph determines which source objects are compiled. Each SoC driver depends on `ARCH_SOPHGO || COMPILE_TEST` and `OF`, selects the common driver, and selects its required operation helper family.

## State and Persistence
There is no runtime state in this file. It persists build policy: which modules can be built, which helpers are linked into the common object, and whether a driver can be modular.

## Dependencies and Integration Points
The file integrates with the kernel configuration system, the Sophgo Makefile, and generic pinctrl framework options. The help text documents module names for the user-visible drivers.

## Risks
Because the helper operation symbols are bool while the drivers are tristate, build combinations must ensure helper objects are linked into the common object when any dependent module is built. Missing `OF` would break probe-time match data, so the explicit dependency is important. Select chains can also pull in generic pinctrl helpers for COMPILE_TEST builds, so compile coverage should include modular and built-in cases.

## Test Signals
Use `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and `ARCH_SOPHGO` builds. Confirm each selected SoC symbol produces its advertised module and that disabling all visible Sophgo SoC symbols omits the common objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/Makefile

## Purpose
This Makefile maps Sophgo pinctrl Kconfig symbols to kernel build objects. It builds the shared Sophgo common module and the individual SoC front-end modules.

## Important Build Rules
`obj-$(CONFIG_PINCTRL_SOPHGO_COMMON) += pinctrl-sophgo.o` creates the common composite object. `pinctrl-sophgo-objs += pinctrl-sophgo-common.o` always includes the shared core in that composite. Conditional object fragments add `pinctrl-cv18xx.o` or `pinctrl-sg2042-ops.o` when their helper-operation symbols are enabled. Individual front ends are built as `pinctrl-cv1800b.o`, `pinctrl-cv1812h.o`, `pinctrl-sg2000.o`, `pinctrl-sg2002.o`, `pinctrl-sg2042.o`, and `pinctrl-sg2044.o`.

## Control Flow
There is no runtime control flow. At build time, Kbuild evaluates each `obj-$()` and composite-object rule, then links helper operation objects into `pinctrl-sophgo.o` and compiles selected SoC drivers as separate objects or modules.

## State and Persistence
The file persists build composition. The common object owns shared operations; SoC-specific objects provide match tables and pin data that call into the common probe.

## Dependencies and Integration Points
It depends directly on the symbols from the adjacent `Kconfig`. The source files named here depend on shared headers such as `pinctrl-sophgo.h`, `pinctrl-cv18xx.h`, or SG2042 operation headers elsewhere in the Sophgo directory.

## Risks
If a SoC driver selects a helper symbol but the Makefile does not include the corresponding helper object in `pinctrl-sophgo.o`, module link failures or missing operation callbacks will result. Conversely, adding a new Kconfig symbol requires both an `obj-*` line and any helper-object wiring.

## Test Signals
Build every Sophgo symbol as built-in and module. Inspect module dependencies to ensure SoC modules resolve shared symbols from `pinctrl-sophgo`. Compile-test configurations should catch stale object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv1800b.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv1800b.c

## Purpose
This file is the Sophgo CV1800B SoC-specific pinctrl front end. It supplies pin descriptors, generated vendor pin metadata, voltage-domain names, and CV1800B-specific electrical mapping callbacks to the shared Sophgo pinctrl core.

## Important APIs, Types, and Data
`enum CV1800B_POWER_DOMAIN` defines five power domains: audio 1.8 V, USB/PLL/ETH/CSI 1.8 V, ETH/USB/SD1 3.3 V-capable domain, RTC VDDIO, and SD0/SPI VDDIO. `cv1800b_power_domain_desc` gives names for these domains. Electrical callbacks are `cv1800b_get_pull_up()`, `cv1800b_get_pull_down()`, `cv1800b_get_oc_map()`, and `cv1800b_get_schmitt_map()`, grouped in `cv1800b_vddio_cfg_ops`.

`cv1800b_pins` lists the public pinctrl pin descriptors, using IDs from `dt-bindings/pinctrl/pinctrl-cv1800b.h`. `cv1800b_pin_data` maps each pin to its power domain, IO type, mux register area/offset/mask width, and pinconf register area/offset using macros from `pinctrl-cv18xx.h`. `cv1800b_pindata` ties those arrays to common CV1800 operations: `cv1800_cfg_ops`, `cv1800_pctrl_ops`, `cv1800_pmx_ops`, and `cv1800_pconf_ops`.

## Control Flow
The platform driver matches `sophgo,cv1800b-pinctrl` and calls `sophgo_pinctrl_probe()` with `cv1800b_pindata` from the OF match data. The common Sophgo probe registers the pins and uses the provided operation tables for mux and config. When pinconf needs bias, drive-strength/open-current, or schmitt thresholds, the common CV18xx layer calls back into the CV1800B VDDIO functions with the pin metadata and current power-domain state map.

## State and Persistence
This file's state is static constant descriptor data. Runtime state, including power-domain voltage state, register mappings, and pinctrl registration, is owned by the shared Sophgo core. The electrical callbacks are pure lookups based on `struct sophgo_pin`, converted to `struct cv1800_pin`, and `psmap[pin->power_domain]`.

## Dependencies and Integration Points
The file depends on Linux module/platform/OF APIs, pinctrl core headers, `dt-bindings/pinctrl/pinctrl-cv1800b.h`, and `pinctrl-cv18xx.h`. It integrates with Kconfig through `CONFIG_PINCTRL_SOPHGO_CV1800B`, with the Makefile as `pinctrl-cv1800b.o`, and with device tree through the `sophgo,cv1800b-pinctrl` compatible.

## Risks
Electrical maps are voltage- and IO-type-sensitive. A wrong power-domain assignment can return the wrong pull resistance, drive map, or schmitt threshold. Unsupported IO types return `-ENOTSUPP`, while invalid voltage state returns `-EINVAL` in some paths; callers must preserve that distinction. The generated pin data must stay ordered and sized exactly with `cv1800b_pins`; otherwise pin IDs and metadata can drift. MIPI pins using `CV1800_GENERATE_PIN_MUX2` have multiple mux locations and are especially sensitive to offset mistakes.

## Test Signals
Test with DT binding validation, probe of `sophgo,cv1800b-pinctrl`, pinmux selection for all listed pins, pinconf bias/drive/schmitt queries under both 1.8 V and 3.3 V domain states, unsupported audio/ETH behavior where appropriate, and module load/unload. Compile tests should verify the generated pin IDs match the binding header and array sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv1800b.c -->
