# Group Research: group_1027_linux_stable_sources_os_linux_linux_stable_fs_nfs_nfstrace_h_source_134884e5df33

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfstrace.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfstrace.h

This header defines the Linux tracepoint surface for the NFS client under `TRACE_SYSTEM nfs`. It is instrumentation-only code: event classes, concrete trace events, and formatting helpers used by NFS client paths to expose inode state, directory operations, page-cache I/O, RPC page I/O, commit/direct I/O, mount parsing, optional local I/O, and XDR decode failures.

Key helpers:
- `nfs_show_cache_validity()` renders `NFS_INO_INVALID_*`, revalidation, deferred invalidation, and metadata invalidation bits.
- `nfs_show_nfsi_flags()` renders selected NFS inode flags such as stale, invalidating, layoutcommit, layoutstats, and odirect.
- `nfs_show_wb_flags()` renders `struct nfs_page` request flags such as busy, mapped, folio, clean, commit-to-DS, inode-ref, headlock, teardown, unlock, uptodate, writeback end, removal, and contention.
- `nfs_show_direct_req_flags()` renders direct I/O state bits.

Major event families:
- Inode lifecycle/cache events: stale marking, refresh/revalidate/invalidate/getattr/setattr/writeback/fsync/access, cache invalidation, readdir force/fill/uncached completion.
- Size/range events: truncate, truncate folio, weak-cache-consistency size updates, grow/update, and readdir cache range invalidation.
- Directory/dentry events: lookup, lookup revalidate, readdir lookup, atomic open, create, mknod, mkdir, rmdir, remove, unlink, symlink, hardlink, rename, async rename, and sillyrename unlink.
- Folio and file I/O events: readpage, writeback folio, folio reclaim, invalidate/launder, update request/folio, write begin/end, writepages, file read/write `kiocb`, and readahead.
- RPC page I/O events: read/write initiation and completion, short reads, pgio error, commit initiation/completion, write verifier/stability reporting, and request-level write/commit errors.
- Direct I/O events: direct commit completion, write completion, iovec scheduling, rescheduling, and completion flags.
- Optional `CONFIG_NFS_LOCALIO` events: local DIO read/write/misaligned and local filehandle open.
- Mount parsing events: assigned mount options, option presence, and mount path.
- XDR events: `nfs_xdr_status` and `nfs_xdr_bad_filehandle`, including SUNRPC task/client identifiers, XID, program/procedure, protocol version, and NFS status.

Important implementation details:
- Payloads consistently include stable correlation identifiers: superblock device major/minor, NFS fileid, and a hashed filehandle via `nfs_fhandle_hash()`.
- Error sign conventions vary by event class. Some normalize negative kernel errors into positive values for `show_nfs_status()`, while RPC completion events often store `task->tk_status` directly.
- The header depends on pretty-printers from `trace/misc/fs.h`, `trace/misc/nfs.h`, and `trace/misc/sunrpc.h`.
- The `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `#include <trace/define_trace.h>` block intentionally sits outside the include guard, following Linux tracepoint generation rules.

Role in this group:
- `pagelist.c` emits `nfs_pgio_error` and uses related NFS request/page I/O trace definitions.
- pNFS files use companion NFSv4 tracepoints from `nfs4trace.h`, while this header covers the generic NFS client tracing surface around the same page/request machinery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfstrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pagelist.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/pagelist.c

This file implements generic NFS read/write request list machinery. It allocates `struct nfs_page` requests, manages page groups, coalesces and splits requests into page I/O descriptors, builds `struct nfs_pgio_header` RPC payloads, submits asynchronous read/write RPC or local I/O, and resends/recoalesces requests after lower-layer failures.

Core responsibilities:
- Maintain the `nfs_page` slab cache with `nfs_init_nfspagecache()` and `nfs_destroy_nfspagecache()`.
- Allocate requests from pages or folios, attach lock/open contexts, bump per-lock-context `io_count`, and release all page/folio/context references on final free.
- Protect request ownership with `PG_BUSY` and page-group mutation with `PG_HEADLOCK`.
- Maintain linked page groups through `wb_head` and `wb_this_page`; synchronize group teardown with `PG_TEARDOWN`.
- Split oversized or partially coalescible requests into subrequests with `nfs_create_subreq()` while preserving page-group semantics.
- Coalesce requests into `nfs_pageio_descriptor` mirrors, submit mirror I/O, and handle recoalescing when drivers return pages to the descriptor.
- Build RPC arguments/page vectors in `nfs_generic_pgio()` and `nfs_pgio_rpcsetup()`.

