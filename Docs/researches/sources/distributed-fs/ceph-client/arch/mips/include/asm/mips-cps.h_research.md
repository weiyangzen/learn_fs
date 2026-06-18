# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-cps.h

Purpose: Top-level MIPS Coherent Processing System helper header. It defines common MMIO accessor generators, includes CM/CPC/GIC register interfaces, and provides topology helpers.

Important APIs/types/functions: `CPS_ACCESSOR_A/R/W/M/RO/WO/RW` create address, read, write, change, set, and clear helpers with 32/64-bit handling. `__cps_access_bad_size()` catches invalid accessor sizes at compile time. Topology helpers include `mips_cps_numclusters()`, `mips_cps_cluster_config()`, `mips_cps_numcores()`, `mips_cps_numiocu()`, `mips_cps_numvps()`, `mips_cps_multicluster_cpus()`, and `mips_cps_first_online_in_cluster()`.

Control flow, state, and persistence: Accessors route through `mips_<unit>_base` and use `mips_cm_is64` to split 64-bit accesses on 32-bit GCR windows. Topology helpers read CM/CPC registers, sometimes under redirected-region locks. No persistent state is introduced beyond hardware register state.

Dependencies and integration: Depends on bitfield, cpumask, I/O, CPU topology, and the included `mips-cm.h`, `mips-cpc.h`, and `mips-gic.h`. It integrates with SMP topology, interrupt routing, power management, and cache coherency.

Risks and test signals: The 64-bit split read/write order and multi-cluster redirect logic are correctness-critical. Test across CM revisions, 32/64-bit kernels, multi-VP cores, multi-cluster systems, and absent-CM fallback paths.
