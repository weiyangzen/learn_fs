<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/metric.h -->
# sources/distributed-fs/ceph-client/fs/ceph/metric.h

## Purpose
`metric.h` defines CephFS client metric type identifiers, supported metric bitsets, packed wire structures, in-memory aggregation structures, and small update/scheduling helpers used by the rest of the CephFS client.

## Important APIs, types, and functions
`enum ceph_metric_type` enumerates all advertised metric types, including cap info, read/write/metadata latency, dentry leases, opened files/inodes, pinned caps, read/write sizes, average/stdev metric identifiers, and subvolume metrics. `CEPHFS_METRIC_SPEC_CLIENT_SUPPORTED` is the feature vector encoded in session-open messages.

Packed wire records include `ceph_metric_header`, `ceph_metric_cap`, read/write/metadata latency records, `ceph_metric_dlease`, `ceph_opened_files`, `ceph_pinned_icaps`, `ceph_opened_inodes`, `ceph_read_io_size`, `ceph_write_io_size`, and `ceph_subvolume_metric_entry_wire`. `ceph_metric` is the in-memory aggregate for one operation class, and `ceph_client_metric` is the mount-wide metrics container.

Inline helpers include `metric_schedule_delayed`, `ceph_update_cap_hit`, `ceph_update_cap_mis`, and wrappers for read, write, metadata, and copyfrom metric updates. External functions are `ceph_metric_init`, `ceph_metric_destroy`, and `ceph_update_metrics`.

## Control flow
Call sites update lightweight counters directly with inline helpers, while latency/size updates route through `ceph_update_metrics`. Periodic sending is kicked through `metric_schedule_delayed`, which observes the global `disable_send_metrics` flag before queuing delayed work. The supported metric spec is consumed by `mds_client.c` when constructing the session-open message.

## State and persistence behavior
The header declares runtime-only state shapes. `ceph_client_metric` persists for a mount and owns counters, aggregate arrays, a retained MDS session pointer, and delayed work. The packed wire structures are transient message layouts. Nothing in this header implies local persistence across unmount.

## Dependencies and integration points
It depends on Ceph type definitions, percpu counters, and kernel time types. It is included by `mds_client.h` and by code paths that update metrics. The wire comments for `ceph_subvolume_metric_entry_wire` explicitly tie the layout to the MDS-side C++ `AggregatedIOMetrics` structure, making cross-language ABI compatibility important.

## Risks and test signals
Risks include changing enum order or supported bits without server compatibility, packed-structure layout drift, mismatch between advertised metrics and actual sender behavior, misuse of `disable_send_metrics`, and unsynchronized readers of aggregate fields. Test signals include compile-time size/layout checks where available, session-open metric-spec decoding by old and new MDSs, metrics update call coverage for successful and allowed-error operations, and subvolume metric wire compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/metric.h -->