Important functions:
- `nfs_pgheader_init()` initializes `nfs_pgio_header` from the active descriptor mirror: first request, inode, credential, byte range, direct-request/netfs state, completion ops, release callback, and mirror index.
- `nfs_set_pgio_error()` records the earliest failing byte, clears EOF, sets `NFS_IOHDR_ERROR`, stores the error once, and traces `nfs_pgio_error`.
- `nfs_page_create_from_page()` and `nfs_page_create_from_folio()` create locked head requests for page-backed or folio-backed I/O.
- `nfs_generic_pg_test()` enforces descriptor block-size and page-vector allocation limits before allowing coalescing.
- `nfs_initiate_pgio()` prepares and starts the RPC task, or routes through `nfs_local_doio()` when local I/O is available.
- `nfs_pageio_add_request()` sets up pNFS mirroring, duplicates requests for mirrors, and adds each request through coalescing/recoalescing logic.
- `nfs_pageio_complete()` drains all mirrors, performs error cleanup, calls descriptor cleanup ops, and releases dynamic mirror storage.
- `nfs_pageio_resend()` transfers failed header requests into a new descriptor and retries them, reporting cleanup errors back to the original header.

Coalescing behavior:
- Requests coalesce only when open contexts match, lock owners match when POSIX/flock locks exist, byte ranges are contiguous, and the active `pg_test` callback accepts the addition.
- If only part of a request fits, the file creates subrequests and updates the original request base/offset/length for the remaining range.
- If the descriptor is full or a lower layer requests recoalescing, current I/O is submitted, lists are restored as needed, and requests are retried.

Mirroring and pNFS integration:
- `pg_get_mirror_count`, `pg_get_mirror`, and `pg_set_mirror` callbacks let pNFS layout drivers supply multiple mirrors.
- Dynamic mirror arrays are bounded by `NFS_PAGEIO_DESCRIPTOR_MIRROR_MAX`.
- Duplicate subrequests are submitted to nonzero mirrors before the original request is submitted to mirror zero.
- The generic exported `nfs_pgio_rw_ops` supplies `pg_test = nfs_generic_pg_test` and `pg_doio = nfs_generic_pg_pgios`; pNFS wrappers in `pnfs.c` layer layout selection on top.

Concurrency and lifetime:
- `PG_CONTENDED1`/`PG_CONTENDED2` wake waiters for head locks and busy locks.
- Subrequests hold references on the head until group teardown.
- `PG_INODE_REF` is propagated from head to subrequests when the write/commit path has an inode request reference.
- Per-lock-context `io_count` wakeups coordinate unlock-context waits and async RPC task sleeps.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pagelist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pnfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/pnfs.c

This file is the main pNFS client layout manager. It selects and registers layout drivers, manages per-inode layout headers and layout segments, performs LAYOUTGET/LAYOUTRETURN/LAYOUTCOMMIT orchestration, routes page I/O to data servers or back to the metadata server, handles recalls/reboots/old stateids, and reports optional layout statistics.

Driver management:
- `pnfs_register_layoutdriver()` and `pnfs_unregister_layoutdriver()` maintain the global `pnfs_modules_tbl` under `pnfs_spinlock`.
- `set_pnfs_layoutdriver()` sorts server-advertised layout types by local preference, requests missing modules, selects one active driver per filesystem, calls optional setup, and increments the client MDS count.
- `unset_pnfs_layoutdriver()` calls driver cleanup, decrements MDS count, purges device IDs when the last MDS reference drops, and releases the module.

