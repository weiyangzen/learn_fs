# subset-b-005153 research

Grouped research for PnP resource helpers, board reset/poweroff drivers, and power-sequencing framework/provider files. Each source file section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/resource.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/resource.c

## Purpose
`resource.c` is the core PnP resource-registration and resource-conflict helper for the Linux PnP bus in this source tree. It lets protocol parsers record possible IRQ, DMA, I/O, memory, and bus resources on a `struct pnp_dev`; validates proposed current resources against kernel resource ownership, user-reserved ranges, PCI legacy IRQ use, and other PnP devices; and exports lookup/add/possible-config helpers used by PnP protocol and driver code.

## Important APIs, Types, and Functions
Key APIs are `pnp_register_irq_resource()`, `pnp_register_dma_resource()`, `pnp_register_port_resource()`, `pnp_register_mem_resource()`, `pnp_free_options()`, `pnp_check_port()`, `pnp_check_mem()`, `pnp_check_irq()`, `pnp_check_dma()` when ISA DMA is enabled, `pnp_resource_type()`, `pnp_get_resource()`, `pnp_add_resource()` and typed add helpers, `pnp_possible_config()`, and `pnp_range_reserved()`. Static boot parameter arrays `pnp_reserve_irq`, `pnp_reserve_dma`, `pnp_reserve_io`, and `pnp_reserve_mem` feed `__setup()` parsers.

## Control Flow
Protocol code first registers option descriptors through `pnp_build_option()` and typed wrappers, then assignment paths add current resources to `dev->resources`. Checkers short-circuit disabled resources, probe global kernel reservations with `request_region()`, `request_mem_region()`, `request_irq()`, or `request_dma()`, compare against boot-reserved ranges, check intra-device duplicates, and walk all PnP devices for conflicts. IRQ checking additionally rejects IRQs above 15, consults PCI devices including legacy IDE compatibility IRQs, and then tests requestability.

## State and Persistence Behavior
Software state lives in the `dev->options` and `dev->resources` lists and in static boot-parameter reservation arrays initialized to `-1`. Resource additions copy a `struct resource` and set names to the PnP device name. Hardware/resource-manager state is not permanently claimed by the check paths except for transient request/release probes; actual ownership is represented by resources and later driver activation.

## Dependencies and Integration Points
It depends on PnP core list helpers, Linux resource management, IRQ and ISA DMA APIs, PCI iteration when configured, libata legacy IRQ helpers, boot-parameter parsing through `get_option()`, and debug helpers from `base.h`. Exported symbols integrate with PnP protocol drivers, PnP client drivers, and system-resource reservation logic.

## Risks and Edge Cases
The range macros take pointers and assume `end >= start`; malformed resources can underflow length calculations. Boot-reserved I/O and memory ranges are stored as `int`, which is narrower than `resource_size_t` on wide-address systems. Conflict checks walk global PnP device lists without local locking in this file, relying on PnP core serialization. PCI legacy IRQ handling is x86/ISA-centric and intentionally conservative. `pnp_possible_config()` only matches exact `min` and `size` for I/O and memory, not all possible aligned alternatives.

## Test Signals
Build with PnP, PCI on/off, and ISA DMA on/off. Exercise resource parsing, disabled resources, overlapping same-device resources, cross-device overlaps, boot parameters `pnp_reserve_irq/dma/io/mem`, PCI IDE legacy IRQ conflicts, and exported helper lookups. Fault-inject allocation failure for option/resource additions and verify no leaked list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/support.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/support.c

## Purpose
`support.c` contains small shared PnP support and debug-formatting utilities. It detects whether a PnP device appears active, converts packed EISA IDs into strings, maps resource/option types to readable names, and formats current resources and possible options for PnP debug output.

## Important APIs, Types, and Functions
The exported or shared helpers are `pnp_is_active()`, `pnp_eisa_id_to_string()`, `pnp_resource_type_name()`, `dbg_pnp_show_resources()`, `pnp_option_priority_name()`, and `dbg_pnp_show_option()`. It uses `pnp_port_start()`, `pnp_port_len()`, `pnp_mem_start()`, `pnp_mem_len()`, `pnp_irq()`, `pnp_dma()`, `pnp_resource_type()`, `pnp_option_is_dependent()`, `pnp_option_set()`, and `pnp_option_priority()` from the PnP core.

## Control Flow
`pnp_is_active()` applies a conservative current-resource heuristic: no meaningful first port, memory, IRQ, or DMA means inactive. The EISA converter endian-swaps the 32-bit ID and formats three compressed vendor characters plus four hex digits. Debug flows build short strings in a fixed buffer, branch by option resource type, enumerate IRQ/DMA bitmaps, add optional/dependent-set metadata, and emit through `pnp_dbg()`.

## State and Persistence Behavior
There is no persistent state in this file. It reads PnP device resource and option lists and writes only caller-provided output buffers or debug logs. The active heuristic depends on current resources that other PnP code owns and may lag true hardware state after disable paths clear only auto-assigned resources.

## Dependencies and Integration Points
It depends on Linux module, ctype/hex helpers, endian conversion, the public PnP API, and `base.h` debug macros. Integration is mostly internal: protocol parsers and resource registration paths call the debug printers, while `pnp_is_active()` is exported for PnP consumers.

## Risks and Edge Cases
The activity heuristic is explicitly documented as unreliable after `pnp_disable_dev()`. `pnp_eisa_id_to_string()` preserves historical Linux six-bit behavior for the first character, so strict EISA spec validation may disagree. `dbg_pnp_show_option()` uses a 128-byte buffer and `scnprintf()`, so very large option ranges are truncated rather than dynamically allocated. Unknown option types are not rendered beyond the enclosing debug call.

## Test Signals
Test EISA conversion against known IDs including historical lower-case/extended first-character cases, active/inactive devices with zero-length resources, each option type's debug formatting, optional IRQ flags, dependent-set priorities, empty IRQ/DMA masks, and buffer truncation under debug-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/system.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/system.c

## Purpose
`system.c` is the PnP system resource reservation driver. It binds generic motherboard/system-resource PnP IDs and reserves their I/O and memory ranges in the kernel resource tree so later allocation avoids firmware-described fixed resources.

## Important APIs, Types, and Functions
The driver table matches `PNP0c02` for general system resources and `PNP0c01` for memory controllers. Important functions are `reserve_range()`, `reserve_resources_of_dev()`, `system_pnp_probe()`, and `pnp_system_init()`. The `system_pnp_driver` uses `PNP_DRIVER_RES_DO_NOT_CHANGE` so the PnP core does not reassign these resources.

## Control Flow
At `fs_initcall` time, the driver registers with PnP. Probe iterates each I/O resource, skips disabled, zero-start, sub-0x100 PC legacy ranges, and invalid ranges, then calls `request_region()`. It also iterates memory resources and calls `request_mem_region()`. Successful reservations have `IORESOURCE_BUSY` cleared so they remain reserved as firmware/system regions but do not look like active driver claims.

## State and Persistence Behavior
Persistent state is in the global kernel resource trees. `reserve_range()` allocates a small region-name string and intentionally leaves it attached to successful resource reservations; failed reservations free the string. No per-device private state is stored. Reservation survives for kernel lifetime because there is no remove path for these system PnP resources.

## Dependencies and Integration Points
It depends on PnP driver registration, the PnP resource helpers from `resource.c`, kernel I/O and memory resource management, and firmware PnP device enumeration. It is deliberately ordered after PCI BAR claims but before uninitialized PCI resource assignment.

## Risks and Edge Cases
Reservation failures are usually benign and logged because other quirks may already reserve the same range. Clearing `IORESOURCE_BUSY` is subtle: it prevents false ownership while still occupying the resource span. I/O resources below `0x100` are skipped because standard PC resources are reserved elsewhere; this assumption is PC-platform-specific. The allocated region name is intentionally not freed on success.

## Test Signals
Boot systems with PNP0c01/PNP0c02 firmware resources, verify `/proc/iomem` and `/proc/ioports` reservations, test overlapping PCI quirk reservations, invalid/disabled resource skips, low I/O range skips, and init ordering relative to PCI assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/power/Kconfig

## Purpose
`drivers/power/Kconfig` is the top-level power-driver Kconfig include point. It pulls in the power-supply, reset/poweroff, sequencing, and supply-class submenus so platform power management drivers are visible from the parent kernel configuration menu.

