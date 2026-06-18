<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/promlib.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/promlib.c

**Purpose:** Implements ARC firmware character I/O helpers used by early console and PROM code.

**Important APIs/types/functions:** `prom_putchar()` writes one character to ARC handle 1. `prom_getchar()` reads one character from ARC handle 0. On 64-bit kernels with 32-bit ARC, `O32_STATIC` ensures firmware buffers live in a low static segment.

**Control flow:** Both helpers disable board cache, perform one ARC read/write, then re-enable board cache.

**State, dependencies, integration:** Depends on `ArcRead`, `ArcWrite`, `bc_disable`, `bc_enable`, and CONFIG-specific O32 pointer constraints. Integrated with `arc_con.c` and early debug paths.

**Risks and test signals:** The helpers are synchronous and assume fixed firmware standard handles. Test console input/output with board cache enabled and disabled, plus 64-bit/ARC32 builds where stack pointers may not be firmware-addressable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/promlib.c -->
