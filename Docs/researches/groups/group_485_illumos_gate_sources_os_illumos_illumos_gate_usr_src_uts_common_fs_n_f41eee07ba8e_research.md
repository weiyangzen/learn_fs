# Group Research: group_485_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_f41eee07ba8e

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All four listed source files were read completely.

Files researched:
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_export.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log_xdr.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_server.c`

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_export.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_export.c

## Purpose

`nfs_export.c` implements the illumos kernel NFS export registry. It owns per-zone export tables, export creation and removal through `exportfs()`, export lookup by path or filehandle identity, public filehandle state, NFSv4 pseudo-namespace security propagation, export reference lifetime, and helpers that manufacture or resolve NFSv2, NFSv3, and NFSv4 filehandles.

It is the shared export substrate used by the NFS server dispatcher, NFSv2/v3 operation implementations, NFSv4 compound processing, NFS logging, and NFS authorization.

## Main Responsibilities

- Creates per-zone `nfs_export_t` state in `nfs_export_zone_init()`, including the placeholder root/public export, export hash tables, auth cache AVL trees, root vnode binding, and export ID registration.
- Initializes global export state in `nfs_exportinit()`: export ID lock/tree and NFS logging caches.
- Implements `exportfs()` for share, reshare, and unshare operations.
- Maintains export hash links by `{fsid, fid}` and by exported path using `export_link()` and `export_unlink()`.
- Maintains globally unique export IDs in `exi_id_tree`, with overflow-aware duplicate avoidance in `exi_id_get_next()`.
- Copies, frees, adds, removes, and transfers `secinfo_t` security flavor lists, including RPCSEC_GSS mechanism OIDs and root-name lists.
- Propagates NFSv4 security flavor visibility up the pseudo namespace tree with `srv_secinfo_treeclimb()`.
- Maps vnodes to containing export entries through `nfs_vptoexi()`.
- Builds NFSv2, NFSv3, and NFSv4 filehandles through `makefh()`, `makefh3()`, and `makefh4()`.
- Builds WebNFS security-negotiation overloaded filehandles through `makefh_ol()` and `makefh3_ol()`.
- Resolves filehandles back to vnodes through `nfs_fhtovp()`, `nfs3_fhtovp()`, and `nfs4_fhtovp()`.
- Cleans export-dependent NFSv4 state, lock-manager state, auth cache entries, logging buffers, charset conversion caches, visible pseudo-namespace nodes, and vnode references during unexport/free.

## Export Lifecycle

`exportfs()` is the central lifecycle path.

For unshare, it first finds an existing non-root export by path, then calls `unexport()`. `unexport()` unlinks the export under `exported_lock`, removes its export ID from `exi_id_tree`, removes explicitly exported security flavor references from ancestors, either replaces the node with a pseudo export when descendants remain visible or removes the namespace branch, then drops the lock before cleaning NFSv4 state via `rfs4_clean_state_exi()` and notifying the lock manager with `lm_unexport()`.

For share and reshare, `exportfs()`:

1. Copies the requested path from userspace and checks whether that path is already exported.
2. Looks up and traverses the target vnode, including autofs trigger handling via `VOP_ACCESS()` and mounted-vfs traversal.
3. Rejects conflicting attempts to share the same path with a different vnode or the same vnode under a different non-pseudo path.
4. Builds a new `exportinfo_t`, initializes vnode references, auth-cache AVL tables, filehandle template data, export path data, logging path/tag data, and user-supplied security data.
5. Converts non-native data model `secinfo` structures, loads root-name lists, deep-copies RPCSEC_GSS mechanism OIDs, and marks each share-provided flavor as explicitly exported with refcount 1.
6. Installs the RPCSEC_GSS callback when any exported flavor uses RPCSEC_GSS.
7. Loads the WebNFS index option and creates NFS logging buffers when requested.
8. Links the export into the hash tables under `exported_lock`.
9. Replaces an old export for the same vnode when resharing, preserving export IDs and visible pseudo children when needed.
10. Updates the NFSv4 namespace tree with `treeclimb_export()` or by reusing an old tree node.
11. Propagates newly exported security flavors up the ancestor tree.
12. Transfers implicit descendant security references from old export data to new export data for reshare and pseudo-to-real export transitions.
13. Publishes public filehandle state and logs share records when logging is enabled.

The error path is carefully staged with labels `out1` through `out7`, freeing only resources initialized before the failing step.

## Security Flavor Accounting

The file contains a substantial NFSv4 security-flavor reference accounting system. Its goal is to make ancestors and pseudo nodes advertise the union of security flavors needed to reach explicitly exported descendants, while preserving the distinction between flavors explicitly exported on a node and flavors implicitly inherited from descendants.

Key routines:

- `build_seclist_nodups()` condenses an export's flavor list by NFS pseudo flavor number, optionally keeping only explicitly exported flavors.
- `srv_secinfo_add()` increments refcounts for existing flavors and deep-copies new flavors into ancestor or visible-node lists. Pseudo nodes force `M_RO`.
- `srv_secinfo_remove()` decrements explicit flavor refs and removes entries whose refcounts become invalid.
- `srv_secinfo_exp2exp()` handles reshare transfer of descendant flavor refs from an old real export to a new real export.
- `srv_secinfo_exp2pseu()` transfers descendant refs from a removed real export to the pseudo export that replaces it.
- `srv_secinfo_treeclimb()` propagates additions/removals from an export up through `treenode_t` ancestors and their `visible` structures.

This logic is used while holding `exported_lock` as writer and is tightly coupled to the NFSv4 pseudo namespace implementation in nearby files.

## Export Lookup and Filehandle Flow

The export table is hashed by XOR over the filesystem ID and export fid. `checkexport()` looks up an export by `{fsid, xfid}`, maps the placeholder public export to the current real public export, takes an `exi_hold()`, and returns it to NFSv2/v3 callers. `checkexport4()` is the NFSv4 variant: the caller must already hold `exported_lock`, it does not manipulate `exi_count`, and it can additionally require vnode identity to disambiguate lofs/pseudo collisions.

`nfs_vptoexi()` walks from a vnode toward the filesystem or zone root, calling `vop_fid_pseudo()` and `checkexport()` or `checkexport4()` at each step. It supports a `walk` counter used by public filehandle `nosub` checks.

Filehandle creation is version-specific:

- `makefh()` overlays the target file fid into an export template for NFSv2.
- `makefh3()` stores target fid plus export-root fid in an NFSv3 handle, with length bookkeeping for old fixed-size compatibility.
- `makefh4()` uses `vop_fid_pseudo()` and encodes export-root data plus target fid into the fixed NFSv4 filehandle format.
- `makefh_ol()` and `makefh3_ol()` build overloaded WebNFS security-negotiation filehandles containing explicit security flavors in batches.

Filehandle-to-vnode conversion uses the export root vnode's `vfs_t` and `VFS_VGET()`. The NFSv4 path has special handling for pseudo exports through `nfs4_vget_pseudo()` and can return `NFS4ERR_FHEXPIRED` under the optional volatile filehandle test code.

## Public Filehandle and Logging Integration

The per-zone root export starts as a placeholder public filehandle target with `EX_PUBLIC`. A real export with the public option moves `ne->exi_public` to that export and clears the `EX_PUBLIC` bit on the real export so it can be distinguished from the placeholder.

`nfs_getfh()` returns a filehandle to privileged callers, supports NFSv2 and NFSv3 layouts, performs autofs trigger and mounted-vfs traversal, and logs `GETFH` activity when the containing export has `EX_LOG`.

Share and unshare operations call `nfslog_share_record()` and `nfslog_unshare_record()` as appropriate. Export free calls `nfslog_disable()` when a logging buffer is attached.

## Zone and Global Lifetime

Global initialization order is export ID state first, then NFS logging. Per-zone initialization builds the root export before server submodules use it. Shutdown walks all linked exports for the zone and unexports every non-root export. Zone finalization removes the root export from the hash and export-ID tree, destroys root auth caches and locks, verifies no export IDs remain for the zone, destroys `exported_lock`, and frees `nfs_export_t`.

## Dependencies and Integration Points

- NFS server globals from `nfs_server.c` via `nfs_srv_getzg()`.
- NFSv4 namespace helpers: `treeclimb_export()`, `treeclimb_unexport()`, `tree_update_change()`, `pseudo_exportfs()`, `free_visible()`.
- NFSv4 state cleanup: `rfs4_clean_state_exi()`.
- Authorization cache: `nfsauth_cache_free()`, AVL auth cache setup.
- Security service helpers: `sec_svc_loadrootnames()`, `sec_svc_freerootnames()`, `sec_svc_control()`, RPCSEC_GSS callback registration.
- Lock manager: `lm_unexport()`.
- NFS logging: `nfslog_init()`, `nfslog_setup()`, `nfslog_disable()`, share/unshare/getfh logging.
- VFS/vnode operations: `lookupname()`, `VOP_FID()`, `vop_fid_pseudo()`, `VFS_VGET()`, `traverse()`, vnode holds/releases.
- Zone infrastructure for root vnode and shutdown credentials.

## Concurrency and Locking Notes

`nfs_export_t.exported_lock` serializes export table and namespace-tree mutations. Readers use it for export lookup by path or filehandle. `nfs_exi_id_lock` separately protects export ID allocation and `exi_id_tree`. Each `exportinfo_t` has `exi_lock` for `exi_count`, and auth-cache tables have `exi_cache_lock`.

Several routines require specific lock context: `srv_secinfo_treeclimb()`, `export_link()`, and `export_unlink()` assert writer ownership of `exported_lock`; `checkexport4()` asserts the lock is already held; `exi_id_get_next()` asserts `nfs_exi_id_lock`.

## Risks and Edge Cases

- Security-flavor reference transfer during reshare/unshare is subtle. Incorrect refcount transfer can advertise wrong NFSv4 `SECINFO` data for pseudo paths.
- `exportfs()` has many partially initialized resources; future changes need to preserve the staged unwind ordering.
- `nfs_vptoexi()` walks parents using `".."`; unusual filesystem behavior or fid failures map to export lookup failure.
- Vnode identity is needed in NFSv4 export lookup because lofs and pseudo nodes may share fsid/fid identity with real nodes.
- NFSv3 filehandle copyout preserves old padding behavior for compatibility, while logging may require a downsized old handle format.
- Public filehandle state is global per zone and interacts with share/unshare logging and WebNFS multicomponent lookup.
- Optional `VOLATILE_FH_TEST` code is explicitly test-oriented and notes incomplete locking/design assumptions.

## Testing and Verification Signals

Useful tests cover share, reshare, unshare, public export changes, pseudo export creation/removal, descendant security flavor propagation, RPCSEC_GSS root-name and mechanism handling, NFSv2/v3/v4 filehandle round trips, lofs/pseudo export disambiguation, WebNFS security-negotiation overloaded filehandles, logging-enabled exports, zone shutdown cleanup, and NFSv4 state cleanup on unexport.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log.c

## Purpose

`nfs_log.c` implements kernel-side NFS server logging buffer management and log record emission. It creates per-log-buffer in-progress files, queues XDR-encoded NFS log records, flushes records to disk, rotates buffers for user-level log processing, and provides synthetic logging records for share, unshare, public filehandle lookup, and `getfh`.

The XDR field-level encoders are in `nfs_log_xdr.c`; this file owns allocation, dispatch selection, buffering, file I/O, and integration with export and request dispatch code.

## Main Data Structures

`struct lr_alloc` is a private header placed before each allocated record buffer. It tracks circular-list links, allocation flags, encoded record address and size, owning kmem cache, related export, and held `log_buffer`.

`struct log_buffer` instances are shared by exports using the same `ex_log_buffer` path. Each buffer tracks a reference count, path, active `log_file`, queued records, number of queued records, queued byte count, and lock. All buffers are linked on global `nfslog_buffer_list`, protected by `nfslog_buffer_list_lock`.

`struct log_file` represents the currently open in-progress file for a buffer. It tracks path, vnode, refcount, writer count, error/printed/waiting flags, and lock/condition variable coordination.

Three kmem caches back record buffers: small, medium, and large. `nfslog_write_record()` retries with larger caches if XDR encoding does not fit.

## Initialization and Export Setup

`nfslog_init()` initializes the global buffer-list rwlock and creates the small/medium/large record allocation caches. It is called from export initialization.

`nfslog_setup()` attaches logging to an export. It first searches `nfslog_buffer_list` for an existing `log_buffer` whose path matches the export's `ex_log_buffer`. If found, it holds that buffer and attaches it to `exi->exi_logbuffer`. Otherwise it creates a new buffer and backing log file, then reacquires the writer lock and searches again to avoid duplicate creation races. New buffers are inserted into the global list and held once for the list and once for the export.

`nfslog_disable()` releases an export's buffer. Final release flushes queued records, removes the buffer from the global list if no new user raced in, releases the backing file, frees the path, and frees the buffer.

## Log File Lifecycle

`log_file_create()` opens `original_path + LOG_INPROG_STRING` using `vn_open()` with create/write flags. It allocates `struct log_file`, stores the vnode reference returned by `vn_open()`, and writes an NFS log buffer header when the file is empty. The header is built by `create_buffer_header()` with `NFSLOG_BUF_VERSION`, timestamp, flags, offset, and a final size patched into the first XDR word.

`log_file_rele()` closes and releases the vnode when the refcount reaches zero, destroys state, and frees the path and structure.

`nfslog_logbuffer_rename()` is the log-rotation path used by `nfsl_flush()`. It flushes queued records, holds the current `log_file`, renames the in-progress file to the daemon-visible buffer path, creates a fresh in-progress file, swaps it into the `log_buffer`, releases the old buffer reference, and waits for old writers to drain before returning.

## Record Allocation, Queueing, and Flush

`nfslog_record_alloc()` allocates a record buffer from a selected kmem cache and returns the payload area after the `lr_alloc` header. If the export still has `EX_LOG`, it holds the export's `log_buffer` and stores it in the record header. The caller receives the `lr_alloc` as an opaque cookie.

`nfslog_record_put()` either discards invalid/empty records, appends public-filehandle records to every buffer, or enqueues the record on its buffer's circular list. It flushes immediately when queued bytes exceed `nfslog_num_bytes_to_write`, record count exceeds `nfslog_num_records_to_write`, or the caller requests sync.

`nfslog_records_flush_to_disk()` and `_nolock()` detach the current queued circular list while holding `lb_lock`, reset queue counters, hold the current `log_file` as a writer, write all records, release writer state, then free the record list.

`nfslog_write_logrecords()` builds an iovec array over encoded records and appends them to the log vnode with `VOP_WRITE()`. It takes a vnode write lock, snapshots file size, enforces a 32-bit maximum buffer file size, and rolls the file size back with `VOP_SETATTR()` if the write fails after size growth. It suppresses repeated warning messages using `L_PRINTED` and reports re-enable when errors clear.

`nfslog_free_logrecords()` frees a circular list of `lr_alloc` records. For normal records it releases the held log buffer and returns the allocation to its cache. `LR_ALLOC_NOFREE` lets one encoded record be reused across all buffers during public-filehandle logging.

## Flush System Call

`nfsl_flush()` copies a `nfsl_flush_args` request from userspace. It validates version, optionally copies a specific buffer name, and either performs the flush synchronously or starts a zthread for asynchronous work.

`nfslog_do_flush()` scans the buffer list with per-buffer holds. `NFSL_ALL` flushes queued records for each live buffer. A specific `NFSL_RENAME` request rotates the matching live buffer. If the requested buffer is not live, it still attempts to rename `buffer + LOG_INPROG_STRING` to `buffer`, which lets the daemon process inactive in-progress files.

There are some early-return paths in `nfsl_flush()` after allocating `tparams` or `buff` that return without freeing previously allocated memory; these are worth preserving as audit notes if this legacy code is ever touched.

## Logging Dispatch Tables

The file defines logging dispatch tables separate from normal NFS dispatch:

- NFSv2 procedures map to logging XDR routines for handles, args, minimal results, and transaction-affecting flags.
- NFSv3 procedures map similarly, with `READDIRPLUS` using a medium record allocation.
- Synthetic `NFSLOG_PROGRAM` version 1 procedures cover share, unshare, lookup, and getfh records.

Each `nfslog_proc_disp` stores argument encoder, result encoder, and whether the operation affects transaction processing. `nfslog_write_record()` skips non-transaction-affecting operations unless the export has `EX_LOG_ALLOPS`.

## Request Logging Flow

`nfslog_get_exi()` determines which export should receive a log record and allocates a record ID. Normally it returns the request's export when that export has `EX_LOG`. It also handles the WebNFS/public-filehandle edge case where a multicomponent lookup starts through the non-logged public export but returns a filehandle in a logged export; in that case it inspects successful v2/v3 lookup results and finds the returned export by filehandle.

`nfslog_write_record()` selects the logging dispatch entry by RPC program/version/procedure, chooses an initial allocation size, XDR-encodes the record header plus operation args/results, retries in larger record buffers when encoding fails, patches the final encoded length into the record's first XDR word, then queues or synchronously writes the record. Share/unshare records use record ID 0 and are written synchronously.

Public-filehandle state changes call `log_public_record()`, which fabricates an `NFSLOG_LOOKUP` record and appends it to all open buffers. `nfslog_share_record()` logs a synthetic share record to the export's buffer when applicable and always emits the public record when any buffer exists. `nfslog_unshare_record()` emits the synthetic unshare record. `nfslog_getfh()` records privileged getfh operations with filehandle and path.

## Dependencies and Integration Points

- Export state from `exportinfo_t`, including `EX_LOG`, `EX_LOG_ALLOPS`, log buffer path, tag, public export, and filehandle templates.
- Filehandle lookup helpers from `nfs_export.c`: `checkexport()`.
- XDR encoders from `nfs_log_xdr.c`.
- VFS/vnode file I/O: `vn_open()`, `vn_rename()`, `VOP_GETATTR()`, `VOP_WRITE()`, `VOP_SETATTR()`, `VOP_CLOSE()`, vnode locking.
- RPC request metadata: `svc_req`, transport remote address, credential flavor, netid.
- Kernel threading for asynchronous flush via `zthread_create()` and `zthread_exit()`.
- Atomic record ID allocation via `atomic_add_32_nv()`.

## Concurrency and Locking Notes

`nfslog_buffer_list_lock` protects global list traversal and insertion/removal. Buffer refcounts are protected by `lb_lock`; file refcounts and writer counts by `lf_lock`. Record queue manipulation occurs under `lb_lock`. Actual file writes are serialized through `LOG_FILE_LOCK_TO_WRITE()` and vnode write locking.

The rename path carefully swaps `lb_logfile` under `lb_lock` so new writers see the new file, then waits for old `lf_writers` to drain before returning the renamed file to user-level processing.

## Risks and Edge Cases

- `nfsl_flush()` has error paths after allocations that do not free `tparams` or copied buffer storage.
- The log file size cap is `MAXOFF32_T`; once exceeded, logging stops for that buffer until state changes.
- `nfslog_write_record()` indexes dispatch tables by version/procedure after selecting a program; it assumes normal server dispatch has already validated requests.
- Public-filehandle logging reuses one record for every buffer by toggling `LR_ALLOC_NOFREE`; mistakes in circular-list relinking would corrupt subsequent writes.
- Logging records intentionally omit file data and encode compact summaries; consumers must not treat them as full RPC replays.
- Buffer removal races are handled by an extra temporary ref in `log_buffer_rele()`, but future changes must preserve that pattern.

## Testing and Verification Signals

Useful tests cover concurrent exports sharing a log buffer, share/unshare logging, public-filehandle lookup into logged exports, synchronous and asynchronous `nfsl_flush()`, buffer rename while writes are active, queue threshold flushing, ENOSPC/write-error recovery, oversized record retry from small to medium/large buffers, and cleanup when the last export using a buffer is unshared.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log_xdr.c

## Purpose

`nfs_log_xdr.c` contains XDR encode routines for NFS server log records. It is not a full protocol XDR implementation. Instead, it serializes compact log-oriented projections of NFSv2, NFSv3, and synthetic NFSLOG operations: request metadata, credentials, remote address, export tag, filehandles, paths, names, statuses, offsets, counts, sizes, and selected result filehandles.

All routines are oriented to the kernel encode path used by `nfs_log.c`.

## Request and Buffer Headers

`xdr_nfslog_buffer_header()` encodes the log buffer header for current versions, including total header length, buffer version, 64-bit offset, flags, and timestamp. The caller initially encodes with a placeholder length, then patches the first XDR word once the final size is known.

`xdr_nfslog_request_record()` encodes the common per-request record header:

- encoded record length placeholder
- record ID
- RPC program, procedure, and version
- credential flavor
- timestamp
- real UID and GID from the kernel credential
- principal name, if present
- RPC transport netid
- export tag
- caller netbuf

It extracts principal names for AUTH_DES and RPCSEC_GSS through `nfsl_principal_name_get()`. AUTH_UNIX and AUTH_NONE do not provide a principal string.

## Synthetic NFSLOG Encoders

The synthetic logging program uses:

- `xdr_nfslog_sharefsargs()` for share/unshare records, encoding export flags, anonymous UID, path, and export filehandle.
- `xdr_nfslog_sharefsres()` for the status.
- `xdr_nfslog_getfhargs()` for privileged getfh logging, encoding the returned NFSv2-style filehandle and path.

These records let user-level log processing observe export lifecycle and getfh events even though they are not ordinary NFS protocol requests.

## NFSv2 Log Encoders

The NFSv2 routines encode only the fields relevant to logging:

- Filehandles through `xdr_fhandle()`.
- Directory operation args through `xdr_nfslog_diropargs()`.
- Attribute-setting args through `xdr_nfslog_sattr()` and `xdr_nfslog_setattrargs()`.
- Create, rename, link, symlink, read, write, readlink, readdir, and statfs args/results.
- Results usually encode status only, plus minimal successful payload such as returned filehandle, file size, byte count, EOF, or readlink text.

`xdr_nfslog_rdlnres()` copies readlink bytes into a temporary NUL-terminated string before XDR string encoding. It avoids writing raw unbounded memory but uses `KM_SLEEP`, so it can block during log encoding.

## NFSv3 Log Encoders

The NFSv3 routines follow the same compact pattern:

- `xdr_nfslog_diropargs3()` encodes directory filehandle plus name, mapping the `nfs3nametoolong` sentinel to an empty string.
- `xdr_nfslog_CREATE3args()` encodes target and creation mode, with size only for unchecked/guarded create.
- `xdr_nfslog_SETATTR3args()` encodes filehandle plus size change only.
- `xdr_nfslog_READ3args()` and `WRITE3args()` encode filehandle, offset, count, and stable mode.
- Successful read/write results encode file size, byte count, EOF, data size, or commit mode but not file data.
- Namespace operation results encode status and, on success where relevant, post-op filehandle.
- Filesystem metadata operations generally encode only status.
- `xdr_nfslog_READDIRPLUS3resok()` walks returned `dirent64` entries plus `entryplus3_info` metadata and encodes a stream of booleans, post-op filehandles, names, and final EOF.

`xdr_nfslog_nfs_fh3()` clamps malformed internal NFSv3 filehandle component lengths before delegating to `xdr_nfs_fh3_server()`. This protects logging from invalid length fields that would otherwise exceed old NFS filehandle component bounds.

## Encoding Style and Safety Properties

Most routines are small discriminated-union encoders: encode status first, then encode selected success-only payload. Failure arms usually contain no additional detail because the log record is meant for audit/transaction reconstruction, not full protocol replay.

Safety behavior includes:

- Rejecting non-encode use in key routines such as `xdr_nfslog_request_record()` and `xdr_nfslog_sharefsargs()`.
- Avoiding bulk read/write payloads.
- Mapping unsupported or invalid create modes to `FALSE`.
- Checking `READDIRPLUS` record lengths and rejecting zero-length `dirent64` records.
- Clamping invalid NFSv3 filehandle component lengths in the logging path.
- Converting non-NUL-terminated readlink data to a temporary string before XDR string encoding.

## Dependencies and Integration Points

- Called by `nfs_log.c` through logging dispatch tables.
- Uses NFS protocol types and selected ordinary XDR helpers from NFSv2/v3 XDR support, including `xdr_fhandle()`, `xdr_post_op_fh3()`, `xdr_nfs_fh3_server()`, `xdr_nfs2_timeval()`, and scalar RPC XDR helpers.
- Reads request credentials and RPCSEC_GSS raw credentials through RPC service APIs.
- Encodes export tags and metadata from `exportinfo_t`.

## Risks and Edge Cases

- `xdr_string(..., ~0)` is used for several already-kernel-resident strings. Correctness depends on those pointers being trusted and NUL-terminated.
- The file encodes a reduced semantic view. Future log consumers must not expect full NFS result details.
- `READDIRPLUS` logging assumes `objp->reply.entries`, `objp->size`, and `objp->infop` are consistent arrays produced by the server implementation.
- `xdr_nfslog_request_record()` depends on `rpc_gss_getcred()` returning usable raw credentials for RPCSEC_GSS principal extraction.
- Some routines use old-style K&R definitions, so signature mismatches are easier to miss during maintenance.

## Testing and Verification Signals

Useful tests cover every logging dispatch entry, malformed NFSv3 filehandle lengths, `nfs3nametoolong`, readlink data with embedded/nonterminated bytes, `READDIRPLUS` entries with skipped inode-zero entries, create mode variants, RPCSEC_GSS and AUTH_DES principal extraction, synthetic share/unshare/getfh records, and record-size retry behavior in `nfs_log.c`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_server.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_server.c

## Purpose

`nfs_server.c` is the illumos NFS server module front door. It handles module initialization, per-zone server globals, `nfs_svc()` transport registration, RDMA listener startup, NFSv4 server start/stop/quiesce coordination, central RPC dispatch for NFS and NFS_ACL programs, authentication and credential mapping, logging hook integration, public filehandle multicomponent lookup, Trusted Extensions label checks, and zero-copy read buffer helpers.

The actual NFSv2/v3 operation bodies live in other files, but this file decides how requests enter those operations and how replies, duplicate request caching, authorization, and logging are handled.

## Module and Global State

`_init()` calls `nfs_srvinit()`, installs the module, registers function pointers used by `nfssys()` for server quiesce and NFSv4 DSS path setup, initializes DSS path globals, and creates the `nfs_xuio_cache` used by zero-copy read support. `_fini()` returns `EBUSY`, so the server module is not unloadable during normal operation.

Global state includes:

- `nfssrv_zone_key` for per-zone `nfs_globals_t`.
- `nfssrv_globals_list` and `nfssrv_globals_rwl` for visibility across zones.
- `nfs_xuio_cache` and `nfs_loaned_buffers` for copy-reduction paths.
- NFSv4 distributed stable storage globals: `rfs4_dss_newpaths`, `rfs4_dss_numnewpaths`, `rfs4_dss_paths`, and `rfs4_dss_oldpaths`.
- Server callout tables for CLTS, COTS, and RDMA transports.

`nfs_srv_getzg()` caches the current zone's server globals in thread-specific data to reduce repeated `zone_getspecific()` lookups.

## Server Startup and Shutdown

`nfs_svc()` is the system-call path used by `nfsd` to register a transport. It validates the file descriptor, initializes the root export filehandle, computes a read buffer size, copies netid and address mask from userspace, records version min/max, selects a transport-specific service callout table, starts the NFSv4 server if the max version is v4, creates a kernel TLI service transport with `svc_tli_kcreate()`, releases the file descriptor, and records the cluster node ID for HA lock-manager state when clustered.

`rfs4_server_start()` serializes NFSv4 server startup with `nfs_server_upordown_lock`. It waits for old stop/offline transitions to finish, registers service pool offline/shutdown callbacks, calls `rfs4_do_server_start()`, and moves state to `NFS_SERVER_RUNNING`.

`nfs_srv_offline()`, `nfs_srv_stop_all()`, `nfs_srv_quiesce_all()`, and `nfs_srv_shutdown_all()` coordinate service-pool offline, full stop, and quiesce. Quiesce preserves NFSv4 state for warm start. Full stop finalizes NFSv4 state and duplicate reply cache state before marking the server stopped.

`rdma_start()` configures RDMA callout versions, starts NFSv4 if needed, creates RDMA transports, waits for RDMA attach/detach/interruption events, and restarts or stops RDMA services accordingly.

## Dispatch Tables

The file defines dispatch tables for:

- NFSv2: procedures 0-17, including ordinary file/namespace operations and unsupported ROOT/WRITECACHE stubs.
- NFSv3: procedures 0-21, including COMMIT and READDIRPLUS.
- NFSv4: NULL and COMPOUND.
- NFS_ACL v2 and v3 procedures.

Each `rpcdisp` entry contains:

- operation function
- normal and fast XDR arg decoders
- arg structure size
- normal and fast XDR result encoders
- result structure size
- result-free function
- dispatch flags
- filehandle extractor

Important flags include `RPC_IDEMPOTENT`, `RPC_ALLOWANON`, `RPC_MAPRESP`, `RPC_PUBLICFH_OK`, and `RPC_AVOIDWORK`.

Large `union rfs_args`, `union rfs_res`, `union acl_args`, and `union acl_res` provide stack storage for all supported argument/result structures.

## Common Dispatch Flow

`common_dispatch()` is the central request engine for NFSv2, NFSv3, and ACL requests.

The flow is:

1. Validate RPC version and procedure against the selected program dispatch table.
2. Increment per-procedure kstats.
3. Decode arguments using fast XDR when allowed and available, otherwise normal XDR.
4. For NFSv4, delegate to `rfs4_dispatch()` after decode.
5. Extract the filehandle when the operation has one.
6. Compute `anon_ok` for exported-root getattr/statfs-style access using equal object/export fids.
7. Resolve `exportinfo_t` with `checkexport()`.
8. Reject pseudo exports for non-v4 clients.
9. Run `checkauth()` to validate flavor/access and map credentials.
10. Allocate result storage, sometimes from transport response buffers when `RPC_MAPRESP` allows fast reply encoding.
11. For non-idempotent operations, consult the duplicate request cache via `SVC_DUP_EXT()`.
12. Call the operation body, with `T_DONTPEND` set to control asynchronous blocking behavior.
13. Finalize duplicate request cache state through `SVC_DUPDONE_EXT()`.
14. Convert operation-level wrong-security responses into `svcerr_weakauth()`.
15. If NFS logging is active, choose a logging export and copy remote netbuf/result data before reply buffers can be freed.
16. Send the reply using fast result XDR when possible.
17. Write the NFS log record after reply send.
18. Free operation-specific result data if not held by duplicate cache.
19. Free decoded args, release export references, and update bad-call/total-call kstats.

This dispatcher is the main point where RPC mechanics, export lookup, auth, duplicate suppression, logging, and operation execution meet.

## Authentication and Credential Mapping

`checkauth()` handles NFSv2/v3 and ACL request authorization. It enforces optional privileged-port checks, obtains RPC credentials with `sec_svc_getcred()`, allows public-filehandle operations after credential setup, asks `nfsauth_access()` for export policy decisions, and maps credentials according to the selected flavor and export policy.

Behavior includes:

- `NFSAUTH_DROP` silently drops the request.
- `NFSAUTH_RO` marks the request read-only for operation handlers.
- `NFSAUTH_DENIED` usually weak-auth fails, except some anonymous mount-related access can map to AUTH_NONE.
- `NFSAUTH_MAPNONE` maps credentials to anonymous because AUTH_NONE was allowed.
- `NFSAUTH_WRONGSEC` is denied for v2/v3.
- AUTH_NONE maps to `ex_anon`.
- AUTH_UNIX root maps to anonymous unless root access or UID mapping permits otherwise.
- AUTH_UNIX with UID/GID mapping updates the request credential and optional group list.
- AUTH_DES and RPCSEC_GSS validate auth window, check root principal lists, map allowed root principals to `s_rootid`, and map unlisted root/nobody principals to anonymous.

`checkauth4()` is the NFSv4 equivalent working from `compound_state`. It uses `nfsauth4_access()`, returns `-2` for wrong security flavor so NFSv4 can produce protocol-level wrongsec behavior, supports limited access via `CS_ACCESS_LIMITED`, and performs similar credential/root/anonymous mapping.

## Public Filehandle Multicomponent Lookup

`rfs_publicfh_mclookup()` evaluates WebNFS/public-filehandle multicomponent lookup paths. It parses the path type with `MCLpath()`:

- printable ASCII means URL path
- `0x80` means native path
- `0x81` means security query, followed by an index byte and another path tag

It resolves the path relative to a starting directory using `rfs_pathname()`, triggers autofs mounts with `VOP_ACCESS()`, traverses mounted filesystems, resolves real vnodes, and checks that the final vnode belongs to an exported filesystem via `nfs_check_vpexi()`. Pseudo exports are rejected for non-v4 public access.

If the export has an index file and the lookup was URL-based into a directory, it tries to resolve the configured index file and may update the export reference accordingly. Security queries set `SEC_QUERY` so filehandle creation can return overloaded security flavor information.

`rfs_pathname()` wraps pathname lookup with zone-root handling, optional URL percent decoding through `URLparse()`, stack-buffer fast path for typical paths, and heap fallback for long paths.

`nfs_check_vpexi()` uses `nfs_vptoexi()` and enforces `EX_NOSUB` by rejecting public lookups that terminate below the exported directory when the export disallows subtree access.

## Zone Lifecycle

`nfs_srvinit()` initializes global server locks/lists/TSD, then initializes export, v2, v3, v4, and auth subsystems in a strict order before creating the zone key.

`nfs_server_zone_init()` allocates `nfs_globals_t`, initializes server start/stop locks and RDMA wait state, records the zone ID, and initializes export, stats, v2/v3/v4 server, and auth per-zone state before linking the globals into `nfssrv_globals_list`.

`nfs_server_zone_shutdown()` calls auth and export shutdown hooks. `nfs_server_zone_fini()` removes the globals from the global list and tears down auth, v4, v3, v2, stats, and export state in reverse order.

`nfs_srvfini()` deletes the zone key, finalizes global submodules in reverse init order, and destroys global TSD/list/lock state. It is primarily used when module install fails because `_fini()` refuses unload.

## Trusted Extensions Label Helpers

`nfs_getflabel()` derives the label for a vnode or, if the vnode has no cached path, the export path. It finds the containing zone by path, holds the zone label, releases the zone, and returns the label.

`do_rfs_label_check()` compares a client label to the server file object's label using equality or dominance, with DTrace instrumentation. These helpers are used by NFSv3 and NFSv4 lookup/access paths.

## Zero-Copy and mblk Helpers

`mblk_to_iov()` converts an mblk chain to an iovec array.

`rfs_setup_xuio()` allocates an `nfs_xuio_t`, initializes a zero-copy xuio wrapper, stores the vnode, sets a reference count, and installs `rfs_free_xuio()` as the external-buffer free callback.

`uio_to_mblk()` wraps uio iovecs in externally stored STREAMS mblks using `esballoca()` and adjusts the xuio reference count to the number of iovecs.

`rfs_free_xuio()` decrements the xuio refcount and only calls `VOP_RETZCBUF()` and releases the vnode when all mblks referencing the loaned buffers have been returned.

`rfs_read_alloc()` allocates mblk chains and corresponding iovecs for read replies, splitting requests into chunks no larger than `kmem_max_cached` to avoid oversized kmem arena costs.

`rfs_rndup_mblks()` sets mblk write pointers to the actual read length and appends XDR padding. For loaned buffers it may allocate an extra padding mblk because loaned buffer sizes are fixed.

## Dependencies and Integration Points

- RPC service transport layer: `svc_tli_kcreate()`, `svc_rdma_kcreate()`, `SVC_GETARGS()`, `svc_sendreply()`, duplicate request cache hooks, service pool callbacks.
- Export management from `nfs_export.c`: `nfs_export_get_rootfh()`, `checkexport()`, `nfs_vptoexi()`, public export state.
- Authorization from `nfs_auth.c`: `nfsauth_access()`, `nfsauth4_access()`, per-zone init/fini/shutdown.
- NFSv2/v3/v4 operation handlers and XDR routines from neighboring server files.
- NFS logging from `nfs_log.c`.
- NFSv4 state, dispatch, and duplicate reply cache: `rfs4_do_server_start()`, `rfs4_dispatch()`, `rfs4_state_zone_fini()`, `rfs4_fini_drc()`.
- VFS/pathname/vnode APIs and STREAMS mblk APIs.
- Cluster/HA and lock-manager state through `clconf_get_nodeid()` and `lm_global_nlmid`.
- Zone infrastructure and Trusted Extensions labels.

## Concurrency and Locking Notes

Server start/stop/quiesce state is protected by `nfs_server_upordown_lock` and coordinated with `nfs_server_upordown_cv`. Per-zone globals are protected globally by `nfssrv_globals_rwl`. Dispatch itself relies on export reference counts returned by `checkexport()`, duplicate request cache synchronization in RPC service code, and operation-specific locking in the called handlers.

The zero-copy path relies on atomic xuio reference counts so external-buffer callbacks return loaned buffers only after every mblk is released.

## Risks and Edge Cases

- `common_dispatch()` is high-risk because it combines decode, auth, duplicate request cache state, logging, reply sending, result freeing, and export reference release.
- Dispatch table entries must stay consistent with operation numbers, XDR functions, result free routines, and `dis_getfh` extractors. A mismatch can cause decode corruption, missing auth checks, or leaks.
- Version callout tables are mutated based on transport and requested min/max; comments note ordering assumptions.
- Public filehandle URL parsing decodes percent escapes in place and treats malformed path tags as `EIO`.
- `checkauth()` has many credential mapping branches; root, anon, UID mapping, AUTH_NONE, RPCSEC_GSS, and root principal lists need regression coverage.
- `nfs_srv_getzg()` caches zone globals in TSD. Correctness depends on calls happening in the intended zone context.
- RDMA restart logic loops on attach/detach events and must stop transports cleanly on service interruption.
- Zero-copy mblk padding differs between copied and loaned buffers; XDR alignment bugs would surface as corrupt read replies.

## Testing and Verification Signals

Useful tests cover NFSv2/v3 dispatch for every procedure, ACL dispatch, NFSv4 compound handoff, bad version/procedure/decode failures, idempotent vs duplicate-cached non-idempotent operations, public filehandle multicomponent lookup and security query paths, AUTH_NONE/AUTH_SYS/AUTH_DES/RPCSEC_GSS credential mapping, read-only export enforcement, wrongsec behavior, NFS logging after reply send, RDMA attach/detach restart, server quiesce vs full stop, zone shutdown/fini ordering, Trusted Extensions label checks, and zero-copy read buffer return/padding behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_server.c -->