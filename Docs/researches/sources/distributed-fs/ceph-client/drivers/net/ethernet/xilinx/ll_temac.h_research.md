# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/ll_temac.h

Purpose: shared definitions for the Xilinx LocalLink TEMAC driver and its MDIO companion.

Important definitions: the header defines frame sizes, option bits, LocalLink DMA register indexes and status bits, direct and indirect TEMAC register offsets, MDIO access bits, descriptor status/control flags, checksum feature flags, and multicast table size. `struct cdmac_bd` models the LocalLink DMA descriptor. `struct temac_local` is the main private data: netdev/device, PHY/MDIO fields, TEMAC and DMA register accessors, IRQs, locks, options, descriptor rings, indices, coalescing values, RX skb array, and restart work.

Control flow and integration: the main driver uses this header for DMA ring setup, TX/RX processing, option programming, PHY attachment, and register access. The MDIO file uses `temac_local`, indirect access helpers, and MDIO register constants. The macros `temac_ior()` and `temac_iow()` dispatch through endian-selected function pointers.

State and persistence: `temac_local` persists across probe and holds both software queue state and mapped hardware resources. Descriptor rings are coherent DMA memory; RX skb ownership alternates between DMA and network stack.

Risks and tests: risks include endian and DCR/MMIO mode mismatch, descriptor bit endianness, shared indirect-lock correctness between TEMAC instances, and max frame sizing. Compile tests plus hardware TX/RX, MDIO, multicast, coalescing, and endian-specific platforms are important.
