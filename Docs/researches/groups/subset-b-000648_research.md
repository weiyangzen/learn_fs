# subset-b-000648 research

Grouped research for ceph-client Linux ARM platform support under MVEBU, MXS, Nomadik, NPCM, and OMAP1. Each file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp.S

Purpose: Armada XP secondary CPU assembly entry point. It switches to BE8 when needed, calls low-level coherency helpers, joins the SMP group, enables hardware coherency, and branches into the generic ARM `secondary_startup` path.

Important APIs/types/functions: `armada_xp_secondary_startup` is the only exported entry. It depends on `ll_add_cpu_to_smp_group`, `ll_enable_coherency`, `secondary_startup`, ARM assembler macros, and the coherency low-level implementation in the same platform.

Control flow, state, and persistence: The control path is intentionally short because it runs before normal C runtime setup on a secondary CPU. Persistent state is only the hardware coherency fabric registers touched by the helper calls.

Dependencies and integration points: `armada_xp_secondary_startup` is the only exported entry. It depends on `ll_add_cpu_to_smp_group`, `ll_enable_coherency`, `secondary_startup`, ARM assembler macros, and the coherency low-level implementation in the same platform. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: If the hard-coded early coherency assumptions drift from the SoC memory map, secondary CPUs can hang before console output is available. Test with SMP boot, CPU hotplug, kexec, and both endian configurations on Armada XP.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 37 lines, 1000 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.c

Purpose: Standby power-management support for Marvell Kirkwood. It maps DDR operation and memory power-control registers and registers suspend callbacks for `PM_SUSPEND_STANDBY`.

Important APIs/types/functions: `kirkwood_pm_init`, `kirkwood_low_power`, `kirkwood_suspend_enter`, and `kirkwood_pm_valid_standby` integrate with Linux suspend through `platform_suspend_ops` and `suspend_set_ops`.

Control flow, state, and persistence: Suspend saves `MEMORY_PM_CTRL`, forces peripheral low power, requests DDR self-refresh, executes `cpu_do_idle`, then restores the saved register. State persists only in the mapped hardware registers.

Dependencies and integration points: `kirkwood_pm_init`, `kirkwood_low_power`, `kirkwood_suspend_enter`, and `kirkwood_pm_valid_standby` integrate with Linux suspend through `platform_suspend_ops` and `suspend_set_ops`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: The code assumes `ioremap` succeeds and only supports standby. Risks are bad physical constants, missing wake sources, and relaxed-write ordering around DDR self-refresh. Test standby/resume, serial wake, peripheral retention, and suspend rejection for unsupported states.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 68 lines, 1495 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.h

Purpose: Small conditional header for Kirkwood PM initialization. It lets Kirkwood machine setup call PM code unconditionally while compiling to a no-op when `CONFIG_PM` is disabled.

Important APIs/types/functions: The visible API is `kirkwood_pm_init()`, either declared for the PM object or defined as an inline empty function.

Control flow, state, and persistence: There is no runtime state in the header. Its behavior is compile-time selection through Kconfig.

Dependencies and integration points: The visible API is `kirkwood_pm_init()`, either declared for the PM object or defined as an inline empty function. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: The main risk is silent loss of suspend registration when PM is disabled or the header guard/API diverges from `kirkwood-pm.c`. Test by building Kirkwood with and without `CONFIG_PM`.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 18 lines, 403 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood-pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.c

Purpose: Device-tree machine initialization for Marvell Kirkwood. It registers cpufreq/cpuidle platform devices, patches Ethernet MAC addresses from controller registers, applies an MBUS error-propagation workaround, initializes PM, and populates DT devices.

Important APIs/types/functions: Important functions are `kirkwood_cpufreq_init`, `kirkwood_cpuidle_init`, `kirkwood_dt_eth_fixup`, `kirkwood_disable_mbus_error_propagation`, and `kirkwood_dt_init`; the machine descriptor is `KIRKWOOD_DT`.

Control flow, state, and persistence: Control flow starts at `kirkwood_dt_init`, performs legacy board fixes before `of_platform_default_populate`, and then registers CPU power helpers. The Ethernet fixup dynamically allocates a `local-mac-address` DT property when firmware left it unset.

Dependencies and integration points: Important functions are `kirkwood_cpufreq_init`, `kirkwood_cpuidle_init`, `kirkwood_dt_eth_fixup`, `kirkwood_disable_mbus_error_propagation`, and `kirkwood_dt_init`; the machine descriptor is `KIRKWOOD_DT`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT, clk, of_iomap, mv643xx Ethernet register layout, MBUS bridge registers, Feroceon L2, common MVEBU helpers, and Kirkwood PM. Risks include leaked properties by design, clock/map failures skipping MAC repair, and SoC-specific register assumptions. Test boot on boards with and without DT MACs, cpufreq/cpuidle probe, MBUS workaround, and standby.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 192 lines, 4712 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.h

Purpose: Kirkwood physical register definition header shared by platform initialization and PM. It centralizes the CPU control, DDR operation, and memory power-control addresses.

Important APIs/types/functions: The exported constants are `DDR_OPERATION_BASE`, `MEMORY_PM_CTRL_PHYS`, and `CPU_CONTROL_PHYS`; there are no functions or types.

Control flow, state, and persistence: State is not stored here; consumers use these constants for `ioremap` or platform resources.

Dependencies and integration points: The exported constants are `DDR_OPERATION_BASE`, `MEMORY_PM_CTRL_PHYS`, and `CPU_CONTROL_PHYS`; there are no functions or types. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: The risk is stale SoC address data because the constants directly select hardware registers. Test users through cpufreq resource registration and Kirkwood standby/cpuidle paths.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 19 lines, 609 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.c

Purpose: MVEBU SoC identification support. It discovers Armada SoC device/revision IDs either through system-controller helpers or, for Armada 370/XP, through PCI vendor/device/class configuration space, then registers a Linux `soc_device`.

Important APIs/types/functions: `mvebu_get_soc_id`, `get_soc_id_by_pci`, `mvebu_soc_id_init`, and `mvebu_soc_device` are the main routines. Globals cache `soc_dev_id` and `soc_rev` after early init.

Control flow, state, and persistence: Control flow prefers `mvebu_system_controller_get_soc_id`; if unavailable on Armada 370/XP it scans PCI buses/devices, filters vendor/class, and reads revision. `postcore_initcall` formats IDs and creates sysfs SoC metadata.

Dependencies and integration points: `mvebu_get_soc_id`, `get_soc_id_by_pci`, `mvebu_soc_id_init`, and `mvebu_soc_device` are the main routines. Globals cache `soc_dev_id` and `soc_rev` after early init. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include PCI, DT machine compatibility, system-controller code, and `sys_soc`. Risks are absent PCI enumeration at early init, incorrect fallback on unsupported machines, and `-EINVAL` cached IDs suppressing soc registration. Test sysfs SoC attributes on Armada 370/XP and newer system-controller platforms.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 175 lines, 4070 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.h

Purpose: Public header for MVEBU SoC ID lookup. It hides whether SoC ID support is compiled in and provides symbolic PCI device IDs for Armada 370 and XP.

Important APIs/types/functions: The API is `mvebu_get_soc_id(u32 *dev, u32 *rev)`, with an inline `-1` fallback when `CONFIG_CACHE_L2X0` is not enabled.

Control flow, state, and persistence: It stores no state itself; the C file owns cached IDs. Compile-time selection means callers must handle failure.

