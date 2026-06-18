# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_txrx.c

## Purpose

`bnge_txrx.c` implements the Broadcom `bnge` Linux network driver's hot-path packet movement: MSI-X interrupt scheduling, NAPI notification queue polling, completion queue dispatch, RX packet construction, TPA/GRO receive coalescing, TX descriptor submission, TX completion cleanup, and feature validation for packets about to be transmitted. It is the central integration point between the kernel networking stack (`ndo_start_xmit`, NAPI/GRO, page pools, SKBs, DMA APIs) and the device's notification, completion, RX, RX-aggregate, and TX rings.

The file assumes rings, page pools, NAPI instances, HWRM tokens, and doorbells have already been allocated/configured by `bnge_netdev.c`, `bnge_hwrm.c`, and the HWRM library. Runtime persistence is in ring producer/consumer indices, software descriptor arrays, page-pool backed buffers, NAPI event flags, and HWRM wait-token states rather than durable storage.

## Important APIs and functions

- `bnge_msix()` is the MSI-X handler registered from `bnge_netdev.c`. It prefetches the current notification queue descriptor and schedules the associated NAPI instance.
- RX helper cluster:
  - `bnge_rx_pkt()` is the normal RX completion dispatcher. It handles TPA aggregate/start/end completions, validates paired completion entries, verifies expected RX consumer order, builds or copies SKBs, attaches aggregate fragments, applies RSS hash/VLAN/checksum metadata, and delivers packets through GRO.
  - `bnge_tpa_start()`, `bnge_tpa_agg()`, and `bnge_tpa_end()` implement TCP packet aggregation state. They map hardware aggregation IDs to local TPA slots, preserve the initial data buffer, collect aggregate completion records, and finally build the completed SKB.
  - `bnge_rx_skb()` builds an SKB around a received head buffer after allocating a replacement RX head buffer.
  - `bnge_copy_skb()` handles copybreak-sized packets by copying into a fresh NAPI SKB and reusing the DMA buffer.
  - `__bnge_rx_agg_netmems()`, `bnge_rx_agg_netmems_skb()`, and `bnge_reuse_rx_agg_bufs()` move page-pool netmem aggregate buffers between completion ownership and producer descriptors.
  - `bnge_rx_vlan()` decodes v1 and v3 RX VLAN metadata and applies `__vlan_hwaccel_put_tag()`.
  - `bnge_rss_ext_op()` maps RX v3 hash type information to `PKT_HASH_TYPE_L3` or `PKT_HASH_TYPE_L4`.
  - `bnge_force_rx_discard()` is used when NAPI has no RX budget, notably netpoll-style combined ring handling; it marks completions as errored so `bnge_rx_pkt()` recycles buffers without delivering packets.
- TPA/GRO helpers:
  - `bnge_tpa_metadata()` and `bnge_tpa_metadata_v2()` parse metadata formats for older and v3 TPA start completions.
  - `bnge_gro_tunnel()`, `bnge_gro_func()`, and `bnge_gro_skb()` finish software-visible GRO metadata for TPA packets when `CONFIG_INET` and `BNGE_NET_EN_GRO` are enabled.
- TX completion cluster:
  - `__bnge_tx_int()` consumes completed TX descriptors, unmaps DMA mappings, frees SKBs with `napi_consume_skb()`, updates `tx_cons`, and wakes the netdev queue through `__netif_txq_completed_wake()`.
  - `bnge_tx_int()` iterates the TX rings attached to a NAPI instance and clears `BNGE_TX_CMP_EVENT`.
  - `bnge_sched_reset_txr()` marks invalid TX completion state with `tx_fault` and logs the ring indices. The actual reset task is a TODO.
- NAPI/completion polling:
  - `__bnge_poll_work()` walks a completion ring from `cp_raw_cons`, validates completion polarity, dispatches TX completions, RX completions, and HWRM completions/events, accumulates RX work, and sets per-CP `has_more_work` when budget or partial completions stop the pass.
  - `__bnge_poll_cqs()` polls all completion rings that have notification queue events pending.
  - `__bnge_poll_cqs_done()` rings completion queue doorbells and then posts RX/TX completion side effects such as TX frees and RX/RX-aggregate producer doorbells.
  - `bnge_napi_poll()` is the exported NAPI poll method. It drains deferred completion work first, walks the notification queue, dispatches notification queue handles to completion rings, arms/rearms queues, and returns the number of RX packets consumed from the NAPI budget.
