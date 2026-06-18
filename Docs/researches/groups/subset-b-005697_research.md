# subset-b-005697 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfstrace.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfstrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pagelist.c -->
# sources/distributed-fs/ceph-client/fs/nfs/pagelist.c

## Purpose
`pagelist.c` is the generic NFS buffered page-I/O request engine. It allocates and frees `struct nfs_page` requests, groups requests that describe contiguous file ranges, splits large or partially coalescible requests into subrequests, supports mirrored pNFS descriptors, builds `struct nfs_pgio_header` RPC arguments, starts asynchronous read/write RPCs or local-I/O operations, and resends failed pNFS requests through a fresh pageio descriptor.

## Important APIs, types, and functions
`nfs_page_create_from_page()` and `nfs_page_create_from_folio()` create request objects tied to open and lock contexts. `nfs_release_request()`, `nfs_unlock_request()`, and `nfs_unlock_and_release_request()` manage request lifetimes and busy-state wakeups. Page-group helpers `nfs_page_group_lock()`, `nfs_page_group_sync_on_bit()`, and `nfs_page_group_destroy()` coordinate split/subrequest teardown. `nfs_pageio_init()`, `nfs_pageio_add_request()`, `nfs_pageio_complete()`, `nfs_pageio_cond_complete()`, and `nfs_pageio_resend()` are the descriptor-level API. `nfs_generic_pg_test()`, `nfs_generic_pgio()`, and `nfs_pgio_rw_ops` provide the default coalescing and RPC setup behavior. `nfs_pgheader_init()`, `nfs_set_pgio_error()`, `nfs_pgio_header_alloc()`, `nfs_pgio_header_free()`, and `nfs_initiate_pgio()` manage RPC headers and submission. `nfs_init_nfspagecache()` and `nfs_destroy_nfspagecache()` own the slab cache.

## Control flow
Callers create `nfs_page` objects for dirty or read pages and feed them to a `nfs_pageio_descriptor`. When the first request enters a mirror, optional `pg_init` may acquire a pNFS layout, and the mirror records base/count state. `nfs_coalesce_size()` verifies compatible open contexts, lock owners, file/page contiguity, descriptor limits, and driver-specific `pg_test` limits. If a request cannot fully fit, `__nfs_pageio_add_request()` submits current I/O, retries after recoalescing, or creates a subrequest linked into the same page group.

For pNFS mirroring, `nfs_pageio_add_request()` duplicates requests for mirrors 1..N, sends duplicates to their mirror descriptors, then sends the original to mirror 0. `nfs_pageio_complete()` drains each mirror via `pg_doio`, handles recoalescing loops, runs error cleanup for leftover requests, invokes `pg_cleanup`, and frees dynamic mirror arrays.

When a mirror is ready for I/O, `nfs_generic_pg_pgios()` allocates a header, initializes it from the descriptor, calls `nfs_generic_pgio()` to move requests to `hdr->pages` and build the page vector, optionally opens a local server filehandle, and calls `nfs_initiate_pgio()`. RPC setup fills filehandle, offset, page base, page array, count, open and lock contexts, stable-write mode, verifier, fattr, and completion callbacks. Completion is routed through `nfs_pgio_common_ops`: prepare asks the protocol to finalize the RPC, done dispatches result/error handling, and release invokes completion operations.

## State and persistence behavior
The file manages in-memory I/O state only, but that state drives durable NFS writes and commits elsewhere. Request state includes page/folio references, lock-context I/O counters, open-context references, page group links, request flags, retry counts, and krefs. Descriptor state includes current mirror, list of pending requests, byte counts, block-size limits, pNFS layout segment, completion ops, direct request and netfs context, error status, and `pg_moreio`/`pg_recoalesce` flow-control flags. Header state owns page arrays and RPC argument/result structures until completion. I/O counters wake synchronous and asynchronous waiters when all request references are cleared.

## Dependencies and integration points
`pagelist.c` sits between NFS read/write paths, pNFS layout drivers, local I/O, SUNRPC, netfs helpers, file locking, and the commit engine. It depends on `internal.h`, `pnfs.h`, `nfstrace.h`, and `fscache.h`; it calls protocol-specific `pgio_rpc_prepare`, `rw_initiate`, `rw_done`, `rw_result`, and completion operation hooks. pNFS code reuses these helpers for DS I/O and MDS fallback.

