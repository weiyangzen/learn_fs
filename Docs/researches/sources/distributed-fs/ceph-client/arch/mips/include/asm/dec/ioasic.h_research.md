<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic.h

**Purpose:** Provides DEC I/O ASIC register accessors and initialization declarations.

**Important APIs/types/functions:** Externs `ioasic_ssr_lock` and `ioasic_base`; inline `ioasic_write()` and `ioasic_read()` index MMIO registers by byte offset/4. Declares `init_ioasic_irqs()` and `dec_ioasic_clocksource_init()`.

**Control flow:** Callers read/write volatile register slots directly through the base pointer.

**State, dependencies, integration:** Shared I/O ASIC base and SSR lock coordinate register access across DEC platform code and drivers.

**Risks and test signals:** Base pointer must be mapped before access; SSR requires lock discipline. Test register read/write offsets, IRQ init, and clocksource initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic.h -->