- HWRM event handling:
  - `bnge_hwrm_handler()` handles HWRM completion and async-event completion types interleaved on completion/notification queues.
  - `bnge_hwrm_update_token()` updates an RCU-protected pending wait token to `BNGE_HWRM_COMPLETE` for HWRM_DONE sequence IDs.
  - `bnge_async_event_process()` reacts to link speed/config/status events by calling `bnge_link_async_event_process()` and queueing service work with `__bnge_queue_sp_work()`.
- TX submission:
  - `bnge_start_xmit()` is the driver's `ndo_start_xmit`. It chooses the mapped TX ring, checks descriptor availability, pads short Ethernet frames, maps the linear SKB and fragments for DMA, emits a long TX BD plus extension BD plus fragment BDs, encodes VLAN/CFA action, checksum/LSO/GSO metadata, sends queue accounting, advances `tx_prod`, rings the TX doorbell or defers via `kick_pending`, and stops the netdev queue when ring space is low.
  - `bnge_txr_db_kick()` enforces descriptor visibility with `wmb()` before ringing the TX doorbell.
  - `bnge_get_gso_hdr_len()` computes header length for TCP or UDP GSO, including encapsulated packets.
  - `bnge_xmit_get_cfa_action()` extracts hardware port mux metadata from `skb_metadata_dst()`.
- `bnge_features_check()` trims advertised TX features for VLAN constraints, excessive fragments when `MAX_SKB_FRAGS > TX_MAX_FRAGS`, and packets whose length hint would exceed `bnge_lhint_arr`.

## Control flow

### Interrupt to NAPI

An MSI-X interrupt enters `bnge_msix()`, which derives `bnge_net` and `bnge_nq_ring_info` from the `bnge_napi` instance, prefetches the notification queue descriptor at `nq_raw_cons`, and schedules NAPI. The handler does not itself acknowledge device state or process packets.

`bnge_napi_poll()` first honors `nqr->has_more_work` from a previous budget-limited pass by polling queued completion rings before reading fresh notification queue entries. It then walks notification queue completions, checking `NQ_CMP_VALID()` polarity against `cp_bit`. For CQ notifications it decodes the handle into a completion ring index and RX/TX type, records `had_nqe_notify` and `toggle`, and calls `__bnge_poll_work()` unless RX budget has already been exhausted. Non-CQ notification entries are treated as HWRM completions/events.

When the notification queue has no valid entry and there is no deferred work, `__bnge_poll_cqs_done()` arms all completion queues that did work with `DBR_TYPE_CQ_ARMALL`, posts RX/RX-aggregate doorbells and TX cleanup, updates `nq_raw_cons`, completes NAPI, and arms the NQ doorbell. If the loop exits due to budget or deferred work, it uses unarmed `DBR_TYPE_CQ` completion queue doorbells and updates the NQ doorbell without completing NAPI.

### Completion ring dispatch

`__bnge_poll_work()` starts at `cpr->cp_raw_cons` and validates each descriptor as a `tx_cmp` using `TX_CMP_VALID()`. After `dma_rmb()`, it dispatches by completion type:

- TX L2 completions set `BNGE_TX_CMP_EVENT`, update the TX ring's hardware consumer either from the opaque producer value or the coalesced SQ consumer, and can force a full-budget return when enough TX descriptors were freed to make NAPI complete and wake TX queues.
- RX completion types call `bnge_rx_pkt()` when RX budget remains, otherwise `bnge_force_rx_discard()`. `-EBUSY` represents a partial completion, such as missing the RX completion extension or aggregate completions, and stops polling without advancing past incomplete work. `-ENOMEM` consumes budget to avoid an infinite loop under persistent allocation failure.
- HWRM completions/events are handed to `bnge_hwrm_handler()`.

After the loop, `cp_raw_cons` is persisted back to the completion ring and accumulated events are ORed into `bnapi->events`. `__bnge_poll_work_done()` later performs side effects keyed by those events: TX completion freeing, RX producer doorbell, and RX aggregate producer doorbell.

### Normal RX packet handling

`bnge_rx_pkt()` first handles `CMP_TYPE_RX_TPA_AGG_CMP` as a TPA aggregate record that does not use the normal paired RX extension completion. Normal RX and TPA start/end completions require a second completion entry; the function advances a temporary raw consumer to the extension, checks `RX_CMP_VALID()`, and uses `dma_rmb()` before reading more fields.

