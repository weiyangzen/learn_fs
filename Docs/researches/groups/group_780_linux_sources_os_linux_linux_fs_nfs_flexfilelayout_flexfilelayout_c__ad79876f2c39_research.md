# Group Research: group_780_linux_sources_os_linux_linux_fs_nfs_flexfilelayout_flexfilelayout_c__ad79876f2c39

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayout.c -->
# File Research: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayout.c

## Purpose
Implements the NFSv4 pNFS flexfile layout driver. It decodes flexfile layout segments, manages mirrors/stripes, routes read/write/commit I/O to data servers, records layout statistics and DS errors, prepares layoutreturn/layoutstats payloads, and registers the `LAYOUT_FLEX_FILES` layout driver.

## Main Responsibilities
- Allocate/free flexfile layout headers and segments.
- Decode layout opaque data: stripe unit, mirror count, DS stripe count, device IDs, efficiency, stateids, filehandles, UID/GID-derived DS credentials, layout flags, and stats report interval.
- Reuse identical mirrors across layout segments using deviceid and filehandle comparisons.
- Sort mirrors by aggregate efficiency.
- Select data servers for reads and writes, including striped DSS selection via `nfs4_ff_layout_calc_dss_id()`.
- Initialize pageio read/write operations and coalescing boundaries so striped I/O does not cross stripe units.
- Dispatch pNFS reads, writes, and commits through DS RPC clients or localio.
- Handle DS errors and decide whether to retry pNFS, fall back to the MDS, mark a layout for return, or treat errors as fatal.
- Track and encode layoutstats and layoutreturn error reports.
- Register/unregister the flexfile layout driver module.

## Key Data Flow
`ff_layout_alloc_lseg()` decodes a layoutget response into `struct nfs4_ff_layout_segment`, containing a flexible array of mirror pointers. Each mirror owns DSS entries with device IDs, filehandles, credentials, localio state, per-DS read/write statistics, and delayed `mirror_ds` resolution.

Read setup:
- `ff_layout_pg_init_read()` obtains or refreshes a read layout.
- `ff_layout_get_ds_for_read()` chooses the best available mirror/stripe.
- `ff_layout_read_pagelist()` prepares DS connection/client/credential/filehandle/stateid and calls `nfs_initiate_pgio()`.

Write setup:
- `ff_layout_pg_get_mirror_count_write()` exposes the mirror count to pageio.
- `ff_layout_pg_init_write()` prepares every mirror needed for mirrored writes.
- `ff_layout_write_pagelist()` dispatches each mirrored write and assigns a DS commit index.

Commit setup:
- Commit index is encoded as `mirror_idx * dss_count + dss_id`.
- `ff_layout_initiate_commit()` maps the commit index back to mirror/DSS, prepares the DS client, and starts `nfs_initiate_commit()`.

## Error and Recovery Behavior
`ff_layout_io_track_ds_error()` maps local/RPC errors into NFSv4 layout error statuses, records them with `ff_layout_track_ds_error()`, marks DS device IDs unreachable for NXIO-style failures, and often marks the layout for return.

`ff_layout_async_handle_error_v3()` and `_v4()` are protocol-specific recovery engines:
- NFSv4 session errors schedule session recovery.
- Delay/grace/jukebox conditions retry after delay.
- Layout-invalidating errors destroy or return layouts.
- Connection failures delete unavailable device IDs.
- `fatal_neterrors` can convert network unreachable cases into fatal I/O.

Fallback logic distinguishes:
- `NFS_IOHDR_RESEND_PNFS` for retrying another DS/mirror.
- `NFS_IOHDR_RESEND_MDS` for MDS fallback.
- `FF_FLAGS_NO_IO_THRU_MDS` and availability checks can force continued pNFS retry behavior.

## Layoutstats and Layoutreturn
Per-DSS read/write stats track requested/completed ops/bytes, not-delivered bytes, busy time, and aggregate completion time. `nfs4_ff_layoutstat_start_io()` triggers layoutstats reporting based on mirror/server interval or global `layoutstats_timer`.

`ff_layout_prepare_layoutreturn()` gathers up to `FF_LAYOUTRETURN_MAXERR` DS errors and up to `FF_LAYOUTSTATS_MAXDEV` stat entries, encodes them into a one-page opaque payload, and frees private data through `layoutreturn_ops`.

When NFSv4.2 is enabled, `ff_layout_send_layouterror()` sends collected DS errors through `nfs42_proc_layouterror()` in bounded batches.

