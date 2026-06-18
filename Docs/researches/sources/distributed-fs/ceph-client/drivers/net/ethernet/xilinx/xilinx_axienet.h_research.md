# sources/distributed-fs/ceph-client/drivers/net/ethernet/xilinx/xilinx_axienet.h

Purpose: shared definitions for the Xilinx AXI Ethernet driver and its MDIO/main sources.

Important definitions: frame size and option constants, AXI DMA channel and descriptor offsets, DMA IRQ/coalescing masks, AXI Ethernet MAC register offsets, VLAN/filter/statistics/MDIO masks, PHY type values, checksum/status feature bits, PCS/PMA switching constants, and the exact hardware statistics counter enum. `struct axidma_bd` defines the aligned AXI DMA descriptor, including 64-bit address fields and SKB pointer. `struct skbuf_dma_descriptor` supports dmaengine mode. `struct axienet_local` is the driver private state for phylink, clocks, MDIO, MAC/DMA mappings, NAPI, DIM, DMA rings, stats accounting, error work, IRQs, PHY mode, options, features, frame limits, and dmaengine channels/rings.

Inline APIs: `axienet_ior()` and `axienet_iow()` access MAC registers. `axienet_dma_out32()` and `axienet_dma_out_addr()` write DMA registers and support 64-bit DMA when configured. `axienet_lock_mii()` and `axienet_unlock_mii()` serialize MDIO users through the bus lock. Prototypes expose `axienet_mdio_setup()` and teardown.

State and dependencies: this header defines the persistent state model used by the AXI Ethernet implementation. It depends on phylink, DIM, netdevice, spinlocks, VLAN, skbuff, interrupts, clocks, DMA descriptors, and optional 64-bit MMIO writes.

Risks and tests: risks include duplicated descriptor mask definitions, 64-bit DMA address handling, stats sequence synchronization, phylink/PCS state, DIM/coalescing setup, and mismatch between `enum temac_stat` order and hardware counter layout. Test AXI DMA ring operation, dmaengine mode, 64-bit DMA systems, phylink modes, MDIO setup, statistics overflow, checksum offload, VLAN/multicast options, and suspend/remove paths in implementation files.
