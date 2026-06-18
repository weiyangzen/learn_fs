# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_wq.c

## Purpose
`enic_wq.c` implements ENIC transmit completion servicing. It decodes WQ completion CQ entries, frees DMA-mapped SKBs, updates TX completion stats, returns WQ descriptors, and wakes stopped TX subqueues when space is available.

## Important APIs, types, and functions
- `enic_wq_cq_service()` polls a TX completion CQ up to a budget.
- `enic_wq_cq_desc_dec()` decodes generic CQ descriptors and handles extended WQ completion index width for large WQ rings.
- `enic_wq_service()` serializes a WQ with `enic->wq[q_number].lock`, calls `vnic_wq_service()`, and wakes the corresponding netdev TX queue when descriptor availability is sufficient.
- `enic_free_wq_buf()` unmaps single or page DMA depending on SOP and frees `skb` only from the buffer that owns it.
- `enic_wq_free_buf()` is the completion callback that updates `cq_work`/`cq_bytes` and delegates buffer release.

## Control flow and state
The CQ poller reads `cq->to_clean`, decodes color/type/queue/completed index, and loops while the hardware color differs from `cq->last_color`. For each completion, it invokes WQ service, then advances the CQ cursor with wrap/color toggling. The WQ service callback walks from `to_clean` through the completed index, freeing each descriptor buffer and returning descriptor availability.

State changes include WQ software cursor and descriptor availability updates, SKB/DMA ownership release, TX stats increments, and netdev queue wakeups.

## Dependencies and integration points
The file depends on ENIC WQ state, `vnic_wq`, `vnic_cq`, netdev TX queue APIs, and CQ descriptor format. It is called from ENIC NAPI/interrupt completion paths for transmit queues.

## Risks and test signals
Important risks include incorrect extended completion-index masking for rings larger than the default, double-unmap/free if SOP/EOP ownership is wrong, missed queue wakeups causing TX stalls, and lock ordering around TX enqueue/completion. Tests should include multi-fragment TX, ring wrap, queue stop/wake behavior, large WQ ring configurations, and TX timeout absence under load.