## Important Types and Operations
- `flexfilelayout_type`: `struct pnfs_layoutdriver_type` registration for `LAYOUT_FLEX_FILES`.
- `ff_layout_pg_read_ops`, `ff_layout_pg_write_ops`: pageio operation tables.
- `ff_layout_commit_ops`: pNFS commit operation table.
- `ff_layout_read/write/commit_call_ops_v3/v4`: DS RPC call operation tables.
- `ff_layout_prepare_layoutstats()`: prepares `LAYOUTSTATS`.
- `ff_layout_cancel_io()`: cancels matching DS RPC tasks for a returned/invalid layout segment.

## Concurrency and Lifetime Notes
- Layout header and mirror lists are protected by inode `i_lock`.
- Mirror stats use `mirror->lock`.
- Mirror references use `refcount_t`; reused mirrors swap credentials and release superseded mirrors.
- Device ID nodes use pNFS device ID refcounting and RCU freeing.
- Credentials are RCU-published per DSS and dropped on mirror free.
- Layoutstats opaque data holds a mirror reference until encode/free completes.
- DS RPC cancellation matches task call ops and calldata against the layout segment.

## Research Notes
This file is the central flexfile pNFS implementation. Changes here affect pNFS correctness, MDS fallback semantics, DS error propagation, mirrored write consistency, layoutreturn behavior, and NFSv4.2 layoutstats/layout error reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayout.h -->
# File Research: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayout.h

## Purpose
Defines the core data structures, constants, inline helpers, and cross-file function declarations for the NFSv4 flexfile layout driver.

## Key Definitions
- Layout flags:
  - `FF_FLAGS_NO_LAYOUTCOMMIT`
  - `FF_FLAGS_NO_IO_THRU_MDS`
  - `FF_FLAGS_NO_READ_IO`
- Safety limits:
  - `NFS4_FLEXFILE_LAYOUT_MAX_MIRROR_CNT`
  - `NFS4_FLEXFILE_LAYOUT_MAX_STRIPE_CNT`
- Layoutstats limits:
  - `FF_LAYOUTSTATS_REPORT_INTERVAL`
  - `FF_LAYOUTSTATS_MAXDEV`

## Core Structures
- `struct nfs4_ff_ds_version`: DS NFS version/minor version, rsize/wsize, coupling mode.
- `struct nfs4_ff_layout_ds`: deviceid node plus DS version table and `nfs4_pnfs_ds`.
- `struct nfs4_ff_layout_ds_err`: layout DS error record for layoutreturn/layouterror.
- `struct nfs4_ff_io_stat`, `struct nfs4_ff_busy_timer`, `struct nfs4_ff_layoutstat`: per-DSS layoutstats accounting.
- `struct nfs4_ff_layout_ds_stripe`: one data-server stripe, including device ID, filehandle versions, stateid, DS credentials, localio state, stats, and resolved DS pointer.
- `struct nfs4_ff_layout_mirror`: mirror containing DSS stripes, refcount, stats lock, flags, and report interval.
- `struct nfs4_ff_layout_segment`: pNFS layout segment with stripe unit, flags, and flexible mirror array.
- `struct nfs4_flexfile_layout`: per-inode layout header with commit info, mirror registry, DS error list, and last stats report time.
- `struct nfs4_flexfile_layoutreturn_args`: private layoutreturn payload state.

## Helper Semantics
- Container helpers convert generic pNFS structures into flexfile-specific structures.
- `FF_LAYOUT_COMP()` safely indexes a mirror by layout segment and mirror index.
- `FF_LAYOUT_DEVID_NODE()` resolves a DSS deviceid node if the DS is available.
- `ff_layout_no_fallback_to_mds()` and `ff_layout_no_read_on_rw()` interpret server layout flags.
- `nfs4_ff_layout_calc_dss_id()` maps an offset to a stripe index using stripe unit and DSS count.

## Cross-File API
Declares the flexfile deviceid and error helpers implemented in `flexfilelayoutdev.c`, plus DS selection/client/credential helpers consumed by `flexfilelayout.c`.

## Research Notes
This header is the contract between the flexfile layout core and device/error support code. The flexible array and refcounted mirror structures are especially important for memory layout and lifetime correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayoutdev.c -->
# File Research: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayoutdev.c

## Purpose
Implements flexfile device ID allocation, DS connection preparation, DS credential selection, DS error list management, and availability/fallback decisions.