## Important APIs, Types, and Functions
It has no C APIs. The important declarations are four `source` statements for `drivers/power/supply/Kconfig`, `drivers/power/reset/Kconfig`, `drivers/power/sequencing/Kconfig`, and `drivers/power/supply/adapters/Kconfig`.

## Control Flow
Kconfig processing reads this file when the driver tree is configured and expands the referenced menus in order. Symbol definitions live in the included files; this file only controls menu reachability and ordering.

## State and Persistence Behavior
There is no runtime state. Configuration state persists in generated kernel config files through symbols declared in the included Kconfig fragments.

## Dependencies and Integration Points
It depends on the kernel Kconfig language and the relative layout of the `drivers/power` subtree. It integrates build-time configuration for power supply class drivers, board reset/poweroff drivers, and the power-sequencing framework.

## Risks and Edge Cases
Broken paths or reordered includes can hide entire driver families from configuration. Since it contains only includes, semantic risk is low but blast radius is high if a source line is deleted.

## Test Signals
Run `make menuconfig`/`olddefconfig` with representative architectures and verify power supply, reset, sequencing, and adapter symbols are reachable. Kconfig lint or allmodconfig builds catch missing sourced files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/Makefile -->
# sources/distributed-fs/ceph-client/drivers/power/Makefile

## Purpose
`drivers/power/Makefile` is the top-level build composition file for the power driver directory. It delegates object construction to the `supply`, `reset`, `sequencing`, and `supply/adapters` subdirectories.

## Important APIs, Types, and Functions
It exposes no C symbols. The important build entries are unconditional `obj-y` additions for `supply/`, `reset/`, `sequencing/`, and `supply/adapters/`; the subdirectory Makefiles decide which objects are compiled based on Kconfig symbols.

## Control Flow
During kbuild, this file causes the listed subdirectories to be visited. Each child directory contributes built-in objects or modules according to its own `obj-$(CONFIG_...)` rules.

## State and Persistence Behavior
No runtime state exists. Build state is generated by kbuild and persists only in build artifacts.

## Dependencies and Integration Points
It depends on kbuild directory traversal and the child Makefiles. Integration is with the kernel build system and the Kconfig symbols defined under `drivers/power`.

## Risks and Edge Cases
Removing an `obj-y` subdirectory silently prevents all contained drivers from building even if their Kconfig symbols are enabled. Adding a missing child directory would produce build failures.

## Test Signals
Use allnoconfig, allyesconfig, and modular builds to confirm the four child directories are traversed and their selected drivers appear in built-in or module outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/power/reset/Kconfig

## Purpose
`drivers/power/reset/Kconfig` defines the board-level reset, restart, poweroff, reboot-mode, and related embedded-controller driver configuration symbols. The menu is gated by `POWER_RESET` and covers platform-specific PMIC, syscon, GPIO, firmware, PCI, I2C, and generic reboot-mode drivers.

## Important APIs, Types, and Functions
Important symbols include `POWER_RESET`, per-driver selectors such as `POWER_RESET_GPIO`, `POWER_RESET_SYSCON`, `POWER_RESET_AT91_RESET`, `POWER_RESET_QCOM_PON`, `POWER_RESET_TORADEX_EC`, `POWER_RESET_QEMU_VIRT_CTRL`, framework symbol `REBOOT_MODE`, and storage backends `SYSCON_REBOOT_MODE` and `NVMEM_REBOOT_MODE`. Dependencies encode architecture, MFD, OF, regmap, I2C, PCI, regulator, and compile-test constraints.

## Control Flow
Kconfig exposes the parent menu, then conditionally offers each driver while applying `depends on`, `default`, and `select` rules. Enabling a driver later maps to an object in `drivers/power/reset/Makefile`. Some options are bool because they are intended built-in restart handlers, while others are tristate modules.

## State and Persistence Behavior
Configuration choices persist in `.config`. There is no runtime behavior, but selecting symbols controls whether shutdown/restart handlers and reboot-mode providers exist in a kernel image.

## Dependencies and Integration Points
It integrates with architecture symbols, MFD/regmap/provider subsystems, OF, ACPI/I2C/PCI, and the reset directory Makefile. `select REBOOT_MODE` couples qcom/syscon/nvmem reboot-mode consumers to the generic reboot-mode core.

## Risks and Edge Cases
Incorrect dependencies can create link failures or hide valid hardware support. Bool restart handlers may need to be built-in for early/critical reset paths. `select` can force framework code without all optional runtime dependencies, so dependency minimalism matters.

## Test Signals
Run Kconfig dependency checks, allmodconfig/allyesconfig across ARM, ARM64, MIPS, x86 compile-test, and targeted configs for AT91, Qualcomm, Broadcom, Renesas, Toradex, QEMU virt, and generic syscon/nvmem reboot modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/Makefile -->
# sources/distributed-fs/ceph-client/drivers/power/reset/Makefile

## Purpose
`drivers/power/reset/Makefile` maps reset/poweroff Kconfig symbols to their driver objects. It is the authoritative build list for the reset subtree.

## Important APIs, Types, and Functions
The file has only `obj-$(CONFIG_...) += ...` assignments. Important mappings include generic `gpio-poweroff.o`, `gpio-restart.o`, `syscon-reboot.o`, `syscon-poweroff.o`, `reboot-mode.o`, `syscon-reboot-mode.o`, `nvmem-reboot-mode.o`, and many platform-specific PMIC/SoC drivers such as AT91, Broadcom, Qualcomm, Renesas, Toradex EC, SpacemiT P1, and QEMU virt control.

## Control Flow
Kbuild evaluates enabled symbols and builds each object as built-in or module according to the symbol type/value. Framework objects such as `reboot-mode.o` are included when their selected symbols resolve to enabled.

## State and Persistence Behavior
No runtime state exists here. Build outputs persist in the kernel build tree.

## Dependencies and Integration Points
It depends on `drivers/power/reset/Kconfig` names staying synchronized with source filenames. It integrates each driver source file with kbuild and module generation.

## Risks and Edge Cases
A mismatched symbol or filename silently drops a driver or breaks builds. Built-in versus module behavior follows the Kconfig symbol, so changing bool/tristate status has direct reset-handler availability implications.

## Test Signals
Validate with `make drivers/power/reset/` under representative configs, allmodconfig, and scripts that compare Kconfig symbols with Makefile entries and source filenames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/arm-versatile-reboot.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/arm-versatile-reboot.c

## Purpose
ARM Integrator, Versatile, and RealView syscon restart driver.

## Important APIs, Types, and Functions
global `syscon_regmap`, `versatile_reboot_type`, `versatile_reboot()`, and `versatile_reboot_probe()` select reset register sequences by compatible string.

## Control Flow
probe finds the first matching syscon node, stores match data, converts it to a regmap, and registers a high-priority restart notifier; restart unlocks the syscon and writes board-specific reset values.

## State and Persistence Behavior
global regmap/type persist after `device_initcall`; hardware reset registers persist only until reset.

## Dependencies and Integration Points
OF matching, syscon/regmap, restart notifier, ARM barrier `dsb()`.

## Risks and Edge Cases
single global instance and no unregister path; wrong compatible data writes the wrong reset sequence; regmap write failures are ignored in notifier context.

## Test Signals
boot each supported board compatible, verify restart, missing syscon failure, and register write traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/arm-versatile-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/as3722-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/as3722-poweroff.c

## Purpose
ams AS3722 PMIC poweroff child driver.

## Important APIs, Types, and Functions
`struct as3722_poweroff`, `as3722_pm_power_off()`, and `as3722_poweroff_probe()` update `AS3722_RESET_CONTROL_REG` through the parent MFD.

## Control Flow
probe requires parent OF node with `ams,system-power-controller`, stores parent driver data, and registers a default-priority poweroff sys-off handler; callback sets `AS3722_POWER_OFF`.

## State and Persistence Behavior
devm state is per platform child; PMIC reset-control bit persists in hardware for final shutdown.

## Dependencies and Integration Points
MFD AS3722, OF property, platform bus, sys-off API.

## Risks and Edge Cases
silently does nothing when the DT property is absent; assumes parent drvdata is valid; callback only logs PMIC write failure.

## Test Signals
probe with/without system-power-controller, regmap failure injection, and real PMIC poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/as3722-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/at91-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/at91-poweroff.c

