# sources/distributed-fs/ceph-client/fs/xfs/xfs_trace.h

## Purpose

`xfs_trace.h` is the XFS tracepoint catalog for this kernel tree. It defines the `TRACE_SYSTEM xfs` trace events consumed by XFS metadata, transaction, allocation, recovery, realtime, health monitoring, and IO paths. The header is not a stable ABI; it is a diagnostic contract between XFS code and Linux ftrace/perf/BPF tooling. The file is source-tree-central: many XFS modules include `xfs_trace.h` and call generated `trace_xfs_*` functions, while this header controls event payloads, symbolic formatting, and tracepoint generation through `<trace/define_trace.h>`.

## Important APIs, Types, and Event Families

- Trace macros: `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TRACE_DEFINE_ENUM`, and local wrapper macros such as `DEFINE_BUF_EVENT`, `DEFINE_TRANS_EVENT`, `DEFINE_ALLOC_EVENT`, `DEFINE_DEFER_EVENT`, and `DEFINE_HEALTHMON_EVENT`.
- Forward declarations cover most XFS runtime types observed by tracepoints: `xfs_mount`, `xfs_trans`, `xfs_log_item`, `xfs_buf`, `xfs_inode`, `xfs_btree_cur`, `xfs_perag`, `xfs_group`, `xfs_rtgroup`, deferred intent structures, fsmap records, health monitor records, and log recovery records.
- Transaction and log observability is concentrated in `xfs_trans_resv_class`, `xfs_trans_class`, `xfs_loggrant_class`, `xfs_log_item_class`, `xfs_ail_class`, `xlog_iclog_class`, and log recovery classes.
- Buffer transaction events use `xfs_buf_item_class` and define `xfs_trans_get_buf`, `xfs_trans_get_buf_recur`, `xfs_trans_getsb`, `xfs_trans_getsb_recur`, `xfs_trans_read_buf`, `xfs_trans_read_buf_recur`, `xfs_trans_log_buf`, `xfs_trans_brelse`, `xfs_trans_bdetach`, `xfs_trans_bjoin`, `xfs_trans_bhold`, `xfs_trans_bhold_release`, and `xfs_trans_binval`.
- Filesystem operation coverage includes attribute listing, directory/attribute btrees, inode locks and references, bmap updates, allocation, extent busy tracking, discard, btree cursor activity, rmap/refcount/deferred intents, reflink, fsmap, metadata directory updates, in-memory btrees, exchange-range/exchange-mapping, parent pointers, quota, blockgc/inodegc, realtime zones, free counter reservations, shutdown, health monitor, and media verification.

## Control Flow and Generated Code

The header follows the standard Linux tracepoint pattern: each event class declares a payload schema in `TP_STRUCT__entry`, fills it in `TP_fast_assign`, and formats it in `TP_printk`. `DEFINE_EVENT` instances bind concrete event names to reusable schemas. Inclusion is guarded by `_TRACE_XFS_H` and `TRACE_HEADER_MULTI_READ`; at the end it sets `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE xfs_trace`, and includes `<trace/define_trace.h>` to emit tracepoint definitions in the one translation unit that defines tracepoints.

Runtime XFS code does not call these macros directly. It calls generated functions such as `trace_xfs_trans_alloc`, `trace_xfs_trans_commit`, `trace_xfs_trans_free_abort`, `trace_xfs_buf_item_format`, `trace_xfs_log_reserve`, and `trace_xfs_force_shutdown`. The event definitions determine which fields are copied before the event is written, so tracepoints must not dereference invalid objects or sleep. Many event classes intentionally snapshot refcounts, flags, AG numbers, inode numbers, LSNs, and caller IPs so later analysis can reconstruct state transitions.

## State and Persistence Behavior

The file itself persists no filesystem state. Its importance is observational: tracepoint payloads capture transient state from persistent subsystems. For transactions, it records ticket ids, transaction flags, reservation sizes, log grant head/tail positions, log item types, LSNs, AIL moves, and CIL/log force activity. For allocation and metadata btrees, it records block numbers, lengths, owner information, record states, and error call sites. For health monitoring, it records event insertion, merge/drop behavior, corruption/sickness domains, shutdown flags, media addresses, and file IO errors.

Trace payload schemas matter for postmortem test and production diagnostics because they decide which pieces of in-core state survive into trace logs. Several events use symbolic flag tables such as `XFS_LI_FLAGS`, `XFS_BUF_FLAGS`, `XFS_DQTYPE_STRINGS`, `XFS_RMAP_INTENT_STRINGS`, `XFS_REFCOUNT_INTENT_STRINGS`, `XFS_HEALTHMON_TYPE_STRINGS`, and `XFS_FREECOUNTER_STR` to make bitfields readable.

## Dependencies and Integration Points

The header depends on Linux tracepoint infrastructure and many XFS-private data structures and flag string tables defined in surrounding headers. It is included by implementation files across `fs/xfs`, including transaction code that emits `trace_xfs_trans_resv_calc`, `trace_xfs_trans_alloc`, `trace_xfs_trans_cancel`, `trace_xfs_trans_commit`, `trace_xfs_trans_dup`, `trace_xfs_trans_free`, `trace_xfs_trans_roll`, `trace_xfs_trans_add_item`, and `trace_xfs_trans_free_items`.

It integrates with conditional feature blocks: realtime/zoned events under `CONFIG_XFS_RT`, intent draining under `CONFIG_XFS_DRAIN_INTENTS`, memory buffer events under `CONFIG_XFS_MEMORY_BUFS`, in-memory btree events under `CONFIG_XFS_BTREE_IN_MEM`, POSIX ACL and compat ioctl events under their feature guards, and tracepoint reservation dumps under `CONFIG_TRACEPOINTS` in transaction code.

## Risks and Maintenance Notes

- Tracepoint payloads can become unsafe if a caller passes partially initialized or already freed objects; schemas dereference deep fields such as `tp->t_mountp`, `bp->b_target`, `lip->li_log`, `cur->bc_ops`, and inode forks.
- Schema drift is a diagnostic compatibility risk even though the file states tracepoints are not stable ABI. BPF programs, perf scripts, and tests may still rely on field names.
- Format helpers must match units and field widths. This header documents unit conventions up front because XFS exposes many similar block units: fs blocks, allocation-group blocks, realtime extents, device blocks, bytes, file offsets, and owner ids.
- Conditional tracepoint blocks can hide compile coverage; feature-specific build configurations are needed to catch stale struct members or missing enum string tables.
- Some events use `data_race`, raw atomic reads, or unlocked snapshots intentionally. Consumers should treat them as diagnostic samples, not synchronization guarantees.

## Test Signals

Useful validation signals include successful XFS builds with `CONFIG_TRACEPOINTS`, `CONFIG_XFS_RT`, `CONFIG_XFS_MEMORY_BUFS`, `CONFIG_XFS_BTREE_IN_MEM`, and `CONFIG_XFS_DRAIN_INTENTS` combinations; boot/runtime checks that `/sys/kernel/debug/tracing/events/xfs/` exposes expected transaction, buffer, log, allocation, and health events; ftrace/perf smoke tests while creating files, allocating extents, rolling transactions, triggering quota reservations, and forcing sync commits; and compile failures after changes to XFS structs or enum tables. Transaction-specific tests should confirm `xfs_trans_*` events appear around allocation, commit, cancel, roll, and reservation calculation paths.
