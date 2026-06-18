<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/proc.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/proc.c

**Purpose:** Supplies `/proc/cpuinfo` system type reporting for generic MIPS machines.

**Important APIs/types/functions:** Global `system_type` can be set by board code. `get_system_type()` returns it, else root DT `model`, else first root `compatible`, else `"Unknown"`.

**Control flow:** Lookup is lazy and read-only except for external `system_type` assignments.

**State, dependencies, integration:** Depends on OF root node and bootinfo. Used by proc CPU information formatting.

**Risks and test signals:** Missing OF root data degrades to `"Unknown"`. Test explicit board override, model-only DT, compatible-only DT, and empty DT properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/proc.c -->