For TPA start, `bnge_tpa_start()` allocates a local aggregation slot, validates the expected RX buffer consumer and hardware error bits, swaps the consumed RX head buffer into the TPA slot, posts replacement RX descriptors, captures hash, GSO type, VLAN/CFA metadata, and clears `agg_count`. It returns no packet.

For TPA end, `bnge_tpa_end()` checks reset state, maps the hardware aggregation ID back to the local slot, reconciles aggregate count, frees the aggregation slot, builds the head SKB either by copybreak or by replacing the TPA backing buffer and using `napi_build_skb()`, attaches aggregate netmem fragments, applies protocol/hash/VLAN/checksum metadata, and optionally finishes GRO metadata. It returns an SKB for delivery or NULL on abort/drop.

For non-TPA RX, `bnge_rx_pkt()` validates `rxcmp->rx_cmp_opaque` against `rxr->rx_next_cons`; mismatch schedules RX reset and discards/recycles the completion. It finds aggregate buffers if present, checks the extension error bits, obtains packet length, either copies or wraps the RX head buffer, attaches aggregate fragments, sets RSS hash, protocol, VLAN tag, and RX checksum state, then delivers through `bnge_deliver_skb()`. At the end of successful or drop paths it advances `rx_prod` and `rx_next_cons` and returns the packet count or error code.

### TX transmit and completion

`bnge_start_xmit()` maps the SKB queue to a hardware TX ring via `bn->tx_ring_map`, checks `bnge_tx_avail()`, and stops the queue if descriptor space is below `nr_frags + 2`. It fills the first descriptor as a long TX BD, encodes an opaque value containing NAPI/ring index, start index, and BD count, writes an extension descriptor containing LSO/checksum/VLAN/CFA metadata, then writes one descriptor per SKB fragment. The last descriptor gets `TX_BD_FLAGS_PACKET_END`. It uses `netdev_xmit_more()` and `kick_pending` to suppress some doorbells, optionally sets `TX_BD_FLAGS_NO_CMPL` when sufficient room remains, and forces a doorbell/queue stop when ring space approaches `MAX_SKB_FRAGS + 1`.

`__bnge_tx_int()` later uses `tx_hw_cons` from TX completions to walk software TX BDs from `tx_cons`, unmap the linear and fragment DMA mappings, clear the owning `skb`, free the SKB, and update queue completion accounting. It treats a missing SKB at a completion-owned descriptor as ring corruption and schedules TX reset.

## State and persistence behavior

- Notification queues persist `nq_raw_cons`, `has_more_work`, a doorbell `nq_db`, stats context, and arrays of child completion rings.
- Completion queues persist `cp_raw_cons`, `had_work_done`, `has_more_work`, `had_nqe_notify`, `toggle`, type/index, and doorbell data.
- RX rings persist `rx_prod`, `rx_agg_prod`, `rx_sw_agg_prod`, `rx_next_cons`, software head and aggregate buffer rings, hardware descriptor pages, page pools, aggregate bitmap, and TPA state tables.
- TX rings persist `tx_prod`, `tx_cons`, `tx_hw_cons`, netdev queue index, NAPI index, `kick_pending`, software TX buffer ring, hardware descriptor pages, and device closing state.
- `bnge_napi` persists transient event bits (`BNGE_RX_EVENT`, `BNGE_AGG_EVENT`, `BNGE_TX_CMP_EVENT`), `in_reset`, and `tx_fault`.
- HWRM completion state is persisted by updating `bnge_hwrm_wait_token.state` under RCU.
- There is no filesystem persistence. All state is in kernel memory and hardware rings/doorbells; reset or device close is expected to reinitialize ring state.

## Dependencies and integration points

- Linux networking APIs: `struct net_device`, `struct sk_buff`, `ndo_start_xmit`, `napi_schedule`, `napi_complete_done`, `napi_build_skb`, `napi_alloc_skb`, `napi_gro_receive`, `tcp_gro_complete`, `eth_type_trans`, `skb_set_hash`, VLAN hwaccel helpers, checksum flags, queue stop/wake helpers, and feature checking.
- DMA/page-pool APIs: `dma_map_single`, `skb_frag_dma_map`, DMA sync/unmap helpers, `page_pool_alloc_frag`, `page_pool_alloc_netmems`, `page_pool_dma_sync_netmem_for_cpu`, `page_pool_free_va`, and netmem fragment helpers.
- Driver-local ring and hardware definitions: descriptor layouts and macros from `bnge_netdev.h`, hardware completion structures from `<linux/bnge/hsi.h>`, doorbell helpers from `bnge.h`/`bnge_db.h`, and allocation helpers from `bnge_netdev.c`.
- Control-plane integration: link async events are routed to `bnge_link_async_event_process()` and service work is queued with `__bnge_queue_sp_work()`. HWRM wait tokens are shared with `bnge_hwrm.c`.
- Registration integration visible elsewhere: `bnge_msix()` is installed as the IRQ handler, `bnge_napi_poll()` is registered with netif NAPI setup, and `bnge_start_xmit()`/`bnge_features_check()` are used in the netdev ops table.

