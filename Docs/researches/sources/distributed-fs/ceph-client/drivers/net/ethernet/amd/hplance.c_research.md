# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/hplance.c

Purpose: implements the HP300 DIO LANCE Ethernet front-end using the generic `7990.h` LANCE core. It handles DIO bus discovery, HP-specific register/NVRAM access, board-level interrupt enable/disable, and netdev registration.

Important APIs and functions: module lifecycle is `hplance_init_module`/`hplance_cleanup_module` around `dio_register_driver`. DIO lifecycle is `hplance_init_one` and `hplance_remove_one`. Board setup is `hplance_init`. Register access callbacks are `hplance_writerap`, `hplance_writerdp`, and `hplance_readrdp`. Netdev operations use wrapper `hplance_open`/`hplance_close` plus generic `lance_start_xmit`, `lance_set_multicast`, optional `lance_poll`, and address helpers.

Control flow: probe allocates a netdev, reserves the DIO memory region, calls `hplance_init`, registers the netdev, and stores drvdata. `hplance_init` resets the board through DIO ID space, reads the Ethernet address from NVRAM as one nibble per byte, fills the embedded generic `struct lance_private` with base address, init-block RAM, IRQ, endian CSR3 value, ring sizes, and callback function pointers. Open calls generic `lance_open`, then enables board-level interrupts by writing `LE_IE` to the DIO status register. Close disables board-level interrupts and delegates to generic `lance_close`. Register callbacks loop until the DIO status register reports `LE_ACK`.

State and persistence: `struct hplance_private` only embeds the generic LANCE state. The MAC address is read from NVRAM but not modified. LANCE init block and buffers live in the DIO memory window at `HPLANCE_MEMOFF`.

Dependencies and integration points: depends on the HP DIO bus API, HP-specific DIO address/ID semantics from `hplance.h`, Linux netdevice helpers, raw big-endian I/O accessors, and the generic `7990.h` LANCE implementation. It integrates with DIO device IDs through `DIO_ID_LAN`.

Risks: register access busy-waits indefinitely for `LE_ACK`; a broken board could hang in the callback. Board-level interrupt status handling is minimal and delegates most work to generic LANCE code. The driver assumes DIO NVRAM nibble layout and fixed memory offsets. Init-block `lance_init_block` is shared through included generic code, so ring-size constants must match the available 16 KB board RAM.

Test signals: DIO probe/remove, NVRAM MAC extraction, generic LANCE open/RX/TX/multicast paths, board interrupt enable/disable, and fault testing for missing `LE_ACK` if hardware simulation is available.