Dependencies and integration points: The API is `mvebu_get_soc_id(u32 *dev, u32 *rev)`, with an inline `-1` fallback when `CONFIG_CACHE_L2X0` is not enabled. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are the surprising dependency on `CONFIG_CACHE_L2X0` and broad fallback return value. Test callers with the option enabled/disabled and on platforms that do not expose SoC ID.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 51 lines, 1076 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/mvebu-soc-id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp-a9.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp-a9.c

Purpose: SMP support for MVEBU Cortex-A9 SoCs such as Armada 375/38x/39x. It writes the secondary startup address, wakes the target CPU, deasserts reset, and supplies Armada 38x hotplug hooks.

Important APIs/types/functions: Key routines are `mvebu_cortex_a9_boot_secondary`, `armada_38x_secondary_init`, `armada_38x_cpu_die`, and `armada_38x_cpu_kill`; CPU methods are declared for `marvell,armada-375-smp`, `-380-smp`, and `-390-smp`.

Control flow, state, and persistence: Boot flow maps Linux CPU to hardware CPU, stores the startup address in either system-controller or PMSU registers, issues a memory barrier, sends a wake IPI, then deasserts reset. Hotplug-offlined CPUs enter deep idle and exit through PMSU idle cleanup.

Dependencies and integration points: Key routines are `mvebu_cortex_a9_boot_secondary`, `armada_38x_secondary_init`, `armada_38x_cpu_die`, and `armada_38x_cpu_kill`; CPU methods are declared for `marvell,armada-375-smp`, `-380-smp`, and `-390-smp`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT compatible strings, `mvebu_cpu_reset_deassert`, PMSU, system-controller boot address registers, and generic ARM SMP. Risks are wrong boot-address backend per SoC and broken deep-idle hotplug. Test SMP boot, CPU online/offline, and kexec on Armada 375 versus 38x/39x.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 111 lines, 3245 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp-a9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp.c

Purpose: Armada XP and 98DX3236 SMP support. It validates BootROM mapping, prepares coherency, synchronizes CPU clocks, sets per-CPU boot vectors, deasserts reset, and provides CPU hotplug by deep-idle entry.

Important APIs/types/functions: Important routines include `armada_xp_boot_secondary`, `armada_xp_smp_init_cpus`, `armada_xp_smp_prepare_cpus`, `armada_xp_sync_secondary_clk`, 98DX resume/boot helpers, and the `armada_xp_smp_ops`/`mv98dx3236_smp_ops` CPU methods.

Control flow, state, and persistence: The primary control path flushes caches, marks the boot CPU coherent, checks the bootrom DT resource equals `0xfff00000/1MiB`, captures boot CPU clock rate, and later writes PMSU or resume-controller boot addresses before waking secondary CPUs.

Dependencies and integration points: Important routines include `armada_xp_boot_secondary`, `armada_xp_smp_init_cpus`, `armada_xp_smp_prepare_cpus`, `armada_xp_sync_secondary_clk`, 98DX resume/boot helpers, and the `armada_xp_smp_ops`/`mv98dx3236_smp_ops` CPU methods. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: State includes the cached boot CPU clock and hardware boot-address registers. Dependencies are DT, clock framework, PMSU, CPU reset, coherency fabric, and BootROM layout. Risks include panic on DT mapping mismatches, clock-reference leaks, and platform-specific CPU count limits. Test SMP boot, hotplug, clock rates, and 98DX single-secondary assumptions.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 255 lines, 6468 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm-board.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm-board.c

Purpose: Board-level suspend glue for Armada 370/XP/38x/39x. It locates SDRAM and SDRAM controller registers and supplies a board-specific `pm_enter` hook to the generic MVEBU PM layer.

Important APIs/types/functions: `mvebu_armada_pm_enter` programs SDRAM self-refresh and low-power commands; `mvebu_armada_pm_init` parses `marvell,armada-xp-sdram-controller` and memory nodes and calls `mvebu_pm_suspend_init`.

Control flow, state, and persistence: Suspend state is hardware register state: source-command bits, SDRAM windows, and controller timing. The init path derives the first memory resource and maps the SDRAM controller once for later suspend.

Dependencies and integration points: `mvebu_armada_pm_enter` programs SDRAM self-refresh and low-power commands; `mvebu_armada_pm_init` parses `marvell,armada-xp-sdram-controller` and memory nodes and calls `mvebu_pm_suspend_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT memory nodes, SDRAM controller compatible strings, `mvebu_pm_suspend_init`, and low-level suspend code. Risks are incorrect memory-node assumptions, missing register maps, and board PM registration failing silently. Test suspend-to-RAM on each Armada family, resume address correctness, and systems with multiple memory banks.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 144 lines, 3312 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm-board.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm.c

Purpose: Generic MVEBU suspend implementation. It saves boot information, copies low-level powerdown code to SRAM, invokes `cpu_suspend`, coordinates board SDRAM powerdown, and registers `platform_suspend_ops`.

Important APIs/types/functions: Important routines include `mvebu_pm_powerdown`, `mvebu_internal_reg_base`, `mvebu_pm_store_armadaxp_bootinfo`, `mvebu_pm_store_bootinfo`, `mvebu_enter_suspend`, `mvebu_pm_enter`, and `mvebu_pm_suspend_init`.

Control flow, state, and persistence: The suspend path persists resume metadata in SRAM or SoC-specific registers, sets the boot address to resume code, saves internal register base information, and calls board PM entry before executing the low-power sequence.

Dependencies and integration points: Important routines include `mvebu_pm_powerdown`, `mvebu_internal_reg_base`, `mvebu_pm_store_armadaxp_bootinfo`, `mvebu_pm_store_bootinfo`, `mvebu_enter_suspend`, `mvebu_pm_enter`, and `mvebu_pm_suspend_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include ARM `cpu_suspend`, SRAM helpers, PMSU/system controller, MBUS/internal register windows, and board-level PM callbacks. Risks include wrong SRAM copy size/address, incomplete bootinfo for newer SoCs, and resume failure after memory-controller changes. Test standby/mem suspend, resume on Armada XP/38x, invalid suspend state rejection, and early-init failures.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 267 lines, 6299 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.c

Purpose: Power Management Service Unit support for MVEBU v7 SoCs. It maps PMSU registers, redirects CPU boot addresses, implements deep-idle/cpuidle/hotplug suspend entry, applies BootROM workarounds, and triggers dynamic frequency scaling transitions.

Important APIs/types/functions: Key APIs are `mvebu_pmsu_set_cpu_boot_addr`, `mvebu_setup_boot_addr_wa`, `armada_370_xp_pmsu_idle_enter`, `armada_38x_do_cpu_suspend`, `mvebu_v7_pmsu_idle_exit`, and `mvebu_pmsu_dfs_request`; init is via `early_initcall` and `arch_initcall`.

Control flow, state, and persistence: State includes `pmsu_mp_base`, `pmsu_mp_phys_base`, selected CPU resume function, and a cpuidle platform device. Idle preparation sets per-CPU wait, wake, mask, L2 powerdown, and DFS bits before WFI; exit clears those bits.