Layout lifecycle:
- `pnfs_layout_hdr` objects are allocated through the active layout driver, attached to `NFS_I(inode)->layout`, listed on server layout lists for callbacks, and refcounted.
- `pnfs_layout_segment` objects carry range, iomode, seqid, flags, refcount, commit linkage, and owning layout header.
- `pnfs_put_lseg()` removes an lseg when its refcount reaches zero, optionally caching it on `plh_return_segs` for LAYOUTRETURN.
- `pnfs_mark_matching_lsegs_invalid()` and `pnfs_mark_matching_lsegs_return()` invalidate or return matching layout ranges and call driver `cancel_io()` for busy segments.
- `pnfs_destroy_layout*()` and bulk destroy helpers invalidate layouts by inode, fsid, clientid, expired lease, or reboot handling.

Stateid and sequencing:
- `pnfs_seqid_is_newer()` compares wrapping layout stateid sequence numbers.
- `plh_barrier` suppresses stale layoutget/layoutreturn replies.
- `pnfs_set_layout_stateid()` installs newer layout stateids, updates credentials, clears invalid-state flags, and updates the barrier.
- `nfs4_layout_refresh_old_stateid()` handles `NFS4ERR_OLD_STATEID` by bumping a caller stateid or forcing matching lsegs toward return.

LAYOUTGET path:
- `pnfs_update_layout()` is the central layout lookup/acquire routine. It checks pNFS enablement, MDS threshold hints, valid open state, lease recovery, bulk recall, prior layoutget failure backoff, layout drain, in-progress layoutreturn, cached segment match, and blocked layoutgets.
- First layoutget after invalid stateid is serialized with `NFS_LAYOUT_FIRST_LAYOUTGET`.
- Requested ranges are page-aligned before `nfs4_proc_layoutget()`.
- `pnfs_layout_process()` validates the returned range, asks the layout driver to allocate an lseg, handles stale/blocked state, updates layout stateid, inserts the lseg, and records return-on-close when requested.
- `pnfs_lgopen_prepare()`, `pnfs_parse_lgopen()`, and `nfs4_lgopen_release()` implement optional LAYOUTGET-on-OPEN compounds.

LAYOUTRETURN and recall handling:
- `_pnfs_return_layout()` clears layoutcommit state, marks all lsegs for return, lets the driver narrow the return range, sends LAYOUTRETURN when valid returnable segments exist, and waits for completion.
- `pnfs_commit_and_return_layout()` blocks new layoutgets and data-server I/O, waits for writeback, performs layoutcommit, then returns the layout.
- `pnfs_layoutreturn_retry_later()` and `pnfs_layoutreturn_free_lsegs()` update local state after failed or successful layoutreturns.
- `pnfs_layoutreturn_before_put_layout_hdr()` opportunistically sends async LAYOUTRETURN when all references have drained.
- `pnfs_roc()`, `pnfs_roc_done()`, and `pnfs_roc_release()` implement return-on-close, including compound layoutreturn when credentials match and fallback async return otherwise.
- Reboot support sends privileged LAYOUTRETURN with `zero_stateid` when the server advertises reboot layoutreturn capability.

I/O routing:
- `pnfs_generic_pg_init_read()` and `pnfs_generic_pg_init_write()` attach suitable layout segments to pageio descriptors via `pnfs_update_layout()`, falling back to MDS read/write when unavailable.
- `pnfs_generic_pg_test()` wraps generic NFS coalescing and caps coalescing at the active layout-segment boundary.
- `pnfs_generic_pg_readpages()` and `pnfs_generic_pg_writepages()` build pgio headers, hold lseg references, and call driver `read_pagelist()`/`write_pagelist()`.
- `PNFS_NOT_ATTEMPTED` falls back to MDS; `PNFS_TRY_AGAIN` restores pages to the descriptor and requests recoalescing.
- `pnfs_ld_read_done()` and `pnfs_ld_write_done()` are completion entry points for non-RPC-based layout drivers, including MDS resend on pNFS errors.
- `pnfs_read_resend_pnfs()` resends through pNFS after dropping the header lseg to avoid layoutreturn deadlocks.

LAYOUTCOMMIT and sync:
- `pnfs_set_layoutcommit()` marks the inode and lseg as needing layoutcommit, records the highest last-write byte, and dirties the inode.
- `pnfs_layoutcommit_inode()` serializes layoutcommit with `NFS_INO_LAYOUTCOMMITTING`, collects RW lsegs, prepares driver-private commit data, sends `nfs4_proc_layoutcommit()`, and re-dirties on failure.
- `pnfs_cleanup_layoutcommit()` calls driver cleanup and releases lseg references.
- `pnfs_generic_sync()` maps sync to synchronous layoutcommit.