## Risks and test signals
High-risk areas are request splitting, page-group refcount teardown, stable-write selection, page-array sizing, lock-context matching, mirror duplication cleanup, recoalescing loops, and error propagation through `good_bytes` and `NFS_IOHDR_ERROR`. Tests should cover contiguous and non-contiguous folio/page requests, partial coalescing across page and block boundaries, open-context and lock-owner mismatch, soft retransmit limits, mirrored pNFS reads/writes, pNFS resend to MDS, local I/O fallback, allocation failures, interrupted I/O-counter waits, and trace `nfs_pgio_error` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pagelist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pnfs.c -->
# sources/distributed-fs/ceph-client/fs/nfs/pnfs.c

## Purpose
`pnfs.c` is the core NFSv4.1+ parallel NFS layout manager. It registers layout drivers, selects a driver for a mount, creates and destroys per-inode layout headers, looks up and fetches layout segments, handles recalls and layout returns, coordinates pNFS read/write attempts and MDS fallback, tracks layoutcommit state, reports layoutstats, and integrates layout recovery with client reboot and lease recovery.

## Important APIs, types, and functions
Driver management is exposed through `pnfs_register_layoutdriver()`, `pnfs_unregister_layoutdriver()`, `pnfs_find_layoutdriver()`, `pnfs_put_layoutdriver()`, `set_pnfs_layoutdriver()`, and `unset_pnfs_layoutdriver()`. Layout lifetime is managed by `pnfs_get_layout_hdr()`, `pnfs_put_layout_hdr()`, `pnfs_destroy_layout()`, `pnfs_destroy_layout_final()`, `pnfs_destroy_all_layouts()`, `pnfs_layout_destroy_byfsid()`, and `pnfs_layout_destroy_byclid()`. Segment operations include `pnfs_get_lseg()`, `pnfs_put_lseg()`, `pnfs_mark_matching_lsegs_invalid()`, `pnfs_mark_matching_lsegs_return()`, `pnfs_generic_layout_insert_lseg()`, and `pnfs_layout_process()`.

The main data-path entry is `pnfs_update_layout()`, used by `pnfs_generic_pg_init_read()` and `pnfs_generic_pg_init_write()`. Read/write integration is provided by `pnfs_generic_pg_readpages()`, `pnfs_generic_pg_writepages()`, `pnfs_ld_read_done()`, `pnfs_ld_write_done()`, `pnfs_read_resend_pnfs()`, `pnfs_read_done_resend_to_mds()`, and `pnfs_write_done_resend_to_mds()`. Return and close support includes `_pnfs_return_layout()`, `pnfs_return_layout()`, `pnfs_commit_and_return_layout()`, `pnfs_roc()`, `pnfs_roc_done()`, `pnfs_roc_release()`, and `pnfs_wait_on_layoutreturn()`. Commit/stat helpers are `pnfs_set_layoutcommit()`, `pnfs_layoutcommit_inode()`, `pnfs_cleanup_layoutcommit()`, `pnfs_generic_sync()`, `pnfs_mdsthreshold_alloc()`, and `pnfs_report_layoutstat()`.

## Control flow
At mount setup, `set_pnfs_layoutdriver()` sorts server-advertised layout types by client preference, loads a matching layout module if necessary, invokes its setup hook, stores it in `server->pnfs_curr_ld`, and increments the MDS count. I/O paths initialize a pageio descriptor with pNFS ops. On the first request or when a request falls outside the current segment, `pnfs_update_layout()` checks pNFS enablement, MDS threshold hints, open state validity, lease recovery, cached segments, recall/return barriers, first-layoutget serialization, fail-bit retry windows, and outstanding drain state. If no cached segment applies, it rounds the requested range to page boundaries, allocates `nfs4_layoutget` reply pages, sends `nfs4_proc_layoutget()`, and processes the result into a layout-driver segment.