Dependencies and integration points: Key APIs are `mvebu_pmsu_set_cpu_boot_addr`, `mvebu_setup_boot_addr_wa`, `armada_370_xp_pmsu_idle_enter`, `armada_38x_do_cpu_suspend`, `mvebu_v7_pmsu_idle_exit`, and `mvebu_pmsu_dfs_request`; init is via `early_initcall` and `arch_initcall`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT PMSU bindings, MBUS windows, SRAM/BootROM workarounds, SCU, CPU PM notifiers, cache/TLB maintenance, and low-level assembly resume code. Risks include disabled Armada 38x idle, timeout-prone DFS polling, register races if CPU mapping is wrong, and fatal resume if boot-address workaround fails. Test cpuidle, CPU hotplug, suspend/resume, DFS on each CPU, and broken-idle DT property handling.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 607 lines, 16597 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.h

Purpose: Internal header for MVEBU PMSU and low-level resume helpers. It exposes the small set of routines needed by SMP, cpuidle, and PM code without exporting PMSU register details.

Important APIs/types/functions: Declarations include `armada_xp_boot_cpu`, `mvebu_setup_boot_addr_wa`, `mvebu_v7_pmsu_idle_exit`, `armada_370_xp_cpu_resume`, `armada_370_xp_pmsu_idle_enter`, and `armada_38x_do_cpu_suspend`.

Control flow, state, and persistence: There is no state in the header; it binds C code to assembly symbols and PMSU implementation functions.

Dependencies and integration points: Declarations include `armada_xp_boot_cpu`, `mvebu_setup_boot_addr_wa`, `mvebu_v7_pmsu_idle_exit`, `armada_370_xp_cpu_resume`, `armada_370_xp_pmsu_idle_enter`, and `armada_38x_do_cpu_suspend`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are signature drift across C/assembly boundaries and missing declarations when low-level resume paths change. Test all MVEBU PM/SMP objects in one build with hotplug and suspend enabled.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 21 lines, 688 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu_ll.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu_ll.S

Purpose: Low-level MVEBU resume and boot workaround assembly. It contains resume entry points for Armada 370/XP and Armada 38x plus a tiny BootROM replacement snippet copied to SRAM.

Important APIs/types/functions: Symbols include `armada_38x_scu_power_up`, `armada_370_xp_cpu_resume`, `armada_38x_cpu_resume`, and `mvebu_boot_wa_start/end`.

Control flow, state, and persistence: Control flow runs before normal kernel C context: resume code re-enables coherency or SCU state, returns through ARM CPU resume machinery, and the boot workaround reads a PMSU boot address register then jumps to it.

Dependencies and integration points: Symbols include `armada_38x_scu_power_up`, `armada_370_xp_cpu_resume`, `armada_38x_cpu_resume`, and `mvebu_boot_wa_start/end`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include ARM assembler macros, CPU resume conventions, PMSU boot-address register layout, and coherency helpers. Risks are instruction-size/layout assumptions, endianness, and copied-code patching of the last word with a register address. Test suspend/resume on Armada 370/XP/38x and verify SRAM workaround code length/patched address.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 71 lines, 1853 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu_ll.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/system-controller.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/system-controller.c

Purpose: MVEBU system-controller support for restart, SoC identification, Armada 375 SMP workaround, and CPU boot address storage. It maps the system-controller node early and exposes helpers used by SMP and PM.

Important APIs/types/functions: Important APIs are `mvebu_restart`, `mvebu_system_controller_get_soc_id`, `mvebu_system_controller_set_cpu_boot_addr`, and `mvebu_system_controller_init`.

Control flow, state, and persistence: State is the mapped controller base, selected register offsets, and compatible-driven feature bits. Restart writes reset-request bits; SoC ID reads dev/rev fields; boot address writes the physical startup address to a shared register.

