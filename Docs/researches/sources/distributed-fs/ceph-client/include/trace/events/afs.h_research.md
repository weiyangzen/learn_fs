# sources/distributed-fs/ceph-client/include/trace/events/afs.h

## Purpose
`afs.h` is the AFS/YFS client tracepoint contract. It covers RPC construction and completion, rxrpc receive/send progress, callback invalidation, directory edit validation, file lock state, cell/server/volume/address-list reference lifetimes, probing, server rotation, and netfs read receive paths.

## Important APIs, types, and functions
The file defines protocol operation enums for AFS FS, VL, CM, and YFS CM operations, plus many trace enums such as `afs_call_trace`, `afs_server_trace`, `afs_volume_trace`, `afs_cell_trace`, `afs_alist_trace`, `afs_estate_trace`, `afs_cb_break_reason`, `afs_dir_invalid_trace`, `afs_edit_dir_op`, `afs_eproto_cause`, `afs_io_error`, `afs_file_error`, `afs_flock_event`, `afs_flock_operation`, and `afs_rotate_trace`. Major events include `afs_receive_data`, `afs_notify_call`, `afs_cb_call`, `afs_call`, `afs_make_fs_call*`, `afs_make_vl_call`, `afs_call_done`, `afs_send_data`, `afs_sent_data`, directory/vnode validity events, protocol/io/file error events, flock events, callback break/miss events, object lifetime events, probe events, `afs_rotate`, `afs_make_call`, and `afs_read_recv`.

## Control flow
The tracepoints follow AFS operation flow from call allocation/reference changes, FS/VL/CM call construction, rxrpc send/receive, state transitions, completion, and error handling. Directory and vnode events fire around local cache validation and edits. Flock events trace VFS lock operations and remote lock state. Probe and rotate events trace server/address selection and retry decisions before a call is finally made.

## State and persistence behavior
No state is owned by the header. Event payloads snapshot debug ids, refs, active counts, operation ids, FIDs, volume ids, names truncated to 23 bytes, data-version values, error/abort codes, rxrpc addresses, probe RTTs, lock ranges, and operation flags. These records persist only as trace output but encode enough state to reconstruct subsystem progress.

## Dependencies and integration points
It depends on AFS internal structures (`afs_call`, `afs_operation`, `afs_vnode`, `afs_server`, `afs_volume`, `afs_cell`, address lists and endpoint state), rxrpc address helpers, VFS `qstr`, `file_lock`, netfs read-subrequest fields, and tracing macros. It integrates AFS with ftrace/perf/BPF and with userspace symbolic enum decoding through `TRACE_DEFINE_ENUM()`.

## Risks and test signals
Risks include stale enum mappings as AFS/YFS protocol operations evolve, exposing only truncated names, dereferencing partially initialized call/vnode objects from trace call sites, and losing diagnostic value if debug ids are not unique enough. Test signals are trace-enabled AFS mount, lookup, read, write, lock, callback-break, server-failover, and cell-management scenarios; expected output should show call ids moving through make/send/receive/done, rotation reasons, and balanced object get/put/free events.