## Risks and edge cases

- RX and TX reset scheduling is incomplete: `bnge_sched_reset_rxr()` and `bnge_sched_reset_txr()` set flags/log warnings but contain TODO comments for initiating the actual reset task. Corruption paths can therefore quarantine a ring but may not recover without surrounding code being added.
- Descriptor polarity and raw-consumer accounting are critical. Incorrect advancement around paired RX completions, aggregate completions, or partial `-EBUSY` exits would desynchronize hardware/software rings.
- Aggregate buffer reuse is delicate because software producer indices may equal consumed indices. The code explicitly zeroes consumed netmem pointers before assigning replacement entries; regressions here can double-own or leak page-pool buffers.
- TPA ID mapping can exhaust `MAX_TPA` slots or see mismatched aggregate counts. The code schedules reset for allocation failure and clamps mismatch to recorded `agg_count`, but such paths can drop packets and rely on reset recovery.
- Copybreak and build-SKB paths have different ownership rules. Copybreak reuses the original RX head buffer immediately; build-SKB allocates a replacement first and transfers the old allocation to the SKB. Allocation failures must preserve/recycle exactly one owner.
- `bnge_force_rx_discard()` mutates completion error bits in memory before routing through normal RX cleanup. This is a purposeful netpoll/budget mechanism but is easy to break if completion structures change.
- TX DMA error cleanup depends on `last_frag = i` and re-walking from the original producer. Bugs in fragment unmap ordering can leak DMA mappings or unmap invalid entries.
- The TX path uses deferred doorbells and `TX_BD_FLAGS_NO_CMPL`; queue wake logic depends on completions being generated often enough. Incorrect free-space thresholds can cause stalls.
- `bnge_lhint_arr[length >> 9]` requires features to reject oversized hint indices. The transmit path itself indexes after computing `length`, so callers rely on `bnge_features_check()`/stack constraints and packet segmentation behavior.
- GRO tunnel handling parses headers using offsets from hardware metadata and only handles direct UDP in IPv4/IPv6 outer headers; malformed metadata could set inappropriate GSO state.

## Test signals

- Build signals: compile with `CONFIG_INET=y` and `CONFIG_INET=n`, 32-bit and 64-bit builds to cover doorbell write variants, `MAX_SKB_FRAGS > TX_MAX_FRAGS`, and driver-local descriptor macros.
- Static analysis: sparse/endian checks for `__le32`/`cpu_to_le32` use, DMA API debug for map/unmap balance, lockdep/RCU checks for HWRM token traversal, and KASAN/KMSAN for RX buffer ownership paths.
- RX runtime tests: single-fragment RX, jumbo/multi-aggregate RX, RX copybreak boundary at `rx_copybreak`, VLAN C-tag/S-tag metadata including invalid TPID, RSS hash types, checksum offload on/off, forced RX errors, consumer mismatch/reset path, and netpoll discard path.
- TPA/GRO tests: TPA start/agg/end with zero, one, and many aggregate buffers; maximum `MAX_SKB_FRAGS`; mismatched aggregate count; invalid hash; VLAN on TPA; IPv4/IPv6 TCP GRO; encapsulated UDP tunnel with and without UDP checksum.
- TX runtime tests: linear SKB, maximum fragment SKB, GSO TCP/UDP and encapsulated GSO, VLAN offload, `skb->no_fcs`, `eth_skb_pad()` failure/drop, DMA mapping fault injection on head and fragments, queue stop/wake thresholds, `netdev_xmit_more()` batching, deferred `kick_pending` flush, and coalesced/non-coalesced TX completions.
- Completion/NAPI tests: budget-limited polling, partial completions returning `-EBUSY`, notification queue rearm behavior, CQ toggle propagation, HWRM_DONE token completion, link async event service scheduling, and TX completion ring corruption detection.
