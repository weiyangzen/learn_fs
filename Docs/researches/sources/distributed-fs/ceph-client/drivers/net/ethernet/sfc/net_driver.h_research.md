# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/net_driver.h

Purpose: this is the central shared type and helper header for the SFC network driver. It defines queue, channel, NIC, filter, RSS, XDP, link, MTD, and NIC-type operation structures used across the driver.

Important types: `struct efx_buffer` wraps coherent DMA buffers; `struct efx_tx_buffer` and `struct efx_tx_queue` model TX descriptor/software rings and counters; `struct efx_rx_buffer`, `struct efx_rx_page_state`, and `struct efx_rx_queue` model page-backed RX descriptors, recycling, refill, XDP, and stats; `struct efx_channel` combines event queue, NAPI, IRQ, RX/TX queues, RFS counters, and PTP sync-event state. `struct efx_nic` is the top-level device state, including PCI resources, interrupt mode, channels, queues, RSS, port/MAC/PHY state, filters, queue flush state, SR-IOV/representor state, PTP, devlink, locks, work items, and stats. `struct efx_nic_type` is the controller-specific operation table.

Control flow and integration: most source files call inline dispatchers that route TX, RX, event, interrupt, filter, MTD, PTP, stats, and port operations through `efx->type`. Helper macros iterate channels and queues, compute queue indices, manage NIC state flags, map timestamp flags, and compute max frame length.

State and persistence: all runtime device state is anchored here. No disk persistence exists, but the structures mirror durable hardware/firmware state: VIs, RSS contexts, MTD partitions, link settings, filters, timestamp configuration, and firmware capabilities.

Dependencies: the header depends on Linux netdev, ethtool, PCI, MTD, XDP, busy-poll, notifier, list, locking, and SFC local `enum.h`, `bitfield.h`, and `filter.h` definitions.

Risks and tests: this header is high blast radius. Layout, concurrency, cache-line annotations, and lifecycle invariants affect the whole driver. Test signals include full driver build coverage, probe/open/stop/remove, RX/TX stress, XDP, RSS/RFS, PTP, MTD, SR-IOV, reset/recovery, ethtool stats/register dumps, and lockdep/KASAN/KCSAN runs.
