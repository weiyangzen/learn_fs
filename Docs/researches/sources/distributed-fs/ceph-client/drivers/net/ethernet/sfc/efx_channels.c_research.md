# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/efx_channels.c

Purpose: Manages SFC interrupt mode selection, channel topology, event queue lifecycle, TX/RX queue probing/removal, XDP TX queue assignment, channel resize, interrupt enable/disable, channel start/stop, and NAPI polling.

Important APIs and functions: Public functions include `efx_probe_interrupts()`, affinity setters, eventq probe/init/start/stop/fini/remove, channel init/probe/remove/realloc, `efx_set_channels()`, interrupt enable/disable pairs, `efx_start_channels()`, `efx_stop_channels()`, and NAPI init/fini. Static helpers compute RSS parallelism, allocate MSI-X channels, allocate/copy channels, assign XDP TX queues, process NAPI events, and adapt IRQ moderation.

Control flow: Probe chooses MSI-X, MSI, or legacy interrupt mode, sizes RX/TX/extra/XDP channels, requests vectors, records IRQs, assigns RSS spread, and sets real netdev queue counts. Channel probe allocates event queues then TX/RX queues. Start initializes TX/RX queues, pushes RX descriptors, and starts event queues. NAPI polling processes events, flushes pending RX packets, refills RX descriptors, updates BQL completion counters, delivers skb lists, adapts RX IRQ moderation, and acknowledges event queue reads. Resize clones channels, swaps queue sizes, probes replacements, and rolls back on failure.

State and persistence: Mutates global module parameters `efx_interrupt_mode` and `rss_cpus`; NIC fields for channel counts, offsets, XDP queue mode/counts, IRQ mode, RSS spread, and `irq_soft_enabled`; per-channel eventq state, IRQ moderation, NAPI state, and stats baselines; and queue arrays. All state is runtime and reconstructed on probe/reset.

Dependencies and integration points: Uses PCI MSI/MSI-X APIs, CPU topology, NAPI, RX/TX common queue code, NIC type eventq and IRQ callbacks, MCDI event/poll modes, RFS acceleration, workarounds, SR-IOV VF sizing, PTP channel update, and XDP flush.

Risks: Channel count math must satisfy vector, VI, XDP, RSS, SR-IOV, and separate-TX constraints. Resize rollback must preserve PTP channel and free only copied resources. Interrupt soft/hard enable ordering and memory barriers protect NAPI/event processing. Borrowed XDP queues can reduce performance and must select checksum-compatible queues. NAPI budget and RX flush behavior can affect packet latency and drops.

Test signals: MSI-X/MSI/legacy fallback, RSS CPU limiting, SR-IOV VF-size RSS limiting, separate TX channel mode, XDP dedicated/shared/borrowed queue modes, channel resize success and rollback, NAPI poll under budget/exhaustion, IRQ moderation adaptation, RFS expiry, and interrupt disable during reset/remove.
