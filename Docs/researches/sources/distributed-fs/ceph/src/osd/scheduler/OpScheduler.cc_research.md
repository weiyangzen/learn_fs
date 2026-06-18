# `sources/distributed-fs/ceph/src/osd/scheduler/OpScheduler.cc`

## Purpose

`OpScheduler.cc` implements the OSD op scheduler factory and stream output for the scheduler abstraction declared in `OpScheduler.h`. It selects either the legacy weighted priority queue adapter or the mClock scheduler based on configuration and objectstore type.

## Important APIs And Functions

- `make_scheduler(CephContext *cct, int whoami, uint32_t num_shards, int shard_id, bool is_rotational, std::string_view osd_objectstore, op_queue_type_t osd_scheduler, unsigned op_queue_cut_off)` returns an `OpSchedulerRef`.
- `operator<<(std::ostream&, const OpScheduler&)` delegates to `OpScheduler::print()`.

## Control Flow And State Behavior

The factory has three branches. If the configured scheduler is `WeightedPriorityQueue` or the objectstore is `filestore`, it constructs `ClassedOpQueueScheduler<WeightedPriorityQueue<OpSchedulerItem, client>>`. The filestore branch forces WPQ because mClock is not supported for filestore. The WPQ adapter receives the priority cutoff plus `osd_op_pq_max_tokens_per_priority` and `osd_op_pq_min_cost` from `cct->_conf`.

If the configured scheduler is `mClockScheduler`, the factory constructs `mClockScheduler` with OSD identity, shard count/id, rotational flag, and cutoff. Any other queue type aborts via `ceph_abort_msg("Invalid choice of wq")`.

## Persistence Behavior

The file has no persistence logic. It consumes runtime OSD configuration and returns an in-memory scheduler object. Scheduler type names are declared in `osd_types.h`/implemented in `osd_types.cc`, and OSD configuration parsing feeds the `op_queue_type_t` value.

## Dependencies And Integration Points

It includes `OpScheduler.h`, `common/WeightedPriorityQueue.h`, and `osd/scheduler/mClockScheduler.h`. The factory is called by `OSDShard` construction in OSD startup/reconfiguration paths. It integrates with config values on `CephContext`, objectstore type detection, and the `OpSchedulerItem` work item type.

## Risks And Edge Cases

- Filestore always forces WPQ even when mClock is configured, so tests and operational expectations must account for objectstore override.
- `op_queue_type_t::PrioritizedQueue` exists in `osd_types.h`, but this factory does not handle it; selecting it reaches `ceph_abort_msg`.
- The WPQ branch passes `cct` to `ClassedOpQueueScheduler` even though the adapter currently does not store it; constructor signature compatibility hides that unused parameter.
- Factory behavior depends on exact string comparison with `"filestore"`.

## Test Signals

Scheduler factory tests should assert WPQ selection for explicit WPQ, WPQ selection for filestore even with mClock requested, mClock selection for mClock on supported stores, and abort behavior for unsupported queue types. OSD startup logs and `operator<<` output provide integration signals for selected scheduler type and parameters.