`pnfs_layout_process()` validates the returned range, asks the layout driver to decode the opaque layout body, initializes segment flags and sequence, checks stateid/barrier validity under `i_lock`, updates the layout stateid and credentials, inserts the segment in sorted order, and honors return-on-close. If a recall or newer stateid conflicts, it frees the decoded segment and asks the caller to retry.

Recall and return paths mark matching segments invalid or return-pending, cancel driver I/O, and either free idle segments immediately or move busy segments to `plh_return_segs` until their refcount drops. `_pnfs_return_layout()` serializes `LAYOUTRETURN`, clears layoutcommit references, invokes driver `return_range`, sends the RPC when needed, waits for completion, and drops layout references. `pnfs_roc()` tries to compound return-on-close into close when open/delegation state makes that safe.

Read/write submission creates normal NFS pgio headers, pins the current lseg, then calls the layout driver `read_pagelist` or `write_pagelist`. `PNFS_NOT_ATTEMPTED` moves pages back to the descriptor and resets it for MDS I/O; `PNFS_TRY_AGAIN` recoalesces for another pNFS attempt; driver completion calls MDS completion hooks or resends to MDS on error. Successful writes call `pnfs_set_layoutcommit()`, and later `pnfs_layoutcommit_inode()` serializes layoutcommit RPCs using `NFS_INO_LAYOUTCOMMITTING`.

## State and persistence behavior
State is per server, client, inode, layout header, and layout segment. `pnfs_modules_tbl` is protected by `pnfs_spinlock`. `struct pnfs_layout_hdr` stores refcounts, outstanding layoutgets, segment and return lists, block counters, retry timestamps, flags, stateid, sequence barriers, return info, last-write byte, layoutcommit credentials, and inode pointer. Segment flags track validity, ROC, layoutcommit, layoutreturn, and unavailability. Most mutations happen under `inode->i_lock`; client layout lists use RCU and `cl_lock`. No pNFS metadata is persisted locally, but layoutcommit/return RPCs update server state and writeback durability contracts.

## Dependencies and integration points
The file integrates NFSv4 stateids, open contexts, delegations, layoutget/layoutreturn/layoutcommit/layoutstats procedures, pNFS layout driver callbacks, NFS pageio, commit/writeback, inode dirtying, reboot recovery, SUNRPC waits, module loading, and tracepoints in `nfs4trace.h`. It relies on helper APIs from `pnfs.h`, `internal.h`, `delegation.h`, `nfs42.h`, and `nfs4_fs.h`.

## Risks and test signals
Key risks are stateid sequence-barrier handling, first layoutget serialization, races between layoutget and layoutreturn, segment refcount/list ownership, layoutcommit reference balancing, MDS threshold decisions, fallback/resend loops, and recovery when devices, sessions, or layouts are recalled. Tests should cover driver registration/unregistration, layoutget success and `LAYOUTUNAVAILABLE`, cached segment reuse, return-on-close, bulk recall by fsid/clientid, client reboot recovery, read/write pNFS success and fallback, `LAYOUTRET_ON_ERROR`, layoutcommit sync and async cases, layoutstats, open-with-layoutget, and fault injection around allocation and RPC errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pnfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pnfs.h -->
# sources/distributed-fs/ceph-client/fs/nfs/pnfs.h

## Purpose
`pnfs.h` is the shared pNFS client contract. It defines the layout segment, layout header, layout driver, data-server address, device-id, and commit interfaces used by the generic NFS client and pNFS layout modules. It also provides inline helpers and disabled stubs so non-NFSv4 builds can compile pNFS call sites away cleanly.

## Important APIs, types, and functions
Core types are `struct pnfs_layoutdriver_type`, `struct pnfs_layout_hdr`, `struct pnfs_layout_segment`, `struct pnfs_device`, `struct pnfs_devicelist`, `struct nfs4_deviceid_node`, `struct nfs4_pnfs_ds_addr`, and `struct nfs4_pnfs_ds`. Driver callbacks cover mount setup/teardown, layout header and segment allocation, segment insertion, range return, pageio ops, DS commit info, sync, read/write pagelist attempts, device-id allocation/free, layoutreturn/layoutcommit/layoutstats preparation, and I/O cancellation. `struct pnfs_commit_ops` defines layout-driver hooks for DS commit bucketing.

