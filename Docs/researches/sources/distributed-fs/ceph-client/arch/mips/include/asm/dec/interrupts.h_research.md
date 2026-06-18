<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/interrupts.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/interrupts.h

**Purpose:** Defines DECstation interrupt numbers, CPU interrupt masks, interrupt mapping tables, and common handler prototypes.

**Important APIs/types/functions:** `DEC_IRQ_*` enumerates ordinary, I/O ASIC DMA, TURBOchannel, and timer/video interrupts. `DEC_NR_INTS`, `DEC_MAX_CPU_INTS`, `DEC_MAX_ASIC_INTS`, CPU IRQ mask macros, `int_ptr`, and extern mapping tables/handlers are declared.

**Control flow:** Platform interrupt setup populates/use mapping tables and dispatches to handlers such as `kn02_io_int`, `asic_dma_int`, and `cpu_all_int`.

**State, dependencies, integration:** Integrates DEC CPU interrupt lines, I/O ASIC masks, and Linux IRQ numbers.

**Risks and test signals:** Misnumbered IRQs attach drivers to wrong lines. Test each DEC machine family interrupt map, FPU IRQ, DMA IRQs, and unimplemented handler paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/interrupts.h -->
