# sources/distributed-fs/ceph-client/block/bfq-cgroup.c

## Purpose
`bfq-cgroup.c` implements blk-cgroup integration for the BFQ I/O scheduler. It maps bios and BFQ queues to cgroups, manages BFQ group lifecycle and hierarchy, exposes cgroup weight controls and statistics, and handles queue migration when tasks move between cgroups.

## Important APIs, types, and functions
When `CONFIG_BFQ_CGROUP_DEBUG` is enabled, `struct bfq_stat` helpers wrap percpu counters and auxiliary counters for recursive stats. Group stat functions update queued IO, wait time, service time, merged IO, idle time, empty time, average queue size, dequeue count, bytes, and IO counts. Under `CONFIG_BFQ_GROUP_IOSCHED`, key helpers include `pd_to_bfqg`, `bfqg_to_blkg`, `blkg_to_bfqg`, `bfqg_parent`, `bfqq_group`, `bfqg_and_blkg_get/put`, `bfq_init_entity`, `bfq_pd_alloc/init/free/offline/reset_stats`, `bfq_link_bfqg`, `bfq_bio_bfqg`, `bfq_bfqq_move`, `bfq_bic_update_cgroup`, `bfq_end_wr_async`, cgroup weight show/write handlers, and `bfq_create_group_hierarchy`. `blkcg_policy_bfq`, `bfq_blkcg_legacy_files`, and `bfq_blkg_files` register the policy and cgroup files.

## Control flow
Policy activation allocates per-cgroup policy data with default weights, then allocates per-device `bfq_group` data for each blkcg-gq. `bfq_pd_init` wires the group to `bfq_data`, initializes its scheduling entity and service trees, and uses blkcg weight defaults. `bfq_bio_bfqg` walks from `bio->bi_blkg` up to the nearest online BFQ policy data, reassociating the bio if it falls back to an ancestor or root.

Queue migration starts in `bfq_bic_update_cgroup`, which compares the cached blkcg serial number with the bio's current group. On change, it links missing ancestors into BFQ's private hierarchy and calls `__bfq_bic_change_cgroup` across actuators. Asynchronous queues are detached if they belong to the old group; synchronous queues are moved with `bfq_sync_bfqq_move`, unless merge chains cross cgroup boundaries, in which case cooperators are broken. `bfq_bfqq_move` temporarily pins the queue, removes it from old service structures, expires in-service queues if needed, updates parent/sched_data, pins the new group, reactivates busy queues, and schedules dispatch if the device became idle.

Offline flow in `bfq_pd_offline` grabs the scheduler lock, reparents active and in-service queues to root, flushes idle service trees, deactivates the group entity, releases async queues, then transfers dead-group stats to parent auxiliary counters so recursive stats remain meaningful.

## State and persistence behavior
Runtime state includes BFQ group hierarchy, per-group scheduling entities, weights and device-specific weights, references on bfq groups and blkgs, per-group service trees, async queue sets, cgroup serial numbers cached in BFQ IO contexts, and cgroup statistics. State is not persisted across reboot; user-visible controls and stats are exposed through cgroup v1 legacy files and cgroup v2 block files.

## Dependencies and integration points
The file depends on blk-cgroup core, cgroup kernfs APIs, BFQ scheduler internals from `bfq-iosched.h`, request queues, bios, rbtree service trees, ioprio classes, and optional debug stats infrastructure. It is linked into the composite BFQ scheduler object by `block/Makefile`.

## Risks
Reference management is subtle because BFQ queues can outlive cgroup online state and can move while merge chains exist. Incorrect migration can dispatch IO under the wrong group or leave stale service-tree entities. Offline reparenting must cover active, idle, and in-service entities to avoid dangling group pointers. Weight updates rely on a write memory barrier before setting `prio_changed`; removing it could expose stale weights to scheduler code. Debug recursive stats intentionally lose completions after offline transfer, which is accepted but important for interpretation.

## Test signals
Useful tests include BFQ enabled with cgroup v1 and v2, task migration during active synchronous and asynchronous IO, queue merge and split scenarios across cgroups, group deletion under load, weight and per-device weight writes including invalid ranges, recursive stat accounting before and after cgroup removal, root fallback for offline blkgs, and builds with `CONFIG_BFQ_GROUP_IOSCHED` and `CONFIG_BFQ_CGROUP_DEBUG` both enabled and disabled.
