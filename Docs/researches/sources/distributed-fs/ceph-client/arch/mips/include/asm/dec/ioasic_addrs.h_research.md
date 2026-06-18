<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_addrs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_addrs.h

**Purpose:** Defines DEC I/O ASIC slot address ranges, register offsets, and system support register bits.

**Important APIs/types/functions:** Constants include `IOASIC_SLOT_SIZE`, device slot offsets for ROM, IOCTL, LANCE, SCC, VDAC, RTC, ISDN, ECC, SCSI, DMA areas, `IO_REG_*` register offsets, `IO_SSR_*` DMA bits, and `KN0X_IO_SSR_*` reset/diagnostic bits.

**Control flow:** Header constants are used by platform and driver code to compute MMIO addresses and manipulate DMA/control bits.

**State, dependencies, integration:** Encodes board-specific address maps for Maxine and non-Maxine DEC I/O ASIC variants.

**Risks and test signals:** Overlapping aliases are intentional for different systems; wrong machine use targets the wrong device. Test address constants against DEC hardware docs and driver probe on Maxine/3max+ variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_addrs.h -->
