# sources/distributed-fs/ceph-client/fs/nfsd/trace.h

## Purpose

`trace.h` defines the tracepoint surface for the in-kernel NFS server. It is not runtime logic by itself; it is the observability ABI consumed by ftrace/perf/BPF tooling and by NFSD developers diagnosing protocol, file-cache, export-cache, duplicate-reply-cache, stateid, callback, control-plane, VFS, pNFS, and server-side-copy behavior.

## Important APIs, Types, and Functions

The file sets `TRACE_SYSTEM nfsd` and relies on Linux tracepoint macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_DEFINE_ENUM`. Reusable field/assignment macros `NFSD_TRACE_PROC_CALL_FIELDS`, `NFSD_TRACE_PROC_CALL_ASSIGNMENTS`, `NFSD_TRACE_PROC_RES_FIELDS`, and `NFSD_TRACE_PROC_RES_ASSIGNMENTS` capture network namespace inode, xid, local address, and remote address from `struct svc_rqst`.

Major event families include XDR decode/encode failures (`nfsd_garbage_args_err`, `nfsd_cant_encode_err`), dynamic thread scaling, NFSv4 compound progress and errors, filehandle verification and export lookups, VFS I/O (`read_*`, `write_*`, `commit_*`), directory entries, clone/copy errors, delegation wakeups, stateid/open/delegation/layout events, session slot sequence events, clientid lifecycle, grace/write-verifier events, file-cache lifetime and GC events, duplicate reply cache events, callback setup/lifetime/completion events, control-file writes, COPY lifecycle, VFS metadata operations, and pNFS fence errors.

Format helpers such as `show_nfsd_may_flags`, `show_fs_file_type`, `show_stid_type`, `show_stid_status`, `show_nfs_slot_flags`, `show_nf_flags`, `show_drc_retval`, `show_cb_state`, `show_nfsd_authflavor`, and `show_nfsd_cb_opcode` translate bitfields and enum values into trace output.

## Control Flow

Callers include trace hooks spread across NFSD request decode/encode, `fh_verify`, export cache lookup/update, VFS read/write/create/rename/unlink/statfs paths, NFSv4 state management, filecache, duplicate reply cache, callback RPC code, server control files, and COPY/CLONE handling. Each tracepoint snapshots only stable scalar data, hashes, copied strings, or socket addresses into the ring buffer; the print format later renders those fields without dereferencing live objects that may have been freed.

## State and Persistence Behavior

The tracepoints do not own persistent NFSD state. They expose identifiers for persistent or long-lived state: net namespace inode, boot time, write verifier bytes, xid, filehandle hash, clientid/session/stateid tuples, callback addresses, file-cache refcounts and flags, duplicate-reply-cache checksums, and operation status codes. These values are snapshots for diagnostics and do not change server behavior.

## Dependencies and Integration Points

This header integrates with Linux trace infrastructure and with NFSD internals from `export.h`, `nfsfh.h`, `xdr4.h`, `state.h`, `filecache.h`, `vfs.h`, and `cache.h`. It also uses shared trace format helpers from `trace/misc/fs.h`, `trace/misc/nfs.h`, and `trace/misc/sunrpc.h`. It ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>`, so include ordering and single-definition rules matter.

## Risks and Edge Cases

Tracepoints run in hot paths, including read/write and file-cache lookup. Field collection must avoid blocking, excessive allocation, and unsafe dereferences. String fields need correct length handling because path, tag, and operation names can come from request data. Some events expose hashed file handles rather than full handles, which is intentional for size and sensitivity but limits correlation. Changes to internal struct fields can silently break trace output if event assignment code is not updated.

## Test Signals

Build with NFSD and tracing enabled to catch tracepoint declaration errors. Runtime validation should enable `nfsd:*` tracepoints while exercising mount/export lookup, NFSv3 and NFSv4 compounds, file reads/writes, commits, creates, renames, unlinks, readdir, callback recall, client recovery, duplicate request replay, and server control files. Useful failure signals are tracepoint format warnings, BPF program load failures due to format changes, missing xid/clientid correlation, or crashes from stale pointer usage in `TP_fast_assign`.
