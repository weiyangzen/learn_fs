# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/mvme147.c

Purpose: implements the MVME147 onboard LANCE Ethernet front-end using the generic `7990.h` LANCE core. It sets up one machine-specific netdev, allocates DMA-capable RAM for the generic LANCE init block and buffers, provides big-endian register callbacks, and controls PCC LAN interrupts.

Important APIs and functions: module lifecycle is `m147lance_init`/`m147lance_exit` around `mvme147lance_probe`. Netdev operations are wrapper `m147lance_open` and `m147lance_close` plus generic `lance_start_xmit`, `lance_set_multicast`, `lance_tx_timeout`, and address helpers. Register callbacks are `m147lance_writerap`, `m147lance_writerdp`, and `m147lance_readrdp`.

Control flow: probe runs only on `MACH_IS_MVME147` and only once, allocates a netdev, reads the board Ethernet address suffix from `ETHERNET_ADDRESS` with OUI `08:00:3e`, allocates 32 KB of DMA pages, fills embedded generic LANCE private state with base address, CPU and LANCE views of the init block, big-endian CSR3 busmaster value, IRQ, ring sizes, and register callbacks, then registers the netdev. Open delegates to generic `lance_open`, clears pending PCC LAN interrupts, and enables IRQ 4 bits in `m147_pcc->lan_cntrl`. Close disables PCC LAN interrupts and delegates to generic close. Exit unregisters the netdev, frees DMA pages, and frees the device.

State and persistence: `struct m147lance_private` embeds generic LANCE state and stores the allocated RAM address. The driver has one global `dev_mvme147_lance`. No persistent storage is written; the MAC source is board firmware/hardware memory.

Dependencies and integration points: depends on MVME147 machine detection and hardware definitions from `asm/mvme147hw.h`, generic LANCE support from `7990.h`, big-endian I/O helpers, and Linux netdevice APIs. It integrates with the platform as a single legacy module rather than a discoverable bus driver.

Risks: probe uses `__get_dma_pages(GFP_ATOMIC, 3)` during module init, which may fail under memory pressure. The generic LANCE init block is passed as both CPU and device-visible address, assuming identity visibility suitable for MVME147. Exit assumes `dev_mvme147_lance` is a valid netdev; if init failed and exit were invoked unexpectedly this would be unsafe, though module core normally calls exit only after successful init. Interrupt control is board-specific magic values with minimal abstraction.

Test signals: module load only on MVME147, MAC derivation from `ETHERNET_ADDRESS`, successful 32 KB buffer allocation, generic LANCE RX/TX/multicast/timeout behavior, PCC interrupt enable/disable, and module unload resource cleanup.
