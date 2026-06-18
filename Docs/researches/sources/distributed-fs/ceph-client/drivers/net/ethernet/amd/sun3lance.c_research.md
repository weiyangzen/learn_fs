# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/sun3lance.c

## Purpose
`sun3lance.c` is a legacy Ethernet driver for the on-board AMD LANCE controller on Sun3/Sun3x systems. It uses fixed or platform-specific register addresses, DVMA memory for the init block and descriptor rings, and the classic netdev interface to support early Sun hardware use cases such as RARP/BOOTP and NFS root.

## Important APIs, Types, And Functions
Hardware formats are `struct lance_rx_head`, `struct lance_tx_head`, `struct lance_init_block`, and `struct lance_memory`. Driver private state is `struct lance_private`, containing I/O register pointers, DVMA shared memory, RX/TX cursors, a bit-lock, and queue-full flag. The netdev operations are `lance_open`, `lance_close`, `lance_start_xmit`, and `set_multicast_list`; receive and interrupt handling is in `lance_rx` and `lance_interrupt`. Probe/module functions are `sun3lance_probe`, `lance_probe`, `sun3lance_init`, and `sun3lance_cleanup`.

## Control Flow
Module init calls `sun3lance_probe`, which rejects non-Sun3/Sun3x machines, checks IDPROM machine type for known on-board LANCE systems, allocates an Ethernet device, calls `lance_probe`, and registers the netdev. `lance_probe` maps the LANCE register area, probes CSR behavior, allocates aligned DVMA shared memory, requests the fixed IRQ, copies the PROM MAC address into the netdev and byte-swapped init block, initializes descriptor base pointers, sets netdev ops, and marks the link present.

Open stops the chip, initializes TX/RX rings, writes CSR1/CSR2 to point at the init block and CSR3 endian/bus mode, starts initialization, busy-waits for IDON, then starts RX/TX with interrupts enabled and starts the netdev queue. TX stops the queue, takes a bit-lock, pads short packets to Ethernet minimum, copies SKB data into the DVMA TX buffer, publishes ownership bits last, advances `new_tx`, writes transmit-demand/start bits, frees the SKB, clears the lock, and restarts the queue if the next descriptor is host-owned.

Interrupt handling flushes CPU cache, reads/acks CSR0, clears errors, reaps TX descriptors and updates stats, wakes the queue when space returns, runs `lance_rx` for RX interrupts, logs babble/miss/memory errors, and restarts the chip on memory error. RX loops while descriptors are host-owned, validates complete packets, allocates SKBs, copies from DVMA RX buffers, passes packets via `netif_rx`, updates stats, then returns descriptors to chip ownership.

## State And Persistence
State is in DVMA shared memory and `lance_private` ring cursors. The driver uses fixed `LANCE_OBIO` and `LANCE_IRQ` for Sun3 and `SUN3X_LANCE` for Sun3x. Module parameter `lance_debug` controls logging. There is no persistent storage.

## Dependencies And Integration Points
The driver depends on m68k/Sun3 architecture headers, IDPROM machine data, DVMA allocation/address translation, cache flushing, low-level I/O register access, Linux netdev/SKB APIs, fixed IRQ registration, and module init/exit. It does not use PCI, NAPI, DMA API, ethtool, or phylib.

## Risks
The driver is hardware- and architecture-specific and relies on empirical fixed addresses/IRQs. It uses old-style bit locking and direct interrupt disabling rather than modern spinlock patterns. Cleanup unregisters and frees the netdev but does not visibly free the DVMA allocation or IRQ in module exit after probe success, which is a legacy lifetime concern. Multicast support is marked untested and mostly uses broad filtering. Cache coherency depends on `flush_cache_all` in interrupt handling.

## Test Signals
Real validation requires Sun3/Sun3x hardware or emulator support. Signals include successful probe at expected address/IRQ, BOOTP/NFS-root traffic, TX/RX packet counters, TX timeout recovery, CSR memory-error restart, multicast/promiscuous toggles, module parameter debug logs, and module unload/reload behavior.
