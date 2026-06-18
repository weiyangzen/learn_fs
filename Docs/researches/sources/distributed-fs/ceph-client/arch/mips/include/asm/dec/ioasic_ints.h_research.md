<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_ints.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_ints.h

**Purpose:** Defines DEC I/O ASIC interrupt status/mask bit numbers and IRQ-number conversion macros.

**Important APIs/types/functions:** `IO_INR_*` names DMA/error interrupt bit positions for SCC, ASC, LANCE, ACCESS.bus, floppy, and ISDN. `IO_IRQ_BASE`, `IO_IRQ_LINES`, `IO_IRQ_NR`, `IO_IRQ_MASK`, `IO_IRQ_ALL`, and `IO_IRQ_DMA` map bits to Linux IRQs.

**Control flow:** Interrupt dispatch code reads status bits, masks them, and converts to IRQ numbers using these macros.

**State, dependencies, integration:** Complements `interrupts.h` and `ioasic_addrs.h` for DEC I/O ASIC IRQ setup.

**Risks and test signals:** Upper/lower bit partition differs for Maxine versus other systems. Test DMA interrupt dispatch for each device class and mask handling for system-specific lower bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_ints.h -->
