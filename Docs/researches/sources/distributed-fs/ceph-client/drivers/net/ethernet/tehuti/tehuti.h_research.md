# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tehuti.h

## Purpose
This header defines the private ABI for the legacy Tehuti driver. It provides compile-time feature switches, driver metadata, FIFO geometry, endian/DMA helpers, register offsets, interrupt/filter bit definitions, descriptor layouts, statistics layout, private driver structures, and debug/assertion macros used by `tehuti.c`.

## Important APIs, Types, and Functions
Key structures are `struct pci_nic`, `struct bdx_priv`, `struct fifo`, `struct rxdb`, `struct txdb`, `struct rxf_desc`, `struct rxd_desc`, `struct pbl`, `struct txd_desc`, and `struct bdx_stats`. Important macros include `READ_REG`, `WRITE_REG`, `CPU_CHIP_SWAP16/32`, `GET_BITS_SHIFT`, interrupt/coalescing helpers, RXD field accessors, `TXD_W1_VAL`, and hardware register constants such as `regISR`, `regIMR`, FIFO config/read/write pointer registers, MAC/VLAN/multicast registers, reset registers, and link status fields.

## Control Flow and State
The header has no direct control flow but encodes the state model used by the C file. `struct bdx_priv` persists all per-port software state, including NAPI, RX/TX FIFOs, descriptor databases, TX flow-control level, coalescing registers, stats, and PCI/netdev back-pointers. FIFO state combines DMA addresses, virtual memory, cached read/write pointers, register offsets, and packet size. Descriptor field macros define how hardware completion data drives RX length, checksum, error, VLAN, and packet-id decisions.

## Dependencies and Integration Points
The header includes Linux module, netdevice, PCI, ethtool, firmware, DMA, VLAN, interrupt, vmalloc, and networking protocol headers. It is tightly coupled to `tehuti.c` and to the specific Bordeaux/Luxor register map. Compile-time switches enable TSO, LLTX, delayed TX write-pointer updates, and optionally MSI when `CONFIG_PCI_MSI` is available.

## Risks and Test Signals
The comment on `struct tx_map` appears inverted relative to driver usage, so maintainers should trust the implementation flow rather than the prose. `BDX_ASSERT` maps to `BUG_ON`, which raises severity of bad descriptor or ring invariants. Register constants and bit masks are brittle; any hardware generation change needs direct validation. Test signals include endian builds, 32-bit and 64-bit DMA builds, descriptor format inspection, interrupt mask behavior, VLAN/multicast programming, and stats name/count agreement with `struct bdx_stats`.
