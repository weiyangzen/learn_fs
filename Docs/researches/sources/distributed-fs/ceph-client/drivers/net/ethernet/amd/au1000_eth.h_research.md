# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/au1000_eth.h

Purpose: defines private constants, buffer descriptor types, hardware descriptor register layouts, MAC register layout, and driver-private state for the Au1x00 Ethernet platform driver.

Important APIs and types: constants include MAC register size, four RX/TX DMA descriptors, four RX/TX buffers, maximum buffer size, TX timeout, minimum packet size, and multicast filter limit. Defines `struct db_dest`, `struct tx_dma`, `struct rx_dma`, `struct mac_reg`, and `struct au1000_private`.

Control flow: no executable code. `au1000_eth.c` uses the structures to allocate coherent buffers, map fixed hardware DMA descriptor registers, address MAC registers by field, and store per-device PHY/ring state.

State and persistence: `struct au1000_private` captures all per-netdev runtime state: free buffer descriptors, descriptor register arrays, in-use buffer arrays, head/tail/full state, MAC ID, MAC enable state, cached link/speed/duplex, MDIO bus, PHY configuration, mapped register pointers, coherent buffer addresses, lock, and debug message level. No persistent storage is defined.

Dependencies and integration points: assumes Linux `u32`, `dma_addr_t`, `spinlock_t`, and `struct mii_bus` declarations from including files. It mirrors Au1x00 MAC/MACDMA hardware register layout and is private to the platform driver.

Risks: fixed descriptor and buffer counts are tied to hardware and leave little room for bursts. `struct mac_reg` field ordering must match the hardware register block exactly. `vaddr` is a `void *` used with byte arithmetic in the C file, which relies on compiler extensions accepted by kernel builds.

Test signals: compile and sparse coverage, register-offset validation against hardware documentation, and runtime RX/TX buffer assignment on Au1x00 hardware.