Concurrency:
- `inode->i_lock` protects inode layout pointer, segment lists, return lists, stateid, barriers, and layout flags.
- `cl_lock` plus RCU protect server/client layout lists used for recalls and bulk destruction.
- `plh_outstanding` tracks in-flight layoutgets and coordinates drain.
- Bit locks serialize first LAYOUTGET, LAYOUTRETURN, and LAYOUTCOMMITTING waiters.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pnfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pnfs.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/pnfs.h

This header defines the public pNFS client interface: shared data structures, flags, layout-driver callback contract, device-id cache node type, commit helper APIs, inline range helpers, and no-op fallbacks for builds without `CONFIG_NFS_V4`.

Key data structures:
- `struct nfs4_pnfs_ds_addr`: one data-server address with socket address, printable address, netid, transport, and list linkage.
- `struct nfs4_pnfs_ds`: cached data-server endpoint with address list, net namespace, `nfs_client`, refcount, and connection-state bit.
- `struct pnfs_layout_segment`: cached layout segment with list nodes, range, refcount, seqid, flags, commit list, and owning layout header.
- `struct pnfs_layout_hdr`: per-inode layout state: refcount, outstanding layoutgets, client/server linkage, active/returned lseg lists, blocked-layoutget count, retry timestamp, flags, layout stateid, sequence barrier, return info, layoutcommit last-write byte, layout credential, inode pointer, and RCU head.
- `struct pnfs_device` and `struct pnfs_devicelist`: GETDEVICEINFO/GETDEVICELIST containers.
- `struct nfs4_deviceid_node`: global device-id cache node keyed by layout driver, NFS client, and deviceid.

Important flags and enums:
- Lseg flags: valid, return-on-close, layoutcommit, layoutreturn, and unavailable.
- Layout flags: RO/RW layoutget failure, bulk recall, layoutreturn in progress/locked/requested, invalid stateid, first-layoutget serialization, inode freeing, hashed layout, and drain.
- Driver policy flags: layoutreturn on setattr, layoutreturn on error, read whole page, and LAYOUTGET-on-OPEN.
- Device-id flags: invalid, unavailable, and no-cache.
- `enum pnfs_try_status`: attempted, not attempted, or try again.
- `enum pnfs_layout_destroy_mode`: invalidate, bulk return, or file bulk return.

Layout-driver contract:
- `struct pnfs_layoutdriver_type` is the plugin interface for pNFS layout drivers.
- Required callbacks are `alloc_lseg` and `free_lseg`; registration rejects drivers without them.
- Optional callbacks cover driver setup/teardown, layout header allocation/freeing, lseg insertion/merge, return-range narrowing, pageio read/write ops, DS commit info, sync, read/write pagelist dispatch, device-id allocation/free, layoutreturn preparation, layoutcommit preparation/cleanup, layoutstats preparation, and I/O cancellation.

Commit interfaces:
- `struct pnfs_commit_ops` lets layout drivers manage data-server commit buckets: setup/release DS info, commit pagelists, mark/clear request commits, scan commit lists, and recover commit requests.
- Inline wrappers fall back cleanly when DS commit state or callbacks are absent.

Major APIs declared:
- Driver management: register/unregister/find/put, set/unset layout driver.
- Layout lifecycle and recalls: update/process layout, put lseg/header, destroy layouts, bulk destroy by fsid/clientid, mark matching lsegs invalid/return, mark invalid stateid, old-stateid refresh, return-on-close, layoutreturn retry/free.
- Page I/O: pNFS pageio init/read/write/test/cleanup, resend-to-MDS helpers, resend-through-pNFS helper.
- Layoutcommit/sync: set/cleanup/commit layoutcommit, generic sync, NFS-layout sync.
- Device cache and DS connection: find/get/delete/init/put device IDs, availability helpers, purge/invalidations, DS add/put/connect, multipath address decode.
- LAYOUTGET-on-OPEN helpers.