Dependencies and integration points: Important APIs are `mvebu_restart`, `mvebu_system_controller_get_soc_id`, `mvebu_system_controller_set_cpu_boot_addr`, and `mvebu_system_controller_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT compatible strings for Armada controllers, `__pa_symbol`, reboot framework, and optional BootROM workaround setup. Risks are incompatible register offset tables, early mapping failure, and SMP boot address writes before init. Test reboot, sysfs SoC ID, Armada 375 secondary boot, and missing-controller fallback.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 177 lines, 4683 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/system-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Kconfig

Purpose: Kconfig definitions for Freescale MXS i.MX23/i.MX28 platform support. It selects ARM926T, AMBA, pinctrl, timer, GPIO, STMP device support, and CPU suspend when PM is enabled.

Important APIs/types/functions: Symbols are `SOC_IMX23`, `SOC_IMX28`, and user-visible `ARCH_MXS` under `ARCH_MULTI_V5` and little-endian constraints.

Control flow, state, and persistence: There is no runtime state. The file controls which platform objects and drivers can be built.

Dependencies and integration points: Symbols are `SOC_IMX23`, `SOC_IMX28`, and user-visible `ARCH_MXS` under `ARCH_MULTI_V5` and little-endian constraints. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are over-selecting both SoCs for any MXS build and missing dependencies for DT-only boards. Test `olddefconfig` and build coverage with and without `CONFIG_PM`.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 28 lines, 569 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Makefile

Purpose: Build glue for Freescale MXS machine support. It compiles suspend support when PM is enabled and the DT machine file when `ARCH_MXS` is selected.

Important APIs/types/functions: Targets are `pm.o` and `mach-mxs.o`.

Control flow, state, and persistence: No runtime state exists; the file only controls object inclusion.

Dependencies and integration points: Targets are `pm.o` and `mach-mxs.o`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are simple Kconfig/object mismatches. Test MXS builds with PM on and off.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 3 lines, 102 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/mach-mxs.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mxs/mach-mxs.c

Purpose: Device-tree machine support for Freescale MXS. It reads OCOTP fuses, patches Ethernet MAC addresses, registers SoC metadata, runs board-specific fixups, populates DT devices, and installs a restart handler.

Important APIs/types/functions: Important functions include `mxs_get_ocotp`, `update_fec_mac_prop`, board init helpers, `mxs_get_soc_id`, `mxs_get_cpu_rev`, `mxs_restart_init`, `mxs_machine_init`, and `mxs_restart`.

Control flow, state, and persistence: The control path caches OCOTP words under a mutex, maps DIGCTL to derive chip/revision, registers a `soc_device`, applies compatible-string fixups for EVK/APF28/APX4/Crystalfontz/Duckbill/M28CU3, then maps CLKCTRL reset registers.

Dependencies and integration points: Important functions include `mxs_get_ocotp`, `update_fec_mac_prop`, board init helpers, `mxs_get_soc_id`, `mxs_get_cpu_rev`, `mxs_restart_init`, `mxs_machine_init`, and `mxs_restart`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: State includes cached OCOTP words, `chipid`, `socid`, system serial fields, and `reset_addr`. Dependencies include DT, OCOTP/DIGCTL/CLKCTRL registers, clk helpers, PHY fixups, SoC bus, and platform population. Risks include unchecked OCOTP map failures, board OUI hard-coding, and reset fallback through address zero. Test MAC fixups, SoC sysfs, board quirks, reboot, and OCOTP timeout handling.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 480 lines, 10610 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/mach-mxs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.c

Purpose: Minimal MXS suspend hook. It registers ARM CPU suspend support for standby and delegates actual low-level entry to `mxs_suspend`.

Important APIs/types/functions: APIs are `mxs_pm_init`, `mxs_suspend_enter`, and `mxs_suspend_valid` through `platform_suspend_ops`.

Control flow, state, and persistence: Runtime state is held by the suspend framework. The file does not persist data; it only validates `PM_SUSPEND_STANDBY` and calls `cpu_suspend(0, mxs_suspend)`.

Dependencies and integration points: APIs are `mxs_pm_init`, `mxs_suspend_enter`, and `mxs_suspend_valid` through `platform_suspend_ops`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include `CONFIG_PM`, ARM CPU suspend, and the external low-level `mxs_suspend` routine. Risks are unsupported suspend states and low-level resume failures. Test standby/resume and no-PM builds.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 32 lines, 561 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.h

Purpose: Header for MXS PM initialization. It exposes `mxs_pm_init()` when PM is enabled and an inline no-op otherwise.

Important APIs/types/functions: There are no types or runtime data; compile-time `CONFIG_PM` controls behavior.

Control flow, state, and persistence: The header integrates with the MXS machine descriptor's `.init_late` hook.

Dependencies and integration points: There are no types or runtime data; compile-time `CONFIG_PM` controls behavior. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are silent no-op behavior in non-PM builds and declaration mismatch with `pm.c`. Test compile coverage with `CONFIG_PM=y/n`.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 15 lines, 240 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mxs/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Kconfig

Purpose: Kconfig for ST-Ericsson Nomadik STn8815 platform support. It selects the ARM926T, VIC, MTU timer, GPIO, syscon, pinctrl, and board-specific I2C support for the NHK board.

Important APIs/types/functions: Symbols include `ARCH_NOMADIK`, `MACH_NOMADIK_8815NHK`, and `NOMADIK_8815`.

Control flow, state, and persistence: It has no runtime state; it constrains build-time inclusion and driver availability.

Dependencies and integration points: Symbols include `ARCH_NOMADIK`, `MACH_NOMADIK_8815NHK`, and `NOMADIK_8815`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks include legacy board dependency on non-DT pieces and broad selected dependencies. Test multi-v5 builds and NHK board config.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 32 lines, 648 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Makefile

Purpose: Build glue for Nomadik. It compiles `cpu-8815.o` when `NOMADIK_8815` is selected.

Important APIs/types/functions: The file has no functions or runtime state.

Control flow, state, and persistence: It integrates Kconfig with the legacy machine descriptor implementation.

Dependencies and integration points: The file has no functions or runtime state. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are object omission if Kconfig symbols change. Test ARCH_NOMADIK builds.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 12 lines, 347 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/cpu-8815.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/cpu-8815.c

Purpose: Nomadik STn8815 machine support. It maps UART1 for early debug, provides a reset hook through the SRC block, and declares DT compatibility for supported boards.

Important APIs/types/functions: Important routines are `cpu8815_map_io`, `cpu8815_restart`, and the `NOMADIK_DT` machine descriptor.

Control flow, state, and persistence: Runtime state is limited to a static `map_desc` and transient SRC `ioremap` during restart. The machine descriptor supplies L2 cache mask values and compatible strings.

Dependencies and integration points: Important routines are `cpu8815_map_io`, `cpu8815_restart`, and the `NOMADIK_DT` machine descriptor. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include hard-coded STn8815 physical addresses, early iotable mapping, SRC reset register semantics, and DT board compatibles. Risks include missing `iounmap` in restart path, no error check for SRC mapping, and reliance on fixed UART virtual address. Test earlyprintk, reboot, and DT match for NHK/USB-S8815.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 96 lines, 3621 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-nomadik/cpu-8815.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Kconfig

Purpose: Kconfig for Nuvoton NPCM BMC platforms. It supports WPCM450 on ARMv5 and NPCM7xx on ARMv7, selecting timer, pinctrl, GIC/SCU/TWD, errata, PL310 workarounds, GPIO, and syscon as needed.

Important APIs/types/functions: Symbols are `ARCH_NPCM`, `ARCH_WPCM450`, and `ARCH_NPCM7XX`.

Control flow, state, and persistence: No runtime state exists. The file defines architecture and SoC support boundaries.

Dependencies and integration points: Symbols are `ARCH_NPCM`, `ARCH_WPCM450`, and `ARCH_NPCM7XX`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are architecture dependency mismatches and SMP errata selections. Test allmodconfig-style ARMv5 and ARMv7 NPCM builds.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 41 lines, 954 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Makefile

Purpose: Build glue for NPCM platforms. It includes WPCM450, NPCM7xx, and SMP startup objects based on Kconfig.

Important APIs/types/functions: Targets are `wpcm450.o`, `npcm7xx.o`, `platsmp.o`, and `headsmp.o`.

Control flow, state, and persistence: It has no runtime state; it controls object inclusion.

Dependencies and integration points: Targets are `wpcm450.o`, `npcm7xx.o`, `platsmp.o`, and `headsmp.o`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are compiling SMP helpers for incompatible non-NPCM SMP builds through broad `CONFIG_SMP`. Test WPCM450 uniprocessor and NPCM7xx SMP builds.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 4 lines, 162 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/headsmp.S

Purpose: NPCM7xx secondary CPU startup shim. It compensates for boot ROM not entering secondaries in SVC mode, masks interrupts, and jumps to generic ARM secondary startup.

Important APIs/types/functions: The single symbol is `npcm7xx_secondary_startup`, using `safe_svcmode_maskall` and `secondary_startup`.

Control flow, state, and persistence: State changes are CPU mode and interrupt masks; no memory state is stored by the file.

Dependencies and integration points: The single symbol is `npcm7xx_secondary_startup`, using `safe_svcmode_maskall` and `secondary_startup`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include ARMv7 assembler support and the SMP boot code writing this physical address to the GCR scratchpad. Test secondary CPU boot and hotplug on NPCM7xx.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 19 lines, 428 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/headsmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/npcm7xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/npcm7xx.c

Purpose: Machine descriptor for Nuvoton NPCM7xx Cortex-A9 BMC SoCs. It declares the DT compatible and L2 cache auxiliary values.

Important APIs/types/functions: The primary artifact is `DT_MACHINE_START(NPCM7XX_DT)` with compatible `nuvoton,npcm750` and `atag_offset` 0x100.

Control flow, state, and persistence: No mutable runtime state is kept in this file; boot-time machine matching drives integration.

Dependencies and integration points: The primary artifact is `DT_MACHINE_START(NPCM7XX_DT)` with compatible `nuvoton,npcm750` and `atag_offset` 0x100. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT, PL310/L2 cache support, and ARM machine descriptor infrastructure. Test DT boot with NPCM750 board files and cache initialization.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 22 lines, 533 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/npcm7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/platsmp.c

Purpose: NPCM7xx SMP bring-up. It enables the Cortex-A9 SCU and writes the secondary startup physical address into the GCR scratchpad before sending an event.

Important APIs/types/functions: Main functions are `npcm7xx_smp_prepare_cpus`, `npcm7xx_smp_boot_secondary`, and the CPU method for `nuvoton,npcm750-smp`.

Control flow, state, and persistence: Control flow maps the SCU node to call `scu_enable`; boot-secondary maps `nuvoton,npcm750-gcr`, writes `__pa_symbol(npcm7xx_secondary_startup)` at `NPCM7XX_SCRPAD_REG`, and executes `dsb_sev()`.

Dependencies and integration points: Main functions are `npcm7xx_smp_prepare_cpus`, `npcm7xx_smp_boot_secondary`, and the CPU method for `nuvoton,npcm750-smp`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT SCU/GCR nodes, physical address translation, and `headsmp.S`. Risks are per-boot remapping overhead, missing node cleanup on some error paths, and scratchpad register offset drift. Test SMP boot, DT node absence errors, and secondary CPU mode.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 78 lines, 1791 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/wpcm450.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-npcm/wpcm450.c

Purpose: Machine descriptor for Nuvoton WPCM450 ARM926 BMC SoCs. It provides a DT match table and machine name.

Important APIs/types/functions: The only runtime integration point is `DT_MACHINE_START(WPCM450_DT)` with compatible `nuvoton,wpcm450`.

Control flow, state, and persistence: There is no file-local state or device registration; DT population and selected drivers do the work.

Dependencies and integration points: The only runtime integration point is `DT_MACHINE_START(WPCM450_DT)` with compatible `nuvoton,wpcm450`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are missing board-specific init for legacy hardware assumptions. Test basic DT boot, timer, interrupt controller, and pinctrl availability.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 13 lines, 271 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-npcm/wpcm450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Kconfig

Purpose: Configuration tree for legacy TI OMAP1 platforms. It selects shared OMAP infrastructure, timers, GPIO, IRQ chips, board types, mux support, clock reset options, serial wake, and board-specific dependencies.

Important APIs/types/functions: Important symbols include `ARCH_OMAP1`, `ARCH_OMAP15XX`, `ARCH_OMAP16XX`, `OMAP_MUX`, `OMAP_32K_TIMER`, `OMAP_MPU_TIMER`, and board symbols for OSK, PalmTE, SX1, Nokia770, and AMS Delta.

Control flow, state, and persistence: No runtime state exists, but selected symbols determine machine descriptors, timers, PM, FIQ, regulators, and device objects.

Dependencies and integration points: Important symbols include `ARCH_OMAP1`, `ARCH_OMAP15XX`, `ARCH_OMAP16XX`, `OMAP_MUX`, `OMAP_32K_TIMER`, `OMAP_MPU_TIMER`, and board symbols for OSK, PalmTE, SX1, Nokia770, and AMS Delta. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are legacy ATAGS dependency, mutually broad board selections, and drivers relying on selected clock/mux options. Test representative defconfigs for each board and PM/timer combinations.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 164 lines, 4532 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Makefile

Purpose: OMAP1 object list. It links common SoC support, clocks, timers, reset, PM, optional I2C/USB/MCBSP support, board files, FIQ code, and SoC-specific GPIO implementations.

Important APIs/types/functions: The main integration is Kbuild object selection through `obj-y`, `obj-$(CONFIG_...)`, and conditional composite variables.

Control flow, state, and persistence: No runtime state exists; build inclusion determines which initcalls and machine descriptors are present.

Dependencies and integration points: The main integration is Kbuild object selection through `obj-y`, `obj-$(CONFIG_...)`, and conditional composite variables. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are accidental inclusion of board glue in multi-board kernels or missing companion assembly for AMS Delta FIQ. Test builds for each board and with optional USB/I2C/MMC/PM toggles.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 41 lines, 1110 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq-handler.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq-handler.S

Purpose: Fast interrupt handler for the Amstrad E3 QWERTY keyboard and selected GPIO interrupts. It runs in FIQ context, samples keyboard clock/data edges, pushes key bits into a shared circular buffer, counts GPIO events, and triggers a deferred IRQ.

Important APIs/types/functions: Symbols are `qwerty_fiqin_start` and `qwerty_fiqin_end`; offsets come from `ams-delta-fiq.h` and platform data headers.

Control flow, state, and persistence: State is the shared `fiq_buffer` addressed through FIQ register r9, GPIO/IRQ controller registers, key state, circular head/tail offsets, counters, and missed-key fields.

Dependencies and integration points: Symbols are `qwerty_fiqin_start` and `qwerty_fiqin_end`; offsets come from `ams-delta-fiq.h` and platform data headers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP1510 GPIO register layout, interrupt-controller virtual addresses, FIQ size limit at vector copy address, and the C initializer. Risks are extremely tight assembly/register coupling, buffer corruption, and edge-count desynchronization. Test keyboard input under load, modem IRQ deferral, buffer overflow counters, and FIQ handler size.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 275 lines, 8813 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq-handler.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.c

Purpose: C setup and deferred interrupt handling for the Amstrad Delta FIQ keyboard path. It claims the FIQ vector, installs assembly code, initializes the shared buffer, reserves keyboard GPIOs, and forwards FIQ-counted GPIO events into normal IRQ handlers.

Important APIs/types/functions: Important APIs are `ams_delta_init_fiq` and the internal `deferred_fiq` ISR. It uses `claim_fiq`, `set_fiq_handler`, `set_fiq_regs`, `request_irq`, GPIO descriptors, and generic IRQ dispatch.

Control flow, state, and persistence: Persistent state includes `fiq_buffer`, cached GPIO IRQ data, the FIQ handler registration, and per-GPIO IRQ counters. The serio platform device is patched with the keyboard IRQ and buffer pointer.

Dependencies and integration points: Important APIs are `ams_delta_init_fiq` and the internal `deferred_fiq` ISR. It uses `claim_fiq`, `set_fiq_handler`, `set_fiq_regs`, `request_irq`, GPIO descriptors, and generic IRQ dispatch. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include gpio-omap default edge handler behavior, OMAP interrupt registers, the assembly symbols, and AMS Delta board code. Risks are leaked own-desc GPIOs by design, fragile IRQ type programming, and missed event replay if counters wrap. Test keyboard serio probe, GPIO IRQ replay, FIQ claim failure paths, and suspend/resume.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 227 lines, 6704 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.h

Purpose: Internal AMS Delta FIQ header that connects board setup with the assembly handler. It declares handler symbol bounds and the FIQ initialization entry point.

Important APIs/types/functions: Visible declarations are `qwerty_fiqin_start`, `qwerty_fiqin_end`, and `ams_delta_init_fiq(struct gpio_chip *, struct platform_device *)`.

Control flow, state, and persistence: There is no state in the header; it describes interfaces to C and assembly state managed elsewhere.

Dependencies and integration points: Visible declarations are `qwerty_fiqin_start`, `qwerty_fiqin_end`, and `ams_delta_init_fiq(struct gpio_chip *, struct platform_device *)`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are declaration mismatch with assembly labels or platform device expectations. Test build/link of AMS Delta with FIQ enabled.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 42 lines, 1101 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/ams-delta-fiq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.c

Purpose: Board support for the Amstrad E3/Delta videophone. It maps board latches/modem space, configures keypad, NAND, LCD, LEDs, audio, codec, modem UART, fixed regulators, GPIO lookup tables, FIQ keyboard support, USB, I2C, serial, and OMAP muxing.

Important APIs/types/functions: Key routines are `omap_gpio_deps_init`, `ams_delta_latch2_init`, `ams_delta_init`, `modem_pm`, `ams_delta_modem_pm_activate`, `ams_delta_modem_init`, and `ams_delta_map_io`; the machine descriptor is `AMS_DELTA`.

Control flow, state, and persistence: State includes latch initial values, GPIO lookup tables, software nodes, modem regulator private data, platform devices, flash partitions, and FIQ-updated serio resources. Init ordering is critical: OMAP GPIO deps, latch safety, devices, latch GPIO providers, regulator names, lookup tables, then LEDs.

Dependencies and integration points: Key routines are `omap_gpio_deps_init`, `ams_delta_latch2_init`, `ams_delta_init`, `modem_pm`, `ams_delta_modem_pm_activate`, `ams_delta_modem_init`, and `ams_delta_map_io`; the machine descriptor is `AMS_DELTA`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP GPIO postcore init, FIQ code, basic-mmio-gpio, regulator/fixed-voltage, serial8250, gpio-nand, omapfb, USB, and legacy ATAGS. Risks are fragile dev_name patching, deliberate GPIO descriptor leaks, unsafe latch defaults, and modem probe ordering. Test boot, NAND access, LCD, LEDs, keyboard FIQ/serio, modem UART PM, and regulator probe deferral.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 873 lines, 24023 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.h

Purpose: AMS Delta board constants shared by board setup and FIQ code. It defines GPIO pin numbers for keyboard, modem, hook switch, NAND ready/busy, and other board signals.

Important APIs/types/functions: The file provides macros such as `AMS_DELTA_GPIO_PIN_KEYBRD_DATA`, `KEYBRD_CLK`, `MODEM_IRQ`, `HOOK_SWITCH`, and `NAND_RB`.

Control flow, state, and persistence: There is no runtime state; these constants align board platform data with low-level FIQ assembly masks.

Dependencies and integration points: The file provides macros such as `AMS_DELTA_GPIO_PIN_KEYBRD_DATA`, `KEYBRD_CLK`, `MODEM_IRQ`, `HOOK_SWITCH`, and `NAND_RB`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are off-by-one GPIO definitions causing wrong FIQ/IRQ behavior. Test by validating keyboard, modem IRQ, hook switch, and NAND ready GPIO routing on hardware.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 42 lines, 1786 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-nokia770.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-nokia770.c

Purpose: Board support for the Nokia 770 Internet Tablet. It registers keypad, LCD MIPID, ADS7846 touchscreen, USB, MMC, CBUS/I2C Retu/Tahvo devices, GPIO software nodes, IRQ lookup tables, and OMAP serial/display setup.

Important APIs/types/functions: Important functions are `mipid_dev_init`, `hwa742_dev_init`, `nokia770_mmc_init`, `nokia770_cbus_init`, and `omap_nokia770_init`; the machine descriptor is `NOKIA770`.

Control flow, state, and persistence: State consists of static platform data, SPI board info, software nodes, GPIO lookup tables, and optional MMC/I2C data. Init unblocks SleepX, registers GPIO chip nodes, patches IRQ numbers from descriptors, then registers SPI/I2C/USB/MMC.

Dependencies and integration points: Important functions are `mipid_dev_init`, `hwa742_dev_init`, `nokia770_mmc_init`, `nokia770_cbus_init`, and `omap_nokia770_init`; the machine descriptor is `NOKIA770`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include gpio descriptors, SPI, omapfb, CBUS GPIO I2C, Retu/Tahvo, MMC OMAP, and USB extcon name `tahvo-usb`. Risks are optional-config stubs, GPIO descriptor lifetime leaks, and hard-coded board IRQ mappings. Test touchscreen IRQ, LCD reset, MMC cover/power, Retu/Tahvo interrupts, USB extcon, and serial wake.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 351 lines, 9174 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-nokia770.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-osk.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-osk.c

Purpose: Board support for TI OMAP5912 OSK. It configures NOR flash, SMC91x Ethernet, CompactFlash, TPS65010 PMIC GPIOs/LEDs/regulators, USB host/device mode, I2C devices, serial, and board EMIFS timing workarounds.

Important APIs/types/functions: Key routines are `osk_tps_setup`, `osk_tps_teardown`, `osk_init_smc91x`, `osk_init_cf`, and `osk_init`; the machine descriptor is `OMAP_OSK`.

Control flow, state, and persistence: State includes platform devices/resources, flash partitions, TPS GPIO descriptors held for board lifetime, LED lookup tables, USB/IRQ GPIO tables, and I2C board info. Init patches IRQ resources from GPIO descriptors before platform registration.

Dependencies and integration points: Key routines are `osk_tps_setup`, `osk_tps_teardown`, `osk_init_smc91x`, `osk_init_cf`, and `osk_init`; the machine descriptor is `OMAP_OSK`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include TPS65010, SMC91x, physmap flash, omap_cf, OHCI/UDC selection, OMAP GPIO, I2C, and EMIFS registers. Risks are unchecked GPIO request failures in PMIC setup, hard-coded CS timings, and config-dependent USB mode. Test Ethernet RX/TX, CF IRQ, flash partitions/VPP, PMIC LEDs, USB power/overcurrent, and I2C IRQ.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 454 lines, 12694 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-osk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-palmte.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-palmte.c

Purpose: Board support for Palm Tungsten E. It defines keypad, PalmOS ROM partitions, LCD/backlight devices, USB peripheral mode, TSC2102 SPI touchscreen/audio, MMC, GPIO IRQ lookups, serial, I2C, and display configuration.

Important APIs/types/functions: Important routines are `palmte_mmc_init` and `omap_palmte_init`; the machine descriptor is `OMAP_PALMTE`.

Control flow, state, and persistence: Runtime state is static platform data and board resources. Init muxes UARTs, registers devices, patches SPI IRQ from GPIO, sets USB/DC detect GPIO input, and initializes serial/USB/I2C/LCD/MMC.

Dependencies and integration points: Important routines are `palmte_mmc_init` and `omap_palmte_init`; the machine descriptor is `OMAP_PALMTE`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP mux, physmap flash, omap-bl, omapfb, SPI, MMC OMAP, USB peripheral, and legacy machine type. Risks are limited error handling for GPIO descriptors, fixed ROM partition sizes, and optional MMC stubs. Test keypad, flash read-only partitions, touchscreen IRQ, backlight, USB detect, and MMC.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 272 lines, 6502 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-palmte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1-mmc.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1-mmc.c

Purpose: Siemens SX1 MMC glue. It powers the MMC slot through the SOFIA I2C companion chip and registers OMAP MMC controller data when MMC support is enabled.

Important APIs/types/functions: Important functions are `mmc_set_power` and `sx1_mmc_init`. The power callback uses `sx1_i2c_read_byte`/`sx1_i2c_write_byte` on `SOFIA_POWER1_REG` and toggles `SOFIA_MMC_POWER`.

Control flow, state, and persistence: State is static MMC platform data and the SOFIA power register bit. No kernel-side persistent object is stored beyond registration.

Dependencies and integration points: Important functions are `mmc_set_power` and `sx1_mmc_init`. The power callback uses `sx1_i2c_read_byte`/`sx1_i2c_write_byte` on `SOFIA_POWER1_REG` and toggles `SOFIA_MMC_POWER`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include SX1 board I2C helpers, SOFIA register constants, and OMAP MMC support. Risks are I2C adapter 0 availability during power callbacks and lack of cover-switch handling. Test MMC insertion/removal, power cycling, and builds with `CONFIG_MMC_OMAP` disabled.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 62 lines, 1356 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.c

Purpose: Board support for Siemens SX1 phone. It exposes SOFIA I2C helper APIs for lights and power, defines keypad, flash partitions, USB peripheral mode, LCD config, GPIO setup, I2C/serial/USB/MMC init, and the SX1 machine descriptor.

Important APIs/types/functions: Important APIs include exported `sx1_i2c_write_byte`, `sx1_i2c_read_byte`, `sx1_set/getkeylight`, `sx1_set/getbacklight`, `sx1_setmmipower`, and `sx1_setusbpower`; `omap_sx1_init` handles board init.

Control flow, state, and persistence: State is mainly SOFIA register contents, static platform data, GPIO defaults, and flash resources. I2C helper calls acquire adapter 0 for each transaction and perform one-byte register reads/writes.

Dependencies and integration points: Important APIs include exported `sx1_i2c_write_byte`, `sx1_i2c_read_byte`, `sx1_set/getkeylight`, `sx1_set/getbacklight`, `sx1_setmmipower`, and `sx1_setusbpower`; `omap_sx1_init` handles board init. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include I2C, SOFIA chip constants, OMAP mux, physmap flash, keypad, USB, MMC glue, and omapfb. Risks include poor read-error handling after the first I2C transfer, exported board-specific APIs, fixed flash layout, and deferred USB power because I2C is not ready. Test keypad, backlight/keylight, LCD power, USB power, MMC, and I2C failure paths.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 371 lines, 9081 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.h

Purpose: Siemens SX1 board header. It defines SOFIA companion-chip I2C address/register bits and declares board helper APIs shared with MMC and other board consumers.

Important APIs/types/functions: Declarations include `sx1_i2c_write_byte`, `sx1_i2c_read_byte`, light/power helpers, and `sx1_mmc_init`; macros define `SOFIA_*` registers and bit masks.

Control flow, state, and persistence: No state is stored in the header; SOFIA hardware registers are manipulated by the C files.

Dependencies and integration points: Declarations include `sx1_i2c_write_byte`, `sx1_i2c_read_byte`, light/power helpers, and `sx1_mmc_init`; macros define `SOFIA_*` registers and bit masks. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are ABI-like exported helper signatures and bit definitions drifting from hardware. Test compile users and SOFIA-controlled backlight/MMC/USB operations.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 45 lines, 1121 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.c

Purpose: OMAP1 common-clock implementation. It provides OMAP-specific recalc, gate, rate-rounding, set-rate, idle-control, DSP-domain, UART, SoSSI, external clock, and propagation operations for the clock data table.

Important APIs/types/functions: Important functions include `omap1_ckctl_recalc`, `omap1_select_table_rate`, `omap1_clk_set_rate_ckctl_arm`, `omap1_set_uart_rate`, `omap1_set_ext_clk_rate`, `omap1_set_sossi_rate`, `omap1_init_ext_clk`, `propagate_rate`, and exported `clk_ops`/`clkops` structures.

Control flow, state, and persistence: State includes `arm_idlect1_mask`, direct pointers to `api_ck`, `ck_dpll1`, and `ck_ref`, and spinlocks protecting shared hardware registers. Rate changes may reprogram DPLL from SRAM and update cached rates.

Dependencies and integration points: Important functions include `omap1_ckctl_recalc`, `omap1_select_table_rate`, `omap1_clk_set_rate_ckctl_arm`, `omap1_set_uart_rate`, `omap1_set_ext_clk_rate`, `omap1_set_sossi_rate`, `omap1_init_ext_clk`, `propagate_rate`, and exported `clk_ops`/`clkops` structures. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP register accessors, SRAM clock reprogramming, common clock framework, CPU/machine detection, and OPP data. Risks are hardware divisor constraints, register locking omissions, DSP-domain access requiring `api_ck`, and legacy sysc handling in clock ops. Test clk enable/disable, cpufreq rate changes, UART 12/48 MHz switching, SoSSI/external rates, and reset-unused-clocks.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 847 lines, 21663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.h

Purpose: OMAP1 clock framework header. It defines `omap_clk`, `clkops`, `omap1_clk`, `arm_idlect1_clk`, `uart_clk`, CPU mask flags, clock flags, and function prototypes for clock operations and init.

Important APIs/types/functions: Important declarations include `CLK`, `CK_*` platform masks, `ENABLE_REG_32BIT`, `CLOCK_IDLE_CONTROL`, `CLOCK_NO_IDLE_PARENT`, `omap1_clk_init`, `omap1_clk_late_init`, rate helpers, and global clock pointers.

Control flow, state, and persistence: The header itself stores no state but describes state fields used by `clock.c` and `clock_data.c`: hardware registers, enable bits, rate offsets, fixed divisors, and idle counters.

Dependencies and integration points: Important declarations include `CLK`, `CK_*` platform masks, `ENABLE_REG_32BIT`, `CLOCK_IDLE_CONTROL`, `CLOCK_NO_IDLE_PARENT`, `omap1_clk_init`, `omap1_clk_late_init`, rate helpers, and global clock pointers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are struct layout coupling between declarative clock data and operation code, and global pointer use before init. Test compile coverage and clock registration on OMAP15xx/16xx/7xx variants.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 195 lines, 6746 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock_data.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock_data.c

Purpose: Declarative OMAP1 clock tree and initialization. It instantiates reference, DPLL, ARM, DSP, TC, UART, USB, MMC, I2C, MCBSP, SoSSI, external, and virtual MPU clocks with CPU masks and clkdev aliases.

Important APIs/types/functions: Important pieces are the static `omap1_clk` definitions, `omap_clks[]`, `omap1_clk_init`, `omap1_clk_late_init`, `omap1_show_rates`, and global `cpu_mask`.

Control flow, state, and persistence: Init clears soft requests, computes CPU mask, stores global clock pointers, derives bootloader DPLL rate, resets DSP/idle registers, registers matching clocks, and later reprograms DPLL to the highest supported table rate from SRAM.

Dependencies and integration points: Important pieces are the static `omap1_clk` definitions, `omap_clks[]`, `omap1_clk_init`, `omap1_clk_late_init`, `omap1_show_rates`, and global `cpu_mask`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP register definitions, machine/cpu detection, common clock registration, SRAM clock code, cpufreq scaling, and board quirks such as AMS Delta BCLK inversion. Risks are large legacy clock table drift, duplicate aliases, bootloader-rate assumptions, and DPLL reprogramming fallout. Test boot rates, clkdev lookup for all platform devices, cpufreq, UART clocks, USB/MMC clocks, and OMAP_RESET_CLOCKS.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 834 lines, 27476 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/clock_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/common.h

Purpose: Shared OMAP1 internal declaration header. It ties board files and common machine code to timer, IRQ, IO, serial, USB, reset, clock, mux, and late-init routines.

Important APIs/types/functions: It declares routines such as `omap1_map_io`, `omap1_init_early`, `omap1_init_irq`, `omap1_timer_init`, `omap1_init_late`, `omap1_restart`, `omap_serial_init`, and optional device helpers.

Control flow, state, and persistence: No state is stored here, but the header defines cross-file integration contracts for machine descriptors.

Dependencies and integration points: It declares routines such as `omap1_map_io`, `omap1_init_early`, `omap1_init_irq`, `omap1_timer_init`, `omap1_init_late`, `omap1_restart`, `omap_serial_init`, and optional device helpers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are declaration drift and board files depending on legacy global init order. Test all OMAP1 board builds and link-time coverage.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 78 lines, 2395 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/devices.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/devices.c

Purpose: Common OMAP1 platform-device registration. It creates RTC, MMC, uWire SPI, RNG, watchdog, SRAM/clock late-init, and associated resources depending on configuration and CPU type.

Important APIs/types/functions: Important functions are `omap1_init_mmc`, `omap_mmc_add`, `omap1_mmc_mux`, `omap1_init_devices`, `omap_init_wdt`, and internal RTC/uWire/RNG init helpers.

Control flow, state, and persistence: State is static platform devices/resources plus per-board MMC platform data patched with features and `dev` pointers. The arch initcall runs after board init to initialize SRAM, late clocks, and on-chip devices.

Dependencies and integration points: Important functions are `omap1_init_mmc`, `omap_mmc_add`, `omap1_mmc_mux`, `omap1_init_devices`, `omap_init_wdt`, and internal RTC/uWire/RNG init helpers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP mux/registers, clock/SRAM, platform data headers, RTC/MMC/uWire/RNG/watchdog drivers, and CPU detection. Risks are board data mutation, hard-coded DMA request numbers, late clock timing, and optional config stubs. Test MMC controllers 0/1, RTC alarms, RNG on OMAP16xx, watchdog reset-source data, and arch init ordering.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 363 lines, 8448 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/dma.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/dma.c

Purpose: OMAP1 system DMA platform setup. It maps DMA registers, defines register layout/resources, supplies low-level read/write/clear/capability callbacks, describes slave request mappings, and registers legacy system DMA plus dmaengine devices.

Important APIs/types/functions: Important routines are `dma_write`, `dma_read`, `omap1_clear_lch_regs`, `omap1_clear_dma`, `omap1_show_dma_caps`, `configure_dma_errata`, and `omap1_system_dma_init`.

Control flow, state, and persistence: State includes mapped `dma_base`, `enable_1510_mode`, DMA attributes, errata flags, logical channel count, and static IRQ resources. Init allocates platform data, determines CPU capabilities, and registers two DMA-facing devices.

Dependencies and integration points: Important routines are `dma_write`, `dma_read`, `omap1_clear_lch_regs`, `omap1_clear_dma`, `omap1_show_dma_caps`, `configure_dma_errata`, and `omap1_system_dma_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include `linux/omap-dma.h`, DMA engine, OMAP IRQs, CPU detection, and register-map semantics. Risks are resource count mismatch in `omap_dma_dev_info` versus full resources on the system device, ioremap lifetime, and 2x16-bit register access ordering. Test DMA clients for MMC, MCBSP, UDC, LCD DMA, OMAP15xx/16xx channel counts, and errata behavior.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 394 lines, 9964 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/fb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/fb.c

