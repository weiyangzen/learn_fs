# sources/distributed-fs/ceph-client/block/blk-cgroup.h

## Purpose

`blk-cgroup.h` is the private block cgroup header for the block layer. It defines blkcg and blkg data structures, policy interfaces, lookup/reference helpers, descendant traversal macros, delay helpers, mergeability checks, configuration parser context, and no-op stubs for non-cgroup builds.

## Important APIs, Types, And Functions

Important types include `struct blkg_iostat`, `struct blkg_iostat_set`, `struct blkcg_gq`, `struct blkcg`, `struct blkg_policy_data`, `struct blkcg_policy_data`, `struct blkcg_policy`, and `struct blkg_conf_ctx`. `enum blkg_iostat_type` defines read/write/discard stat categories.

Inline helpers include `css_to_blkcg()`, `bio_issue_as_root_blkg()`, `blkg_lookup()`, `blkg_to_pd()`, `blkcg_to_cpd()`, `pd_to_blkg()`, `cpd_to_blkcg()`, `blkg_get()`, `blkg_tryget()`, `blkg_put()`, `blkcg_use_delay()`, `blkcg_unuse_delay()`, `blkcg_set_delay()`, `blkcg_clear_delay()`, `blk_cgroup_mergeable()`, and `blkcg_policy_enabled()`.

## Control Flow, State, And Persistence

`struct blkcg_gq` is the per `(blkcg, request_queue)` association. It stores queue and blkcg links, parent blkg, percpu refcount, online state, percpu/global iostat sets, per-policy data, optional async bio state, delay fields, and RCU release state. `struct blkcg` owns the CSS, lookup radix tree and hint, blkg hlist, per-policy cgroup data, stat-update llist heads, congestion count, and optional FC app ID/writeback list.

Policy state is split between per-blkg `blkg_policy_data` and per-blkcg `blkcg_policy_data`, with `struct blkcg_policy` providing allocation, init, online/offline, free, reset, and stat callbacks. `blkg_lookup()` prefers root, then hint, then radix-tree lookup. Reference helpers wrap the percpu ref and support RCU-safe tryget.

Delay helpers update per-blkg delay fields and per-blkcg congestion count. `blk_cgroup_mergeable()` requires matching blkg ownership and matching root-issued metadata/swap status before allowing request merge.

## Dependencies And Integration Points

The header depends on blk-cgroup, cgroup, kthread, blk-mq, llist, and internal block structures. It is used by core blkcg code, bio code, BFQ, legacy rwstat helpers, and FC app ID support.

## Risks And Test Signals

Most helpers require RCU or queue-lock context, and descendant traversal needs RCU plus stronger locks for exact online sets. `blkg_tryget()` can fail during teardown, and `bio_issue_as_root_blkg()` affects throttling and merge behavior. Test cgroup-enabled and disabled builds, lookup during teardown, policy data access, mergeability checks, delay races, and descendant traversal with online/offline children.
