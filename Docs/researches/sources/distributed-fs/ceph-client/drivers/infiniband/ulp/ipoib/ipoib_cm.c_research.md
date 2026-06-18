# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_cm.c

## Purpose
`ipoib_cm.c` implements IPoIB connected mode over reliable-connected QPs. It creates passive receive-side CM listeners, accepts remote REQs, builds active transmit connections per neighbour/path, handles CM RX/TX completions, manages shared receive queue fallback behavior, exposes the sysfs `mode` attribute, and performs stale connection and cleanup work.

## Important APIs, Types, And Functions
The module parameter `max_nonsrq_conn_qp` limits non-SRQ connected receive QPs. Receive helpers include `ipoib_cm_alloc_rx_skb()`, `ipoib_cm_post_receive_srq()`, `ipoib_cm_post_receive_nonsrq()`, `ipoib_cm_create_rx_qp()`, `ipoib_cm_modify_rx_qp()`, `ipoib_cm_req_handler()`, `ipoib_cm_rx_handler()`, and `ipoib_cm_handle_rx_wc()`. Transmit helpers include `ipoib_cm_create_tx()`, `ipoib_cm_tx_start()`, `ipoib_cm_tx_init()`, `ipoib_cm_send_req()`, `ipoib_cm_rep_handler()`, `ipoib_cm_send()`, `ipoib_cm_handle_tx_wc()`, `ipoib_cm_destroy_tx()`, and `ipoib_cm_tx_reap()`. Device lifecycle is handled by `ipoib_cm_dev_init()`, `ipoib_cm_dev_open()`, `ipoib_cm_dev_stop()`, and `ipoib_cm_dev_cleanup()`.

## Control Flow And State
Initialization creates CM work items and, where supported, an SRQ plus receive buffers. `ipoib_cm_dev_open()` creates an RDMA CM ID and listens on `IPOIB_CM_IETF_ID | priv->qp->qp_num`. Passive REQs allocate an `ipoib_cm_rx`, create an RC QP, move it INIT/RTR/RTS, optionally allocate per-QP receive buffers, enqueue the connection in `passive_ids`, and send REP private data containing QPN and MTU. Receive completions decode the WR ID, replace or reuse RX buffers, copy small packets below `IPOIB_CM_COPYBREAK`, restore the pseudo-header, update stats, and pass packets into the stack.

Active transmit starts when neighbour/path logic calls `ipoib_cm_create_tx()`. A work item pulls entries from `start_list`, snapshots the SA path record, creates a TX QP/CM ID, sends REQ, and on REP moves the QP to RTR/RTS, marks it operational, and requeues neighbour packets. `ipoib_cm_send()` validates MTU/frags, maps DMA, updates global TX ring accounting, posts sends, and stops/wakes the netdev queue around ring pressure. Completion errors detach the neighbour and move the TX object to `reap_list`.

Receive teardown is deliberately staged. RX connections move from `passive_ids` to `rx_error_list`, then to `rx_flush_list` on `IB_EVENT_QP_LAST_WQE_REACHED`, then through a drain WR to `rx_drain_list`/`rx_reap_list`, then are destroyed. `ipoib_cm_stale_task()` ages unused passive IDs. `ipoib_cm_skb_too_long()` queues packets for asynchronous IPv4/IPv6 packet-too-big feedback.

## Dependencies And Integration Points
This file uses RDMA CM (`ib_cm_*`), verbs QP/SRQ/CQ operations, DMA mapping helpers from `ipoib_ib.c`, path/neighbour APIs from `ipoib_main.c`, sysfs mode handling through `ipoib_set_mode()`, and netdevice queue/stat APIs. It relies on `priv->wq`, `priv->lock`, NAPI CQ polling, and shared `priv->tx_wr`/SGE construction from `ipoib_build_sge()`.

## Risks And Test Signals
Primary risks are teardown races across CM callbacks, QP last-WQE events, CQ drain completions, and neighbour references; MTU/private-data validation; global TX ring accounting shared with UD; and SRQ versus non-SRQ error paths. Test signals include connected/datagram sysfs switching, large MTU unicast with multicast drop warning, SRQ and no-SRQ devices, CM REQ/REP/REJ/DREQ events, TX completion failures, PMTU ICMP generation, stale connection reap, and module builds with CM disabled.