## Purpose
legacy Atmel AT91 SAM9/SAMA5 shutdown-controller poweroff driver.

## Important APIs, Types, and Functions
global `at91_shdwc`, wakeup mode parser, `at91_poweroff()` ARM assembly, DT wakeup configuration, and platform probe/remove.

## Control Flow
probe maps SHDWC, enables slow clock, reports wake source, programs wakeup mode/counter/RTC/RTT bits, optionally maps LPDDR2/3 DDR controller, and assigns `pm_power_off`; callback powers down DDR then writes the shutdown key.

## State and Persistence Behavior
global base pointers, slow clock, optional MPDDRC mapping, and `pm_power_off` persist until remove; wake mode and DDR low-power writes persist in hardware.

## Dependencies and Integration Points
AT91 clocks, OF address lookup, SHDWC registers, DDRSDRC definitions, platform driver, legacy global poweroff hook.

## Risks and Edge Cases
inline assembly is ARM-specific and must run from cache-aligned code; global singleton prevents multiple controllers; wakeup strings outside known values only warn; MPDDRC lookup is compatible-string-specific.

## Test Signals
DT wakeup property tests, LPDDR and non-LPDDR boards, slow-clock failure, wake-source logging, remove clearing `pm_power_off`, and real shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/at91-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/at91-reset.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/at91-reset.c

## Purpose
Atmel AT91 reset/restart and device-reset-controller driver.

## Important APIs, Types, and Functions
`struct at91_reset`, `struct at91_reset_data`, restart notifier `at91_reset()`, reset reason sysfs attribute, reset-controller ops, OF xlate, and platform probe/remove.

## Control Flow
probe maps RSTC, optional RAM controllers, slow clock, SoC match data, user-reset async configuration, registers restart handler, creates `power_on_reason`, and optionally registers reset-controller ops for device reset bits; restart powers down SDRAM then writes reset key/args.

## State and Persistence Behavior
per-device state stores bases, clock, notifier, reset-controller device, spinlock, and RAM low-power offset; hardware mode/status and device-reset bits persist until reset or rewritten.

## Dependencies and Integration Points
AT91 DDR/SDRAM headers, reset-controller framework, power-on-reason strings, OF compatible data, clocks, sysfs, restart notifier.

## Risks and Edge Cases
reset assembly relies on valid RAM controller mappings; reset reason mapping is only as accurate as RSTC status; device reset ids are range-checked but wrong DT cells can hit wrong bits; sysfs creation failure aborts probe after handler registration cleanup paths matter.

## Test Signals
restart on each compatible, reset-controller assert/deassert/status IDs, invalid xlate cells, power_on_reason contents, SAM9X60 async bit programming, and RAM-controller absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/at91-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/at91-sama5d2_shdwc.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/at91-sama5d2_shdwc.c

## Purpose
SAMA5D2-compatible AT91 shutdown-controller poweroff driver with richer wake input/debounce support.

## Important APIs, Types, and Functions
`struct reg_config`, `struct shdwc`, global `at91_shdwc`, wake status, `at91_poweroff()`, debouncer/input parsing, SoC register configs, and platform probe/remove.

## Control Flow
probe maps SHDWC, enables slow clock, matches SoC config, optionally maps PMC/DDR controller for LPDDR poweroff, logs wake source, configures debounce/RTC/RTT/wakeup child inputs, and installs `pm_power_off`; callback writes PMC DDR sleep if needed, LPDDR powerdown, and SHDWC shutdown key.

## State and Persistence Behavior
global singleton backs legacy `pm_power_off`; per-SoC register offsets and DT wake configuration persist in SHDWC/PMC registers.

## Dependencies and Integration Points
AT91 clocks/PMC helpers, OF child nodes, DDRSDRC, platform driver, global poweroff hook.

## Risks and Edge Cases
global hook means only one active controller; child wake input parsing must match hardware input numbers; debounce conversion uses fixed 32.768 kHz table; inline assembly and DDR sequencing are hardware-critical.

## Test Signals
SAMA5D2/SAM9X60/SAMA7G5 DTs, wake child nodes, debounce boundaries, LPDDR and non-LPDDR shutdown, wake-source status, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/at91-sama5d2_shdwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/atc260x-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/atc260x-poweroff.c

## Purpose
Actions Semi ATC260x PMIC poweroff and restart driver.

## Important APIs, Types, and Functions
`struct atc260x_pwrc`, chip-specific `atc2603c_do_poweroff()`/`atc2609a_do_poweroff()`, init helpers, and sys-off callbacks.

## Control Flow
probe obtains parent ATC260x/regmap, selects chip-specific function and initialization, registers default poweroff and restart handlers; callbacks program PMU system-control bits differently for shutdown and restart.

## State and Persistence Behavior
driver state is devm-managed; PMIC PMU control bits persist and drive final power state.

## Dependencies and Integration Points
MFD_ATC260X, regmap, platform bus, sys-off API.

## Risks and Edge Cases
chip-type switch must stay aligned with MFD enum; callbacks return `NOTIFY_BAD` on write errors but final state may be partially programmed; init changes wake/power behavior before handlers are used.

## Test Signals
probe each chip type, register-write failure injection, restart versus poweroff PMU bit sequences, and real board shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/atc260x-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/axxia-reset.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/axxia-reset.c

## Purpose
LSI Axxia syscon restart driver.

## Important APIs, Types, and Functions
`axxia_restart_handler()` and `axxia_reset_probe()` use a `syscon` phandle regmap and write critical-key, latch, efuse-status, and reset-control registers.

## Control Flow
probe resolves the syscon regmap and registers a restart sys-off handler at priority 128; handler unlocks writes, sets reset latch, clears efuse done, and requests system/chip reset.

## State and Persistence Behavior
no local persistent data beyond devm handler callback data; syscon register writes persist until reset.

## Dependencies and Integration Points
OF, syscon/regmap, platform driver, sys-off restart.

## Risks and Edge Cases
handler ignores intermediate regmap errors and always returns done; wrong syscon phandle can write unrelated registers.

## Test Signals
DT phandle validation, restart on Axxia hardware, and regmap error tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/axxia-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/brcm-kona-reset.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/brcm-kona-reset.c

## Purpose
Broadcom Kona reset-manager restart driver.

## Important APIs, Types, and Functions
global `kona_reset_base`, `kona_reset_handler()`, and probe map reset manager MMIO and register a high-priority restart handler.

## Control Flow
probe maps resource 0; restart writes password/access-enable to write-access register and then writes zero to soft-reset register.

## State and Persistence Behavior
global MMIO pointer persists for built-in driver lifetime; hardware reset manager state changes only during restart.

## Dependencies and Integration Points
platform resources, OF compatible `brcm,bcm21664-resetmgr`, MMIO, sys-off.

## Risks and Edge Cases
global singleton and no unregister path; write ordering/password constants are hardware-specific; no post-write failure detection.

## Test Signals
resource mapping failure, OF match, restart register trace, and actual reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/brcm-kona-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/brcmstb-reboot.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/brcmstb-reboot.c

## Purpose
Broadcom STB syscon reboot driver.

## Important APIs, Types, and Functions
global regmap and reset-mask pointer, `struct reset_reg_mask`, `brcmstb_restart_handler()`, and `brcmstb_reboot_probe()`.

## Control Flow
probe reads syscon phandle args as reset-source and master-reset offsets, chooses 40nm/65nm masks by compatible, and registers restart; handler writes source-enable then master-reset masks with readbacks and delays.

## State and Persistence Behavior
global regmap, offsets, and mask data persist after `subsys_initcall`; syscon reset bits persist until hardware reset.

## Dependencies and Integration Points
OF phandle args, syscon/regmap, restart sys-off, Broadcom compatible data.

## Risks and Edge Cases
driver uses globals so multiple instances conflict; readback errors only log; exact phandle arg count and mask data must match binding.

## Test Signals
40nm and 65nm compatibles, bad phandle args, regmap write/read failures, and reboot hardware tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/brcmstb-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/ep93xx-restart.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/ep93xx-restart.c

## Purpose
Cirrus EP93xx restart driver using syscon auxiliary-device glue.

## Important APIs, Types, and Functions
auxiliary probe state, restart handler, syscon regmap writes to device configuration and software-lock registers.

