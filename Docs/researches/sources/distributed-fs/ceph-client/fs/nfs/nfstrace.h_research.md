# sources/distributed-fs/ceph-client/fs/nfs/nfstrace.h

## Purpose
`nfstrace.h` defines the Linux tracepoint surface for the NFS client core. It does not implement normal runtime control flow; instead it declares event classes and concrete `TRACE_EVENT`/`DEFINE_EVENT` instances that compile into ftrace/perf tracepoints under `TRACE_SYSTEM nfs`. The file gives operators and tests visibility into inode cache invalidation, lookup and directory operations, buffered and direct I/O, page request state, commit behavior, mount option parsing, local I/O, and XDR decode errors.

## Important APIs, types, and functions
The main exported interface is the generated set of `trace_nfs_*()` call sites. Reusable event classes include `nfs_inode_event`, `nfs_inode_event_done`, `nfs_update_size_class`, `nfs_inode_range_event`, `nfs_readdir_event`, `nfs_lookup_event`, `nfs_lookup_event_done`, `nfs_directory_event`, `nfs_directory_event_done`, `nfs_rename_event`, `nfs_rename_event_done`, `nfs_folio_event`, `nfs_folio_event_done`, `nfs_kiocb_event`, `nfs_page_class`, `nfs_page_error_class`, `nfs_direct_req_class`, optional `nfs_local_dio_class`, and `nfs_xdr_event`.

Formatting helpers `nfs_show_cache_validity()`, `nfs_show_nfsi_flags()`, `nfs_show_wb_flags()`, and `nfs_show_direct_req_flags()` translate NFS bitfields into stable textual names. Concrete events cover inode refresh/revalidate/getattr/setattr/fsync/access, readdir cache activity, lookup/open/create/mkdir/remove/rename/link/sillyrename, folio reads/writes/invalidation, file read/write kiocbs, readahead, pgio read/write initiation and completion, pgio errors, request and commit errors, direct-write state, mount parsing, local filehandle open, and XDR status/filehandle failures.

## Control flow
Each event follows the kernel tracepoint pattern: `TP_PROTO` declares arguments accepted by `trace_nfs_*()`, `TP_STRUCT__entry` declares the ring-buffer payload, `TP_fast_assign` snapshots fields from live kernel objects, and `TP_printk` renders a human-readable line. Event classes avoid repeating common payload layouts, while concrete `DEFINE_EVENT` calls bind names to those layouts.

The common snapshot pattern records stable identifiers rather than full object contents: device major/minor, NFS fileid, hashed filehandle, inode version, size, offsets, counts, flags, error codes, verifier bytes, names, cookies, and RPC task identifiers. I/O events read from `struct nfs_pgio_header`, `struct nfs_commit_data`, `struct nfs_page`, `struct nfs_direct_req`, `struct kiocb`, and `struct iov_iter`; metadata events read from `struct inode`, `struct dentry`, `struct file`, mount parameters, or XDR stream RPC context.

## State and persistence behavior
There is no persistent state. Runtime impact is limited to tracepoint static keys and event-buffer writes when enabled. The important state behavior is observational: fields are copied synchronously at the call site, so trace output records a point-in-time view of NFS inode flags, writeback flags, commit verifiers, and RPC status. Dynamic strings such as dentries, mount options, and sillyrename names are copied into trace buffers to avoid later lifetime issues.

## Dependencies and integration points
This header depends on kernel tracepoint infrastructure, `trace/misc/fs.h`, `trace/misc/nfs.h`, `trace/misc/sunrpc.h`, NFS inode/page/direct/request structures, SUNRPC task/request fields, and optional `CONFIG_NFS_LOCALIO`. It is included by NFS client source files that emit `trace_nfs_*` calls, including the page I/O code in `pagelist.c`. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` block is required for tracepoint code generation and must stay outside the include guard.

## Risks and test signals
The main risks are tracepoint ABI churn, unsafe dereferences in `TP_fast_assign`, incorrect sign handling for errors, stale flag renderers after bit definitions change, and payload reads from objects whose lifetime is not guaranteed at the call site. Tests should enable tracefs events while running NFS lookup, create, readdir, buffered read/write, commit, direct I/O, local I/O when configured, and XDR error paths. Build tests should cover `CONFIG_NFS_LOCALIO` both enabled and disabled and should catch missing includes or changed structure fields.
