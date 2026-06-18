# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif.h

Purpose: defines the DPMAIF HIF software data structures shared by RX, TX, orchestration, and netdev layers.

Important APIs/types: `struct t7xx_skb_cb` stores netif index, TX queue, and RX packet type in SKB control buffer. BAT structures model hardware BAT entries plus software SKB/page tracking. `struct dpmaif_bat_request` owns coherent BAT table, bus address, write/release indexes, software buffer table, bitmap, refcount, lock, and type. `struct dpmaif_rx_queue` owns PIT table/indexes, shared BAT refs, NAPI, current RX assembly state, and processing flags. `struct dpmaif_tx_queue` owns DRB table/indexes, TX budget, workqueue, lock, waitqueue, and queued SKBs. `struct dpmaif_ctrl` owns hardware info, queues, shared BATs, interrupts, PM entity, TX thread, callbacks, and state.

Control flow and state: RX consumes PIT descriptors to pull normal BAT SKBs and fragment BAT pages; TX queues DRBs. `t7xx_ring_buf_*` helpers provide common ring math. `dpmaif_callbacks` integrate state notifications and SKB delivery with the network layer.

Dependencies and integration points: includes DPMAIF hardware definitions, t7xx PCI, state monitor, SKBs, NAPI, workqueues, and netdevice types.

Risks and test signals: shared BAT refcounts, bitmap/index consistency, SKB control-buffer use, and NAPI/sleep-lock state need careful validation. Test RX fragmentation, TX queue full, multi-netif delivery, and teardown with pending NAPI/work.