## Control Flow
the syscon MFD/auxiliary path instantiates the restart driver; probe registers restart, and callback writes the EP93xx unlock/key sequence to request software reset.

## State and Persistence Behavior
state is device-managed; reset request registers persist until reset.

## Dependencies and Integration Points
MFD_SYSCON, auxiliary bus, sys-off/restart, EP93xx architecture defaults.

## Risks and Edge Cases
depends on correct auxiliary creation and register offsets; restart writes are irreversible and lightly checked.

## Test Signals
EP93xx compile/probe, auxiliary binding, restart sequence trace, and reset failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/ep93xx-restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/gemini-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/gemini-poweroff.c

## Purpose
Cortina Gemini power controller poweroff and power-button driver.

## Important APIs, Types, and Functions
`struct gemini_powercon`, power-button IRQ handler, `gemini_poweroff()`, probe, and sys-off registration.

## Control Flow
probe maps power controller, requests power-button IRQ if present, registers poweroff; IRQ acknowledges/clears status and calls `orderly_poweroff()`, while poweroff writes the shutdown command and delays.

## State and Persistence Behavior
MMIO base and IRQ state persist in driver; hardware power-controller status/command bits persist until poweroff.

## Dependencies and Integration Points
OF, MMIO, IRQ, input-less power button handling, sys-off poweroff.

## Risks and Edge Cases
power button path relies on controller status semantics; built-in driver has no module unload; poweroff failure can only log after timeout.

## Test Signals
Gemini DT probing, IRQ press handling, status clear, orderly poweroff invocation, and final power cut.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/gemini-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/gpio-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/gpio-poweroff.c

## Purpose
generic GPIO-driven poweroff driver.

## Important APIs, Types, and Functions
`struct gpio_poweroff`, `gpio_poweroff_do_poweroff()`, and probe parse GPIO, active/inactive delays, timeout, and priority.

## Control Flow
probe obtains an output GPIO and optional timing properties, then registers a poweroff handler; callback drives active, waits, optionally drives inactive, waits timeout, and warns if still running.

## State and Persistence Behavior
driver stores GPIO descriptor and timings; GPIO output level persists after callback until board power is removed or another consumer changes it.

## Dependencies and Integration Points
OF, gpiod consumer API, sys-off poweroff.

## Risks and Edge Cases
wrong GPIO polarity or timings can hang shutdown; no hardware confirmation other than timeout warning; GPIO shared with another consumer can conflict.

## Test Signals
DT polarity and delay properties, active-low boards, timeout path, and repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/gpio-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/gpio-restart.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/gpio-restart.c

## Purpose
generic GPIO-driven restart driver.

## Important APIs, Types, and Functions
`struct gpio_restart`, `gpio_restart_notify()`, and probe parse GPIO, priority, active/inactive delays, and open-source mode.

## Control Flow
probe configures GPIO output and registers a restart handler; callback toggles active/inactive/active with requested delays to trigger external reset circuitry.

## State and Persistence Behavior
GPIO descriptor and timing state are devm-managed; line level persists until reset.

## Dependencies and Integration Points
OF, GPIO descriptors, sys-off restart.

## Risks and Edge Cases
timing/polarity mistakes can fail reset; open-source handling depends on board pull-ups; callback assumes sleeping delays are acceptable in sys-off context.

## Test Signals
DT property combinations, active-low/open-source, priority ordering, and scope/logic-analyzer reset pulse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/gpio-restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/hisi-reboot.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/hisi-reboot.c

## Purpose
HiSilicon board reboot driver.

## Important APIs, Types, and Functions
global MMIO base and reboot offset, restart notifier `hisi_restart_handler()`, and platform probe.

## Control Flow
probe maps MMIO, reads optional reboot offset, registers restart notifier; handler writes magic/reset value to the mapped offset and delays.

## State and Persistence Behavior
global base/offset persist for module lifetime; hardware reset register controls final reboot.

## Dependencies and Integration Points
ARCH_HISI, OF platform, MMIO, restart notifier.

## Risks and Edge Cases
single global instance; no unregister in built-in usage; minimal error checking after write.

## Test Signals
HiSilicon DT probe, custom offset, restart register trace, and reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/hisi-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/keystone-reset.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/keystone-reset.c

## Purpose
TI Keystone reset controller/restart driver.

## Important APIs, Types, and Functions
global PLL control regmap and `rspll_offset`, `rsctrl_enable_rspll_write()`, `rsctrl_restart_handler()`, and probe.

## Control Flow
probe maps reset control resource, resolves PLL syscon and offset, optionally checks device properties, and registers restart; restart enables reset-isolation/PLL writes then triggers reset.

## State and Persistence Behavior
global regmap/offset plus handler persist; hardware reset-control writes persist until reset.

## Dependencies and Integration Points
ARCH_KEYSTONE, syscon/regmap, MMIO, OF, sys-off restart.

## Risks and Edge Cases
global state is not multi-instance safe; PLL write-enable sequence must match SoC; restart failure only logs.

## Test Signals
Keystone DT, syscon phandle/offset errors, restart path, and compile-test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/keystone-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/linkstation-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/linkstation-poweroff.c

## Purpose
Buffalo LinkStation PHY-based poweroff driver.

## Important APIs, Types, and Functions
MDIO/PHY lookup helpers, GPIO-like PHY output programming, and poweroff handler that manipulates Ethernet PHY output for WoL-compatible shutdown.

## Control Flow
probe locates the configured PHY through OF MDIO/PHYLIB, configures output state, and registers poweroff; callback writes PHY registers to signal board power controller.

## State and Persistence Behavior
state holds PHY device and output bit information; PHY register state persists across shutdown and may enable wake-on-LAN behavior.

## Dependencies and Integration Points
ARCH_MVEBU/OF_MDIO/PHYLIB, sys-off poweroff, DT PHY references.

## Risks and Edge Cases
depends on board-specific PHY wiring; MDIO failures during late poweroff can leave system on; shared PHY configuration can interact with network driver state.

## Test Signals
LS421D/E DTs, PHY lookup failure, WoL behavior, MDIO error injection, and physical shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/linkstation-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/ltc2952-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/ltc2952-poweroff.c

## Purpose
LTC2952 PowerPath controller poweroff and watchdog/trigger driver.

## Important APIs, Types, and Functions
state structure with trigger/kill GPIOs and watchdog timer, IRQ/work handlers, and sys-off poweroff callback.

## Control Flow
probe obtains GPIOs/IRQ and timing properties, arms watchdog handling, and registers poweroff; external trigger events initiate orderly shutdown while poweroff asserts kill after required delays.

## State and Persistence Behavior
software timers/work track trigger and watchdog timing; GPIO levels persist into final powerdown.

## Dependencies and Integration Points
OF, GPIO descriptors, IRQ, timers/workqueues, sys-off poweroff.

## Risks and Edge Cases
timing properties must match the external controller; missed trigger IRQs or kill polarity errors can power-cycle unexpectedly; concurrent watchdog/work and shutdown paths need ordering.

## Test Signals
trigger IRQ, watchdog timeout, kill pulse timing, active-low GPIOs, suspend interaction, and board poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/ltc2952-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/macsmc-reboot.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/macsmc-reboot.c

## Purpose
Apple SMC reset/poweroff driver for Apple Silicon Macs.

## Important APIs, Types, and Functions
SMC command helpers, sys-off poweroff/restart handlers, and platform/MFD child probe.

## Control Flow
probe obtains the parent Apple SMC handle and registers restart/poweroff; callbacks send SMC commands/keys for reset or shutdown and delay while firmware acts.

## State and Persistence Behavior
state is device-managed; SMC firmware owns persistent final power state.

## Dependencies and Integration Points
MFD_MACSMC, platform bus, sys-off API, Apple SMC command interface.

## Risks and Edge Cases
firmware command failures may leave machine running; behavior is model/firmware-specific; handlers need high priority relative to generic fallbacks.

## Test Signals
Apple Silicon shutdown/restart, command failure injection, module bind/unbind, and priority ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/macsmc-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/msm-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/msm-poweroff.c

## Purpose
Qualcomm MSM PS_HOLD poweroff/restart driver.

## Important APIs, Types, and Functions
global mapped PS_HOLD address, poweroff and restart callbacks that clear or write PS_HOLD control.

## Control Flow
probe maps the Qualcomm control register and installs poweroff/restart hooks; shutdown drops PS_HOLD so PMIC powers down, restart requests reset behavior then drops hold.

