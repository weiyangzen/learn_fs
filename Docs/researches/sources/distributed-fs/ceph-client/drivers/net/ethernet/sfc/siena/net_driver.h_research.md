# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/net_driver.h

## Purpose

`net_driver.h` is the main shared state and callback contract for the Siena SFC net driver. It defines queue/channel/NIC data structures, feature limits, RX/TX buffer state, RSS/RFS/XDP/PTP/MTD integration fields, link state, flow control flags, and the large `struct efx_nic_type` hardware operation table used to bind common driver code to specific NIC implementations.

## Important APIs, Types, and Functions

Core structures include `struct efx_buffer` for coherent DMA memory, `struct efx_special_buffer` for buffer-table-backed rings, `struct efx_tx_buffer` and `struct efx_tx_queue` for software and hardware TX state, `struct efx_rx_buffer`, `struct efx_rx_page_state`, and `struct efx_rx_queue` for RX descriptors and recycled pages, `struct efx_channel` for event/NAPI/RX/TX grouping, `struct efx_msi_context` for stable IRQ handler context, `struct efx_rss_context`, optional `struct efx_arfs_rule` and `struct efx_async_filter_insertion`, `struct efx_mtd_partition`, and `struct efx_nic`.

`struct efx_nic_type` is the main integration table. It contains lifecycle callbacks, reset, port, MCDI, interrupt, queue, event, filter, MTD, PTP, SR-IOV, VLAN, UDP tunnel, stats, and hardware property callbacks.

Inline helpers provide channel iteration, queue lookup, RX buffer lookup/wrapping, max frame size calculation, timestamp TX flag manipulation, TX fill-level approximations, supported feature union, and TX insert-buffer access with paranoid checks.

## Control Flow

Most driver code takes an `efx_nic` and dispatches through `efx->type` for hardware-specific operations. Channels group one event queue with at most one RX queue and several TX queues. Common code iterates channels with `efx_for_each_channel()`, accesses traffic or XDP channels by offsets, and uses queue type indexes to select checksum/high-priority/XDP TX queues.

The NIC state structure is organized by write frequency: rarely written configuration and lifecycle fields first, then frequently updated monitor, interrupt, stats, and drop counters. Locking contracts are documented in field comments: RTNL serializes device state, `mac_lock` protects port/MAC/PHY fields, `filter_sem` protects filter table existence, RFS has mutex/spinlock split, and stats updates use `stats_lock`.

## State and Persistence Behavior

This header defines nearly all long-lived in-memory driver state: PCI mapping, interrupt mode, queue arrays, DMA ring dimensions, RSS context, firmware vport ID, IRQ status, MCDI state, port/link/PHY state, XDP program pointer, filter table state, queue flush counters, SR-IOV counters, PTP data, VPD serial, and node/no-descriptor drop accounting. It also defines per-queue producer/consumer counters that persist across NAPI cycles and reset only during queue lifecycle operations.

## Dependencies and Integration Points

It includes Linux netdevice, ethtool, VLAN, PCI, workqueue, MTD, busy-poll, and XDP headers plus local `enum.h`, `bitfield.h`, and `filter.h`. Because most translation units include it, changes here affect TX, RX, event handling, ethtool, MCDI, PTP, MTD, SR-IOV, reset, and probe paths.

## Risks and Test Signals

The file's risk is structural coupling: field layout, callback semantics, and inline assumptions are used throughout the driver. Queue index helpers rely on correctly dimensioned channel offsets; incorrect `n_channels`, `tx_channel_offset`, or XDP channel counts can silently route to the wrong queues. Locking mistakes around `port_enabled`, `xdp_prog`, filter state, or RFS arrays can race with NAPI/workqueue paths. Test signals include all-config builds, sparse/lockdep/KCSAN runs, queue/channel dimension tests, XDP attach/detach, PTP channel allocation, MTD enabled/disabled builds, RFS enabled/disabled builds, and reset/open/close stress.
