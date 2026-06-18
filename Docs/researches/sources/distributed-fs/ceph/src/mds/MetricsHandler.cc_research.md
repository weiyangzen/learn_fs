# sources/distributed-fs/ceph/src/mds/MetricsHandler.cc

## Purpose

`MetricsHandler.cc` implements the per-MDS-rank metrics collector. It accepts `MClientMetrics` messages from clients, stores per-session metric deltas, samples local rank CPU/open-request telemetry, aggregates subvolume metrics, and periodically sends `MMDSMetrics` updates to rank 0.

## Important APIs, Types, and Functions

- `MetricsHandler::MetricsHandler()` records `_SC_CLK_TCK` for CPU sampling.
- `init()` creates local `mds_rank_perf` counters for non-rank0 ranks, reads `subv_metrics_window_interval`, and starts the `mds-metrics` updater thread.
- `shutdown()` sets `stopping`, joins the updater, and removes local rank perf counters.
- `add_session()` creates a `client_metrics_map` entry with `UPDATE_TYPE_REFRESH`.
- `remove_session()` either erases unseen sessions locally or zeroes all metrics and marks `UPDATE_TYPE_REMOVE`.
- `handle_client_metrics()` validates active state, resolves a `Session`, and visits every payload variant.
- `handle_payload()` overloads update cap hits, latency, dentry leases, opened files/inodes, pinned icaps, IO sizes, and subvolume samples.
- `update_rank0()` samples rank telemetry, packages client and subvolume updates, increments sequence state, and sends `MMDSMetrics` to rank 0.
- `aggregate_subvolume_metrics()` folds client subvolume reports into a single path-level `SubvolumeMetric`.
- `maybe_update_subvolume_quota()` records quota/used bytes learned from quota broadcasts.
- `sample_cpu_usage()` and `sample_open_requests()` fill `RankPerfMetrics`.

## Control Flow

The updater thread sleeps for `mds_metrics_update_interval`, wakes under the metrics lock, then calls `update_rank0()`. Client metric messages update in-memory deltas under the same lock. Subvolume payloads are special: the handler temporarily releases the metrics lock while resolving inode ids to paths through `MDSRank::get_path()`, then reacquires it to append samples.

MDS ping messages from rank 0 set `next_seq`; outbound `MMDSMetrics` include that sequence. `last_updated_seq` increments only after rank 0 has assigned a nonzero sequence, which lets session removal collapse locally if rank 0 never saw the session.

`update_rank0()` samples CPU/open requests, skips if rank0 address is not known, copies and resets/removes client metric entries, resolves subvolume used bytes outside the metrics lock, aggregates subvolume path metrics, evicts stale quota entries, then sends the message without holding the metrics lock.

## State and Persistence Behavior

The class maintains runtime state only. `client_metrics_map` stores per-client deltas and sequence bookkeeping. `subvolume_metrics_map` buffers per-path aggregated IO samples between periodic sends. `subvolume_quota` caches quota and used bytes with activity timestamps. `rank_telemetry` stores the previous process CPU sample and latest rank metrics. Non-rank0 local rank perf counters are registered in the perf-counter collection.

## Dependencies and Integration Points

Dependencies include client metric payload types from `include/cephfs/metrics/Types.h`, `MClientMetrics`, `MMDSMetrics`, `MMDSPing`, `MDSRank`, `MDCache`, `CInode`, `SessionMap`, perf counters, `ceph::read_process_cpu_ticks`, and `op_tracker`. It integrates with `MetricAggregator.cc` by sending rank/client/subvolume metrics to rank 0.

## Risks

- The updater uses `sleep()`, so shutdown can wait for the current interval.
- Correctness depends on the lock being released around MDS operations that may take `mds_lock`; future code must preserve that ordering.
- `remove_session()` relies on `last_updated_seq` to avoid sending removes for sessions rank 0 never saw.
- Subvolume `used_bytes == 0` is both a valid value and a cache-miss signal for fallback lookup.
- Payload handlers silently ignore metrics for unknown sessions.
- Rank0 does not create local rank perf counters here; `MetricAggregator` creates counters for all ranks, so startup ordering matters.

## Test Signals

Tests should cover session add/remove before and after `last_updated_seq` advances, client payload visitation, subvolume path resolution with missing paths, quota update with `force_zero`, stale quota eviction, rank0 address changes in `notify_mdsmap()`, CPU sampling on first sample and counter reset, and send-without-lock behavior. Multi-rank tests should verify that rank 0 receives messages only after ping sequence setup.
