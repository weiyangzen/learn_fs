# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_tx.h

Purpose: Declares EF100 TX queue, completion, descriptor-limit, and skb enqueue entry points.

Important APIs: Exposes `ef100_tx_probe()`, `ef100_tx_init()`, `ef100_tx_write()`, `ef100_tx_max_skb_descs()`, `ef100_ev_tx()`, `ef100_enqueue_skb()`, and `__ef100_enqueue_skb()`. It includes `ef100_rep.h` because internal enqueue can target a representor.

Control flow and integration: The generic `efx_enqueue_skb()` wrapper in `efx.h` uses an indirect call to `ef100_enqueue_skb()` for EF100 NICs. Event dispatch uses `ef100_ev_tx()`, and queue probe/init paths use the queue setup declarations.

State and persistence: Header owns no state, but its APIs mutate TX rings, netdev queues, and representor statistics.

Dependencies: Requires `net_driver.h` types, EF100 representor declarations, and implementation in `ef100_tx.c`.

Risks: `__ef100_enqueue_skb()` is intentionally lower-level and accepts an optional representor; misuse from non-representor paths could bypass normal backpressure assumptions.

Test signals: Compile coverage of EF100 NIC-type TX callbacks, generic hard-start-xmit dispatch, and representor TX callers.