## State and Persistence Behavior
global register pointer persists; PS_HOLD state directly controls PMIC/platform power.

## Dependencies and Integration Points
ARCH_QCOM, OF/MMIO, legacy `pm_power_off` and restart/sys-off integration.

## Risks and Edge Cases
wrong register mapping can immediately kill power; global hooks are singleton; limited confirmation after PS_HOLD drop.

## Test Signals
QCOM DT probe, shutdown and reboot on boards, register offset validation, and fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/msm-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/mt6323-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/mt6323-poweroff.c

## Purpose
MediaTek MT6323 PMIC RTC/BBPU poweroff driver.

## Important APIs, Types, and Functions
PMIC register definitions, `mt6323_do_pwroff()`, and probe obtaining parent regmap.

## Control Flow
probe checks for PMIC/RTC parent data and sets global poweroff; callback writes BBPU key/enable bits and waits for external shutdown.

## State and Persistence Behavior
global regmap pointer and poweroff hook persist; PMIC RTC BBPU bits persist in hardware.

## Dependencies and Integration Points
MFD_MT6397/MT6323, regmap, platform driver, legacy poweroff.

## Risks and Edge Cases
global singleton; key-protected register writes must be exact; callback may spin/delay if PMIC fails to cut power.

## Test Signals
MT6323 board shutdown, regmap failure, probe with missing parent, and poweroff register trace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/mt6323-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/nvmem-reboot-mode.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/nvmem-reboot-mode.c

## Purpose
generic reboot-mode backend that stores reboot magic in an NVMEM cell.

## Important APIs, Types, and Functions
private structure containing `struct reboot_mode_driver` and `struct nvmem_cell`, write callback, and platform probe.

## Control Flow
probe obtains an NVMEM cell from DT, initializes reboot-mode driver, and registers it; reboot notifier writes selected magic bytes to the cell before reboot.

## State and Persistence Behavior
selected mode persists in nonvolatile or retention-backed cell until bootloader/firmware consumes or overwrites it.

## Dependencies and Integration Points
OF, NVMEM consumer API, reboot-mode core.

## Risks and Edge Cases
cell size/endianness must match bootloader contract; NVMEM write failures occur late in reboot notifier path; repeated writes may affect flash-backed endurance.

## Test Signals
mode property parsing through reboot-mode core, NVMEM cell sizing, write failure injection, and bootloader mode consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/nvmem-reboot-mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/ocelot-reset.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/ocelot-reset.c

## Purpose
Microsemi Ocelot/Sparx5 syscon restart driver.

## Important APIs, Types, and Functions
restart context with regmap/mask/offset data and sys-off restart handler.

## Control Flow
probe resolves syscon registers from DT, registers restart, and callback writes reset bits then delays/logs if reset does not happen.

## State and Persistence Behavior
context is device-managed; syscon reset bit persists until reset.

## Dependencies and Integration Points
MFD_SYSCON, MSCC_OCELOT/ARCH_SPARX5, OF, sys-off.

## Risks and Edge Cases
generic syscon writes rely on binding-provided offsets/masks; no hardware completion detection beyond timeout.

## Test Signals
Ocelot/Sparx5 DT, mask/offset validation, and reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/ocelot-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/odroid-go-ultra-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/odroid-go-ultra-poweroff.c

## Purpose
Odroid Go Ultra board-specific poweroff preparation driver.

## Important APIs, Types, and Functions
data structure with two PMIC regmaps, PMIC lookup helper, `odroid_go_ultra_poweroff_prepare()`, manual platform-device init/exit, and sys-off prepare handler.

## Control Flow
module init registers a singleton platform device/driver; probe finds RK817 and RK818 PMIC devices by compatible, stores regmaps, and registers a poweroff-prepare handler that writes PMIC bits needed before final shutdown.

## State and Persistence Behavior
global platform device pointer and PMIC references persist while module loaded; PMIC register writes persist into shutdown.

## Dependencies and Integration Points
ARCH_MESON/OF/I2C, regmap, sys-off prepare mode, board-specific PMIC compatibles.

## Risks and Edge Cases
board-specific singleton design; PMIC lookup by compatible can bind the wrong instance on unusual systems; preparation failure can compromise poweroff.

## Test Signals
Odroid Go Ultra DT, PMIC lookup failure/defer, prepare writes, module unload cleanup, and full poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/odroid-go-ultra-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/piix4-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/piix4-poweroff.c

## Purpose
Intel PIIX4 PCI southbridge poweroff driver, mainly for MIPS Malta-like systems.

## Important APIs, Types, and Functions
global `pm_dev` and `io_offset`, ACPI PM I/O register enum, PCI probe/remove, and `piix4_poweroff()`.

## Control Flow
probe enables the PCI PM I/O BAR, stores offset, and installs `pm_power_off`; callback programs PMCNTRL for SOff/S5-like state using I/O port accesses.

## State and Persistence Behavior
global PCI device reference, I/O offset, and poweroff hook persist until remove; PM control register state persists for final poweroff.

## Dependencies and Integration Points
PCI core, HAS_IOPORT, MIPS/compile-test, legacy global poweroff.

## Risks and Edge Cases
global singleton; platform-specific ACPI PM semantics; I/O BAR decoding must be enabled; remove must clear hook only when owning it.

## Test Signals
PIIX4 PCI ID probe, I/O resource enable failure, poweroff on Malta, and remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/piix4-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/pwr-mlxbf.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/pwr-mlxbf.c

## Purpose
Mellanox/NVIDIA BlueField ACPI power-handling driver.

## Important APIs, Types, and Functions
`struct pwr_mlxbf`, IRQ handler, deferred reboot work, and ACPI platform probe.

## Control Flow
probe obtains the platform IRQ, initializes work, and requests IRQ; interrupt schedules reboot/power handling work that calls orderly reboot or low-power flow depending on GPIO/firmware event semantics.

## State and Persistence Behavior
state contains device, IRQ, and work item; pending work persists until flushed by driver core removal.

## Dependencies and Integration Points
ACPI IDs, BlueField GPIO dependencies, IRQ/workqueue, reboot helpers.

## Risks and Edge Cases
interrupt context is deliberately deferred; event storms can queue repeated work; behavior depends on platform firmware exposing the correct ACPI device and IRQ.

## Test Signals
ACPI match, IRQ trigger, work scheduling, reboot action, and unload with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/pwr-mlxbf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/qcom-pon.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/qcom-pon.c

## Purpose
Qualcomm SPMI PMIC PON reboot-mode driver.

## Important APIs, Types, and Functions
`struct qcom_pon`, `qcom_pon_reboot_mode_write()`, and probe with reboot-mode registration.

## Control Flow
probe obtains parent regmap/base address from resources or match data, initializes reboot-mode driver, and registers it; write callback stores magic into PON spare/reset-reason register fields.

## State and Persistence Behavior
selected reboot mode persists in PMIC PON registers for bootloader/firmware after reset.

## Dependencies and Integration Points
ARCH_QCOM, MFD_SPMI_PMIC, regmap, OF match data, reboot-mode core.

## Risks and Edge Cases
register offsets/masks vary by PMIC generation; wrong magic layout breaks bootloader interpretation; write failures happen during reboot notification.

## Test Signals
Qualcomm DT compatibles, reboot modes such as bootloader/recovery, regmap failure injection, and bootloader consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/qcom-pon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/qemu-virt-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/qemu-virt-ctrl.c

## Purpose
QEMU virt machine system-controller reset/poweroff driver.

## Important APIs, Types, and Functions
MMIO register definitions, sys-off poweroff/restart handlers, and platform probe.

## Control Flow
probe maps the virt-control resource and registers restart/poweroff; callbacks write command values to QEMU-provided MMIO registers and delay/log on failure.

## State and Persistence Behavior
MMIO base is device-managed; command writes are consumed by the emulator and do not persist past VM exit/reset.

## Dependencies and Integration Points
HAS_IOMEM, platform/OF, sys-off API, QEMU virt hardware model.

## Risks and Edge Cases
only works when QEMU exposes the controller; writes on nonmatching hardware would be meaningless; no completion except VM action.

## Test Signals
QEMU virt DT probe, guest poweroff/reboot, unmapped resource failure, and command-value tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/qemu-virt-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/qnap-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/qnap-poweroff.c

