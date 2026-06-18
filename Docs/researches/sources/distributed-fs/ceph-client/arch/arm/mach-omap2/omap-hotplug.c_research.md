<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-hotplug.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-hotplug.c

## Purpose
`omap-hotplug.c` implements OMAP4 CPU hotplug platform hooks for taking secondary CPUs down and verifying they reached low-power/off state.

## Important APIs, Types, and Functions
Public functions are `omap4_cpu_die(unsigned int cpu)` and `omap4_cpu_kill(unsigned int cpu)`. They call into `omap4_hotplug_cpu()` from MPUSS low-power code and inspect CPU powerdomain state.

## Control Flow
`omap4_cpu_die()` flushes the CPU from coherency as needed and enters the requested CPU low-power path, typically CPU off. `omap4_cpu_kill()` waits/polls for the target CPU powerdomain to report off, returning success only when the hardware state confirms the CPU is down.

## State and Persistence Behavior
State is per-CPU powerdomain state and hotplug lifecycle state managed by the kernel CPU hotplug core. No persistent data is written.

## Dependencies and Integration Points
It depends on SMP/hotplug core, powerdomain helpers, OMAP4 MPUSS low-power functions, and OMAP PM state definitions. It integrates through `omap4_smp_ops.cpu_die` and `.cpu_kill`.

## Risks
If `cpu_die` does not actually place the CPU in a terminal low-power state, CPU hotplug can hang. If `cpu_kill` checks the wrong powerdomain or timeout behavior, the kernel may believe a CPU is dead when it is not, or fail valid hotplug operations.

## Test Signals
Run repeated `echo 0/1 > /sys/devices/system/cpu/cpu1/online` loops under interrupt load. Verify powerdomain previous/current states, no RCU stalls, no GIC wake issues, and successful return to SMP scheduling after re-online.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-hotplug.c -->
