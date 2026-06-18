# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/hydra.c

Purpose: Zorro-II Amiga Hydra Systems Amiganet driver using an embedded 8390 core. It supports a memory-mapped NS8390 clone with onboard RAM, 10BASE-2/AUI connectors, Zorro resource discovery, and direct board-memory packet transfers.

Important APIs, types, and functions: main paths are `hydra_init_one()`, `hydra_init()`, `hydra_open()`, `hydra_close()`, `hydra_reset_8390()`, `hydra_get_8390_hdr()`, `hydra_block_input()`, `hydra_block_output()`, `hydra_remove_one()`, and module init/exit. The driver supplies `hydra_netdev_ops` backed by internal `__ei_*` functions.

Control flow: the Zorro driver claims the 64 KiB board resource, allocates a 8390 netdev, reads the MAC from the board address PROM, sets word and big-endian mode, requests shared `IRQ_AMIGA_PORTS`, fills `ei_status` pages/callbacks/register offsets, initializes the core stopped, registers the netdev, and stores driver data. TX/RX packet movement copies directly between Zorro memory and SKBs, with wrap handling on input.

State and persistence: device state is mostly `struct ei_device`: big-endian word mode, register-offset table, TX/RX pages, and callbacks. No real hardware reset state exists; `hydra_reset_8390()` logs that reset is unavailable.

Dependencies and integration points: depends on Amiga/Zorro APIs, Zorro-II address translation, `IRQ_AMIGA_PORTS`, `z_memcpy_toio/fromio`, and included `lib8390.c`.

Risks: lack of hardware reset limits recovery from stuck NIC state. All devices share the Amiga ports IRQ. Endianness is manually handled in header reads with `WORDSWAP()`. Resource cleanup must use physical address translation matching the virtual base arithmetic.

Test signals: Zorro product match, resource claim/release, valid PROM MAC, netdev registration, shared IRQ delivery, TX/RX through direct board memory, RX ring wrap, big-endian header decoding, and graceful behavior on tx-timeout despite no reset.
