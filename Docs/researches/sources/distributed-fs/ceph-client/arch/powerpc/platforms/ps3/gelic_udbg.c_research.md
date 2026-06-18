## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/gelic_udbg.c

### Purpose
`gelic_udbg.c` implements early debug output by sending UDP broadcast packets through the PS3 GELIC network device using LV1 calls.

### Important APIs, Types, And Functions
Important functions are `map_dma_mem()`, `unmap_dma_mem()`, `gelic_debug_init()`, `gelic_debug_shutdown()`, `gelic_sendbuf()`, `ps3gelic_udbg_putc()`, exported `udbg_shutdown_ps3gelic()`, and init `udbg_init_ps3gelic()`.

### Control Flow
Initialization opens the GELIC device, maps a static debug block for DMA, builds Ethernet/VLAN/IP/UDP headers from LV1 MAC/VLAN queries, and installs `udbg_putc`. Characters accumulate until newline or a 1000-byte limit, then `gelic_sendbuf()` fills lengths/checksum, marks the descriptor card-owned, starts TX DMA, and busy-waits for completion. Shutdown unmaps DMA and closes the LV1 device.

### State, Persistence, And Dependencies
State is static DMA bus address, descriptor packet buffer, header pointers, and current message pointer. Dependencies include LV1 net control/TX DMA, raw Ethernet/IP/UDP structures, DMA mapping through LV1, and early `udbg` hooks.

### Integration Points
Selected by early debug config and used before normal console/network drivers are available.

### Risks
Errors call `lv1_panic(0)`, appropriate only for early debug. Checksums and header fields are manually built and endian-sensitive. Busy-waiting can hang if DMA never completes.

### Test Signals
Receiving UDP broadcasts on port 18194, VLAN and non-VLAN paths, shutdown cleanup, and long-line flushing validate behavior.
