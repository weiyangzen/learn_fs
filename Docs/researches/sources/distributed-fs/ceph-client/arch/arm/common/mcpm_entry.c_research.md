<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_entry.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/mcpm_entry.c

## Purpose
High-level C implementation of ARM multi-cluster power management (MCPM) state transitions. It coordinates CPU and cluster power-up/down, race avoidance, platform hooks, and synchronization state shared with the assembly entry path.

## Important APIs/types/functions
- Global synchronization: `struct sync_struct mcpm_sync`.
- Entry vector APIs: `mcpm_set_entry_vector()` and `mcpm_set_early_poke()`.
- Platform registration: `mcpm_platform_register()`, `mcpm_is_available()`.
- Power APIs: `mcpm_cpu_power_up()`, `mcpm_cpu_power_down()`, `mcpm_wait_for_cpu_powerdown()`, `mcpm_cpu_suspend()`, `mcpm_cpu_powered_up()`.
- Initialization/test APIs: `mcpm_sync_init()` and, under CPU suspend, `mcpm_loopback()`.
- Internal state: `platform_ops`, `arch_spinlock_t mcpm_lock`, and `mcpm_cpu_use_count[][]`.

## Control flow
`mcpm_sync_init()` initializes all clusters down except the boot cluster and writes the optional physical setup hook for assembly entry. `mcpm_cpu_power_up()` increments a use count under `mcpm_lock`, powers a cluster if unused, then powers the CPU. `mcpm_cpu_power_down()` marks the CPU going down, decrements use counts, determines whether it is the last CPU in the cluster, optionally enters the outbound critical section, runs platform prepare hooks, disables CPU or cluster cache, marks CPU down, waits for power removal, and if necessary resets through `mcpm_entry_point`. `mcpm_cpu_powered_up()` marks the CPU/cluster live after entry.

## State and persistence behavior
State is volatile but shared across cache-off and MMU-off transitions: `mcpm_sync` is cacheline-aligned and explicitly cleaned, entry vectors are physical addresses, early pokes are physical MMIO writes, and use counts track requested liveness. WFE/SEV and cache maintenance provide persistence across power-state transitions, not storage.

## Dependencies and integration points
Depends on platform `mcpm_platform_ops`, CPU reset, idmap/reboot MM setup, CPU PM, cacheflush helpers, `asm/mcpm.h`, CPU suspend, and the assembly `mcpm_entry_point`. The big.LITTLE switcher and SMP operations use this API.

## Risks and edge cases
The algorithm is race-sensitive and assumes correct platform hooks. Incorrect cache maintenance or sync state alignment can deadlock CPU bring-up/down. Use counts can be `0`, `1`, or transient `2`; other values are BUGs. Power-down requires IRQs disabled. If platform wait-for-powerdown is absent, callers receive `-EUNATCH`.

## Test signals
Run SMP secondary boot, CPU hotplug, suspend/resume, MCPM loopback, and big.LITTLE switcher tests on a multi-cluster ARM platform. Enable lockdep and trace CPU PM events where possible, but keep instrumentation out of `mcpm_entry.o` as the Makefile does.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_entry.c -->
