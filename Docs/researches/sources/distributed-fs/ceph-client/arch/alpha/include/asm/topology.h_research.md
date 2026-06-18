<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/topology.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/topology.h

**Purpose:** Provides Alpha topology include glue, deferring most NUMA/topology behavior to generic code.

**Important APIs/types/functions:** Includes Linux SMP/thread/NUMA headers, `asm/machvec.h`, and `asm-generic/topology.h`.

**Control flow:** No direct control flow. Generic scheduler and memory code consume topology definitions through this header.

**State and persistence behavior:** No state here; topology state is generic or machine-vector-provided.

**Dependencies and integration points:** Depends on generic topology and Alpha machine-vector data.

**Risks:** Alpha-specific topology omissions may make all CPUs/nodes appear generic even on complex systems.

**Test signals:** Build NUMA/SMP configs and inspect scheduler/sysfs topology output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/topology.h -->
