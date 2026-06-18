<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.h

## Purpose
`11n_aggr.h` declares the mwifiex A-MSDU aggregation/deaggregation interface and constants used to identify firmware A-MSDU packets.

## Important APIs, Types, And Functions
It defines `PKT_TYPE_AMSDU` as the firmware packet type and `MIN_NUM_AMSDU` as the minimum aggregation count. It declares `mwifiex_11n_deaggregate_pkt()` for RX-side deaggregation and `mwifiex_11n_aggregate_pkt()` for Tx aggregation from a WMM RA-list. The aggregation prototype documents lock semantics with `__releases(&priv->wmm.ra_list_spinlock)`.

## Control Flow
The header has no executable flow. It allows Tx scheduling code to call aggregation while transferring ownership of the RA-list spinlock to the implementation.

## State And Persistence
No state is held. The declared functions operate on runtime skbs, RA lists, and mwifiex private state.

## Dependencies And Integration Points
It is included by `11n.h` and `11n_aggr.c`; RX reorder code also interprets `PKT_TYPE_AMSDU`. It depends on `struct mwifiex_private`, `struct mwifiex_ra_list_tbl`, and `struct sk_buff` being declared by including files.

## Risks
The lock annotation is part of the API contract; callers must enter with the RA-list spinlock held and must not unlock again after calling. Mismatched use can cause deadlocks or unlock imbalance.

## Test Signals
Build-time sparse/lock checking is valuable because of the `__releases` annotation. Runtime signals are the same aggregation/deaggregation paths that consume the declared functions and packet type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.h -->
