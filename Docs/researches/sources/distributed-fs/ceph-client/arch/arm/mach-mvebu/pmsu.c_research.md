<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.c

Purpose: Power Management Service Unit support for MVEBU v7 SoCs. It maps PMSU registers, redirects CPU boot addresses, implements deep-idle/cpuidle/hotplug suspend entry, applies BootROM workarounds, and triggers dynamic frequency scaling transitions.

Important APIs/types/functions: Key APIs are `mvebu_pmsu_set_cpu_boot_addr`, `mvebu_setup_boot_addr_wa`, `armada_370_xp_pmsu_idle_enter`, `armada_38x_do_cpu_suspend`, `mvebu_v7_pmsu_idle_exit`, and `mvebu_pmsu_dfs_request`; init is via `early_initcall` and `arch_initcall`.

Control flow, state, and persistence: State includes `pmsu_mp_base`, `pmsu_mp_phys_base`, selected CPU resume function, and a cpuidle platform device. Idle preparation sets per-CPU wait, wake, mask, L2 powerdown, and DFS bits before WFI; exit clears those bits.

Dependencies and integration points: Key APIs are `mvebu_pmsu_set_cpu_boot_addr`, `mvebu_setup_boot_addr_wa`, `armada_370_xp_pmsu_idle_enter`, `armada_38x_do_cpu_suspend`, `mvebu_v7_pmsu_idle_exit`, and `mvebu_pmsu_dfs_request`; init is via `early_initcall` and `arch_initcall`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include DT PMSU bindings, MBUS windows, SRAM/BootROM workarounds, SCU, CPU PM notifiers, cache/TLB maintenance, and low-level assembly resume code. Risks include disabled Armada 38x idle, timeout-prone DFS polling, register races if CPU mapping is wrong, and fatal resume if boot-address workaround fails. Test cpuidle, CPU hotplug, suspend/resume, DFS on each CPU, and broken-idle DT property handling.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 607 lines, 16597 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/pmsu.c -->
