# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-reg.h

Purpose: Defines the XLGMAC MAC/MMC/MTL/DMA register map, bit positions, enumerated field values, descriptor attribute bits, and register-address helper macros.

Important APIs/constants: MAC offsets cover TX/RX control, packet filter, hash tables, VLAN, flow control, queue mapping, interrupts, version/features, MAC addresses, and RSS. MMC offsets cover TX/RX counters and interrupt enables. MTL offsets cover operation mode, queue scheduling, FIFO, flow-control, interrupts, and traffic-class registers. DMA offsets cover reset, system bus, interrupt status, debug/status, per-channel control, ring base/tail/length, interrupt enable, watchdog, and status. Descriptor constants describe RX/TX normal/context descriptor fields, packet attributes, error bits, RSS type values, VLAN insertion, and helper macros `XLGMAC_MTL_REG()`/`XLGMAC_DMA_REG()`.

Control flow and state: Declarative only. These constants are the hardware ABI used by `dwc-xlgmac-hw.c`, `dwc-xlgmac-net.c`, `dwc-xlgmac-common.c`, and ethtool stats. Descriptor bit definitions also define the state machine for DMA ownership and packet metadata propagation.

Dependencies and integration points: Paired with bit manipulation macros from `dwc-xlgmac.h`. Kconfig selects CRC/bitrev support because hash programming in hardware code uses those helpers with this register map.

Risks and test signals: Wrong positions or lengths silently corrupt hardware programming. Some queue mapping constants are fixed for queues 0-11, while the driver advertises up to 16 DMA channels. Test feature-register decoding, TX/RX descriptor bit interpretation, RSS/VLAN/MAC hash writes, interrupt enable masks, and MTL queue mapping on hardware variants.
