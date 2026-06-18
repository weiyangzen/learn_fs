# sources/distributed-fs/ceph-client/arch/sparc/prom/mp.c

Purpose: exposes SPARC32 PROM support for starting secondary CPUs on PROM V3 systems.

Important APIs/functions: defines `prom_startcpu(int cpunode, struct linux_prom_registers *ctable_reg, int ctx, char *pc)`.

Control flow: under `prom_lock`, the function checks `prom_vers`. PROM V3 calls `romvec->v3_cpustart()` with CPU node, context-table register, context number, and start PC. Other PROM versions return `-1`. `restore_current()` is called after firmware returns.

State and persistence: no owned state; starts firmware CPU execution state.

Dependencies and integration points: used by SPARC32 SMP boot code. Depends on PROM V3 ROM vector CPU-start method, context-table setup, and PROM locking.

Risks: wrong context-table or PC arguments prevent secondary CPU boot. Calling on unsupported PROM versions cannot work. Firmware may disturb current-task state unless restored.

Test signals: SMP boot on PROM V3 sun4m/sun4d, unsupported PROM fallback, and secondary CPU entry validation.
