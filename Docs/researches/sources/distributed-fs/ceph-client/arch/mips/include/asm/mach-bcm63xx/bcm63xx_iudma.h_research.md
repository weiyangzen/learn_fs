# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_iudma.h

**Purpose:** Defines the BCM63xx internal DMA descriptor format and status/control masks used by Ethernet and USB DMA paths.

**Important APIs/types/functions:** Exports `struct bcm_enet_desc` with `len_stat` and `address`; control masks for length, owner, EOP, SOP, ESOP, wrap, USB zero/no-zero; status masks for underrun, append CRC, oversize, RX error, CRC, overflow; and combined `DMADESC_ERR_MASK`.

**Control flow:** Network/USB drivers fill descriptors with address, length, SOP/EOP/WRAP/OWNER bits, hand ownership to hardware, then read status/error bits on completion.

**State and persistence behavior:** Descriptor rings in DMA-coherent memory are shared mutable state between CPU and hardware. The header defines layout only.

**Dependencies and integration points:** Depends on Linux fixed-width types. Integrated by BCM63xx Ethernet MAC/switch and USB device DMA engines, plus cache/DMA mapping code.

**Risks:** Bit ownership and length masks must match hardware exactly. Wrong cache coherency, wrap, or owner handling can corrupt packets or hang DMA. Error mask excludes `DMADESC_APPEND_CRC`, which is status not necessarily error.

**Test signals:** Run RX/TX network traffic, USB DMA transfers, ring wrap stress, error injection for CRC/overflow/underrun, and verify descriptor ownership transitions with DMA debug enabled.
