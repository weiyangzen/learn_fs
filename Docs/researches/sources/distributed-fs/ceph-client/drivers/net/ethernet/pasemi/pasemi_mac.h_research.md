# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac.h

Purpose: Defines the PaSemi MAC driver's software state, ring sizing, ring access macros, MAC type identifiers, and MAC configuration register offsets/bitfields.

Important APIs/types/functions: `struct pasemi_mac_txring`, `struct pasemi_mac_rxring`, and `struct pasemi_mac_csring` wrap `struct pasemi_dmachan` with locks, ring indexes, descriptor metadata, timers, buffer rings, checksum event flags, and back-pointers. `struct pasemi_mac` is the private netdev state tying together PCI devices, NAPI, DMA interface, RX buffer size, checksum rings, PHY link values, IRQ names, and debug mask. Descriptor macros (`TX_DESC`, `RX_DESC`, `CS_DESC`, `*_INFO`, `RX_BUFF`) and `RING_USED`/`RING_AVAIL` provide the implementation's index arithmetic. Register constants cover `PCFG`, `MACCFG`, address registers, TX pause timing, RMON counters, and DMA interface channel mapping.

State and persistence: The header fixes RX/TX/checksum ring sizes as powers of two and encodes the hardware register ABI used by `pasemi_mac.c` and `pasemi_mac_ethtool.c`. The first-member `pasemi_dmachan` comments are part of the allocation contract with `pasemi_dma_alloc_chan()`.

Dependencies and integration: Includes netdev, ethtool, spinlock, and PHY definitions, and relies on PA Semi DMA descriptor/register definitions from platform headers included by C files.

Risks and test signals: Ring masks assume power-of-two sizes; changing sizes requires validating all descriptor increment units, hardware size programming, and RING math. Register bitfield macros are hardware ABI, so tests should include build coverage and runtime validation of MTU, link speed/duplex, RMON stats, and DMA descriptor wraparound.