## Device ID Handling
`nfs4_ff_alloc_deviceid_node()` decodes a `GETDEVICEINFO` opaque payload:
- Multipath DS address count and address list.
- DS version count.
- Supported DS NFS versions: NFSv3, NFSv4.0, NFSv4.1, NFSv4.2.
- DS rsize/wsize, clamped to `NFS_MAX_FILE_IO_SIZE`.
- Tight-coupling flag.

It builds an `nfs4_ff_layout_ds`, adds/looks up a shared `nfs4_pnfs_ds`, and frees decoded address records after the DS object takes ownership/reference as needed.

`nfs4_ff_layout_free_deviceid()` releases the pNFS DS, version table, and RCU-frees the flexfile DS wrapper.

## DS Error Tracking
`ff_layout_track_ds_error()` creates error records keyed by:
- Operation number.
- NFS status.
- Stateid.
- Deviceid.
- Byte range.

The insertion path sorts and merges overlapping or contiguous matching errors. Error records live on `nfs4_flexfile_layout.error_list` under inode `i_lock`.

`ff_layout_encode_ds_ioerr()` emits the layoutreturn XDR form of these errors. `ff_layout_fetch_ds_ioerr()` moves intersecting errors out of the layout list, with overflow discard behavior when max count is reached.

## DS Preparation
`ff_layout_init_mirror_ds()` lazily resolves a DSS deviceid via `nfs4_find_get_deviceid()` and publishes it with `cmpxchg()` to avoid duplicate initialization races.

`nfs4_ff_layout_prepare_ds()`:
- Resolves the DS deviceid.
- Connects the DS if needed using module parameters `dataserver_timeo` and `dataserver_retrans`.
- Starts async localio probing.
- Clamps DS rsize/wsize to RPC max payload.
- On failure, records NXIO, sends layouterror if possible, and may mark the layout for return.

## Credentials and RPC Clients
`ff_layout_get_ds_cred()` returns per-DSS read/write credentials for loosely coupled DSes; tightly coupled DSes use the MDS credential.

`nfs4_ff_find_or_create_ds_client()` returns the v3 DS client directly or creates/finds an NFSv4 DS client with the MDS auth flavor.

## Availability/Fallback Decisions
Read availability needs at least one usable mirror/DSS. RW availability requires all mirrors/DSS entries to be usable. These checks feed:
- `ff_layout_avoid_mds_available_ds()`
- `ff_layout_avoid_read_on_rw()`

## Research Notes
This file is the bridge between layout metadata and usable data-server connections. It owns the error aggregation logic consumed by layoutreturn/layouterror and strongly influences whether flexfile I/O retries pNFS or falls back to the MDS.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayoutdev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/fs_context.c -->
# File Research: sources/os/linux/linux/fs/nfs/fs_context.c

## Purpose
Implements NFS mount/fs_context handling for the new mount API and legacy binary mount data. It parses options, validates transport/version/security settings, prepares NFS fs contexts, and registers `nfs`/`nfs4` filesystem types.

## Mount Parameters
Defines the NFS parameter table for options such as:
- Version: `v2`, `v3`, `v4`, `vers=`, `nfsvers=`, `minorversion=`.
- Transport: `proto=`, `tcp`, `udp`, `rdma`, `xprtsec=`.
- TLS keys: `cert_serial`, `privkey_serial`.
- Cache/consistency: `ac`, `noac`, `cto`, `lookupcache`, `rdirplus`, `fsc`.
- Locking: `lock`, `local_lock`.
- Retry behavior: `soft`, `softerr`, `hard`, `softreval`, `timeo`, `retrans`, `fatal_neterrors`.
- Mount protocol options for NFSv2/v3.
- Multi-connection: `nconnect`, `max_connect`.
- Security flavors: `sec=`.

## Parsing and Validation
`nfs_fs_context_parse_param()` uses `fs_parse()` and updates `struct nfs_fs_context`. It handles booleans, numeric bounds, address parsing via `rpc_pton()`, string ownership transfer, transport tokens, security flavor lists, and sloppy option behavior.

`nfs_validate_transport_protocol()` rejects unsupported UDP cases, defaults unknown transport to TCP, and maps TCP plus `xprtsec` into `XPRT_TRANSPORT_TCP_TLS`.

`nfs_parse_source()` splits `fc->source` into hostname and export path, including bracketed IPv6 hostnames.

