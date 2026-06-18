<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle44xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle44xx.c

## Purpose
`cpuidle44xx.c` implements cpuidle support for OMAP4 and OMAP5 MPUSS idle states. It coordinates per-CPU low-power entry with MPUSS powerdomain programming, timer broadcast, CPU PM notifiers, coupled idle barriers, and OMAP4 GIC-distributor erratum handling.

## Important APIs, Types, and Functions
The public entry is `omap4_idle_init()`. Key internals are `struct idle_statedata`, `omap4_idle_data[]`, `omap5_idle_data[]`, `omap_enter_idle_simple()`, `omap_enter_idle_smp()`, `omap_enter_idle_coupled()`, `omap4_idle_driver`, and `omap5_idle_driver`. Shared state includes `mpu_pd`, `cpu_pd[]`, `cpu_clkdm[]`, `abort_barrier`, `cpu_done[]`, `state_ptr`, and `mpu_lock`.

## Control Flow
Initialization selects OMAP5 data for OMAP54xx and OMAP4 data otherwise, resolves MPU/CPU powerdomains and CPU clockdomains, then registers cpuidle against online CPUs. C1 executes plain WFI. OMAP5 C2 uses a spinlock and per-state vote counter so the MPU state is programmed only when all online CPUs vote for the same state. OMAP4 coupled states wait for CPU1 to enter off, enter timer broadcast, save CPU and cluster PM context, program MPUSS state from CPU0, call `omap4_enter_lowpower()`, wake CPU1 if needed, restore GIC/WakeupGen context, and pass through the coupled abort barrier.

## State and Persistence Behavior
State is powerdomain target state, coupled-idle synchronization flags, timer broadcast state, and CPU/cluster PM saved context. `cpu_done[]` prevents CPU0 from spinning forever if CPU1 attempted and left idle. The driver does not write persistent storage, but it depends on lower MPUSS code to use SAR RAM for context restore.

## Dependencies and Integration Points
It depends on cpuidle, tick broadcast, CPU PM, OMAP PM low-power entry, PRM/powerdomain/clockdomain helpers, SoC detection, GIC erratum helpers from `omap4-common.c`, and `omap4_enter_lowpower()` from `omap-mpuss-lowpower.c`.

## Risks
Coupled idle is concurrency-sensitive. Races around CPU1 off detection, GIC distributor disable/reenable, or CPU PM error fallback can hang SMP resume or lose timer interrupts. Wrong `state_count` or state data can make cpuidle index assumptions invalid. OMAP5 voting must correctly track online CPUs or MPUSS state may be over-programmed.

## Test Signals
Boot SMP OMAP4/OMAP5 with cpuidle enabled, inspect cpuidle state residency, repeatedly offline/online CPU1, run timer wakeup tests, and stress idle under interrupts. On OMAP446x, verify no local-timer loss after GIC erratum handling and no stalls at the coupled barrier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cpuidle44xx.c -->