Declared functions cover layout driver registration, NFSv4 layout procedures, layout cache lifecycle, layout update, layout return/commit, pNFS read/write completion, generic pageio integration, device-id cache operations, data-server cache/connect/decode, generic commit helpers, open-time layoutget helpers, mdsthreshold allocation, layout error handling, and layoutstats reporting. Inline helpers include `pnfs_enabled_sb()`, `pnfs_get_lseg()`, `pnfs_is_valid_lseg()`, `pnfs_calc_offset_end()`, `pnfs_calc_offset_length()`, `pnfs_end_offset()`, range-intersection helpers, commit helper dispatchers, `pnfs_sync_inode()`, `pnfs_return_layout()`, and `pnfs_lseg_cancel_io()`.

## Control flow
Consumers include this header to decide whether pNFS is active for an `nfs_server`, obtain or drop lseg/device references, dispatch to layout-driver operations, and fall back when pNFS is unavailable. Under `CONFIG_NFS_V4`, calls resolve to real functions implemented mostly in `pnfs.c`, `pnfs_dev.c`, and `pnfs_nfs.c`. Without NFSv4 support, the same names become harmless stubs returning false, zero, `NULL`, `PNFS_NOT_ATTEMPTED`, or no-op behavior, preserving call-site simplicity.

The header is also the main compile-time coupling between generic NFS pageio and layout modules: pNFS-aware read/write descriptors call `pnfs_update_layout()`, driver-specific pageio ops can call generic coalescing helpers, and commit code can route pages either to MDS lists or DS bucket lists through `pnfs_commit_ops`.

## State and persistence behavior
The declarations describe in-memory state. `pnfs_layout_hdr` holds volatile client layout state and sequence tracking; `pnfs_layout_segment` represents a server-granted range with refcounts and flags; `nfs4_deviceid_node` is a cached decoded `GETDEVICEINFO` result; `nfs4_pnfs_ds` represents a cached data-server endpoint set and optional connected `nfs_client`. None of these structures persist on disk. Server-visible persistence is mediated through RPCs declared here, especially `LAYOUTGET`, `LAYOUTRETURN`, `LAYOUTCOMMIT`, DS writes/commits, and layoutstats.

## Dependencies and integration points
The header depends on Linux refcounts, workqueues, NFS inode/page structures, NFSv4 stateid and layout UAPI types, RPC transport identifiers, and layout-driver modules such as files, flexfiles, block, SCSI, or object layouts. It is included by generic NFS code, NFSv4 procedure code, pNFS device code, and individual layout drivers. The `CONFIG_NFS_V4_2` guarded layoutstats declaration integrates with NFSv4.2 only when available.

## Risks and test signals
Risks center on API contract misuse: missing mandatory driver callbacks, refcount imbalance for lsegs/device IDs/data servers, wrong range arithmetic at `NFS4_MAX_UINT64`, using pNFS helpers when `pnfs_curr_ld` is `NULL`, commit op dispatch without initialized DS info, and divergence between real functions and stub semantics. Build tests should cover NFSv4 enabled/disabled and NFSv4.2 enabled/disabled. Runtime tests should exercise each inline dispatch path with no layout driver, a working driver, unavailable devices, invalid lsegs, DS commit pages, range boundary values, and layout return/commit policy flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pnfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pnfs_dev.c -->
# sources/distributed-fs/ceph-client/fs/nfs/pnfs_dev.c

## Purpose
`pnfs_dev.c` implements the generic pNFS device-id cache. A device ID is unique per NFS client and layout type; this file hashes, looks up, fetches, inserts, removes, invalidates, temporarily marks unavailable, and purges decoded device-id nodes. Layout drivers provide the actual opaque `GETDEVICEINFO` decode via `alloc_deviceid_node()` and final free via `free_deviceid_node()`.