Purpose: OMAP framebuffer platform-device registration. It stores board-provided LCD configuration and registers `omapfb` only if a board called `omapfb_set_lcd_config`.

Important APIs/types/functions: The main API is `omapfb_set_lcd_config`; init is `omap_init_fb` at `arch_initcall`.

Control flow, state, and persistence: State includes `omapfb_lcd_configured`, `omapfb_config`, a 32-bit DMA mask, and LCD/SOSSI IRQ resources. Boards persist their LCD controller name through the copied config.

Dependencies and integration points: The main API is `omapfb_set_lcd_config`; init is `omap_init_fb` at `arch_initcall`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include `CONFIG_FB_OMAP`, omapfb platform data, LCD IRQ definitions, and board files. Risks are late/missing board calls causing no framebuffer device and shallow-copy assumptions for config fields. Test boards with LCD, no-LCD builds, IRQ resources, and DMA mask behavior.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 84 lines, 1728 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.c

Purpose: OMAP1 NOR flash VPP control helper. It toggles the EMIFS write-protect/VPP bit for physmap flash platform data.

Important APIs/types/functions: The only API is `omap1_set_vpp(struct platform_device *pdev, int enable)`.

Control flow, state, and persistence: State is the EMIFS_CONFIG hardware register. The helper reads, sets or clears `OMAP_EMIFS_CONFIG_WP`, then writes it back.