Inline helpers:
- `pnfs_enabled_sb()` checks whether a mount has an active layout driver.
- `pnfs_layout_is_valid()` checks invalid-stateid state.
- `pnfs_get_lseg()` refcounts an lseg with a memory barrier.
- Range helpers calculate inclusive/exclusive pNFS offsets and intersections for layout ranges and NFS page requests.
- `pnfs_return_layout()` marks return requested and calls `_pnfs_return_layout()` when pNFS is active.
- `pnfs_sync_inode()` dispatches to the active driver sync callback.

Build configuration:
- Under `CONFIG_NFS_V4`, the full pNFS interface is declared.
- Without `CONFIG_NFS_V4`, no-op inline stubs preserve callers while disabling pNFS behavior.
- `pnfs_report_layoutstat()` is active only under `CONFIG_NFS_V4_2`; otherwise it returns zero.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pnfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pnfs_dev.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/pnfs_dev.c

This file implements the global pNFS device-id cache. A device ID is unique per layout driver and NFS client, and maps to layout-driver-specific device information obtained through NFSv4.1 GETDEVICEINFO.

Cache structure:
- The cache is a fixed 32-bucket hash table, `nfs4_deviceid_cache`.
- `nfs4_deviceid_lock` protects insertion, removal, and purge operations.
- Readers use RCU over hash buckets.
- Nodes are `struct nfs4_deviceid_node`, declared in `pnfs.h`, with layout driver, NFS client, flags, unavailable timestamp, deviceid, temporary purge node, RCU head, and atomic refcount.

Important functions:
- `nfs4_deviceid_hash()` hashes the raw 16-byte NFSv4 deviceid with a multiply-by-37 byte fold.
- `_lookup_deviceid()` searches a hash bucket for matching layout driver, client, and deviceid, ignoring nodes whose refcount is zero.
- `nfs4_get_device_info()` allocates a `pnfs_device`, reply pages, and page vector sized from the session max response size; calls `nfs4_proc_getdeviceinfo()`; then asks the active layout driver to decode and allocate a device-id node. It marks `NFS_DEVICEID_NOCACHE` when the server forbids caching.
- `nfs4_find_get_deviceid()` first attempts an RCU cache lookup and refcount acquisition. On a miss, it fetches device info, then handles races with another inserter under the device-id lock.
- `nfs4_delete_deviceid()` unhashes a node, clears no-cache state, and drops the initial cache reference.
- `nfs4_init_deviceid_node()` initializes layout-driver-owned nodes before insertion.
- `nfs4_put_deviceid_node()` decrements references and frees through `ld->free_deviceid_node()` at zero. No-cache nodes trigger deletion when their active reference count reaches the special threshold.
- `nfs4_mark_deviceid_available()`, `nfs4_mark_deviceid_unavailable()`, and `nfs4_test_deviceid_unavailable()` implement temporary device backoff with `PNFS_DEVICE_RETRY_TIMEOUT`.
- `nfs4_deviceid_purge_client()` removes all cached device IDs for a client when pNFS MDS use is active.
- `nfs4_deviceid_mark_client_invalid()` marks all client device IDs invalid after recovery conditions require clients to stop using old mappings.

Concurrency and lifetime:
- RCU enables lockless lookup while deletion uses `hlist_del_init_rcu()`.
- The spinlock serializes cache mutations and purge list construction.
- Atomic references protect nodes while layout drivers or I/O paths use them.
- Purge first unhashes matching nodes into a temporary list, then drops references outside the spinlock.

Error and retry behavior:
- GETDEVICEINFO allocation or RPC failure returns no node and traces `nfs4_find_deviceid(..., -ENOENT)`.
- Unavailable device IDs remain suppressed until their timestamp ages out of `PNFS_DEVICE_RETRY_TIMEOUT`, after which the unavailable flag is cleared and callers may retry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pnfs_dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pnfs_nfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/pnfs_nfs.c

This file provides common NFS I/O helpers for file-based pNFS layout drivers. It covers generic read/write RPC release glue, data-server commit bucket management, data-server endpoint caching and connection setup, multipath data-server address decoding, request commit marking, and NFS-layout sync behavior.

