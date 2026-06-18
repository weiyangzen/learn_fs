<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheops.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheops.h

**Purpose:** Defines numeric encodings for MIPS `cache` instruction operations across processor families.

**Important APIs/types/functions:** Constants identify I/D/T/S/V caches, operation fields, R4000-style ops, R5000/RM7000/R10000/Loongson-specific ops, and `Cache_Barrier`.

**Control flow:** No code; other assembly/C cache helpers combine constants into `cache` instructions.

**State, dependencies, integration:** Used by cache management, BMIPS ZSCM access, and CPU errata workarounds.

**Risks and test signals:** Wrong opcode constants can invalidate/write back the wrong cache. Test cache flush routines on relevant CPU families and inspect emitted cache op values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheops.h -->
