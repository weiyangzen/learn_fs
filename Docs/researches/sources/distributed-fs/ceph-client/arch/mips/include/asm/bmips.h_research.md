<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips.h

**Purpose:** Defines Broadcom BMIPS register offsets, SMP operations, reset vectors, shared state, and ZSCM register access helpers.

**Important APIs/types/functions:** `BMIPS_GET_CBR`, many BMIPS register offsets, `register_bmips_smp_ops()`, external reset/SMP vectors, `bmips_*` globals/functions, and `bmips_read_zscm_reg`/`bmips_write_zscm_reg`.

**Control flow:** SMP registration selects UP, BMIPS43xx, or BMIPS5000 ops based on `current_cpu_type()` when CPU_BMIPS and SMP are enabled. ZSCM access uses cache tag operations with sync/nop hazards.

**State, dependencies, integration:** Integrates BMIPS platform setup, SMP bring-up, CP0 registers, cache operations, and shared masks/offsets.

**Risks and test signals:** Cache-op-based ZSCM access is hazard-sensitive; CBR can point above 0xff000000. Test all BMIPS CPU types, SMP boot, reset vector copying, and ZSCM read/write ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips.h -->