## Important APIs, types, and functions
`nfs4_find_get_deviceid()` is the primary lookup API: it returns a referenced `struct nfs4_deviceid_node`, fetching device info from the MDS on cache miss. `nfs4_delete_deviceid()` unhashes one node. `nfs4_init_deviceid_node()` initializes driver-allocated nodes. `nfs4_put_deviceid_node()` drops references and frees nodes when no longer cached or used. `nfs4_mark_deviceid_available()`, `nfs4_mark_deviceid_unavailable()`, and `nfs4_test_deviceid_unavailable()` implement temporary backoff after device failures. `nfs4_deviceid_purge_client()` removes all cached nodes for a client, and `nfs4_deviceid_mark_client_invalid()` marks all client nodes invalid after MDS clientid recall. Debug builds also export `nfs4_print_deviceid()`.

## Control flow
`nfs4_find_get_deviceid()` hashes the 16-byte device ID, performs an RCU lookup for the current layout driver and client, and uses `atomic_inc_not_zero()` to pin a live node. On miss, `nfs4_get_device_info()` allocates a `pnfs_device`, page vector, and reply pages sized from the NFSv4.1 session max response, calls `nfs4_proc_getdeviceinfo()`, and hands the result to the layout driver to allocate/decode a node. If the server marks the device non-cacheable, the node gets `NFS_DEVICEID_NOCACHE`.

After fetching, insertion is serialized by `nfs4_deviceid_lock`. The code rechecks the cache to avoid duplicate nodes, frees the unused new node if another thread won, or adds the new node to the RCU hlist with an extra cache reference. Deletion removes the node from the hlist under the spinlock, clears the non-cache bit, and drops the cache reference. Purge walks each hash bucket, unhashes all matching client nodes into a temporary list, then drops references outside the global lock.

Unavailable marking stores `jiffies` then sets `NFS_DEVICEID_UNAVAILABLE`; tests suppress use until `PNFS_DEVICE_RETRY_TIMEOUT` expires, after which the flag is cleared. Client invalidation is weaker: it sets `NFS_DEVICEID_INVALID` under RCU so data paths can stop trusting affected nodes.

## State and persistence behavior
The cache is a static 32-bucket RCU hash table protected by `nfs4_deviceid_lock` for mutation. Node lifetime is atomic-reference based, with one reference for cache membership and additional references for users. `NFS_DEVICEID_NOCACHE` changes put behavior so a non-cacheable node is deleted when the last non-cache user drops it. Device unavailable timestamps are volatile; no device information is persisted locally.

## Dependencies and integration points
This file depends on NFSv4 sessions for `max_resp_sz`, `nfs4_proc_getdeviceinfo()` for server fetches, layout driver decode/free callbacks, RCU hlist primitives, `pnfs.h` state flags, and `nfs4trace.h` tracepoints (`trace_nfs4_find_deviceid`, `trace_nfs4_deviceid_free`). It is invoked by layout drivers when mapping layout segments to storage devices or data servers, and by pNFS teardown/recovery in `pnfs.c`.

## Risks and test signals
Risks include duplicate insertion races, freeing a node still visible to RCU readers, incorrect handling of non-cacheable devices, leaked reply pages on partial allocation failure, stale invalid/unavailable flags, and purging while layout segments still hold references. Tests should cover concurrent lookup of the same device ID, GETDEVICEINFO failure, driver decode failure, `nocache` nodes, delete while referenced, client purge, client invalidation after lease recovery, unavailable timeout behavior, and layout-driver free callback invocation under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pnfs_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pnfs_nfs.c -->
# sources/distributed-fs/ceph-client/fs/nfs/pnfs_nfs.c

## Purpose
`pnfs_nfs.c` provides common support for file-based pNFS layout drivers. It handles generic DS read/write release, DS commit bucketing and recovery, data-server address caching, NFSv3/NFSv4 data-server connection setup, multipath address decoding from XDR, request marking for DS commit, and sync behavior that combines DS COMMIT with LAYOUTCOMMIT.

## Important APIs, types, and functions
I/O release helpers are `pnfs_generic_rw_release()`, `pnfs_generic_prepare_to_resend_writes()`, `pnfs_generic_write_commit_done()`, and `pnfs_generic_commit_release()`. Commit-array APIs include `pnfs_alloc_commit_array()`, `pnfs_free_commit_array()`, `pnfs_add_commit_array()`, `pnfs_generic_clear_request_commit()`, `pnfs_generic_scan_commit_lists()`, `pnfs_generic_recover_commit_reqs()`, `pnfs_generic_commit_pagelist()`, `pnfs_generic_ds_cinfo_release_lseg()`, and `pnfs_generic_ds_cinfo_destroy()`. Data-server APIs include `nfs4_pnfs_ds_add()`, `nfs4_pnfs_ds_put()`, `nfs4_pnfs_ds_connect()`, `nfs4_pnfs_v3_ds_connect_unload()`, and `nfs4_decode_mp_ds_addr()`. `pnfs_layout_mark_request_commit()` assigns written requests to DS buckets, and `pnfs_nfs_generic_sync()` drives commit plus layoutcommit.

