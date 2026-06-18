<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_head.S -->
# sources/distributed-fs/ceph-client/arch/arm/common/mcpm_head.S

## Purpose
Low-level MMU-off ARMv7 MCPM kernel entry point used when CPUs power up or re-enter after cluster power transitions.

## Important APIs/types/functions
- Entry symbol: `mcpm_entry_point`.
- BSS symbols: `mcpm_entry_vectors`, `mcpm_entry_early_pokes`, and `mcpm_power_up_setup_phys`.
- Per-cluster `first_man_locks` using `vlock_trylock()` and `vlock_unlock()`.
- Uses `mcpm_sync` offsets and state constants from `asm/mcpm.h`.

## Control flow
The entry code reads MPIDR, derives CPU/cluster indices, parks unexpected CPUs in WFI/WFE, locates shared variables position-independently, performs optional early MMIO pokes, marks the CPU `CPU_COMING_UP`, attempts to become the first CPU setting up the cluster, waits for teardown races to resolve, invokes `power_up_setup` for cluster and CPU levels, marks the cluster and CPU up, then spins at a gate until the C code installs an entry vector. Finally it branches to the vector, such as `secondary_startup` or `cpu_resume`.

## State and persistence behavior
State is in `.bss` arrays and `mcpm_sync`, accessed before normal virtual addressing is available. It relies on barriers, WFE/SEV, and byte stores visible across CPUs. Entry vectors are physical addresses written by C code.

## Dependencies and integration points
Depends on ARMv7-A, `assembler.h`, `vlock.h`, MCPM sync layout, optional debug LL printing, and `mcpm_entry.c` initialization. Used by CPU reset paths and platform power controllers.

## Risks and edge cases
Struct layout assumptions are enforced with assembler `.error`. Incorrect MPIDR affinity, wrong `MAX_CPUS_PER_CLUSTER`, or broken Device/Strongly-Ordered memory assumptions can park CPUs forever. The gate intentionally waits for nonzero vectors, so missed `mcpm_set_entry_vector()` calls deadlock bring-up.

## Test signals
CPU hotplug and secondary boot must reliably pass through this entry. Debug LL traces can show "kernel mcpm_entry_point" and "released" when enabled. Stress with repeated cluster power-down/up cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_head.S -->
