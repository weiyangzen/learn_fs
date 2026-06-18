# sources/distributed-fs/ceph-client/net/sched/sch_generic.c

## Purpose
`sch_generic.c` is the generic qdisc and device scheduler core. It provides the default qdisc selection, qdisc allocation/destruction, transmit run loop, requeue handling, carrier/watchdog integration, default `noop`, `noqueue`, and `pfifo_fast` qdiscs, device activation/deactivation, rate precompute helpers, and mini-qdisc RCU swap helpers.

## Important APIs, Types, And Functions
Exported symbols include `default_qdisc_ops`, `noop_qdisc`, `pfifo_fast_ops`, `qdisc_alloc()`, `qdisc_create_dflt()`, `qdisc_reset()`, `qdisc_put()`, `qdisc_put_unlocked()`, `dev_graft_qdisc()`, `dev_activate()`, `dev_deactivate()`, `mq_change_real_num_tx()`, `dev_qdisc_change_tx_queue_len()`, `dev_init_scheduler()`, `dev_shutdown()`, `psched_ratecfg_precompute()`, `psched_ppscfg_precompute()`, and `mini_qdisc_pair_*()`. The central transmit path is `__qdisc_run()` -> `qdisc_restart()` -> `dequeue_skb()` -> `sch_direct_xmit()`.

## Control Flow
`dequeue_skb()` first handles requeued GSO packets, stopped single-TX queues, and bad-TXQ requeues, then calls the qdisc’s dequeue function and may bulk-dequeue compatible packets. `sch_direct_xmit()` drops the qdisc lock, validates skb lists, takes the driver TX lock, calls `dev_hard_start_xmit()`, and requeues on busy/incomplete transmit. `__qdisc_run()` repeats until queue empty/throttled or `dev_tx_weight` quota is exhausted, then reschedules as needed. Device activation attaches default qdiscs if still noop, transitions sleeping qdiscs to active qdiscs, and starts the watchdog. Deactivation swaps active qdiscs to noop, waits for in-flight enqueue/run activity, and optionally resets.

## State And Persistence
Core state is in `struct Qdisc`, `struct netdev_queue`, and `struct net_device`: qdisc pointers under RCU, qdisc refcounts, busy state bits, `gso_skb`, `skb_bad_txq`, qstats/bstats, watchdog timer, and carrier counters. `pfifo_fast` private state is three `skb_array` rings sized to `tx_queue_len`. There is no disk persistence; all state is kernel runtime state exposed through netlink/stat APIs elsewhere.

## Dependencies And Integration Points
This file is the integration point between qdiscs and netdevice drivers. It uses RCU, rtnl locking, qdisc locks, hard TX locks, skb validation, XFRM offload, BPF module refs, tracepoints, linkwatch, qdisc hash support, per-CPU stats, and qdisc watchdogs. It initializes default qdiscs for normal, noqueue, CAN, and multiqueue devices.

## Risks
The transmit path relies on strict lock ordering: qdisc root lock and driver TX lock must not be held in the wrong combination. Requeue accounting for `gso_skb` and `skb_bad_txq` must keep qlen/backlog correct for both normal and per-CPU stats qdiscs. `qdisc_maybe_clear_missed()` uses memory barriers to avoid missed wakeups. Device deactivation waits by polling busy qdiscs, so state-bit bugs can hang shutdown. `pfifo_fast` is lockless/per-CPU-stat capable and its ring allocation/destruction must tolerate partial init failure.

## Test Signals
Exercise qdisc allocation failure paths, default qdisc fallback to noqueue, multiqueue default attach, `pfifo_fast` priority ordering and ring resize, GSO and bad-TXQ requeue accounting, driver busy requeue, bulk dequeue queue-mapping constraints, watchdog timeout and carrier on/off paths, device deactivate/reactivate with reset, qdisc refcount destruction via RCU, rate precompute edge cases, and mini-qdisc RCU swap under concurrent readers.