Generic completion/release helpers:
- `pnfs_generic_rw_release()` releases a data-server `nfs_client` reference and delegates final header release to the saved MDS RPC ops.
- `pnfs_generic_prepare_to_resend_writes()` fakes an unstable write verifier so commit release logic retries writes.
- `pnfs_generic_write_commit_done()` delegates write commit completion to the saved MDS callback and may trigger RPC resend behavior.
- `pnfs_generic_commit_release()` completes commit data, releases the lseg and DS client, then releases commit data.

Commit bucket management:
- `pnfs_alloc_commit_array()` allocates a flexible `pnfs_commit_array` with per-bucket `written` and `committing` lists and invalid direct verifiers.
- `pnfs_add_commit_array()` installs a commit array for a layout segment, links it to DS commit info and the lseg, and initializes the refcount.
- Commit arrays are looked up under RCU by lseg; missing arrays are created through layout-driver `setup_ds_info()`.
- `pnfs_generic_clear_request_commit()` clears `PG_COMMIT_TO_DS`, decrements DS written count, removes the request from its commit list, and drops an lseg reference if the bucket became empty.
- `pnfs_generic_scan_commit_lists()` moves requests from bucket `written` lists to `committing` lists, updating `nwritten` and `ncommitting`.
- `pnfs_generic_recover_commit_reqs()` drains written requests into a recovery list and drops bucket lseg references when buckets become empty.
- `pnfs_generic_commit_pagelist()` builds commit calls for both MDS pages and DS buckets, initializes `nfs_commit_data`, and dispatches either generic MDS commit or layout-driver DS commit initiation.

Data-server cache:
- Data servers are cached per network namespace in `nfs4_data_server_cache`, protected by `nfs4_data_server_lock`.
- `same_sockaddr()` compares IPv4/IPv6 socket addresses, including IPv6 link-local scope IDs.
- `_same_data_server_addrs_locked()` treats one address list as matching when all its addresses appear in the cached DS address list.
- `nfs4_pnfs_ds_add()` deduplicates DS entries by address list, splices address ownership into a new DS, builds a debug remotestr, sets refcount/net/client fields, or increments an existing DS refcount.
- `nfs4_pnfs_ds_put()` removes and destroys a DS when its refcount reaches zero, releasing the DS client and address list.

Data-server connection setup:
- `nfs4_pnfs_ds_connect()` serializes connection attempts with `NFS4DS_CONNECTING`, honors device-id unavailable backoff, dispatches to v3 or v4 setup, validates client initialization, traces the result, and returns connection status.
- `_nfs4_pnfs_v3_ds_connect()` lazily requests `nfs3_set_ds_client`, creates or aliases transports for NFSv3 data servers, handles TCP-with-TLS policy, and disables soft retry behavior on the DS RPC client.
- `_nfs4_pnfs_v4_ds_connect()` creates or trunks NFSv4 DS clients, initializes sessions, handles TLS transport servername requirements for trunked addresses, and stores the ready DS client.
- `nfs4_pnfs_v3_ds_connect_unload()` releases the dynamically requested NFSv3 DS connect symbol.

Address decoding:
- `nfs4_decode_mp_ds_addr()` decodes RFC 5665 multipath DS address entries from XDR: netid string, address string with decimal-octet port, IPv4/IPv6 sockaddr, transport identifier, printable remotestr, and netid ownership.
- It currently supports IPv4, IPv6, and one multipath address entry at a time; parse failures free all partial allocations.

Request commit marking and sync:
- `pnfs_layout_mark_request_commit()` looks up/creates the commit array for an lseg, selects the DS commit bucket, stores an lseg reference on non-empty buckets, sets `PG_COMMIT_TO_DS`, increments DS written count, adds the request to the bucket, and marks the folio unstable. If the lseg is unavailable or invalid, it reschedules the write through completion ops.
- `pnfs_nfs_generic_sync()` first commits pending unstable writes with `nfs_commit_inode(FLUSH_SYNC)`, then performs synchronous layoutcommit unless the caller requested datasync-only behavior.

Concurrency and lifetime:
- Commit list movement requires `NFS_I(inode)->commit_mutex`.
- Commit arrays are RCU-listed and refcounted; release can happen under inode lock.
- DS connection state uses a bit wait/wake protocol so concurrent callers share the same connection attempt.
- DS objects own address lists after insertion and hold `nfs_client` references until final put.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/pnfs_nfs.c -->