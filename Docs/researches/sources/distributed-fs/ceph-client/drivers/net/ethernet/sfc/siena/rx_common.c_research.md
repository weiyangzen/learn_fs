# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx_common.c

## Purpose

`rx_common.c` implements shared Siena RX queue lifecycle, page allocation/recycling, descriptor refill, GRO fragment delivery support, RSS indirection defaults, filter spec hashing/equality, filter table probe/remove, and optional accelerated RFS rule insertion/expiry. It is the resource-management counterpart to packet delivery in `rx.c`.

## Important APIs, Types, and Functions

RX queue lifecycle APIs are `efx_siena_probe_rx_queue()`, `efx_siena_init_rx_queue()`, `efx_siena_fini_rx_queue()`, and `efx_siena_remove_rx_queue()`. Buffer/page helpers include `efx_siena_recycle_rx_pages()`, `efx_siena_discard_rx_packet()`, `efx_siena_free_rx_buffers()`, `efx_siena_rx_slow_fill()`, `efx_siena_rx_config_page_split()`, and `efx_siena_fast_push_rx_descriptors()`.

Delivery support includes `efx_siena_rx_packet_gro()` and `efx_siena_set_default_rx_indir_table()`. Filter helpers are `efx_siena_filter_is_mc_recipient()`, `efx_siena_filter_spec_equal()`, `efx_siena_filter_spec_hash()`, `efx_siena_probe_filters()`, and `efx_siena_remove_filters()`. Under `CONFIG_RFS_ACCEL`, it adds ARFS hash/rule helpers, `efx_siena_filter_rfs()`, worker `efx_filter_rfs_work()`, and `__efx_siena_filter_rfs_expire()`.

## Control Flow

Queue probe rounds requested RX entries up to a power-of-two minimum, allocates the software buffer ring, and delegates hardware descriptor allocation to `efx_nic_probe_rx()`. Init resets producer/consumer counters, creates the recycle ring, computes max fill and refill trigger based on `rx_refill_threshold`, registers XDP RXQ info, and initializes the hardware RX queue.

Fast refill checks fill level against `fast_fill_trigger`, allocates batches of pages, maps them for DMA, slices pages into one or more RX buffers with XDP headroom and alignment, marks the last buffer in each page, and notifies hardware when `added_count` advances. If allocation or mapping fails in atomic context, it schedules a slow-fill timer that generates a refill event later.

Page recycling stores only fully consumed pages whose last buffer has completed. Reuse requires `page_count(page) == 1`; otherwise the DMA mapping is unmapped and the page reference dropped. Queue finalization deletes slow-fill timers, frees outstanding descriptor pages, drains the recycle ring, and unregisters XDP RXQ info.

Filter probe holds `mac_lock` and `filter_sem`, delegates hardware filter table probe, and optionally allocates per-channel RFS flow-id arrays. RFS insertion dissects skb flow keys, builds an RX filter spec, reserves an in-flight slot, records/updates an ARFS hash rule, schedules asynchronous insertion, and later records filter IDs per channel for expiry.

## State and Persistence Behavior

Persistent state includes RX buffer arrays, descriptor rings, page recycle rings and counters, fill thresholds, slow-fill timers, XDP RXQ registration, RSS indirection table contents, filter table state, per-channel RFS arrays/counters, and `efx->rps_slot_map`/hash table. DMA mappings are held in `struct efx_rx_page_state` at the start of each allocated page.

## Dependencies and Integration Points

It depends on page allocator and DMA APIs, XDP RXQ registration, NAPI GRO, RPS/RFS APIs, flow dissector, filter APIs from `filter.h`, NIC type RX/filter callbacks, and queue/channel definitions in `net_driver.h`. It integrates with `rx.c`, farch event completion, netdev RFS hooks, XDP attach lifecycle, and reset/open/close queue management.

## Risks and Test Signals

Risk areas include page reference accounting, recycle ring wrap logic, DMA unmap exactly once per page, partial page insertion on refill failure, slow-fill timer cancellation, XDP RXQ unregister on init failure, RFS in-flight slot leaks, and filter hash equality staying aligned with `struct efx_filter_spec`. Tests should include RX refill under memory pressure, IOMMU DMA mapping errors, queue fini with outstanding descriptors, page recycle reuse/failure/full counters, RFS concurrent insert/expire/remove, filter table probe failure unwind, and XDP attach/detach around RX queue reinitialization.
