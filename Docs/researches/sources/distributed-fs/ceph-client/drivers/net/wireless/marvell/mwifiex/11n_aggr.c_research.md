<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.c

## Purpose
`11n_aggr.c` implements mwifiex Tx A-MSDU aggregation. It dequeues multiple MSDUs from a WMM receiver-address list, encapsulates them as A-MSDU subframes with LLC/SNAP headers and padding, prepends a firmware TxPD, and submits the aggregate through the active bus interface.

## Important APIs, Types, And Functions
`mwifiex_11n_aggregate_pkt()` is the exported aggregation entry point and releases `priv->wmm.ra_list_spinlock` as part of its contract. `mwifiex_11n_form_amsdu_pkt()` creates one A-MSDU subframe from an Ethernet skb and computes four-byte padding. `mwifiex_11n_form_amsdu_txpd()` constructs the firmware `txpd` for a completed aggregate, including priority, packet delay, BSS identifiers, packet type `PKT_TYPE_AMSDU`, TDLS flag, tx control, and power-save last-packet marker.

## Control Flow
The aggregation path peeks the RA queue, allocates a DMA-aligned aggregate buffer sized by `adapter->tx_buf_size`, reserves interface header and TxPD space, inherits metadata from the first skb, and repeatedly dequeues source skbs while the aggregate can fit. It unlocks while copying each subframe and completing the original skb, then relocks and verifies the RA-list is still valid. After trimming final padding, it forms the TxPD, pushes interface headroom, and either queues behind existing data/tx lock state or calls `host_to_card()` for USB or generic data.

If the bus returns `-EBUSY`, the aggregate is requeued on the RA list and marked requeued. On hard failure it updates debug counters and completes the skb with error. On success or in-progress, normal completion/rotation occurs.

## State And Persistence
The function mutates WMM RA-list queues, per-list packet counts, `priv->wmm.tx_pkts_queued`, adapter `tx_queued`, `tx_data_q`, `data_sent`, and `tx_lock_flag`. It also uses skb control block metadata. All state is in-memory queue state.

## Dependencies And Integration Points
It depends on WMM RA-list validity and rotation, DMA-aligned skb allocation, bus `host_to_card` operations, mwifiex write completion, firmware `txpd`, TDLS flags, STA power-save/UAPSD helpers, and the packet type constant from `11n_aggr.h`.

## Risks
Aggregation is concurrency-sensitive because it drops and reacquires the RA-list spinlock inside the loop. Revalidating `pra_list` prevents use-after-free, but missed validation would be dangerous. The aggregate buffer limit check includes payload plus LLC/SNAP length but padding and header reservations must remain consistent with `tx_buf_size`. Requeueing an aggregate on `-EBUSY` changes queue contents from normal MSDUs to an aggregate skb, so downstream code must honor the requeued/aggr flags.

## Test Signals
Signals include aggregate creation from multiple queued skbs, exact subframe length/padding checks, TDLS flag propagation, STA UAPSD last-packet behavior, USB and non-USB send paths, `-EBUSY` requeue handling, RA-list invalidation during aggregation, and WMM queue/count invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.c -->