`nfs_fs_context_validate()` checks:
- Source presence.
- Version/minor version compatibility.
- Migration option constraints.
- Address family consistency with `proto=`/`mountproto=`.
- Server address validity.
- Transport validity.
- NFSv4 availability.
- Port defaults.
- Source parsing limits.
- NFS protocol module lookup and `fc->fs_type` correction.

## Legacy Mount Data
`nfs23_parse_monolithic()` converts old `struct nfs_mount_data` for NFSv2/v3, including legacy filehandles, flags, timeouts, lock behavior, SELinux context compatibility, and transport validation.

When NFSv4 is enabled, `nfs4_parse_monolithic()` handles `struct nfs4_mount_data`, including compat syscall conversion, user pointer copies, auth flavor, host/export/client strings, and protocol validation.

## Context Lifecycle
`nfs_init_fs_context()` allocates defaults for fresh mounts or copies current server state for reconfigure/remount. It allocates `mntfh`, sets default timeouts/cache values, selects TCP by default, initializes TLS policy fields, and attaches fs context ops.

`nfs_fs_context_dup()` deep-copies resource-owning fields where needed. `nfs_fs_context_free()` releases server refs, module refs, strings, fhandles, clone fattrs, and context memory.

## Filesystem Registration
Exports:
- `nfs_fs_type`
- `nfs4_fs_type` when NFSv4 is enabled

Both use `nfs_init_fs_context`, `nfs_fs_parameters`, and `nfs_kill_super`.

## Research Notes
This file is the main user/kernel boundary for NFS mounts. Option parsing here directly controls transport security, version selection, cache semantics, locking behavior, fallback policy, and protocol module handoff.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/fs_context.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/fscache.c -->
# File Research: sources/os/linux/linux/fs/nfs/fscache.c

## Purpose
Implements NFS integration with FS-Cache and the netfs read helper layer.

## Superblock Cache Volume
`nfs_fscache_get_super_cookie()` builds a cache volume key from:
- NFS protocol version/minor version.
- Server address and port.
- FSID.
- Superblock flags.
- NFS server flags.
- rsize/wsize.
- attribute cache timers.
- auth flavor.
- optional `fsc=` uniquifier.

It acquires an FS-Cache volume with `fscache_acquire_volume()` and stores it in `nfs_server.fscache`. `nfs_fscache_release_super_cookie()` relinquishes the volume and frees the uniquifier.

## Inode Cache Cookies
`nfs_fscache_init_inode()` creates filehandle-indexed cookies for regular files when the superblock has fscache enabled. It uses auxiliary coherency data from mtime, ctime, and NFSv4 change attribute, then marks the mapping for release callbacks.

`nfs_fscache_clear_inode()` relinquishes the per-inode cookie.

## Open/Close Behavior
`nfs_fscache_open_file()` uses a cookie on open. For write opens, it invalidates the cache using current auxiliary data and file size.

`nfs_fscache_release_file()` unuses the cookie and supplies updated auxiliary data and size.

## Netfs Read Integration
`nfs_netfs_read_folio()` and `nfs_netfs_readahead()` call into netfs only if the inode has a cache cookie; otherwise they return `-ENOBUFS`.

`nfs_netfs_issue_read()` turns one netfs subrequest into NFS pageio reads. It allocates `nfs_netfs_io_data`, initializes an NFS read pageio descriptor, walks the mapping xarray over requested pages, adds folios to NFS read I/O, completes pageio, and terminates the netfs subrequest through reference-counted completion.

## Completion Semantics
`nfs_netfs_io_data.refcount` ensures `netfs_read_subreq_terminated()` is called exactly once even if one netfs subrequest maps to multiple NFS RPC completions. Completion records transferred bytes or error, handles EOF tail clearing, and caps transferred length in the header inline helper.

## Netfs Ops
Exports `nfs_netfs_ops` with:
- `.init_request`
- `.free_request`
- `.issue_read`

`init_request` stores an NFS open context, assigns a debug id, uses deprecated PG_private_2 cache-write tracking, and sets max subrequest length from NFS rsize.

## Research Notes
This file is the active implementation behind the `CONFIG_NFS_FSCACHE` API declared in `fscache.h`. It links NFS pageio and FS-Cache/netfs while preserving NFS-specific open context and completion behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/fscache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/fscache.h -->
# File Research: sources/os/linux/linux/fs/nfs/fscache.h

## Purpose
Declares and conditionally stubs NFS FS-Cache/netfs integration.

