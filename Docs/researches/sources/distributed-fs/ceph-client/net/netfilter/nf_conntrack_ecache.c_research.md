# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ecache.c

## Purpose
`nf_conntrack_ecache.c` implements conntrack event caching and delivery. It stores per-connection event masks, reports conntrack and expectation events to registered notifiers, tracks missed events, and retries destroy events that could not be delivered immediately.

## Important APIs, Types, And Functions
`nf_conn_pernet_ecache()` returns per-net event state. Reporting flows through `nf_conntrack_eventmask_report()`, `__nf_conntrack_eventmask_report()`, `nf_ct_deliver_cached_events()`, and `nf_ct_expect_event_report()`. Notifier registration uses `nf_conntrack_register_notifier()` and `nf_conntrack_unregister_notifier()` under `nf_ct_ecache_mutex`. Destroy retry uses `ecache_work_evict_list()`, `ecache_work()`, and `nf_conntrack_ecache_work()`. Extension allocation uses `nf_ct_ecache_ext_add()`.

## Control Flow
Event reporting ignores unconfirmed conntracks or missing ecache extensions. It builds an event item, merges requested events with missed bits, calls the RCU notifier, and updates the `missed` bitmask if the notifier reports congestion. Destroy event failure moves conntracks to a per-net dying list; delayed work retries event delivery, unlinks successfully delivered entries, and finally drops conntrack references. Per-net initialization sets the default sysctl event mode, delayed work, dying list, and spinlock.

## State And Persistence
State is per connection (`struct nf_conntrack_ecache`: masks, cached events, missed bits, portid, optional timestamp) and per net namespace (dying list, lock, delayed work, event callback pointer). Sysctl default comes from module-level `nf_ct_events`; no durable storage exists.

## Dependencies And Integration Points
The file integrates with conntrack extensions, ctnetlink event listeners, expectation reporting, per-net conntrack state, delayed workqueues, RCU notifier pointers, and timestamp extension support.

## Risks
Destroy-event retry changes ownership: if delivery fails, `nf_ct_put()` is deferred to the ecache worker. Missed events may be sent more than once, intentionally. Event mask width is guarded by build checks. Registration assumes a single notifier per netns and relies on netns pre-exit RCU synchronization.

## Test Signals
Test listener absent/present/autodetect modes, cached event delivery, missed-event retry, destroy event congestion and later success, expectation new/destroy notification, notifier register/unregister, timestamp refresh, per-net cleanup canceling delayed work, and ctnetlink listener toggling.
