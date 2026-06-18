# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-tx.c

## Purpose
Transmit path for Octeon Ethernet hardware queues and optional POW software handoff.

## Important APIs, Types, And Functions
Exports `cvm_oct_xmit()`, `cvm_oct_xmit_pow()`, `cvm_oct_transmit_qos()` by declaration context, `cvm_oct_tx_initialize()`, `cvm_oct_tx_shutdown()`, and `cvm_oct_tx_shutdown_dev()`. Important internals are `cvm_oct_free_tx_skbs()`, `cvm_oct_adjust_skb_to_free()`, `cvm_oct_kick_tx_poll_watchdog()`, cleanup tasklet, and timer IRQ handler.

## Control Flow
`cvm_oct_xmit()` selects a QoS queue, optionally linearizes skbs with too many fragments, pads small CN3XXX half-duplex frames, builds PKO command and buffer/gather pointers, optionally places eligible skb data buffers into the FPA for hardware freeing, enables IPv4 TCP/UDP checksum offload, checks FAU cleanup counters, throttles when the free-list depth is high, sends through PKO, queues core-owned skbs for later cleanup or records hardware-free debt, frees completed skbs, and arms a timer watchdog. `cvm_oct_xmit_pow()` copies skb data into FPA packet memory, builds a WQE, submits it to a POW group, updates stats, and consumes the skb. Cleanup tasklet scans all devices and frees skbs whose FAU counters show hardware completion.

## State And Persistence
Uses per-port `tx_free_list[qos]`, FAU outstanding counters, static cleanup tasklet, and CIU timer interrupt. Scratch registers are saved/restored around async IOBDMA. No durable state.

## Dependencies And Integration Points
Depends on netdev TX APIs, PKO, POW, FPA, FAU, CVMX scratch/IOBDMA, skb fragment APIs, checksum/IP helpers, global `cvm_oct_device[]`, and queue stop/wake.

## Risks
The skb reuse fast path is delicate and must reset stack-owned metadata correctly. Queue-depth handling can stop/wake netdev queues under lock pressure. Fragment gather supports at most six segment pointers. Hardware-free versus core-free accounting uses negative FAU conventions that are easy to regress.

## Test Signals
Linear and fragmented skbs, more than five frags, short CN3XXX half-duplex packets, checksum offload eligibility, queue stop/wake at depth, hardware-free skb reuse with netfilter on/off, POW transmit, cleanup timer/tasklet, shutdown draining all QoS lists, and TX failure/drop paths.
