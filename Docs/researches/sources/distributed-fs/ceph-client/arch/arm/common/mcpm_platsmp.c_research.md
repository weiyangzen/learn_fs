<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/mcpm_platsmp.c

## Purpose
SMP operation glue that connects generic ARM SMP boot/hotplug callbacks to MCPM physical CPU and cluster power APIs.

## Important APIs/types/functions
- `mcpm_smp_set_ops()` installs `mcpm_smp_ops`.
- SMP callbacks: `mcpm_boot_secondary()`, `mcpm_secondary_init()`, and under hotplug `mcpm_cpu_kill()`, `mcpm_cpu_can_disable()`, `mcpm_cpu_die()`.
- Helper `cpu_to_pcpu()` maps logical CPU to MPIDR affinity levels.

## Control flow
Booting a secondary clears its entry vector, powers up the physical CPU/cluster, sets entry vector to `secondary_startup`, sends wakeup IPI, and emits SEV. Secondary init calls `mcpm_cpu_powered_up()`. CPU hotplug die clears the local entry vector and enters MCPM power-down; kill waits for platform powerdown completion.

## State and persistence behavior
No private persistent state. It mutates MCPM entry vectors and MCPM power state via shared APIs.

## Dependencies and integration points
Depends on `cpu_logical_map()`, ARM SMP core, `secondary_startup`, MCPM APIs, and CPU hotplug.

## Risks and edge cases
Incorrect logical-to-physical mapping boots the wrong CPU. Missing platform `wait_for_powerdown` weakens hotplug kill verification. The code assumes all CPUs may be disabled.

## Test signals
Boot all secondary CPUs, repeatedly online/offline CPUs, verify MPIDR debug logs, and confirm platform power controller state matches kernel CPU state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_platsmp.c -->