Dependencies and integration points: The only API is `omap1_set_vpp(struct platform_device *pdev, int enable)`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP1 register accessors, EMIFS definitions, and MTD/physmap board data. Risks are global EMIFS bit side effects across multiple flash devices and lack of locking. Test flash erase/write enable/disable on OSK, PalmTE, and SX1.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 26 lines, 440 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.h

Purpose: Header for OMAP1 flash VPP support. It declares the helper used by board physmap flash data.

Important APIs/types/functions: The API is `omap1_set_vpp(struct platform_device *pdev, int enable)`.

Control flow, state, and persistence: No state exists in the header; hardware state is in EMIFS registers manipulated by `flash.c`.

Dependencies and integration points: The API is `omap1_set_vpp(struct platform_device *pdev, int enable)`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are missing declaration if flash support changes. Test compile of all board files using physmap flash.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 14 lines, 255 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/flash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio15xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio15xx.c

Purpose: OMAP15xx GPIO platform-device registration. It describes the MPU IO GPIO bank and the OMAP1510 GPIO bank register offsets/resources and registers them before machine init.

Important APIs/types/functions: Important data includes `omap15xx_mpuio_regs`, `omap15xx_gpio_regs`, `omap15xx_mpu_gpio`, `omap15xx_gpio`, and `omap15xx_gpio_init` as a `postcore_initcall`.

