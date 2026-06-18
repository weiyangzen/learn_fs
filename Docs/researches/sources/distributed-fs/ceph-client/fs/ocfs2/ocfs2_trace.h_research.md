# sources/distributed-fs/ceph-client/fs/ocfs2/ocfs2_trace.h

Purpose: defines the OCFS2 ftrace tracepoint surface for metadata, allocation, refcount, file I/O, inode, superblock, xattr, reservation, quota, directory, namespace, dentry, export, journal, recovery, buffer I/O, and metadata-cache operations.

Important APIs and types: the file declares reusable `DECLARE_EVENT_CLASS` templates for common argument shapes such as int, unsigned int, `u64`, pointer, string, pairs/triples, btree operations, truncate-log operations, get-block operations, file operations, and refcount-tree operations. It then instantiates many `DEFINE_OCFS2_*_EVENT` and `TRACE_EVENT` entries, including namei-relevant events such as `ocfs2_lookup_ret`, `ocfs2_mknod`, `ocfs2_link`, `ocfs2_unlink_noent`, `ocfs2_double_lock`, `ocfs2_rename`, `ocfs2_rename_not_permitted`, `ocfs2_rename_target_exists`, `ocfs2_rename_disagree`, `ocfs2_rename_over_existing`, `ocfs2_create_symlink_data`, `ocfs2_symlink_begin`, `ocfs2_blkno_stringify`, `ocfs2_orphan_add_begin/end`, and `ocfs2_orphan_del`.

Control flow: when included with tracing enabled, each tracepoint records typed fields through `TP_STRUCT__entry`, assigns values in `TP_fast_assign`, and formats them through `TP_printk`. The header uses the standard tracepoint multi-read pattern and includes `trace/define_trace.h` outside the include guard so one C file can instantiate tracepoint definitions.

State and persistence: tracepoints do not persist filesystem state. They expose transient runtime state such as block numbers, clusters, inode numbers, names, return codes, allocation decisions, and lock flow to ftrace/perf consumers.

Dependencies and integration: depends on Linux tracepoint infrastructure and is included throughout OCFS2 implementation files. It is the main observability integration for debugging cluster races, allocation failures, journal recovery, quota sync, dentry invalidation, and namespace operations.

Risks: tracepoint field or name changes can break user scripts and diagnostics. String handling must avoid reading unstable memory after events. High-frequency tracepoints in allocation, I/O, and metadata-cache paths can add overhead when enabled. Format mistakes can hide the values needed to debug corruption or deadlocks.

Test signals: kernel build with tracing enabled and disabled, `trace-cmd`/ftrace smoke tests for representative events, namespace operation traces from create/unlink/rename, allocation and recovery trace coverage during stress tests, and checks that event formats remain parseable by existing tools.
