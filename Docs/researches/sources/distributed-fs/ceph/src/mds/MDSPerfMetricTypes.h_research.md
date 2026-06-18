# sources/distributed-fs/ceph/src/mds/MDSPerfMetricTypes.h

## Purpose
Defines CephFS MDS performance metric payload types for client metrics, subvolume metrics, and rank metrics exchanged between MDS ranks and metric aggregation/manager code.

## Important APIs, Types, And Functions
`UpdateType` distinguishes refresh/remove. Leaf structs cover cap hits, read/write/metadata latency, dentry lease hits, opened files, pinned icaps, opened inodes, read/write IO sizes, and rank CPU/open-request counters. Each provides DENC encoding, `dump(Formatter*)`, and stream output. `Metrics` aggregates client metric groups. `metrics_message_t` carries sequence, source rank, client map, subvolume vector, and rank metrics.

## Control Flow
Producers populate metric structs and encode them into `metrics_message_t`. Decode uses struct-version gates so older senders can omit newer fields. Dump functions present the same data to admin/manager consumers.

## State And Persistence Behavior
These are transient message contracts, not local durable state. Compatibility is versioned: latency aggregates and newer metric groups are guarded by struct versions, and missing rank metrics default to empty values on old messages.

## Dependencies And Integration Points
Depends on `Formatter`, DENC, `utime_t`, entity instances, rank ids, and `mdstypes.h` for `SubvolumeMetric`. Integrates with `MetricsHandler`, `MetricAggregator`, `MMDSMetrics`, MDS messenger dispatch, and manager publishing.

## Risks
Dump keys include typo-like names such as `avg_read_alatency`; consumers may depend on them. Some `updated` fields are encoded but not dumped. Mixed-version decode paths must remain stable. Producers must initialize aggregate fields before send.

## Test Signals
DENC round trips for all structs, old-version decode fixtures, dump field assertions, refresh/remove handling, rank metrics defaulting, and aggregation from multiple `entity_inst_t` clients.
