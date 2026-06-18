# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/epic100.c

## Purpose
`epic100.c` is the PCI Fast Ethernet driver for SMC83c170/83c175 EPIC/100 and EPIC/C controllers, including SMC EtherPower II 9432 and related CardBus hardware. It manages PCI resources, MII PHY access, DMA descriptor rings, NAPI RX/TX completion, multicast filtering, ethtool/MII control, media monitoring, and PCI power management.

## Important APIs, Types, and Functions
- `struct epic_private` stores RX/TX rings, SKB arrays, DMA addresses, locks, NAPI object, ring indices, interrupt mask, RX buffer size, MMIO base, PCI device, chip flags, timer, FIFO threshold, multicast filter cache, PHY list, MII state, and queue/media flags.
- `struct epic_tx_desc` and `struct epic_rx_desc` are host-endian DMA descriptors; big-endian systems program descriptor byte swapping in `GENCTL`.
- PCI entry points are `epic_init_one()` and `epic_remove_one()`.
- Netdev operations are `epic_open()`, `epic_close()`, `epic_start_xmit()`, `epic_tx_timeout()`, `epic_get_stats()`, `set_rx_mode()`, and `netdev_ioctl()`.
- NAPI and interrupt paths are `epic_interrupt()`, `epic_poll()`, `epic_rx()`, `epic_tx()`, and `epic_rx_err()`.
- PHY helpers are `mdio_read()`, `mdio_write()`, `check_media()`, and MII-backed ethtool operations.

## Control Flow
Probe enables PCI, validates BAR size, requests regions, allocates the netdev, maps the selected BAR, initializes MII callbacks, allocates coherent TX/RX rings, applies module media/duplex options, powers the chip enough to read MII and MAC registers, reads the MAC from LAN registers, discovers PHY addresses, powers down MII-capable chips, sets netdev operations/NAPI/watchdog, registers the device, and reports resources.

Open resets the chip, enables NAPI, requests the IRQ, initializes rings and RX buffers, applies documented TEST1 magic, powers MII where required, programs endian/GENCTL behavior, writes MAC registers, chooses duplex from forced media or link partner, writes TX/RX descriptor base registers, starts RX, starts the queue, enables interrupts, and starts a media timer. Interrupts acknowledge normal non-NAPI events immediately, schedule NAPI for RX/TX events while masking those sources, and handle uncommon counter overflow, TX underrun, and PCI bus errors. Polling reclaims TX, receives packets up to budget, handles RX overflow/full, and reenables NAPI interrupts when complete.

TX pads short packets, maps the SKB, fills descriptor fields with ownership last, advances `cur_tx`, stops the queue near `TX_QUEUE_LEN`, and kicks `TxQueued`. TX completion checks success/error bits, updates stats, unmaps DMA, frees SKBs, and wakes the queue. RX consumes descriptors no longer owned by hardware, copies small packets below `rx_copybreak` or takes ownership of the mapped SKB, passes packets with `netif_receive_skb()`, then refills descriptors.

## State and Persistence
Persistent runtime state is in `epic_private`, coherent rings, SKB mappings, cached multicast filter, MII state, and hardware registers. Module parameters persist for the loaded module: `debug`, per-card `options`, per-card `full_duplex`, and `rx_copybreak`. Hardware error counters are latched in device registers and accumulated into `dev->stats`. There is no filesystem persistence.

## Dependencies and Integration Points
The driver depends on PCI, DMA mapping, NAPI, Linux netdev, MII helpers, ethtool, timers, spinlocks, CRC32 multicast hashing, and PM callbacks. It integrates with Kconfig through `CONFIG_EPIC100`, with generic MII ioctl/ethtool paths, and with netpoll indirectly through NAPI-safe interrupt handling.

## Risks and Edge Cases
- Descriptor endianness is unusual: descriptors are host-endian and hardware byte-swaps on big-endian systems.
- RX initialization and refill lack explicit DMA mapping error checks in some allocation paths, so mapping failures are a risk area.
- The multicast hash path is effectively bypassed for multicast due to a documented chip bug, accepting all multicasts.
- PCI bus errors trigger pause/restart from interrupt context; restart must preserve ring indices correctly.
- Ettool and ioctl power the device up temporarily when the interface is down and must power it down symmetrically using `ethtool_ops_nesting`.

## Test Signals
Test PCI probe/remove, NAPI RX/TX traffic, ring wrap at 256 descriptors, TX queue stop/wake near `TX_QUEUE_LEN`, FIFO underrun threshold increase, PCI bus error restart, multicast/promiscuous mode, small-packet copy path, MTU-driven RX buffer size, MII reads while down via ioctl/ethtool, forced duplex module options, suspend/resume, and big-endian builds.
