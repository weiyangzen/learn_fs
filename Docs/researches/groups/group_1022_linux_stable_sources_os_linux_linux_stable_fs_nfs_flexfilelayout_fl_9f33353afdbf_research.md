# Group Research: group_1022_linux_stable_sources_os_linux_linux_stable_fs_nfs_flexfilelayout_fl_9f33353afdbf

Scope: learn_fs subset A, source tree `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayout.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayout.c

## Purpose

Implements the NFSv4 pNFS flexfile layout driver. It decodes layout segments, manages mirrors and data-server stripes, routes reads/writes/commits to DS clients or MDS fallback, records layout errors/statistics, and registers the `LAYOUT_FLEX_FILES` layoutdriver.

## Main Entry Points

- `ff_layout_alloc_layout_hdr()` / `ff_layout_free_layout_hdr()`: allocate and release flexfile per-layout state.
- `ff_layout_alloc_lseg()` / `ff_layout_free_lseg()` / `ff_layout_add_lseg()`: decode, cache, merge, sort, and release flexfile layout segments.
- `ff_layout_pg_init_read()` / `ff_layout_pg_init_write()` / `ff_layout_pg_test()`: pageio setup and coalescing rules for striped DS I/O.
- `ff_layout_read_pagelist()` / `ff_layout_write_pagelist()`: initiate async DS read/write RPCs or localio.
- `ff_layout_commit_pagelist()` / `ff_layout_initiate_commit()`: send unstable-write commits to the right DS stripe.
- `ff_layout_async_handle_error_v3()` / `ff_layout_async_handle_error_v4()`: translate DS/RPC errors into retry, pNFS resend, MDS fallback, or fatal I/O.
- `ff_layout_prepare_layoutreturn()` / `ff_layout_encode_layoutreturn()`: collect DS errors and stats for LAYOUTRETURN.
- `ff_layout_prepare_layoutstats()` and stats encoding helpers: prepare LAYOUTSTATS payloads.
- `nfs4flexfilelayout_init()` / `nfs4flexfilelayout_exit()`: register/unregister the layout driver.

## Control Flow And State

Layout segment allocation decodes XDR layout data: stripe unit, mirror count, per-mirror DS stripe count, device IDs, efficiencies, DS stateids, filehandle versions, and per-DS credentials. Mirrors are deduplicated at the layout level by matching device IDs and filehandles, refcounted, then sorted by summed efficiency.

Read pageio selects one mirror/stripe, preferring available device IDs and falling back to other mirrors before MDS fallback. Write pageio prepares every mirror because RW flexfile layouts require all mirrors. Stripe boundaries limit request coalescing. DS I/O setup chooses filehandles, stateids, credentials, DS RPC clients, localio handles when available, and version-specific call ops.

Completion paths update layoutstats, handle NFSv3/NFSv4 protocol errors, record DS errors, mark device IDs unavailable or reachable, resend to another pNFS mirror when possible, or reset through MDS. Successful writes and commits trigger layoutcommit unless the layout says not to. Layoutreturn and layoutstats encode accumulated IO error records and latency/count data into flexfile layoutupdate XDR.

## Dependencies

Depends on the pNFS core, NFS pageio/read/write/commit infrastructure, NFSv4 session and stateid handling, DS deviceid cache, RPC task/call ops, fscache-independent localio helpers, `nfs42` LAYOUTERROR/LAYOUTSTATS support, and structures declared in `flexfilelayout.h`.

## Risks

The driver is concurrency-heavy: mirror lists are protected by inode locks, per-mirror stats by mirror locks, credentials through RCU, and DS device IDs by pNFS caches. Error handling must avoid infinite pNFS/MDS retry loops while preserving layoutreturn diagnostics. XDR decoding must reject invalid mirror/stripe counts and bad filehandles, because counts can drive large allocations. Layoutstats and LAYOUTRETURN share mirror references and private XDR cleanup paths, so missed refcount/free handling can leak or use stale mirror state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayout.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayout.h

## Purpose

Defines the private data model and helper API for the NFSv4 flexfile pNFS layout driver.

## API Surface

- Layout flags: `FF_FLAGS_NO_LAYOUTCOMMIT`, `FF_FLAGS_NO_IO_THRU_MDS`, and `FF_FLAGS_NO_READ_IO`.
- Limits and stats constants: maximum mirror/stripe counts and layoutstats intervals.
- `struct nfs4_ff_layout_ds`: cached flexfile deviceid node, supported DS protocol versions, and DS address object.
- `struct nfs4_ff_layout_mirror`: one mirror containing DS stripes, credentials, stats, refcount, lock, and reporting state.
- `struct nfs4_ff_layout_ds_stripe`: per-stripe device ID, filehandles, DS stateid, DS credentials, localio state, and read/write stats.
- `struct nfs4_ff_layout_segment`: pNFS segment plus stripe unit, flags, and mirror array.
- `struct nfs4_flexfile_layout`: per-layout header, commit info, mirror list, error list, and last stats report time.
- Inline helpers convert generic pNFS headers to flexfile objects, compute stripe IDs, expose mirror/deviceid counts, and interpret fallback/read restrictions.
- Function declarations cover deviceid allocation, DS preparation, DS credential/filehandle selection, error tracking/encoding, LAYOUTERROR sending, and fallback policy.

## Dependencies

Includes Linux refcounting and NFS pNFS declarations. It is consumed by both `flexfilelayout.c` and `flexfilelayoutdev.c`.

## Risks

This header is the shared contract between the flexfile I/O path and device/error path. The flexible-array layout segment and per-mirror refcounting require callers to respect lifetime rules. `nfs4_ff_layout_calc_dss_id()` assumes validated stripe counts and stripe unit semantics from layout decoding.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayoutdev.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayoutdev.c

## Purpose

Implements flexfile deviceid decoding, DS connection preparation, DS credential selection, DS error aggregation, and fallback-availability policy.

## Main Entry Points

- `nfs4_ff_alloc_deviceid_node()`: decodes GETDEVICEINFO opaque data into DS addresses and supported protocol versions.
- `nfs4_ff_layout_prepare_ds()`: resolves a mirror stripe’s deviceid, connects to the DS, clamps rsize/wsize to RPC payload limits, and reports connection failures.
- `nfs4_ff_find_or_create_ds_client()`: returns the correct DS RPC client for NFSv3 or NFSv4 DS access.
- `ff_layout_get_ds_cred()`: chooses per-DS credentials unless the DS is tightly coupled.
- `ff_layout_track_ds_error()`: records DS I/O errors for LAYOUTERROR/LAYOUTRETURN.
- `ff_layout_encode_ds_ioerr()` / `ff_layout_fetch_ds_ioerr()` / `ff_layout_free_ds_ioerr()`: serialize, move, cap, and free tracked error records.
- `ff_layout_avoid_mds_available_ds()` / `ff_layout_avoid_read_on_rw()`: expose fallback policy decisions.

## Control Flow And State

Deviceid allocation decodes multipath DS addresses, filters unsupported DS NFS versions, normalizes I/O sizes, and installs an `nfs4_pnfs_ds` address object. DS preparation lazily resolves device IDs into `mirror_ds` with `cmpxchg`, connects if no DS client exists, probes localio, and records `NFS4ERR_NXIO` plus LAYOUTERROR on failure. RW layouts mark for return when any required mirror is unusable; read layouts can continue if any mirror is still usable.

Error tracking stores sorted, mergeable records keyed by opnum, status, stateid, deviceid, and adjacent/overlapping byte ranges. Fetching moves matching records out of the layout list and discards overflow when a caller’s maximum is reached.

## Dependencies

Uses pNFS deviceid helpers, DS address decoding, DS connection helpers, RPC client creation, NFSv4 stateid utilities, inode locking, RCU credentials, and flexfile structures from `flexfilelayout.h`.

## Risks

Deviceid and DS connection state is shared across racing I/O paths, so the lazy `mirror_ds` initialization and deviceid refcounting must remain precise. Error-list merging is order-sensitive and protected by `i_lock`; mistakes can lose LAYOUTRETURN diagnostics or grow unbounded. Read and RW availability differ deliberately: reads require one usable mirror, writes require all mirrors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayoutdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/fs_context.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/fs_context.c

## Purpose

Implements NFS mount context parsing and validation for the modern fs_context API, including text mount options, legacy binary NFSv2/v3/v4 mount data, remount context duplication, and `nfs`/`nfs4` filesystem type registration.

## Main Entry Points

- `nfs_fs_context_parse_param()`: parses individual text mount options.
- `nfs_parse_security_flavors()` / `nfs_parse_xprtsec_policy()` / `nfs_parse_version_string()`: parse security, transport security, and NFS version options.
- `nfs23_parse_monolithic()` / `nfs4_parse_monolithic()`: translate legacy binary mount data into `struct nfs_fs_context`.
- `nfs_fs_context_validate()`: validates addresses, versions, transports, migration use, source syntax, and loads the protocol module.
- `nfs_get_tree()`: validates and invokes the version-specific tree creation path.
- `nfs_fs_context_dup()` / `nfs_fs_context_free()`: clone and clean mount contexts.
- `nfs_init_fs_context()`: allocate defaults for new mounts or copy state for remounts.
- `nfs_fs_type` / `nfs4_fs_type`: exported filesystem type definitions.

## Control Flow And State

The parser maps a large option table into `nfs_fs_context` fields: cache behavior, close-to-open, hard/soft behavior, transports, mount side-protocol options, readdirplus policy, fscache uniquifiers, security flavors, TLS key serials, lookup caching, local locks, connection counts, and attribute timeouts. Validation checks protocol/address-family consistency, rejects UDP for NFSv4 or disabled UDP builds, maps xprtsec to TCP-TLS transports, assigns default ports, parses `host:path`, and switches `fc->fs_type` to the loaded NFS subversion module.

Legacy monolithic parsing supports old NFSv2/v3 mount structures, SELinux context passthrough for version 6 data, and NFSv4 version-1 binary mount data including compat conversion. Remount contexts are initialized from the live `nfs_server`, including network namespace and protocol module references.

## Dependencies

Depends on Linux fs_context/fs_parser, NFS mount structures, RPC transport identifiers, RPC-with-TLS handshake policy, key lookup when TLS keys are enabled, NFS protocol module lookup, and version-specific `try_get_tree()` implementations.

## Risks

Mount option interactions are subtle: version/minorversion, proto/address-family, mountproto/mountaddr, xprtsec transport support, fscache string ownership, and remount defaults must be kept consistent. Legacy binary parsing handles user pointers and historical structure versions, so bounds and compatibility checks are security-sensitive.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/fs_context.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/fscache.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/fscache.c

## Purpose

Connects the NFS client to fscache and netfs. It builds cache volume/cookie keys, manages per-inode cache cookies, enables/disables caching on file open/close, and adapts NFS pageio reads to netfs subrequests.

## Main Entry Points

- `nfs_fscache_get_super_cookie()` / `nfs_fscache_release_super_cookie()`: acquire and release per-superblock cache volumes.
- `nfs_fscache_init_inode()` / `nfs_fscache_clear_inode()`: acquire and release per-regular-file cache cookies.
- `nfs_fscache_open_file()` / `nfs_fscache_release_file()`: use/unuse cookies and invalidate cache on write-open.
- `nfs_netfs_read_folio()` / `nfs_netfs_readahead()`: enter netfs read paths when a cache cookie exists.
- `nfs_netfs_issue_read()`: split a netfs subrequest into NFS pageio folio reads.
- `nfs_netfs_initiate_read()` / `nfs_netfs_read_completion()`: reference and complete the shared netfs I/O state for NFS RPC completions.
- `nfs_netfs_ops`: netfs request operations exported to inode initialization.

## Control Flow And State

Superblock cache keys include NFS protocol version, minor version, server address, fsid, mount/server flags, I/O sizes, attribute cache timings, auth flavor, and optional fscache uniquifier. Inode cookies use the NFS filehandle as the index key plus auxiliary coherency data from mtime, ctime, and NFSv4 change attribute.

Netfs reads allocate `nfs_netfs_io_data` because one netfs subrequest may become multiple NFS RPCs. Each initiated NFS read increments the refcount; completions accumulate transferred byte counts or errors. The final put clamps the transferred length to the requested subrequest length, fills netfs completion state, and calls `netfs_read_subreq_terminated()` once.

## Dependencies

Depends on Linux fscache, netfs, xarray page iteration, NFS pageio read helpers, open contexts, inode versioning, fattr-derived coherency data, and declarations in `fscache.h`.

## Risks

Cache key construction must remain bounded and collision-resistant enough for NFS mount identity. Cache coherency depends on auxiliary data being updated before cookie invalidation/unuse. Netfs completion is refcount-sensitive: only the last NFS RPC may terminate the netfs subrequest, and overread clamping avoids netfs warnings for full-page NFS reads serving partial subrequests.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/fscache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/fscache.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/fscache.h

## Purpose

Defines the NFS fscache/netfs interface, auxiliary cache coherency data, netfs read aggregation state, and no-op fallbacks when `CONFIG_NFS_FSCACHE` is disabled.

## API Surface

- `struct nfs_fscache_inode_auxdata`: mtime, ctime, and NFSv4 change attribute used for cache coherency.
- `struct nfs_netfs_io_data`: refcounted bridge between one netfs subrequest and potentially many NFS RPC completions.
- `nfs_netfs_get()` / `nfs_netfs_put()`: manage the bridge lifetime and final netfs termination.
- Declarations for superblock cookie, inode cookie, open/release, folio read, readahead, and pageio/netfs completion helpers.
- `nfs_fscache_release_folio()`: waits for deprecated `PG_private_2` cache writeback when needed and notes page release.
- `nfs_fscache_update_auxdata()` / `nfs_fscache_invalidate()`: build coherency metadata and invalidate cookies.
- `nfs_server_fscache_state()` and pageio header/descriptor transfer helpers.
- Disabled-config stubs return no-cache behavior and keep callers simple.

## Dependencies

Includes Linux swap, NFS mount/filesystem headers, fscache, netfs request APIs, and inode versioning.

## Risks

The enabled and disabled branches must preserve identical caller semantics. `nfs_netfs_put()` owns final netfs completion and must not run early. Folio release behavior must avoid sleeping from reclaim contexts while still waiting for cache writes when safe.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/fscache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/getroot.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/getroot.c

## Purpose

Obtains and installs the root dentry for an NFS mount from the mount root filehandle.

## Main Entry Points

- `nfs_superblock_set_dummy_root()`: creates an invisible dummy superblock root dentry for the NFS superblock.
- `nfs_get_root()`: fetches root attributes, gets the root inode, obtains the dentry, applies LSM mount options, and stores `fc->root`.

## Control Flow And State

`nfs_get_root()` duplicates the mount source string for possible dentry fsdata, allocates labeled fattrs, calls the protocol `getroot()` operation, turns the returned filehandle/attributes into an inode with `nfs_fhget()`, and ensures the superblock has a dummy root. The actual mount root is acquired with `d_obtain_root()`, security hooks instantiate it, and the source name is attached to root dentry fsdata when safe.

For cloned submounts, the function verifies the root is a directory and clones security mount options from the parent superblock. For ordinary mounts, it applies parsed security options. It also disables NFS security-label capability if the LSM did not accept native labels.

## Dependencies

Depends on protocol `getroot`, `nfs_fhget()`, NFS fattr allocation/security label handling, VFS dentry helpers, LSM superblock/dentry hooks, and mount context clone data.

## Risks

The dummy root deliberately removes itself from the inode alias list to avoid later dcache splicing problems during unmount. Error paths must release fattrs, root dentries, and the duplicated source name correctly. Security-label capability must reflect the final LSM mount-option result.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/getroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/inode.c

## Purpose

Provides core NFS inode and superblock support: inode lookup/allocation, attribute caching and revalidation, setattr/getattr, open and lock contexts, page-cache invalidation, weak cache consistency updates, inode slab management, NFS workqueues, per-net setup, and NFS client module initialization.

## Main Entry Points

- `nfs_fhget()` / `nfs_ilookup()`: find or create inodes by filehandle, fileid, and type.
- `nfs_set_cache_invalid()` / `nfs_zap_caches()` / `nfs_clear_invalid_mapping()` / `nfs_revalidate_mapping()`: manage attribute and page-cache invalidation.
- `nfs_getattr()` / `nfs_setattr()` / `nfs_setattr_update_inode()`: VFS attribute operations.
- `__nfs_revalidate_inode()` / `nfs_revalidate_inode()` / `nfs_refresh_inode()` / `nfs_update_inode()`: fetch, compare, and update cached server attributes.
- `nfs_post_op_update_inode()` / `nfs_post_op_update_inode_force_wcc()`: update inode state after mutating operations.
- `alloc_nfs_open_context()` / `nfs_open()` / `nfs_file_set_open_context()` / `nfs_file_clear_open_context()`: file open context lifecycle.
- `nfs_get_lock_context()` / `nfs_put_lock_context()`: per-open lock context lifecycle.
- `nfs_alloc_inode()` / `nfs_free_inode()` and inode cache init/destroy: NFS inode slab lifecycle.
- `init_nfs_fs()` / `exit_nfs_fs()`: global module setup and teardown.

## Control Flow And State

`nfs_fhget()` uses `iget5_locked()` with filehandle-aware matching, initializes new inodes by type, assigns protocol-specific file/dir ops, handles mountpoint/referral automounts, sets initial attributes from fattrs, initializes fscache/netfs state, and refreshes existing inodes. Attribute validity is tracked through `NFS_I(inode)->cache_validity`, with delegations suppressing invalidation of attributes the client owns.

Revalidation flushes pNFS layoutcommit-sensitive state, gets fresh fattrs, refreshes the inode, clears ACL invalidation when needed, and applies security labels. `nfs_update_inode()` compares generation counters and NFSv4 change attributes, handles out-of-order replies, weak cache consistency pre/post data, size changes, writer/delegation races, directory cache invalidation, access/ACL/xattr invalidation, and adaptive attribute timeout growth.

Open contexts hold dentries, credentials, lock context lists, localio state, and close-to-open behavior. Lock contexts are keyed by the caller’s file table. Mapping invalidation serializes `NFS_INO_INVALIDATING` with wait-bit logic so one invalidator clears data while others observe consistent state.

Module initialization sets up keyring support, sysfs, per-net data, workqueues, proc entries, NFS page/read/write/direct caches, inode cache, and filesystem registration; teardown reverses those pieces.

## Dependencies

Depends on VFS inode/page-cache/stat/setattr APIs, NFS protocol operation tables, pNFS, delegation logic, fscache/netfs hooks, NFS access/ACL/xattr/security-label helpers, RPC stats/metrics, lockd-related mount semantics, per-network namespace infrastructure, sysfs/proc support, and NFS page/read/write/direct caches.

## Risks

Attribute coherency is the main complexity. The code must reconcile server attributes, client dirty data, delegations, pNFS layoutcommit, out-of-order RPC replies, and weak cache consistency without corrupting size/change state. Mapping invalidation uses memory barriers and bit locks; weakening those races stale page-cache data. Inode identity checks must detect fileid/type changes and mark stale inodes. Initialization and teardown have many staged resources and must unwind in the correct order.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/inode.c -->