## Purpose
QNAP NAS microcontroller poweroff driver.

## Important APIs, Types, and Functions
UART/serial or platform command helpers, global poweroff command path, and platform probe.

## Control Flow
probe validates Orion/QNAP platform data and registers poweroff; callback sends the board-specific command sequence to the microcontroller controlling main power.

## State and Persistence Behavior
minimal driver state; the external microcontroller owns persistent power-control state.

## Dependencies and Integration Points
PLAT_ORION, platform data/firmware interface, legacy poweroff hook.

## Risks and Edge Cases
command protocol is board-specific and usually unacknowledged at final shutdown; wrong model can send ineffective commands.

## Test Signals
supported QNAP NAS shutdown, command failure logging, and absence on unsupported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/qnap-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/reboot-mode.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/reboot-mode.c

## Purpose
generic reboot-mode core framework.

## Important APIs, Types, and Functions
`struct mode_info`, reboot notifier, sysfs class/device helpers, property parser, `reboot_mode_register()`, `reboot_mode_unregister()`, and devm wrappers.

## Control Flow
providers register a `reboot_mode_driver` with a write callback; the core parses DT properties named for reboot modes into a list, registers a reboot notifier, exposes a class device, and on reboot command match writes the corresponding magic or normal magic.

## State and Persistence Behavior
mode list and class device persist until unregister; selected magic is not stored here, but delegated to provider write callbacks such as syscon or nvmem.

## Dependencies and Integration Points
reboot notifier chain, device class/sysfs, OF properties, devres, provider drivers.

## Risks and Edge Cases
mode-name parsing depends on DT property names; unregister must remove notifier and class device; write callback errors late in reboot may not stop reboot; list lifetime is per provider.

## Test Signals
register/unregister/devm paths, DT mode parsing, sysfs class device creation, reboot command matching, duplicate providers, and write failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/reboot-mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/regulator-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/regulator-poweroff.c

## Purpose
generic regulator-disable poweroff driver.

## Important APIs, Types, and Functions
`regulator_poweroff_do_poweroff()` and probe obtaining `cpu` regulator.

## Control Flow
probe gets the named regulator and registers poweroff; callback disables the regulator, waits up to three seconds, and warns if the system remains alive.

## State and Persistence Behavior
regulator handle is devm-managed; regulator enable state persists and should cut CPU/system power.

## Dependencies and Integration Points
OF, regulator consumer API, sys-off poweroff.

## Risks and Edge Cases
only appropriate when disabling the regulator really powers the board off; shared regulators can affect unexpected domains; failure to cut power leaves kernel running after regulator state change.

## Test Signals
DT supply lookup, regulator disable failure, timeout warning, and board poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/regulator-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/restart-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/restart-poweroff.c

## Purpose
fallback poweroff driver that restarts instead of powering off.

## Important APIs, Types, and Functions
`restart_poweroff_do_poweroff()` and platform probe.

## Control Flow
probe registers a poweroff handler; callback sets `reboot_mode = REBOOT_HARD` and calls `machine_restart(NULL)`.

## State and Persistence Behavior
no private state; global reboot mode is changed for the final path.

## Dependencies and Integration Points
sys-off poweroff, reboot core, OF compatible `restart-poweroff`.

## Risks and Edge Cases
does not truly power off; depends on bootloader holding or halting after reset; can surprise users expecting power removal.

## Test Signals
poweroff command on supported boards, reboot-mode value, and fallback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/restart-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/rmobile-reset.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/rmobile-reset.c

## Purpose
Renesas R-Mobile/SH-Mobile reset driver.

## Important APIs, Types, and Functions
global `sysc_base2`, `rmobile_reset_handler()`, and platform probe.

## Control Flow
probe maps resource 1 of the system controller and registers restart; callback writes `RESCNT2_PRES` to request soft power-on reset.

## State and Persistence Behavior
global MMIO pointer persists; reset control bit persists until hardware resets.

## Dependencies and Integration Points
ARCH_RMOBILE/HAS_IOMEM, OF platform, sys-off restart.

## Risks and Edge Cases
uses resource index 1, so DT resource ordering is critical; global singleton; no confirmation beyond delay/log.

## Test Signals
Renesas DT resource mapping, restart register trace, and reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/rmobile-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/sc27xx-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/sc27xx-poweroff.c

## Purpose
Spreadtrum/Unisoc SC27xx PMIC poweroff driver.

## Important APIs, Types, and Functions
global regmap, syscore shutdown hook, `sc27xx_poweroff_do_poweroff()`, and probe.

## Control Flow
probe obtains parent regmap, installs `pm_power_off`, and registers a syscore op; syscore shutdown prepares for late poweroff, and callback writes sleep-control and hardware power-down bits.

## State and Persistence Behavior
global regmap and poweroff hook persist; PMIC bits persist into final shutdown.

## Dependencies and Integration Points
MFD_SC27XX_PMIC, regmap, syscore, legacy poweroff.

## Risks and Edge Cases
global singleton rejects second instance; comments note CPU shutdown to avoid regmap/SPI mutex races, so late ordering is delicate; no remove cleanup of global hook.

## Test Signals
SC27xx board poweroff, duplicate probe, regmap absence, syscore ordering, and PMIC write trace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/sc27xx-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/spacemit-p1-reboot.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/spacemit-p1-reboot.c

## Purpose
SpacemiT P1 PMIC reboot/poweroff driver.

## Important APIs, Types, and Functions
poweroff/restart sys-off callbacks set `PWR_CTRL2_SHUTDOWN` or `PWR_CTRL2_RST` through parent regmap.

## Control Flow
probe gets parent regmap and registers both poweroff and restart handlers using helper wrappers; callbacks set the requested bit and return notifier status.

## State and Persistence Behavior
regmap callback data is devm-managed; PMIC control bits persist and should trigger final action.

## Dependencies and Integration Points
MFD_SPACEMIT_P1, regmap, platform IDs, sys-off helpers.

## Risks and Edge Cases
assumes parent regmap exists; bit definitions must match PMIC revision; write failures prevent handler success but may leave partial state.

## Test Signals
platform ID probe, poweroff/restart bits, regmap failure injection, and real PMIC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/spacemit-p1-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/st-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/st-poweroff.c

## Purpose
STMicroelectronics STi restart driver using syscfg regmap.

## Important APIs, Types, and Functions
`struct reset_syscfg`, static STiH407 register/mask data, global selected config, restart notifier, and platform probe.

## Control Flow
probe matches compatible data, resolves `st,syscfg` regmap, and registers restart; callback updates syscfg bits to request reset and delays.

## State and Persistence Behavior
global pointer to selected syscfg config persists; syscfg bits persist until reset.

## Dependencies and Integration Points
ARCH_STI, syscon/regmap, OF, restart notifier.

## Risks and Edge Cases
global state is single-instance; no unregister for built-in path; exact masks are SoC-specific.

## Test Signals
STiH407 DT probe, syscfg phandle failure, restart bit trace, and reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/st-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/syscon-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/syscon-poweroff.c

## Purpose
generic syscon/regmap poweroff driver.

## Important APIs, Types, and Functions
`struct syscon_poweroff_data`, `syscon_poweroff()`, and probe parsing `regmap`, `offset`, `value`, and `mask`.

## Control Flow
probe resolves regmap by phandle or parent syscon, parses offset/value/mask with legacy mask-as-value fallback, and registers a poweroff handler; callback updates the register then delays/warns if still alive.

## State and Persistence Behavior
driver data persists via devm; target syscon bits persist into shutdown.

## Dependencies and Integration Points
OF, MFD_SYSCON, regmap, sys-off poweroff.

## Risks and Edge Cases
binding mistakes can write wrong syscon bits; legacy fallback semantics are subtle; no success confirmation except actual power loss.

## Test Signals
DT variants with value/mask/legacy mask, parent versus phandle regmap, write failure injection, and poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/syscon-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/syscon-reboot-mode.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/syscon-reboot-mode.c

## Purpose
generic syscon-backed reboot-mode provider.

## Important APIs, Types, and Functions
`struct syscon_reboot_mode`, write callback, and platform probe.

## Control Flow
probe gets parent syscon regmap, reads required `offset` and optional `mask`, initializes a reboot-mode driver, and registers it; callback writes magic into masked register bits.

## State and Persistence Behavior
mode magic persists in syscon/retention register until boot firmware consumes or clears it.