Control flow, state, and persistence: State is static platform data/resources. Runtime GPIO state is owned by the gpio-omap driver after registration.

Dependencies and integration points: Important data includes `omap15xx_mpuio_regs`, `omap15xx_gpio_regs`, `omap15xx_mpu_gpio`, `omap15xx_gpio`, and `omap15xx_gpio_init` as a `postcore_initcall`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP1 MPUIO/GPIO register definitions, IRQ numbers, and `cpu_is_omap15xx`. Risks are early registration ordering and register offset coupling with AMS Delta FIQ code. Test GPIO numbering, IRQs, keypad/modem/NAND GPIO consumers, and non-15xx no-op behavior.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 116 lines, 2813 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio15xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio16xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio16xx.c

Purpose: OMAP16xx GPIO platform-device registration. It defines MPUIO plus four GPIO banks, initializes each bank's SYSCONFIG for smart idle/wakeup, and registers them before machine init.

Important APIs/types/functions: Important data includes `omap16xx_mpuio_regs`, `omap16xx_gpio_regs`, five platform devices, and `omap16xx_gpio_init`.

Control flow, state, and persistence: State is static resources/platform data plus transient ioremaps used to write SYSCONFIG before device registration. Runtime state moves to gpio-omap.

Dependencies and integration points: Important data includes `omap16xx_mpuio_regs`, `omap16xx_gpio_regs`, five platform devices, and `omap16xx_gpio_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include OMAP16xx register addresses, `ULPD_CAM_CLK_CTRL` system-clock enable, IRQ numbers, and CPU detection. Risks are ioremap failure aborting later banks, hard-coded CAM clock control for GPIO, and early GPIO consumers relying on labels. Test all GPIO bank labels/IRQs, wakeup, smart idle, and non-16xx builds.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 251 lines, 6136 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/gpio16xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/hardware.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/hardware.h

Purpose: Legacy OMAP1 hardware-address header. It defines memory controller, chip-select, peripheral, and compatibility constants used by board and platform code.

Important APIs/types/functions: Important helpers/macros include `omap_cs0m_phys`, `omap_cs3_phys`, OMAP chip-select bases, register base constants, and included SoC/IO headers.

Control flow, state, and persistence: There is no mutable state; inline helpers derive physical addresses from TC/EMIFS register settings.

Dependencies and integration points: Important helpers/macros include `omap_cs0m_phys`, `omap_cs3_phys`, OMAP chip-select bases, register base constants, and included SoC/IO headers. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Risks are hard-coded physical address assumptions and broad inclusion of legacy definitions into board drivers. Test board flash/CF mappings, chip-select helpers, and compile coverage across OMAP15xx/16xx.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 235 lines, 8575 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/hardware.h -->
