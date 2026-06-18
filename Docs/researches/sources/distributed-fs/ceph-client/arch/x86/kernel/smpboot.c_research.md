# sources/distributed-fs/ceph-client/arch/x86/kernel/smpboot.c

## Purpose
`smpboot.c` implements x86 secondary CPU startup, topology mask construction, scheduler topology setup, AP wakeup, CPU hotplug teardown, and offline CPU dead loops.

## Important APIs, Types, And Functions
Major functions include `start_secondary()`, `set_cpu_sibling_map()`, `common_cpu_up()`, `native_kick_ap()`, `arch_cpuhp_kick_ap_alive()`, `native_smp_prepare_cpus()`, `native_smp_prepare_boot_cpu()`, `native_smp_cpus_done()`, `cpu_disable_common()`, `native_cpu_disable()`, `mwait_play_dead()`, `smp_kick_mwait_play_dead()`, and `native_play_dead()`. It exports per-CPU sibling/core/die masks and `__max_smt_threads`.

## Control Flow
AP startup initializes CR4/page tables, exception handling, microcode, hotplug alive sync, CPU/FPU/RCU/per-CPU clocks, APIC, topology, TSC sync, delay calibration, mitigations, vector allocator state, interrupts, clockevents, and idle. Wakeup validates APIC IDs, saves MTRRs, prepares idle stack/canary/IRQ stacks, sets trampoline state and optional warm reset vector, then sends platform or INIT/SIPI wakeups. Hotplug disable removes topology state, migrates IRQs, disables local APIC, and enters cpuidle or halt dead loops.

## State, Persistence, Dependencies, Integration
Persistent topology state includes sibling/core/die/LLC/L2 masks, `cpu_sibling_setup_mask`, booted core counts, SMT flags, scheduler topology levels, `__max_smt_threads`, and `x86_topology_update`. Dependencies include APIC, real-mode trampoline, microcode, TSC, FPU, RCU, NUMA SLIT data, scheduler topology, MTRR, cpuidle, TBoot, SEV-SNP wakeup overrides, and mitigation code.

## Risks And Test Signals
Startup ordering is fragile around microcode, CPUID topology, vector locks, and online state. Topology must respect NUMA while handling SNC/COD quirks. Warm reset vector reference counting, parallel bringup, MWAIT dead CPU kexec handling, and cpuidle fallback are high-risk. Test single/many CPU boots, SMT on/off, NUMA, Intel SNC/COD, AMD TOPOEXT, APIC variants, parallel bringup, CPU hotplug stress, suspend/thaw, and kexec with offline CPUs.