## Dependencies and Integration Points
MFD_SYSCON, reboot-mode core, OF.

## Risks and Edge Cases
mask defaults to all bits and can overwrite unrelated fields; parent must be a syscon; write failures occur during reboot notification.

## Test Signals
mode property parsing, mask behavior, bootloader recovery/bootloader modes, and regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/syscon-reboot-mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/syscon-reboot.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/syscon-reboot.c

## Purpose
generic syscon/regmap restart driver with optional Google GS101 mode-specific reset data.

## Important APIs, Types, and Functions
`struct reboot_mode_bits`, `struct reboot_data`, `struct syscon_reboot_context`, restart notifier, and probe.

## Control Flow
probe resolves regmap by phandle or parent, parses priority, either uses match data or DT offset/value/mask fallback, then registers restart; notifier selects mode-specific bits when available and updates the register.

## State and Persistence Behavior
context is devm-managed; syscon reset bits persist until reset.

## Dependencies and Integration Points
OF, MFD_SYSCON, regmap, restart notifier, reboot mode enum values.

## Risks and Edge Cases
bad offset/mask can write unrelated syscon bits; mode-specific table covers only selected reboot modes; `reg` legacy alias complicates bindings; no completion beyond timeout log.

## Test Signals
generic syscon reboot DTs, GS101 warm/soft modes, priority ordering, value/mask fallback, and reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/syscon-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/tdx-ec-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/tdx-ec-poweroff.c

## Purpose
Toradex SMARC embedded-controller I2C poweroff/restart driver.

## Important APIs, Types, and Functions
regmap config/access tables, `tdx_ec_cmd()`, poweroff/restart callbacks, registration helper, and I2C probe.

## Control Flow
probe initializes 8-bit I2C regmap, bulk-reads chip ID and firmware version, logs them, and registers firmware-priority restart and poweroff handlers; callbacks write command register and wait one second.

## State and Persistence Behavior
regmap is devm-managed; EC command register is volatile and consumed by controller firmware.

## Dependencies and Integration Points
I2C, regmap cache/access tables, OF compatible `toradex,smarc-ec`, sys-off API.

## Risks and Edge Cases
chip ID is logged but not validated against known constants; if firmware ignores command, kernel only warns after delay; read/write access tables must match EC firmware.

## Test Signals
I2C probe, ID/version read failures, command write failures, poweroff/restart on SMARC iMX8MP/iMX95, and timeout warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/tdx-ec-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/th1520-aon-reboot.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/th1520-aon-reboot.c

## Purpose
T-Head TH1520 AON firmware poweroff/restart auxiliary driver.

## Important APIs, Types, and Functions
packed empty RPC message, poweroff/restart sys-off callbacks, and auxiliary-device probe.

## Control Flow
probe receives `struct th1520_aon_chan` via platform data from PM-domain/AON parent and registers poweroff and restart handlers; callbacks send WDG service RPC functions for power off or restart.

## State and Persistence Behavior
no owned persistent hardware state; AON firmware channel and parent own communication state.

## Dependencies and Integration Points
auxiliary bus, TH1520 AON firmware RPC API, sys-off handlers.

## Risks and Edge Cases
platform_data must be a valid channel; RPC return value is ignored; firmware protocol size constants must match.

## Test Signals
auxiliary match, missing/invalid channel, RPC tracing, poweroff/restart firmware tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/th1520-aon-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/tps65086-restart.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/tps65086-restart.c

## Purpose
TI TPS65086 PMIC restart driver.

## Important APIs, Types, and Functions
`tps65086_restart_notify()` and probe using parent `struct tps65086`.

## Control Flow
probe gets parent MFD data and registers high-priority restart; callback writes `TPS65086_FORCESHUTDN`, delays, and warns if still running.

## State and Persistence Behavior
parent PMIC pointer persists as callback data; PMIC force-shutdown bit persists into reset.

## Dependencies and Integration Points
MFD_TPS65086, regmap, platform IDs, sys-off restart.

## Risks and Edge Cases
parent drvdata is assumed valid; write failure logs but returns done; force-shutdown semantics may power-cycle rather than clean reset depending on board.

## Test Signals
platform child probe, regmap failure, restart behavior, and timeout warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/tps65086-restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/vexpress-poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/vexpress-poweroff.c

## Purpose
ARM Versatile Express config-bus reset/shutdown/reboot driver.

## Important APIs, Types, and Functions
global poweroff/restart devices, restart notifier refcount, sysfs `active` selector, `vexpress_reset_do()`, and platform probe.

## Control Flow
probe initializes vexpress config regmap and dispatches by compatible: shutdown installs `pm_power_off`, reset/reboot register restart handler and optional active sysfs control. Callback writes zero to config function register and waits.

## State and Persistence Behavior
global selected devices and notifier refcount persist; sysfs `active` changes which reset device is used; config writes are consumed by platform firmware.

## Dependencies and Integration Points
VEXPRESS_CONFIG regmap, OF/property match data, legacy poweroff, restart notifier, sysfs.

## Risks and Edge Cases
global mutable active device can be changed by userspace; no remove path for built-in driver; poweroff and restart devices are singleton pointers.

## Test Signals
VExpress reset/shutdown/reboot compatibles, sysfs active switching, config write failure, and board/emulator reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/vexpress-poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/xgene-reboot.c -->
# sources/distributed-fs/ceph-client/drivers/power/reset/xgene-reboot.c

## Purpose
AppliedMicro X-Gene MMIO reboot driver.

## Important APIs, Types, and Functions
`struct xgene_reboot_context`, restart sys-off handler, and platform probe.

## Control Flow
probe allocates context, maps CSR resource, reads optional `mask` defaulting to all bits, and registers restart; callback writes mask and delays/warns.

## State and Persistence Behavior
context is devm-managed; CSR write persists until reset.

## Dependencies and Integration Points
ARM64 X-Gene, OF platform resources, sys-off restart.

## Risks and Edge Cases
mask property must match hardware; no reset completion detection; only restart, not shutdown.

## Test Signals
DT mask values, mapping failure, restart register trace, and reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/reset/xgene-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/power/sequencing/Kconfig

## Purpose
`drivers/power/sequencing/Kconfig` defines the generic Linux power-sequencing subsystem and its provider drivers. The subsystem lets consumers request named power targets from a provider that sequences shared regulators, clocks, GPIOs, and delays.

## Important APIs, Types, and Functions
Important symbols are `POWER_SEQUENCING`, `POWER_SEQUENCING_QCOM_WCN`, `POWER_SEQUENCING_PCIE_M2`, and `POWER_SEQUENCING_THEAD_GPU`. Dependencies pull in OF, regulator, clock, GPIO, PCI/serdev support, and provider-specific platform constraints.

## Control Flow
Kconfig exposes the framework first, then provider drivers. Enabling provider symbols causes `drivers/power/sequencing/Makefile` to build `core.o` and selected providers. Consumer drivers depend on the exported pwrseq API at compile and probe time.

## State and Persistence Behavior
No runtime state exists in Kconfig. Persistent configuration state is carried in `.config` and determines whether the pwrseq bus/framework and providers exist.

## Dependencies and Integration Points
It integrates with kbuild, OF-based embedded platforms, M.2 connector support, Qualcomm WCN PMUs, and T-Head GPU sequencing.

## Risks and Edge Cases
Too-narrow dependencies hide useful providers under compile-test; too-broad dependencies can build providers without required framework APIs. Provider symbols must remain synchronized with Makefile object names.

## Test Signals
Run olddefconfig/allmodconfig, check menu visibility, compile provider combinations, and verify consumers defer cleanly when providers are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/Makefile -->
# sources/distributed-fs/ceph-client/drivers/power/sequencing/Makefile

## Purpose
`drivers/power/sequencing/Makefile` maps power-sequencing Kconfig symbols to framework and provider objects.

## Important APIs, Types, and Functions
It builds `core.o` for `CONFIG_POWER_SEQUENCING`, `pwrseq-qcom-wcn.o` for Qualcomm WCN PMUs, `pwrseq-pcie-m2.o` for M.2 connectors, and `pwrseq-thead-gpu.o` for T-Head GPU sequencing.

## Control Flow
Kbuild evaluates the selected symbols and compiles the core and provider modules/built-ins. Providers rely on `core.o` exporting the pwrseq provider and consumer APIs.

