# sources/distributed-fs/ceph-client/include/net/gen_stats.h

Purpose: declares generic scheduler/statistics helpers for exporting traffic statistics through rtnetlink and maintaining rate estimators. It supports basic byte/packet counters, queue stats, app-specific xstats, compatibility `tc_stats`, and estimator lifecycle.

Important APIs/types: `struct gnet_stats_basic_sync` stores byte and packet counters with `u64_stats_sync` for lockless 64-bit updates. `struct gnet_dump` tracks the skb, lock, tail attribute, compatibility flags, xstats, and tc stats during a stats dump. Copy/add APIs include `gnet_stats_copy_basic()`, `_basic_hw()`, `_queue()`, `_app()`, and their add variants. Estimator APIs include `gen_new_estimator()`, `gen_kill_estimator()`, `gen_replace_estimator()`, `gen_estimator_active()`, and `gen_estimator_read()`.

Control flow and state: callers initialize counters, start a dump with `gnet_stats_start_copy*()`, append basic/rate/queue/app stats, then finish with `gnet_stats_finish_copy()`. Estimators are RCU pointers updated under a supplied lock and read into 64-bit samples.

Dependencies and integration: uses Linux gen_stats UAPI, sockets, rtnetlink, packet scheduler definitions, skb/nlattr, spinlocks, per-CPU counters, and RCU. It integrates with qdiscs, tc actions, and offload stats.

Risks: concurrent stats writers need sync helpers; direct field writes are safe only for non-concurrent storage. Compat attributes must remain aligned with older tc userspace. Tests should exercise 32-bit counter consistency, per-CPU aggregation, estimator replace/kill under RCU, hardware stats copy, and netlink dump failure unwinding.
