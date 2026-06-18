# Group Research: group_785_linux_sources_os_linux_linux_fs_nfs_nfstrace_h_sources_os_linux_linu_5974cc8dcea5

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfstrace.h -->
# File Research: sources/os/linux/linux/fs/nfs/nfstrace.h

## Purpose
`nfstrace.h` defines the Linux tracepoint surface for the NFS client. It is a trace-event declaration header, not an algorithm implementation file. Its role is to expose structured observability for NFS inode state, directory operations, page-cache I/O, pgio RPCs, direct I/O, mount parsing, localio, and XDR status failures.

## Main Trace Areas
- Defines `TRACE_SYSTEM nfs` and includes trace helpers from `trace/misc/fs.h`, `trace/misc/nfs.h`, and `trace/misc/sunrpc.h`.
- Provides display helpers for NFS inode cache-validity bits, NFS inode flags, writeback request flags, direct request flags, stable-write modes, verifier values, file types, open flags, lookup flags, and IOCB flags.
- Defines reusable trace event classes for common record layouts:
  - `nfs_inode_event` and `nfs_inode_event_done`
  - `nfs_update_size_class`
  - `nfs_inode_range_event`
  - `nfs_readdir_event`
  - `nfs_lookup_event` and `nfs_lookup_event_done`
  - `nfs_directory_event` and `nfs_directory_event_done`
  - `nfs_folio_event` and `nfs_folio_event_done`
  - `nfs_kiocb_event`
  - `nfs_page_class` and `nfs_page_error_class`
  - `nfs_direct_req_class`
  - `nfs_xdr_event`

## Covered Operations
- Inode/cache lifecycle: stale marking, refresh, revalidate, mapping invalidation, getattr/setattr, writeback, fsync, access, cache invalidation, readdir cache completion.
- Size/range changes: truncate, truncate-folio, WCC size update, grow/update, and readdir cache range invalidation.
- Directory/name operations: lookup, lookup revalidation, readdir lookup, atomic open, create, mknod, mkdir, rmdir, remove, unlink, symlink, hard link, rename, async rename completion, and sillyrename unlink.
- Page-cache and buffered I/O: readpage, readahead, writeback, folio reclaim, invalidate/launder, update/write begin/write end/writepages, file read/write entry tracepoints.
- RPC pgio/commit operations: initiate/read done/read short/pgio error/initiate write/writeback done/write setup/do writepage/write/commit errors/initiate commit/commit done.
- Direct I/O: direct write completion, commit completion, reschedule paths, write scheduling, and request flags.
- Optional localio: direct read/write/misaligned events when `CONFIG_NFS_LOCALIO` is enabled.
- Mount/local/XDR diagnostics: mount option assignment/parsing/path events, local filehandle open, XDR status, and bad-filehandle events.