## Enabled Configuration
When `CONFIG_NFS_FSCACHE` is enabled:
- Defines `struct nfs_fscache_inode_auxdata` for cache coherency metadata.
- Defines `struct nfs_netfs_io_data` for coordinating split NFS RPC completions for one netfs subrequest.
- Provides inline refcount helpers `nfs_netfs_get()` and `nfs_netfs_put()`.
- Declares fscache and netfs functions implemented in `fscache.c`.
- Implements helper inlines for folio release, auxiliary data generation, cache invalidation, readable server cache state, and pageio/netfs pointer transfer.

## Disabled Configuration
When `CONFIG_NFS_FSCACHE` is disabled, all integration points become no-op or negative stubs:
- Inode init/clear/open/release do nothing.
- Netfs reads return `-ENOBUFS`.
- Folio unlock helper returns that NFS should unlock.
- Server fscache state reports `"no "`.

## Important Details
`nfs_fscache_release_folio()` waits for deprecated private-2 folio state unless reclaim context forbids sleeping, then notifies fscache of page release.

`nfs_fscache_update_auxdata()` uses inode mtime/ctime and NFSv4 raw i_version as coherency data.

`nfs_fscache_invalidate()` updates auxdata and calls `fscache_invalidate()` with inode size and invalidation flags.

`nfs_netfs_put()` caps final transferred length to the netfs subrequest length to avoid netfs overread warnings when NFS reads full pages for partial-page requests.

## Research Notes
This header cleanly isolates optional FS-Cache behavior. Call sites can invoke fscache/netfs hooks unconditionally while build-time configuration determines whether they are active or stubs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/fscache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/getroot.c -->
# File Research: sources/os/linux/linux/fs/nfs/getroot.c

## Purpose
Gets and installs the root dentry for an NFS mount from the mount root filehandle.

## Main Flow
`nfs_get_root()`:
- Duplicates `fc->source` for possible storage in root dentry `d_fsdata`.
- Allocates an NFS fattr with security label support.
- Calls protocol `getroot()` using the mount filehandle.
- Converts the root filehandle/fattr into an inode with `nfs_fhget()`.
- Obtains a root dentry via `d_obtain_root()`.
- Instantiates security state on the dentry.
- Stores the mount source name in root `d_fsdata` when appropriate.
- Sets `s->s_root` and `fc->root`.
- Applies or clones LSM mount options.
- Clears `NFS_CAP_SECURITY_LABEL` if LSM mount options do not preserve native labels.
- Applies inode security label data with `nfs_setsecurity()`.

## Clone/Reconfigure Behavior
When cloning from an existing superblock, it verifies the root inode is an NFS directory and clones security mount options from the parent superblock. It also copies `has_sec_mnt_opts` from the clone source server.

## Error Handling
Failure paths release fattrs, source-name storage, and root dentries as needed. Errors are reported through `nfs_errorf()` with mount-context-visible messages.

## Research Notes
This is the root installation point after mount context and server setup. It ties together protocol root getattr, inode creation, dentry setup, security labels, and superblock root assignment.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/getroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/inode.c -->
# File Research: sources/os/linux/linux/fs/nfs/inode.c

## Purpose
Implements NFS inode and superblock support: inode cache allocation, filehandle-based inode lookup, attribute cache validation/update, open and lock contexts, fscache hooks, revalidation, data-cache invalidation, workqueues, per-net initialization, and module init/exit.

## Inode Lifecycle
- `nfs_alloc_inode()` allocates `struct nfs_inode` from `nfs_inode_cachep`, initializes NFSv4/netfs fields, and returns embedded VFS inode.
- `nfs_free_inode()` frees out-of-order state and the slab object.
- `nfs_clear_inode()` clears ACL/access/fscache state and asserts no writebacks/open files.
- `nfs_evict_inode()` truncates pages, clears the inode, and calls NFS cleanup.
- Slab cache is created/destroyed by `nfs_init_inodecache()` and `nfs_destroy_inodecache()`.

## Filehandle-Based Inode Lookup
`nfs_fhget()` is the central inode acquisition path:
- Uses filehandle plus fileid/type matching, not just inode number.
- Handles mounted-on fileid.
- Initializes new inodes according to type: regular, directory, symlink, special.
- Sets operation tables from protocol ops.
- Initializes pagecache ops, regular-file commit state, directory state, mountpoint/referral automount behavior, timestamps, ownership, blocks, cache validity flags, security labels, and fscache.
- Existing inodes are refreshed through `nfs_refresh_inode()`.

