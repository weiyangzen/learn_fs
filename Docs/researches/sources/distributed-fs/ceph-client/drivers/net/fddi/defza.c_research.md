# sources/distributed-fs/ceph-client/drivers/net/fddi/defza.c

## Purpose
Implements the Linux TURBOchannel driver for DEC FDDIcontroller 700/700-C DEFZA devices. Unlike `defxx.c`, this driver talks to the FZA shared packet memory and FZA command/ring protocol defined by the DEC FDDIcontroller 700 port specification. It probes TC devices, maps the full MMIO resource, resets and initializes firmware, publishes a `net_device`, handles RX/TX and SMT rings, maintains link/reset state, and supports module-configured loopback mode.

## Important APIs, Types, And Functions
The module registers one `tc_driver` from `fza_init()` and unregisters it in `fza_exit()`. `fza_probe()` and `fza_remove()` are the lifecycle entry points. `net_device_ops` connects `fza_open()`, `fza_close()`, `fza_start_xmit()`, `fza_set_rx_mode()`, `fza_set_mac_address()`, and `fza_get_stats()`.

MMIO helpers `fza_reads()`, `fza_writes()`, `fza_moves()`, and `fza_zeros()` perform packet-memory transfers using 32- or 64-bit relaxed accesses while respecting the board's word-access constraints. Reset and command helpers include `fza_do_shutdown()`, `fza_do_reset()`, `fza_reset()`, `fza_cmd_send()`, and `fza_init_send()`. Ring processing is handled by `fza_rx_init()`, `fza_do_xmit()`, `fza_do_recv_smt()`, `fza_tx()`, `fza_rx_err()`, `fza_rx()`, `fza_tx_smt()`, `fza_uns()`, and `fza_tx_flush()`. `fza_interrupt()` dispatches command, TX, RX, SMT, flush, link, unsolicited, and state-change events.

The module parameter `loopback` is sanitized in probe and sent through the PARAM command. The static purger and beacon multicast addresses are always inserted into the CAM before user multicast entries.

## Control Flow
Probe allocates an FDDI netdev, reserves and maps the TC memory resource, initializes private pointers to registers and rings, sets wait queues/spinlock/timer, shuts the board down, requests the shared IRQ, enters driver mode, resets the board, sends INIT, reads hardware address, revision strings, ring addresses/sizes, default link parameters, SMT version, and PMD type, then closes the interface back to the uninitialized state before registering the netdev.

Open allocates and 512-byte-aligns all host receive skbs, DMA-maps them, sends INIT again, programs CAM/promiscuous mode, sends PARAM, and waits for command completion. Subsequent state-change interrupts move the device from initialized to running/maintenance, call `fza_rx_init()`, mark the queue active, and wake TX. Close stops the queue, deletes the reset timer, issues SHUT, waits for uninitialized state, then unmaps/frees RX skbs.

TX prepends a three-byte packet request header based on the FDDI frame-control byte, temporarily masks SMT TX poll interrupts to serialize access to the RMC transmit ring, copies skb data into board packet memory through `fza_do_xmit()`, frees the skb immediately after queuing, and returns the queuing result. `fza_do_xmit()` fragments into 512-byte board buffers, writes all non-first descriptors before finally handing the first descriptor to the RMC, and stops the netdev queue when remaining ring space falls below one MTU plus header.

RX walks the host receive ring until ownership returns to FZA, reads the RMC status, validates errors and length in `fza_rx_err()`, allocates a replacement aligned skb, unmaps the completed buffer, optionally feeds non-promiscuous async management frames into the SMT RX ring, trims preamble/starting delimiter/FCS, calls `fddi_type_trans()`, submits via `netif_rx()`, updates counters, and returns the descriptor to FZA. SMT TX frames from firmware can be mirrored to packet taps with `dev_queue_xmit_nit()` and then queued into the RMC TX ring. Unsolicited events currently account RX-overrun events.

## State And Persistence Behavior
All state is in `struct fza_private` for the netdev lifetime: MMIO pointers, ring indices, RX skb/DMA arrays, command/state wait flags, reset timer state, queue-active flag, interrupt mask, counters, and firmware-provided link parameters. Hardware command buffers and rings live in adapter memory and are addressed via offsets returned by INIT. RX buffers are allocated per open and freed on close/remove. The reset timer persists while recovery is in progress; if a reset times out it asserts reset harder for one second, then clears reset and waits again. There is no disk persistence.

## Dependencies And Integration Points
The file depends on Linux TURBOchannel, FDDI netdev setup, DMA mapping, wait queues, timers, interrupt APIs, MMIO APIs including non-atomic lo-hi 64-bit I/O, and constants/types from `defza.h`. It integrates with the net stack through `alloc_fddidev()`, `register_netdev()`, `netif_rx()`, carrier state, queue wake/stop, packet taps, and `fddi_type_trans()`. It is matched only to TC module `PMAF-AA`.

## Risks
Hardware access ordering and access width are critical; packet memory comments state only word writes/reads are permitted. `fza_start_xmit()` frees the skb even when `fza_do_xmit()` reports busy, so return semantics are sensitive and should be audited against current netdev expectations. Open error paths after RX allocation or command failure do not obviously free every allocated RX skb before returning in all cases. State transitions rely on interrupts and wait queues; missed `STATE_CHG` or `CMD_DONE` events cause multi-second timeouts. Reset recovery manipulates timers from interrupt and timer contexts, so synchronization around `reset_timer` and `fp->lock` matters. `fza_set_mac_address()` returns `-EOPNOTSUPP`, so address changes are intentionally unsupported despite CAM programming for multicast.

## Test Signals
Build with `CONFIG_DEFZA` and TURBOchannel support. Runtime smoke tests should show probe, reset completion, INIT success, revision/MAC logging, close-to-uninitialized during probe, successful `register_netdev()`, open PARAM completion, link carrier changes, RX/TX counters, queue stop/wake behavior, multicast/promiscuous updates, SMT traffic handling, close SHUT completion, and remove cleanup. Fault signals include reset timeout recovery, HALTED-state reset, command timeout logs, RX overrun unsolicited events, memory-pressure drops, and no divide-by-zero or ring-index corruption during early interrupts.