## Control flow
For DS commits, layout drivers organize written requests by layout segment and DS commit index in `pnfs_commit_array` buckets. `pnfs_layout_mark_request_commit()` looks up or creates the commit array for an lseg, validates the lseg, pins the bucket's lseg reference if the bucket was empty, marks `PG_COMMIT_TO_DS`, increments DS written counters, and adds the request to the bucket's written list. If setup fails, the request is rescheduled through normal write completion ops.

Commit scanning moves requests from bucket `written` lists to `committing` lists under `commit_mutex` and updates counters. `pnfs_generic_commit_pagelist()` builds a list of MDS commit calls for normal pages and DS commit calls for each non-empty bucket, initializes each `nfs_commit_data`, and either uses generic `nfs_initiate_commit()` for MDS pages or a layout-driver `initiate_commit()` callback for DS pages. On allocation failure or retry, committing requests are moved back with `nfs_retry_commit()`. Completion releases lseg and DS client references through `pnfs_generic_commit_release()`.

The data-server cache is per network namespace. `nfs4_pnfs_ds_add()` canonicalizes a list of decoded addresses by subset matching; an existing DS gets a refcount increment, otherwise the address list is moved into a new cached DS with a debug remote string. `nfs4_pnfs_ds_connect()` serializes connection attempts with `NFS4DS_CONNECTING`, respects device unavailable backoff, dispatches to v3 or v4 connect helpers, and validates that the resulting `nfs_client` completed initialization. V3 uses a dynamically requested `nfs3_set_ds_client` symbol and adds matching transports as aliases. V4 creates DS clients, initializes sessions, and may test/add session-trunked transports, including TLS servername handling.

`nfs4_decode_mp_ds_addr()` decodes RFC 5665 netid and universal address strings from XDR, splits the final two decimal octets into a TCP/UDP port, parses IPv4/IPv6 addresses, maps netid to an RPC transport, and stores a printable address string.

## State and persistence behavior
Commit state is in-memory and protected by the inode commit mutex plus RCU for commit-array lists. Counters `nwritten` and `ncommitting` reflect requests staged for DS commit. Buckets hold lseg references while non-empty. DS cache state is per-net namespace, protected by `nfs4_data_server_lock`, and each DS owns an address list, debug string, optional connected `nfs_client`, refcount, and connection-state bit. The file does not persist state, but DS COMMIT and subsequent LAYOUTCOMMIT affect server-side durability.

## Dependencies and integration points
The file depends on generic NFS commit helpers, pNFS layout segments and device IDs, SUNRPC transport/address utilities, NFS network namespace state, NFSv3 DS connector symbol, NFSv4 DS client/session setup, session trunking, TLS transport policy, XDR decoding, and `nfs4trace.h`. It is used by file and flexfile layout drivers rather than by block/object layout drivers that need different DS semantics.

## Risks and test signals
Risks include commit counter drift, lseg reference leaks from buckets or arrays, RCU/list races when arrays are removed during scanning, requests stranded on committing lists after allocation failure, address subset matching that aliases distinct DS sets, v3 connector module lifetime mistakes, connection serialization deadlocks, TLS trunk servername errors, and universal address parsing edge cases. Tests should cover DS and MDS mixed commits, commit retry/resend, clear-request on rewritten dirty pages, lseg invalidation while commit buckets are non-empty, DS cache reuse and destroy, concurrent connect attempts, unavailable device backoff, v3/v4/TLS/trunking connections, IPv4/IPv6 decode, malformed XDR addresses, and `pnfs_nfs_generic_sync()` with and without pending layoutcommit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/pnfs_nfs.c -->