`nfs_ilookup()` performs lookup without allocation.

## Attribute Cache and Invalidation
The file maintains detailed cache-validity flags:
- Attribute fields: mode, owner/group, nlink, size, blocks, atime/mtime/ctime/btime, change attr.
- Data/access/ACL/xattr invalidation.
- Revalidation forcing and stale marking.

`nfs_set_cache_invalid()` respects delegated attributes, invalidates fscache for data changes, uses release/acquire memory ordering against mapping invalidation, and clears out-of-order tracking when appropriate.

`nfs_zap_caches()`/`nfs_zap_mapping()` invalidate local metadata/data caches.

## Revalidation and Mapping Invalidation
`__nfs_revalidate_inode()` syncs pNFS layout state for regular files, fetches attributes through protocol `getattr`, handles softreval timeouts, marks stale inodes, refreshes attributes, clears ACL invalidation, and updates security labels.

`nfs_revalidate_mapping()` revalidates inode metadata when needed and calls `nfs_clear_invalid_mapping()`.

`nfs_clear_invalid_mapping()` serializes pagecache invalidation with the `NFS_INO_INVALIDATING` bit, clears `NFS_INO_INVALID_DATA` under lock before invalidating, syncs regular mappings, invalidates pages, and wakes waiters.

## Attribute Update Ordering
A global attribute generation counter prevents older RPC replies from overwriting newer inode state. Key helpers:
- `nfs_fattr_init()`
- `nfs_fattr_set_barrier()`
- `nfs_inode_attrs_cmp*()`
- `nfs_refresh_inode_locked()`

The code also tracks out-of-order change-attribute gaps (`nfsi->ooo`) so stale/interleaved replies do not corrupt cache state.

## Metadata Updates
`nfs_setattr()` handles VFS setattr:
- Blocks direct I/O for regular files.
- Validates truncates.
- Optimizes delegated atime/mtime updates.
- Flushes dirty data before server setattr.
- Calls protocol `setattr()`, truncates last folio if size changed, and refreshes attributes.

`nfs_setattr_update_inode()` and post-op update helpers combine local updates, weak cache consistency data, invalidation flags, and full inode refresh.

`nfs_update_inode()` is the main attribute application engine. It validates fileid/type, updates fsid, delegation-adjusted attrs, weak cache consistency, pNFS layoutcommit interaction, change attr, timestamps, size, mode, owner/group, nlink, blocks, attr timeout backoff, and invalidation flags. On identity/type mismatch it marks the inode stale.

## Open and Lock Contexts
- `alloc_nfs_open_context()` creates per-open context with dentry, creds, mode, lock context, localio state, and superblock active ref.
- `nfs_file_set_open_context()` attaches context to a file and inode open list.
- `nfs_file_clear_open_context()` clears file private data, invalidates pages after write errors, and drops the context synchronously.
- `nfs_find_open_context()` finds matching open context by credential and mode.
- `nfs_get_lock_context()` and `nfs_put_lock_context()` manage per-open lock-owner contexts with RCU and inode locking.

`nfs_close_context()` revalidates change/size on synchronous write close when close-to-open consistency requires it.

## Stat and File Attributes
`nfs_getattr()` implements statx behavior:
- Honors `AT_STATX_DONT_SYNC` and `AT_STATX_FORCE_SYNC`.
- Flushes writes before ctime/mtime/change-cookie queries.
- Avoids atime revalidation under noatime/nodiratime.
- Revalidates only requested stale attributes.
- Fills stat fields, NFS-compatible inode number, change cookie, btime, and DIO alignment values.

`nfs_fileattr_get()` reports case-insensitive/case-nonpreserving capabilities as file attributes.

## Global Initialization
`init_nfs_fs()` initializes:
- Optional keyring.
- NFS sysfs.
- Per-net subsystem.
- `nfsiod` and optional `nfslocaliod` workqueues.
- procfs support.
- NFS page/read/write/direct caches.
- Inode cache.
- NFS filesystem registration.

`exit_nfs_fs()` tears these down in reverse. The module exports `enable_ino64` to control user-visible 64-bit inode numbers.

## Research Notes
This is foundational NFS client infrastructure. It coordinates VFS inode identity, cache coherency, fscache, pNFS layoutcommit interactions, open context lifetime, workqueue/module setup, and stat behavior. Bugs here can affect all NFS protocol versions and layout drivers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/inode.c -->