## State and Persistence Behavior
There is no runtime state. Build products persist in the kernel object tree.

## Dependencies and Integration Points
It depends on symbol names in `drivers/power/sequencing/Kconfig` and source filenames in this directory.

## Risks and Edge Cases
If a provider object is listed without the core dependency satisfied, link errors or unresolved exports can occur. Missing entries silently make Kconfig-enabled providers unavailable.

## Test Signals
Build with each provider enabled as built-in and module, compare Kconfig-to-Makefile coverage, and run allmodconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/core.c -->
# sources/distributed-fs/ceph-client/drivers/power/sequencing/core.c

## Purpose
`core.c` implements the Linux power-sequencing framework. It creates a `pwrseq` bus, lets providers register sequencers exposing named targets made from dependency-ordered units, and lets consumers acquire descriptors and call `pwrseq_power_on()`/`pwrseq_power_off()` with shared reference counting.

## Important APIs, Types, and Functions
Important types are private `struct pwrseq_unit`, `pwrseq_unit_dep`, `pwrseq_target`, `pwrseq_device`, and `pwrseq_desc`. Exported APIs are `pwrseq_device_register()`, `pwrseq_device_unregister()`, `devm_pwrseq_device_register()`, `pwrseq_device_get_drvdata()`, `pwrseq_get()`, `devm_pwrseq_get()`, `pwrseq_put()`, `pwrseq_power_on()`, and `pwrseq_power_off()`. Debugfs support exposes target/unit state.

## Control Flow
Provider registration validates config, allocates an ID/device, checks each target dependency graph for cycles with a radix tree, builds unique unit objects and dependency references, and adds the sequencer to the pwrseq bus under `pwrseq_sem`. Consumer lookup scans the bus, invokes provider `.match()`, finds the requested target name, pins the provider module, and returns a descriptor. Power-on locks the provider, recursively enables dependencies before the target, increments enable counts, then runs post-enable outside the state lock. Power-off disables the target and dependencies in reverse when the last user releases them, with rollback on dependency disable failure.

## State and Persistence Behavior
Persistent state includes the global IDA, bus registration, global `pwrseq_sem`, provider devices, unit dependency lists, enable counts, descriptors' `powered_on` flags, and optional debugfs dentry. Provider removal is guarded by device and rwsem references and warns on active users.

## Dependencies and Integration Points
It depends on the driver core bus/device model, krefs, IDA, list/radix-tree helpers, rwsems/mutexes, module owner pinning, cleanup guards, debugfs/seq_file, and public pwrseq consumer/provider headers. Providers in this tree register through the provider API; consumers use the descriptor API.

## Risks and Edge Cases
Reference counting and lock ordering are central risks: provider unregister, consumer lookup, and power transitions must not race. Post-enable failure rolls back after the state lock is reacquired. Dependency-cycle checking uses unit-data pointer identity, so provider static data must be stable. `pwrseq_get()` returns `-EPROBE_DEFER` when no provider matches, which can hide permanent DT mismatches. Removal only warns about active users; misuse can leave hardware on.

## Test Signals
Test provider registration/unregistration, invalid configs, cyclic dependencies, shared dependencies with multiple targets, concurrent consumers, post-enable failure rollback, disable failure rollback, module unload while descriptors exist, debugfs output, and probe-defer behavior when providers appear late.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-pcie-m2.c -->
# sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-pcie-m2.c

## Purpose
`pwrseq-pcie-m2.c` is a power-sequencing provider for PCIe M.2 Key M and Key E connectors. It exposes `pcie` and, for Key E, `uart` targets backed by connector regulators and W_DISABLE GPIOs, and can dynamically create a Bluetooth serdev device for Qualcomm WCN7850 cards discovered over PCIe.

## Important APIs, Types, and Functions
Important state is `struct pwrseq_pcie_m2_ctx` with pwrseq device, connector OF node, regulator array, W_DISABLE GPIOs, PCI notifier, optional serdev, and OF changeset. Unit callbacks bulk-enable regulators and drive `w-disable1`/`w-disable2`; targets include `pcie` and `uart` with optional 50 ms post-enable delay. Matching walks OF graph endpoints to associate consumers with the connector.

## Control Flow
Probe reads match data for Key M or Key E, obtains all regulators from the connector node, gets optional W_DISABLE GPIOs initially high, registers the pwrseq provider, and conditionally registers a PCI bus notifier when the connector has both PCIe and serial graph links. The notifier filters PCI devices by the connector's PCIe endpoint and, for Qualcomm vendor device `0x1107`, creates or removes a serdev child plus a dynamic `bluetooth` OF node.

## State and Persistence Behavior
Persistent state includes regulator handles, GPIO output levels, pwrseq units' enable counts in the core, PCI notifier registration, optional serdev device, and an OF changeset that must be reverted on removal. Hardware rails and W_DISABLE lines persist while targets are powered.

## Dependencies and Integration Points
It depends on OF graph bindings for M.2 connectors, regulator bulk APIs including `of_regulator_bulk_get_all()`, GPIO descriptors, PCI bus notifiers, serdev, dynamic OF changesets, and the pwrseq provider core.

## Risks and Edge Cases
The WCN7850 serdev creation path is tightly coupled to PCI discovery order and graph port numbers. Regulator arrays are manually freed, so error/remove paths must stay balanced. A fixed 50 ms delay is a known FIXME because not all cards need it. Optional GPIO absence is allowed, so target semantics depend on connector wiring. Notifier unregister is called even if no notifier was registered, relying on core tolerance.

## Test Signals
Test Key M and Key E DT graph matching, regulator failure paths, W_DISABLE GPIO polarity, shared regulator refcounts through pwrseq core, PCI add/remove notifier filtering, WCN7850 serdev creation/removal and changeset rollback, and module removal with powered targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-pcie-m2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-qcom-wcn.c -->
# sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-qcom-wcn.c

## Purpose
`pwrseq-qcom-wcn.c` is a Qualcomm WCN Bluetooth/WLAN PMU power-sequencing provider. It models chip-specific regulator sets, optional VDDIO, reference clock, enable GPIOs, XO clock GPIO sequencing, inter-GPIO delays, and named `bluetooth` and `wlan` targets for consumers.

## Important APIs, Types, and Functions
Important data types are `struct pwrseq_qcom_wcn_pdata` for per-compatible regulator/delay/target/match data and `struct pwrseq_qcom_wcn_ctx` for runtime handles. Unit callbacks enable VDDIO, regulator bulks, clocks, BT/WLAN GPIOs, and WCN6855 XO assert/deassert sequencing. Match helpers associate consumers by regulator phandles such as `vddaon-supply`, `vddio-supply`, or `vdd-1.8-xo-supply`.

## Control Flow
Probe selects compatible data for WCN3950/3988/3990/3991/3998, QCA6390, WCN6750, WCN6855, or WCN7850; allocates regulator bulk data; gets regulators, optional VDDIO, BT/WLAN/XO GPIOs, and optional clock; preserves existing WLAN GPIO value while forcing output; then registers the pwrseq provider. Power-on follows dependency order: regulators and clock first, optional XO assertion, target GPIO enable with required spacing, then post-enable delay or XO deassert delay.

## State and Persistence Behavior
Persistent state includes regulator/clock/GPIO handles, `last_gpio_enable_jf` for spacing BT/WLAN enables, pwrseq core enable counts, and physical rail/GPIO/clock states while targets are on.

## Dependencies and Integration Points
It depends on OF platform matching, regulator bulk APIs, optional clocks, GPIO descriptors, jiffies/delay helpers, and the pwrseq provider framework. Consumer matching depends on DT supply phandles pointing back to this PMU node.

## Risks and Edge Cases
The WLAN GPIO uses `GPIOD_ASIS` to avoid dropping an already enumerated PCIe link, a deliberate workaround until controller link-down handling improves. Regulator phandle matching is topology-sensitive and can fail on unusual regulator node layouts. Delay values are chip data, so incorrect compatibles can violate hardware timing. Shared BT/WLAN targets require careful enable-count behavior in the core.

## Test Signals
Test every compatible's regulator names, optional VDDIO and clock handling, BT and WLAN target power-on/off independently and together, GPIO delay enforcement, WCN6855 XO timing, WLAN-as-is preservation, phandle matching failures, and provider removal while consumers defer or hold descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-qcom-wcn.c -->
