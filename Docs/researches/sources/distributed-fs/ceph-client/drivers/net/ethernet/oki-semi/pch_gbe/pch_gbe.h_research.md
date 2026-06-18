# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe.h

## Purpose
Shared private interface for the OKI/LAPIS/Intel EG20T PCH Gigabit Ethernet driver. It defines MMIO register layout, bit masks, descriptors, rings, hardware/MAC/PHY state, stats, platform quirks, and cross-file prototypes.

## Important APIs, Types, And Functions
Key types include `struct pch_gbe_regs`, RX/TX descriptors, `struct pch_gbe_buffer`, ring structs, `struct pch_gbe_hw_stats`, `struct pch_gbe_hw`, `struct pch_gbe_privdata`, and `struct pch_gbe_adapter`. Constants cover interrupts, MAC mode/reset, TCP/IP accelerator, FIFO thresholds, descriptor limits, flow control, RGMII, WOL, and checksum status.

## Control Flow
Allows `pch_gbe_main.c` to own PCI/netdev lifecycle while using PHY, ethtool, and parameter helper files. The adapter object is the shared runtime context for PCI device, netdev, MMIO registers, rings, NAPI, timer, work item, MII, PTP device, stats, and quirks.

## State And Persistence
Defines in-memory state layouts but allocates none. Hardware-visible state includes descriptors, DMA addresses, MAC/PHY config, WOL masks, timestamp settings, and feature bits. No disk persistence.

## Dependencies And Integration Points
Includes PCI, netdevice, etherdevice, ethtool, MII, vmalloc, and IP/TCP/UDP headers. Integrates with PCH PTP, DMA, ethtool stats, MII ioctls, and parameter validation.

## Risks And Edge Cases
The register struct must match hardware. Ring counts must remain multiples of eight. Descriptor DMA fields are 32-bit while probe attempts a 64-bit DMA mask first. 32-bit stats can wrap.

## Test Signals
Compile cross-file users, ethtool register dump sanity, descriptor setup, interrupt decoding, MII access, WOL, checksum offload, and PTP timestamp paths.
