# sources/distributed-fs/ceph-client/net/core/link_watch.c

Purpose: Implements deferred network device link state notification and RFC2863 operational state policy. It batches carrier/dormant/testing changes, rate-limits non-urgent notifications, and activates/deactivates qdiscs when device link state changes.

Important APIs, types, and functions: Public entry points are `linkwatch_init_dev()`, `__linkwatch_sync_dev()`, `linkwatch_sync_dev()`, `linkwatch_run_queue()`, and `linkwatch_fire_event()`. Internal pieces include `default_operstate()`, `rfc2863_policy()`, `linkwatch_urgent_event()`, `linkwatch_add_event()`, `linkwatch_schedule_work()`, `linkwatch_do_dev()`, `__linkwatch_run_queue()`, and delayed work `linkwatch_work`.

Control flow: `linkwatch_fire_event()` determines urgency, sets the device pending bit, queues the device with a held ref if not already pending, and schedules delayed work. Urgent events can force immediate work and set `LW_URGENT`; non-urgent work respects `linkwatch_nextevent` rate limiting. The work handler takes RTNL and runs the queue, optionally urgent-only. Queue processing splices the global list to a local list, skips absent devices or non-urgent devices during urgent-only runs, clears pending state with memory ordering, updates RFC2863 operstate, activates/deactivates qdisc state based on carrier, emits `netif_state_change()`, releases device refs, and requeues leftover work.

State and persistence: Global state includes `linkwatch_flags`, `linkwatch_nextevent`, delayed work, event list, and spinlock. Each device uses `link_watch_list`, a pending bit, and a tracker-held reference while queued. State is boot/runtime only.

Dependencies and integration points: Integrates with netdevice carrier/dormant/testing flags, DSA/lower-layer iflink logic, LAG devices, qdisc activation/deactivation, RTNL locking, workqueues, jiffies, and netdev reference tracking.

Risks: Reference release must occur under the documented lock/tracker ordering or devices can be freed while processed. Rate limiting must not delay urgent up/qdisc-changing events too long. `default_operstate()` has special behavior when devices are unregistering and RTNL may not be held. Pending-bit memory ordering protects against lost events. Lock ordering across event list spinlock, RTNL, and per-device ops locks is critical.

Test signals: Simulate carrier up/down, dormant/testing, lower-layer down through iflink, LAG port/master events, qdisc changing on up events, repeated flapping to test rate limit, urgent-only processing, sync during unregister, and concurrent fire/sync under lockdep and reftracker diagnostics.