## Integration Points
- Used by NFS client source files via `trace_nfs_*` calls.
- Depends on NFS core types such as `struct nfs_inode`, `struct nfs_page`, `struct nfs_pgio_header`, `struct nfs_commit_data`, `struct nfs_direct_req`, `struct nfs_unlinkdata`, and RPC/XDR types.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE nfstrace`, and `<trace/define_trace.h>`, following kernel tracepoint header conventions.

## Invariants and Risks
- Trace fast assignments dereference NFS-specific fields and assume call sites pass valid objects with stable lifetime for the tracepoint invocation.
- Error fields are sometimes normalized as positive NFS status codes for display and sometimes stored directly; consumers must read each event format rather than assume one convention.
- This file has no direct unit-test surface. Validation is mostly compile-time tracepoint generation plus runtime tracing via ftrace/perf/tracefs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/nfstrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/pagelist.c -->
# File Research: sources/os/linux/linux/fs/nfs/pagelist.c

## Purpose
`pagelist.c` implements generic NFS read/write request management. It allocates `struct nfs_page` requests, groups and splits them, coalesces contiguous requests into larger pgio RPCs, manages mirrored pageio descriptors, initiates RPC or localio pgio calls, and handles resend/error cleanup.

## Request Lifetime
- Uses `nfs_page_cachep`, initialized by `nfs_init_nfspagecache()` and destroyed by `nfs_destroy_nfspagecache()`, to allocate `struct nfs_page`.
- `nfs_page_create_from_page()` and `nfs_page_create_from_folio()` create head requests from locked page/folio input.
- `nfs_create_subreq()` splits an existing request into subrequests that share the same page group.
- Request cleanup releases page/folio references, lock contexts, open-context-derived I/O counters, and wakes waiters.
- `nfs_release_request()` uses a `kref` callback that coordinates page-group teardown so all grouped requests are freed together when safe.

## Page Group Synchronization
- `PG_HEADLOCK` protects request group traversal and modification.
- `nfs_page_group_lock()` locks both the request and head when needed; `nfs_page_group_unlock()` releases in reverse.
- `nfs_page_group_sync_on_bit_locked()` lets all requests in a group rendezvous on a `PG_*` bit, then clears the bit across the group.
- Teardown uses `PG_TEARDOWN` to ensure subrequests do not free shared group state prematurely.

## Coalescing and Splitting
- `nfs_generic_pg_test()` enforces block-size and page-array-size limits.
- `nfs_coalesce_size()` additionally requires matching open contexts, compatible lock owners when POSIX/flock locks exist, and contiguous page/folio/file offsets.
- `__nfs_pageio_add_request()` adds a request to the active descriptor or splits it into subrequests when only part of the request can fit.
- When coalescing fails because the current batch is full, the code submits current I/O, then retries the request.
- `nfs_do_recoalesce()` handles layout-driver or mirror-triggered recoalescing by rebuilding descriptor lists.

## Pageio Descriptor and Mirroring
- `nfs_pageio_init()` initializes an `nfs_pageio_descriptor` with operation tables, completion ops, rw ops, block size, and one static mirror.
- Mirror count can be changed by `pg_get_mirror_count`; dynamic mirrors are allocated up to `NFS_PAGEIO_DESCRIPTOR_MIRROR_MAX`.
- `nfs_pgio_current_mirror()` and layout-driver hooks select the active mirror.
- `nfs_pageio_complete()` drains each mirror, runs error cleanup, calls optional `pg_cleanup`, and frees dynamic mirror storage.
- `nfs_pageio_stop_mirroring()` completes outstanding I/O, reducing operation back to normal non-mirrored behavior.

## RPC Setup and Dispatch
- `nfs_pgheader_init()` builds `struct nfs_pgio_header` from a descriptor and current mirror.
- `nfs_generic_pgio()` moves requests from the descriptor to the header, builds the page vector, sets stable-write behavior, initializes commit info, and fills RPC args/results.
- `nfs_generic_pg_pgios()` allocates a header, prepares pgio, optionally opens a localio filehandle, and calls `nfs_initiate_pgio()`.
- `nfs_initiate_pgio()` sets up an async RPC task on `nfsiod_workqueue`, marks moveable tasks when supported, delegates protocol-specific initiation to `rw_ops`, and can run via `nfs_local_doio()` when localio is available.

## Error and Resend Behavior
- `nfs_set_pgio_error()` records the earliest failed byte and marks the header as errored.
- `nfs_pgio_result()` delegates protocol-specific done/result logic, then records task errors or successful results.
- `nfs_pgio_error()` marks `NFS_IOHDR_REDO` and invokes completion.
- `nfs_pageio_error_cleanup()` calls completion error cleanup on every mirror list when descriptor errors exist.
- `nfs_pageio_resend()` moves a failed header’s requests into a fresh descriptor and resubmits, falling back to cleanup and pgio error recording if resend cannot drain all pages.

## Integration Points
- Exports core helpers used by normal NFS and pNFS paths: `nfs_generic_pgio`, `nfs_pageio_add_request`, `nfs_pageio_complete`, `nfs_pageio_resend`, `nfs_initiate_pgio`, request allocation/free helpers, and page-group synchronization.
- Includes `pnfs.h`, `nfstrace.h`, and `fscache.h`, making it the bridge between generic NFS page-cache writeback/readback and layout-driver-specific routing.

## Invariants and Risks
- Request splitting mutates the original request’s base, offset, and byte count after subrequest submission; callers must not assume the original range is unchanged during batching.
- The page-vector size check prevents slab-unfriendly allocations; changing this logic risks allocation failures or oversized RPC setup.
- Open-context, lock-context, contiguity, and layout/mirror constraints are all part of safe coalescing. Relaxing any one can merge I/O that must remain distinct.
- Concurrency correctness relies heavily on bit locks, `kref`, `io_count`, and descriptor list ownership.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/pagelist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/pnfs.c -->
# File Research: sources/os/linux/linux/fs/nfs/pnfs.c

## Purpose
`pnfs.c` is the central pNFS client coordinator. It registers and selects pNFS layout drivers, manages layout headers and layout segments, performs `LAYOUTGET`, handles recalls and returns, routes read/write pgio to data servers through layout drivers, falls back to MDS I/O, manages layoutcommit, handles reboot recovery, and reports layout statistics.

## Layout Driver Registration and Selection
- Maintains `pnfs_modules_tbl` under `pnfs_spinlock`.
- `pnfs_register_layoutdriver()` and `pnfs_unregister_layoutdriver()` manage layout-driver modules.
- `set_pnfs_layoutdriver()` sorts server-advertised layout types by built-in preference and attempts to find or autoload a matching layout driver.
- Supported preference order is SCSI, block volume, OSD2 objects, flex files, and NFSv4.1 files.
- `unset_pnfs_layoutdriver()` calls driver cleanup, decrements MDS count, purges deviceid cache when needed, and releases the module.

## Layout Header and Segment Lifetime
- Layout headers are allocated by the active layout driver and attached to `NFS_I(inode)->layout`.
- `pnfs_put_layout_hdr()` coordinates final detach, layoutreturn-before-free behavior, inode-freeing wakeups, and driver-specific header freeing.
- Layout segments carry ranges, iomode, seqid, refcount, validity bits, layoutcommit bits, layoutreturn bits, and return-on-close state.
- `pnfs_put_lseg()` removes invalid/unused segments, may cache them for later layoutreturn, and frees them through the layout driver.
- `pnfs_generic_layout_insert_lseg()` inserts valid segments sorted by range, with driver hooks available for custom merging/insertion.

## Stateid and Recall Handling
- Tracks layout stateid validity with `NFS_LAYOUT_INVALID_STID`.
- Maintains a sequence barrier (`plh_barrier`) to reject stale layoutget/layoutreturn replies.
- `nfs4_layout_refresh_old_stateid()` handles `NFS4ERR_OLD_STATEID` by updating or bumping stateid sequence use.
- `pnfs_mark_layout_stateid_invalid()` invalidates layout state, clears layoutcommit, drains outstanding layoutgets, and marks/free matching segments.
- `pnfs_mark_matching_lsegs_invalid()` and `pnfs_mark_matching_lsegs_return()` implement recall-range matching, segment invalidation, return marking, and in-flight I/O cancellation via driver hooks.

## LAYOUTGET Flow
- `pnfs_update_layout()` is the main layout acquisition path for read/write I/O.
- It skips pNFS when disabled, when MDS threshold hints say to use MDS, when open stateid is invalid, during bulk recall, or while failed-layout retry windows are active.
- It serializes first layoutget per file with `NFS_LAYOUT_FIRST_LAYOUTGET`, waits on layoutreturn/drain when necessary, and checks the existing segment cache first.
- When needed, it allocates `struct nfs4_layoutget`, page buffers sized to server/session limits, aligns the requested range to page boundaries, calls `nfs4_proc_layoutget()`, and processes the returned segment through `pnfs_layout_process()`.
- `pnfs_layout_process()` validates returned ranges, asks the layout driver to decode/allocate an lseg, updates layout stateid, inserts the segment, and handles return-on-close flags.

## LAYOUTGET-on-OPEN
- `pnfs_lgopen_prepare()` optionally attaches layoutget arguments to an OPEN compound when the layout driver advertises `PNFS_LAYOUTGET_ON_OPEN` and the server supports `NFS_CAP_LGOPEN`.
- Attached and floating layoutget preparations differ based on whether open state already exists.
- `pnfs_parse_lgopen()` consumes the layoutget result, disables `NFS_CAP_LGOPEN` on known unsupported errors, and inserts successful segments.
- `nfs4_lgopen_release()` releases outstanding first-layoutget state and layoutget storage.

## Layout Return and Return-on-Close
- `_pnfs_return_layout()` commits/marks all segments for return, optionally asks the driver to adjust return range, sends `LAYOUTRETURN`, waits for completion, and frees returned lsegs.
- `pnfs_commit_and_return_layout()` blocks new layoutgets, waits for dirty data, performs layoutcommit, then returns layout.
- `pnfs_layoutreturn_before_put_layout_hdr()` can trigger async layoutreturn when the final header put sees pending return state.
- `pnfs_roc()` implements return-on-close compounding when no conflicting open state/delegation remains, with `pnfs_roc_done()` and `pnfs_roc_release()` handling retry, release, stateid update, and error cases.
- `pnfs_wait_on_layoutreturn()` lets RPC tasks sleep while layoutreturn is in progress.

## Bulk Recall, Destroy, and Reboot Recovery
- `pnfs_destroy_layout()` and `pnfs_destroy_layout_final()` invalidate and eventually detach an inode layout.
- Bulk destroy helpers build per-client/per-fsid lists of layout headers using RCU and superblock activity protection.
- `pnfs_layout_destroy_byfsid()` and `pnfs_layout_destroy_byclid()` invalidate or return layouts in bulk.
- `pnfs_destroy_all_layouts()` invalidates deviceids, purges deviceid cache, and destroys client layouts after lease expiry.
- `pnfs_layout_handle_reboot()` builds a recover list, attempts privileged reboot layoutreturns where supported, then invalidates remaining layouts.

## pNFS Read/Write Routing
- `pnfs_generic_pg_init_read()` and `pnfs_generic_pg_init_write()` select or acquire a matching layout segment for a pageio descriptor.
- If no segment is available, the descriptor is reset to normal MDS read/write.
- `pnfs_generic_pg_test()` wraps generic coalescing with layout-segment boundary checks.
- `pnfs_generic_pg_readpages()` and `pnfs_generic_pg_writepages()` allocate pgio headers, attach layout segment refs, build generic pgio data, and dispatch through the layout driver.
- Layout-driver read/write outcomes:
  - `PNFS_ATTEMPTED`: driver owns completion.
  - `PNFS_NOT_ATTEMPTED`: retry through MDS.
  - `PNFS_TRY_AGAIN`: recoalesce and retry pNFS.
- `pnfs_ld_read_done()` and `pnfs_ld_write_done()` are completion helpers for non-RPC layout drivers.
- On data-server errors, optional `PNFS_LAYOUTRET_ON_ERROR` returns the layout, and failed I/O is resent to MDS.

## Layoutcommit and Sync
- `pnfs_set_layoutcommit()` marks inode and lseg layoutcommit state, records last written byte, and dirties the inode for later layoutcommit.
- `pnfs_layoutcommit_inode()` serializes layoutcommit with `NFS_INO_LAYOUTCOMMITTING`, collects RW lsegs, prepares driver-specific layoutcommit data, sends `nfs4_proc_layoutcommit()`, and redirties on failure.
- `pnfs_cleanup_layoutcommit()` calls layout-driver cleanup and releases lseg references.
- `pnfs_generic_sync()` delegates sync to layoutcommit.

## MDS Thresholds and Layoutstats
- `pnfs_within_mdsthreshold()` implements RFC threshold hints from OPEN to keep small file or small I/O on the MDS.
- `pnfs_mdsthreshold_alloc()` allocates threshold state.
- Under `CONFIG_NFS_V4_2`, `pnfs_report_layoutstat()` prepares and sends layout statistics if pNFS and server capabilities allow it.
- `layoutstats_timer` is exported as a module parameter.

## Invariants and Risks
- The inode `i_lock`, client `cl_lock`, RCU list traversal, refcounts, and bit locks form the main safety model.
- First-layoutget serialization is required by protocol errata; removing it can violate stateid sequencing.
- Layoutreturn and layoutget are serialized to avoid freeing lsegs while new layoutgets depend on old state.
- Error fallback to MDS is essential for pNFS correctness; layout drivers must honor the `PNFS_*` try-status contract.
- Layoutcommit lseg references are subtle: references taken in `pnfs_set_layoutcommit()` are released through layoutcommit cleanup paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/pnfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/pnfs.h -->
# File Research: sources/os/linux/linux/fs/nfs/pnfs.h

## Purpose
`pnfs.h` defines the internal pNFS client interface shared by NFS core code and pNFS layout drivers. It declares layout-driver operations, layout and deviceid structures, commit helper contracts, data-server structures, exported pNFS functions, range helpers, and no-op stubs for builds without NFSv4 support.

## Core Data Structures
- `struct nfs4_pnfs_ds_addr`: one data-server address, including sockaddr, length, netid, transport, human-readable address string, and list linkage.
- `struct nfs4_pnfs_ds`: cached data-server object with address list, network namespace, `nfs_client`, refcount, and connection state.
- `struct pnfs_layout_segment`: one cached layout range with list nodes, layoutcommit list, commit arrays, range, refcount, sequence, flags, and parent layout header.
- `struct pnfs_layout_hdr`: per-inode layout cache, with refcount, outstanding layoutget count, client/server list links, segment lists, return lists, flags, stateid, seq barrier, return info, last-write byte, credential, and inode.
- `struct pnfs_device` and `struct pnfs_devicelist`: GETDEVICEINFO/GETDEVICELIST transport containers.
- `struct nfs4_deviceid_node`: global deviceid cache entry keyed by layout driver, NFS client, and deviceid.

## Layout Driver Contract
`struct pnfs_layoutdriver_type` is the main plugin ABI for pNFS layout drivers. It includes hooks for:
- Mount setup/cleanup: `set_layoutdriver`, `clear_layoutdriver`.
- Layout object allocation/free: `alloc_layout_hdr`, `free_layout_hdr`, `alloc_lseg`, `free_lseg`, optional `add_lseg`.
- Layoutreturn and layoutcommit preparation/cleanup.
- Pageio read/write operation tables and data-server commit info.
- Data I/O dispatch: `read_pagelist`, `write_pagelist`.
- Deviceid allocation/free.
- Layoutstats preparation.
- I/O cancellation on recalled segments.

## Commit Contract
`struct pnfs_commit_ops` defines generic data-server commit behavior:
- Allocate/release per-layout data-server commit info.
- Commit data-server page lists.
- Mark and clear requests that must commit to a data server.
- Scan commit lists, and recover commit requests back to generic retry lists.

## Flags and Modes
- Segment flags include valid, return-on-close, layoutcommit, layoutreturn, and unavailable.
- Layout header flags include failed RO/RW layoutget, bulk recall, layoutreturn in progress/locked/requested, invalid stateid, first layoutget, inode freeing, hashed, and drain.
- Layout-driver policy flags include layoutreturn on setattr, layoutreturn on error, read-whole-page, and layoutget-on-open.
- Destroy modes distinguish invalidation, bulk return, and file bulk return.
- Deviceid flags distinguish invalid, temporarily unavailable, and no-cache deviceids.

## Exported Functions
The header declares pNFS entry points implemented in `pnfs.c`, `pnfs_dev.c`, and `pnfs_nfs.c`, including:
- Layout driver registration and selection.
- Layout update, processing, invalidation, return, return-on-close, reboot handling, and layoutcommit.
- Generic pNFS pageio read/write initialization, cleanup, tests, and submission.
- Data-server commit helpers.
- Deviceid lookup, deletion, availability marking, purge, and invalidation.
- Data-server address decoding, cache insertion, connection, and release.
- Layoutget-on-open preparation/parse/release.
- Layoutstats reporting.

## Inline Helpers
- `nfs_have_layout()`, `pnfs_layout_is_valid()`, `pnfs_enabled_sb()`, `pnfs_is_valid_lseg()`.
- Reference helpers: `nfs4_get_deviceid()`, `pnfs_get_lseg()`.
- Commit wrappers: `pnfs_commit_list()`, `pnfs_get_ds_info()`, `pnfs_init_ds_commit_info*()`, `pnfs_release_ds_info()`, `pnfs_mark_request_commit()`, `pnfs_clear_request_commit()`, `pnfs_scan_commit_lists()`, `pnfs_recover_commit_reqs()`.
- Policy wrappers: `pnfs_ld_layoutret_on_setattr()`, `pnfs_ld_read_whole_page()`, `pnfs_sync_inode()`, `pnfs_layoutcommit_outstanding()`, `pnfs_return_layout()`, `pnfs_use_threshold()`.
- Range arithmetic helpers: offset end/length calculation, range copy, exclusive-end calculation, range intersection, and request/segment intersection.
- `pnfs_lseg_cancel_io()` delegates cancellation to the layout driver if provided.

## Conditional Compilation
- Under `CONFIG_NFS_V4`, the real pNFS declarations are active.
- Without `CONFIG_NFS_V4`, the header provides no-op or false/zero stubs so generic NFS code can compile without pNFS support.
- `pnfs_report_layoutstat()` is real only with `CONFIG_NFS_V4_2`; otherwise it returns success without work.

## Invariants and Risks
- Layout drivers must provide at least `alloc_lseg` and `free_lseg`; registration rejects drivers without them.
- Refcount helpers assume objects are already valid and externally synchronized where required.
- Range helpers use exclusive-end semantics in several places; callers must not mix them with inclusive-end assumptions.
- Stub behavior means callers must rely on helpers rather than open-coding pNFS checks if they need NFSv4-disabled builds to remain correct.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/pnfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/pnfs_dev.c -->
# File Research: sources/os/linux/linux/fs/nfs/pnfs_dev.c

## Purpose
`pnfs_dev.c` implements the pNFS deviceid cache. Deviceids identify pNFS data devices for a given layout driver and NFS client. This file looks up cached deviceids, fetches missing device information with `GETDEVICEINFO`, inserts deviceid nodes with RCU protection, handles no-cache/unavailable state, deletes entries, purges client entries, and marks client deviceids invalid.

## Cache Structure
- Uses a global 32-bucket hash table: `NFS4_DEVICE_ID_HASH_BITS` is 5.
- Cache is protected by `nfs4_deviceid_lock` plus RCU list traversal.
- A cache key is `(layout driver, nfs_client, nfs4_deviceid)`.
- Hashing walks raw deviceid bytes with a simple multiply-by-37 accumulator.

## Lookup and Population
- `_lookup_deviceid()` scans one hash bucket and returns a matching node with nonzero refcount.
- `__nfs4_find_get_deviceid()` performs RCU lookup and takes a reference with `atomic_inc_not_zero()`.
- `nfs4_find_get_deviceid()` first checks cache, then calls `nfs4_get_device_info()` on miss, then rechecks under lock to handle races before inserting a new node.
- If another thread inserted the same deviceid during fetch, the newly decoded node is freed through the layout driver.

## GETDEVICEINFO Flow
- `nfs4_get_device_info()` sizes the reply buffer from the session max response size.
- Allocates a `struct pnfs_device`, a page pointer array, and reply pages.
- Fills layout type, deviceid, page buffer fields, and maxcount adjusted by `nfs41_maxgetdevinfo_overhead`.
- Calls `nfs4_proc_getdeviceinfo()`.
- Delegates decoded deviceid-node allocation to `pnfs_curr_ld->alloc_deviceid_node()`.
- Preserves `pdev->nocache` as `NFS_DEVICEID_NOCACHE` on the node.
- Frees temporary pages and `pnfs_device` storage regardless of success.

## Deletion and Refcounting
- `nfs4_init_deviceid_node()` initializes hash nodes, layout-driver/client key fields, flags, deviceid, and refcount.
- `nfs4_delete_deviceid()` removes a matching cache node under the cache lock, clears nocache, and drops the initial cache reference.
- `nfs4_put_deviceid_node()` handles normal refcount drop. For no-cache entries, it forces deletion when only cache/user refs remain, then frees through the layout driver when refcount reaches zero.
- Deviceid frees are traced through `trace_nfs4_deviceid_free()`.

## Availability and Invalidation
- `nfs4_mark_deviceid_unavailable()` stores `jiffies` and sets `NFS_DEVICEID_UNAVAILABLE`.
- `nfs4_test_deviceid_unavailable()` suppresses reuse during `PNFS_DEVICE_RETRY_TIMEOUT`; after the timeout, it clears the unavailable bit.
- `nfs4_mark_deviceid_available()` clears temporary unavailable state.
- `nfs4_deviceid_mark_client_invalid()` marks every cached deviceid for a client with `NFS_DEVICEID_INVALID`.
- `nfs4_deviceid_purge_client()` removes and puts all cached deviceids for a client when pNFS MDS exchange flags indicate pNFS use.

## Integration Points
- Depends on layout-driver callbacks `alloc_deviceid_node()` and `free_deviceid_node()`.
- Called by layout drivers that need to map layout deviceids to concrete data-server/device state.
- Includes `nfs4trace.h` and emits find/free tracepoints.
- Works with `pnfs.h` deviceid flags and with NFSv4 session sizing from `nfs4session.h`.

## Invariants and Risks
- RCU lookup plus atomic refcounting protects readers from nodes being freed while found.
- The second cache lookup after `GETDEVICEINFO` is required to avoid duplicate insertion.
- Nocache handling is subtle because the node can still be briefly hashed and referenced.
- Temporary unavailability is time-window based; callers must call `nfs4_test_deviceid_unavailable()` before reconnect attempts.
- Client purge first unhashes into a temporary list, then drops refs outside the global lock to avoid freeing under the cache lock.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/pnfs_dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/pnfs_nfs.c -->
# File Research: sources/os/linux/linux/fs/nfs/pnfs_nfs.c

## Purpose
`pnfs_nfs.c` provides generic helpers for NFS-based pNFS layout drivers, especially file/flexfile-style layouts. It manages data-server commit buckets, commit-array lifetime, generic commit submission, data-server address/cache handling, data-server client connection setup for NFSv3/NFSv4, multipath address decoding, and sync integration.

## Generic Read/Write and Commit Release
- `pnfs_generic_rw_release()` releases the data-server `nfs_client`, then delegates to MDS pgio release ops.
- `pnfs_generic_prepare_to_resend_writes()` fabricates an unstable verifier result so commit release logic retries writes.
- `pnfs_generic_write_commit_done()` delegates completion to MDS commit done ops and may trigger resend.
- `pnfs_generic_commit_release()` runs commit completion, releases lseg and data-server client references, and frees commit data.

## Commit Bucket Model
- `pnfs_commit_array` contains multiple `pnfs_commit_bucket`s, each with written and committing lists, a layout segment ref, and direct verifier state.
- Arrays are associated with a layout segment and linked into both data-server commit info and the lseg’s commit list.
- `pnfs_alloc_commit_array()` allocates flexible bucket storage and initializes all lists.
- `pnfs_add_commit_array()` inserts a new array unless one already exists for the same lseg.
- RCU and refcounts protect commit arrays while scanners iterate.

## Marking, Clearing, Scanning, and Recovering Commits
- `pnfs_layout_mark_request_commit()` places a write request into the correct data-server commit bucket, sets `PG_COMMIT_TO_DS`, increments `nwritten`, and marks the folio unstable.
- If the lseg is invalid or commit array lookup/setup fails, it reschedules the write through generic completion ops.
- `pnfs_generic_clear_request_commit()` removes a request from its commit list, clears `PG_COMMIT_TO_DS`, updates counters, and releases bucket lseg refs when buckets empty.
- `pnfs_generic_scan_commit_lists()` moves requests from written to committing lists across all arrays/buckets up to `max`.
- `pnfs_generic_recover_commit_reqs()` pulls written requests back to a destination list for retry/recovery.
- Empty buckets release their held lseg refs through `pnfs_free_bucket_lseg()`.

## Generic Commit Submission
- `pnfs_generic_commit_pagelist()` mirrors generic `nfs_commit_list` behavior.
- It creates one MDS commit data object for `mds_pages` when present.
- It allocates data-server commit data for each nonempty committing bucket.
- MDS commits use `nfs_initiate_commit()` against the normal NFS client.
- Data-server commits call the layout-driver-provided `initiate_commit()` callback.
- Allocation failure retries affected commits through `nfs_retry_commit()`.

## Data-Server Cache
- Data servers are cached per network namespace in `nfs4_data_server_cache`, protected by `nfs4_data_server_lock`.
- `nfs4_pnfs_ds_add()` either inserts a new `struct nfs4_pnfs_ds` for a multipath address list or returns an existing matching data server with incremented refcount.
- Address matching treats the first list as a subset of the second and compares IPv4/IPv6 address and port, with IPv6 link-local scope-id checks.
- `nfs4_pnfs_ds_put()` removes and destroys a data server when its refcount drops to zero.
- `destroy_ds()` releases the DS client, all decoded addresses, remote string, and the DS object.

## Data-Server Connection Setup
- `nfs4_pnfs_ds_connect()` serializes connection attempts using `NFS4DS_CONNECTING`.
- It waits for in-progress connection, rejects temporarily unavailable deviceids, then dispatches by data-server NFS version.
- NFSv3 DS connection uses a dynamically requested `nfs3_set_ds_client` symbol and can add compatible transports as aliases.
- NFSv4 DS connection uses `nfs4_set_ds_client()`, initializes DS sessions, and can add session-trunked transports.
- For TLS transports, it adjusts transport identity and server name for the trunked address.
- After connection, it validates `ds_clp` and client initialization status, then traces the result.
- `nfs4_pnfs_v3_ds_connect_unload()` releases the dynamically requested v3 connect symbol.

## Multipath Address Decoding
- `nfs4_decode_mp_ds_addr()` decodes one `netid` and universal address from XDR.
- Parses RFC-style address-plus-port strings where the port is encoded as two decimal octets.
- Supports IPv4 and IPv6, including bracketed human-readable IPv6 remote strings.
- Resolves transport identity with `xprt_find_transport_ident()`.
- Returns a populated `nfs4_pnfs_ds_addr` or cleans up all partial allocations on parse failure.

## Sync Integration
- `pnfs_nfs_generic_sync()` first commits unstable writes with `nfs_commit_inode(..., FLUSH_SYNC)`.
- If the sync is not datasync, it then sends `pnfs_layoutcommit_inode()` to commit layout metadata.
- This is the generic sync behavior for NFS-based pNFS layout drivers.

## Integration Points
- Provides exported helpers used by pNFS layout drivers through declarations in `pnfs.h`.
- Relies on generic NFS commit helpers, RPC transport helpers, NFSv3/NFSv4 DS client setup, NFS net namespace state, and pNFS layout segment validity.
- Bridges layout-driver commit grouping to core NFS commit scheduling.

## Invariants and Risks
- Commit list manipulation assumes `NFS_I(inode)->commit_mutex` is held for paths that modify request lists.
- Commit arrays are RCU-visible; removal must use RCU-safe deletion and refcount checks.
- Bucket lseg references are transferred between written/committing lists and commit data; leaks or premature puts would corrupt layoutcommit/commit retry behavior.
- DS connection serialization prevents duplicate client setup, but callers must still handle temporary device unavailability and incomplete client initialization.
- Address subset matching can intentionally coalesce multipath representations, so layout drivers should supply stable address lists.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/pnfs_nfs.c -->