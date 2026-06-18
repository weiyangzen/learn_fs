# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/octeon/octeon_mgmt.c

Purpose: Implements the Cavium Octeon MII management-port netdev driver for platform devices compatible with `cavium,octeon-5750-mix`.

Important APIs, types, and functions: `struct octeon_mgmt` stores MIX/AGL register bases, port/IRQ, TX/RX DMA rings, SKB queues, NAPI, tasklet, PHY node, link cache, and resource metadata. RX helpers fill the input ring with DMA-mapped SKBs, dequeue completed ring entries, handle split packets, process optional RX timestamps, and run under NAPI. TX helpers map SKBs into output ring entries, request TX timestamps, ring hardware, and clean completions in a tasklet. `octeon_mgmt_open()` allocates rings, resets/configures hardware, initializes PHY, requests IRQ, enables interrupts/NAPI, and starts queues. `octeon_mgmt_stop()` reverses that. Probe maps resources, sets netdev ops/ethtool ops, configures MTU bounds, MAC, PHY, DMA mask, and registers the netdev.

Control flow: IRQ reads and clears MIX ISR, disables RX/TX interrupt sources, schedules NAPI or TX cleanup, then each bottom half reenables its interrupt source. Link changes reprogram AGL GMX speed/duplex/clocking under lock.

State and persistence: Runtime state is in netdev stats, SKB queues, DMA rings, hardware CSRs, PHY state, and timestamp flags. No persistent storage.

Dependencies and integration: Uses Octeon CSR accessors, OF platform resources, PHY framework, netdev/NAPI/tasklet APIs, hardware timestamping, and ethtool link operations.

Risks: DMA ring fill/clean counters must match SKB queues. RX split-packet assembly can fail under memory pressure. Hardware timestamp support is CN6XXX-specific. Open error unwinding returns `-ENOMEM` for several failure classes, which may hide root cause.

Test signals: Probe/remove with missing resources, open/stop leak checks, RX packet and split-packet receive, TX queue stop/wake, IRQ/NAPI/tasklet interaction, PHY link changes, MTU changes, multicast/promisc filtering, and hwtstamp set/get.
