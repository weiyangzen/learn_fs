# sources/distributed-fs/ceph-client/net/core/gro_cells.c

Purpose: Provides per-cpu GRO cells for virtual or tunnel devices that want to enqueue received skbs into a per-cpu NAPI context before running GRO and normal receive processing.

Important APIs, types, and functions: `struct gro_cell` contains a per-cpu skb queue, NAPI instance, and local BH lock. Public functions are `gro_cells_receive()`, `gro_cells_init()`, and `gro_cells_destroy()`. `gro_cell_poll()` is the NAPI poll method. `percpu_free_defer_callback()` frees per-cpu storage after an RCU grace period.

Control flow: `gro_cells_receive()` takes RCU, drops packets if the device is down, falls back to `netif_rx()` when cells are unavailable, the skb is cloned, or GRO is elided, otherwise locks the current CPU cell, checks queue length against `net_hotdata.max_backlog`, enqueues the skb, schedules NAPI for the first queued skb, and returns receive status. Polling dequeues up to budget under the local lock and passes each skb to `napi_gro_receive()`, completing NAPI when under budget. Init allocates per-cpu cells, initializes queues/locks, marks NAPI as no busy poll, adds NAPI to the device, and enables it for every possible CPU. Destroy disables/deletes NAPI, purges queued skbs, and frees per-cpu memory by `call_rcu()` or expedited synchronize fallback.

State and persistence: Per-cpu queues and NAPI state persist for the lifetime of the owning `gro_cells`. `gcells->cells` is nulled after destroy. Device references are implicit through NAPI registration; no disk persistence exists.

Dependencies and integration points: Depends on skb queues, per-cpu allocation, local locks, NAPI, `net_hotdata.max_backlog`, device up flags, RCU, and virtual/tunnel device receive paths.

Risks: Destroy must not free per-cpu cells while netpoll or RCU readers can still traverse device NAPI lists. Queue overflow must drop and account correctly. Cloned skbs bypass cells to avoid unsafe GRO mutation. Local lock use must match BH context assumptions and PREEMPT_RT behavior.

Test signals: Initialize/destroy cells on virtual devices, receive while device is up/down, queue overflow at `max_backlog`, cloned skb fallback, `netif_elide_gro()` fallback, NAPI budget-limited polling, and destroy during namespace cleanup with RCU callback allocation failure.
