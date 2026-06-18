# Research Report: subset-b-005690

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayout.c -->
## sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayout.c

Purpose: implements the NFSv4 pNFS flexfile layout driver. It registers `LAYOUT_FLEX_FILES`, decodes layout segments returned by the metadata server, chooses data servers for read/write/commit, sends asynchronous data-server RPCs, tracks per-DS errors, emits `LAYOUTERROR`, `LAYOUTRETURN`, and `LAYOUTSTATS` opaque payloads, and falls back to MDS I/O when policy and availability allow.

Important APIs and types: the exported surface is the `pnfs_layoutdriver_type flexfilelayout_type`, with callbacks for layout header/lseg allocation, pageio read/write ops, commit ops, device-id allocation, layoutreturn/stat preparation, and cancellation. Core in-file helpers include `ff_layout_alloc_layout_hdr`, `ff_layout_alloc_lseg`, `ff_layout_free_lseg`, `ff_layout_pg_init_read`, `ff_layout_pg_init_write`, `ff_layout_read_pagelist`, `ff_layout_write_pagelist`, `ff_layout_initiate_commit`, `ff_layout_prepare_layoutreturn`, and `ff_layout_prepare_layoutstats`. It works on `struct nfs4_flexfile_layout`, `struct nfs4_ff_layout_segment`, `struct nfs4_ff_layout_mirror`, and `struct nfs4_ff_layout_ds_stripe` from the companion header.

Control flow: module init registers the layout driver. On `LAYOUTGET`, `ff_layout_alloc_lseg` decodes stripe unit, mirror count, per-mirror stripe count, device ids, efficiency, DS stateids, filehandles, and UID/GID strings from XDR. Mirrors are deduplicated against the layout header's mirror list by device id and filehandle and then sorted by efficiency. Pageio initialization obtains or validates a layout segment, maps offsets to stripe ids, prepares DS connections, and sets per-mirror block sizes. Read dispatch selects the best reachable mirror and may retry another mirror before MDS fallback. Write dispatch targets every mirror required by the RW layout. Commit dispatch maps `ds_commit_index` back to mirror/stripe and sends COMMIT to the selected DS. Async callbacks share common v3/v4 error handlers that convert RPC/NFS status into pNFS retry, MDS retry, fatal I/O, device-id deletion, or session recovery.

State and persistence behavior: state is kernel-resident. The layout header owns `commit_info`, `mirrors`, `error_list`, and `last_report_time`. Segments own an array of mirror references and stripe parameters. Mirrors carry refcounts, RCU credentials, DS filehandles/stateids, localio handles, availability-derived flags, and read/write layoutstat counters. Write and commit completion set layoutcommit state unless the layout flags suppress it. DS errors are merged by op/status/stateid/deviceid/range and later consumed by `LAYOUTERROR` or `LAYOUTRETURN`.

Dependencies and integration points: depends heavily on NFS pNFS core (`pnfs_update_layout`, generic pageio and commit helpers), SunRPC task/call ops, NFSv3/v4 client ops, NFSv4 session recovery, NFSv4.2 layoutstats/layout-error support, tracepoints, localio, deviceid cache operations implemented in `flexfilelayoutdev.c`, and NFS inode/writeback helpers. It integrates with mount/runtime policy through server flags such as soft/softerr and flexfile flags such as no-MDS fallback and no read-on-RW.

Risks: the XDR decoder must reject malformed mirror/stripe counts and missing fields without leaking partially built mirrors or credentials. Retry loops with `NO_IO_THRU_MDS` can sleep and retry until DS availability changes, so soft-mount retrans bounds matter. RCU credential swapping during mirror deduplication is subtle. Error handling differs between v3 and v4 and can delete device ids or destroy layouts, so regressions can cause excessive MDS fallback, infinite pNFS retry, or lost layoutcommit. Layoutstats and busy-time accounting are protected by mirror locks but are shared with layoutreturn/stat encoding paths.

Test signals: exercise pNFS flexfile reads, mirrored writes, unstable write plus COMMIT, DS failover, DS connection refusal, NFSv4 session reset errors, `NFS4ERR_DELAY/GRACE`, no-MDS-fallback layouts, read-on-RW avoidance, localio paths, layoutreturn error payload generation, and NFSv4.2 layoutstats emission. Tracepoints such as `trace_nfs4_pnfs_read/write`, `trace_ff_layout_*_error`, and MDS fallback tracepoints are useful behavioral evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayout.h -->
## sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayout.h

Purpose: defines the shared data model and helper accessors for the NFSv4 flexfile pNFS layout driver. It is the contract between the main layout driver and device-id/DS helper code.

Important APIs and types: defines layout flags `FF_FLAGS_NO_LAYOUTCOMMIT`, `FF_FLAGS_NO_IO_THRU_MDS`, and `FF_FLAGS_NO_READ_IO`; mirror and stripe caps; layoutstats constants; `struct nfs4_ff_ds_version`; `struct nfs4_ff_layout_ds`; `struct nfs4_ff_layout_ds_err`; `struct nfs4_ff_io_stat`; `struct nfs4_ff_layoutstat`; `struct nfs4_ff_layout_ds_stripe`; `struct nfs4_ff_layout_mirror`; `struct nfs4_ff_layout_segment`; `struct nfs4_flexfile_layout`; and `struct nfs4_flexfile_layoutreturn_args`. Inline helpers translate generic pNFS objects to flexfile containers and compute stripe ids.

Control flow: the header itself has no active control flow, but its accessors shape driver behavior. `FF_LAYOUT_FROM_HDR`, `FF_LAYOUT_LSEG`, and `FF_LAYOUT_MIRROR_DS` are container conversions. `FF_LAYOUT_COMP` and `FF_LAYOUT_DEVID_NODE` safely select mirror/device nodes. `nfs4_ff_layout_calc_dss_id` maps a file offset through stripe unit and stripe count to the selected DS stripe. Flag helpers decide whether MDS fallback and reads on RW layouts are allowed.

State and persistence behavior: all structures are in-memory runtime state. Device ids are chained through the global pNFS deviceid cache. Mirrors are refcounted and linked on the layout header. DS errors persist until fetched for layout error/return reporting. Credentials are RCU pointers in each stripe. Layoutstats counters and busy timers accumulate until reported or encoded.

Dependencies and integration points: includes Linux refcounting and the NFS pNFS header. It declares functions implemented by `flexfilelayout.c` and `flexfilelayoutdev.c` for device-id allocation/free, DS preparation, DS client selection, credentials, error tracking/encoding/fetching, filehandle/stateid selection, and fallback policy.

Risks: structure invariants matter: all mirrors in a segment are expected to have a valid `dss_count`, `mirror_array_cnt` must not exceed the configured cap, `mirror_ds` may be NULL or an ERR_PTR during connection setup, and RCU credential pointers require paired refcount handling. `nfs4_ff_layout_ds_version` assumes `mirror_ds` and at least one version are valid, so callers must prepare/check DS state first.

Test signals: compile coverage with pNFS flexfile enabled, KASAN/lockdep/RCU checks during layout allocation/free, striped offset tests for `nfs4_ff_layout_calc_dss_id`, DS unavailable paths that use `FF_LAYOUT_DEVID_NODE`, and layout flag tests for fallback/read selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayoutdev.c -->
## sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayoutdev.c

Purpose: owns flexfile device-id decoding, DS connection preparation, DS error aggregation, DS credential selection, DS client selection, and availability policy helpers for the flexfile layout driver.

Important APIs and functions: exported helpers include `nfs4_ff_alloc_deviceid_node`, `nfs4_ff_layout_put_deviceid`, `nfs4_ff_layout_free_deviceid`, `nfs4_ff_layout_prepare_ds`, `nfs4_ff_find_or_create_ds_client`, `ff_layout_get_ds_cred`, `ff_layout_track_ds_error`, `ff_layout_encode_ds_ioerr`, `ff_layout_fetch_ds_ioerr`, `ff_layout_free_ds_ioerr`, `nfs4_ff_layout_select_ds_fh`, `nfs4_ff_layout_select_ds_stateid`, `ff_layout_avoid_mds_available_ds`, and `ff_layout_avoid_read_on_rw`. Module parameters tune data-server timeout and retransmission behavior.

Control flow: device-id allocation builds an XDR stream over the opaque GETDEVICEINFO pages, decodes multipath DS addresses, decodes a version list, validates supported NFS versions, clamps DS rsize/wsize, and inserts/reuses an `nfs4_pnfs_ds` address set. DS preparation lazily resolves a device id into a flexfile DS node, connects the DS client if needed, probes localio, clamps sizes to RPC payload limits, and on failure records `NFS4ERR_NXIO`, sends layout error, and may mark the layout for return. Error tracking allocates `nfs4_ff_layout_ds_err`, sorts/merges by op/status/stateid/deviceid/range, and later moves matching records to layoutreturn or layouterror consumers.

State and persistence behavior: decoded DS versions and DS address references live under `struct nfs4_ff_layout_ds` until the deviceid node is freed. `mirror->dss[dss_id].mirror_ds` is initialized once using `cmpxchg`, allowing races to converge without duplicate retained references. DS error records live on `nfs4_flexfile_layout.error_list` under inode lock and are consumed/destructively moved when fetched.

Dependencies and integration points: uses NFS pNFS deviceid cache (`nfs4_find_get_deviceid`, `nfs4_put_deviceid_node`, `nfs4_pnfs_ds_add/connect/put`), SunRPC payload sizing, NFS localio probing, XDR decode helpers, and the flexfile layout header. It is called by pageio setup, read/write/commit dispatch, layoutreturn encoding, and fallback decisions in `flexfilelayout.c`.

Risks: malformed device opaque data can leak address/version allocations if cleanup paths regress. Unsupported DS version filtering currently permits NFSv3 and NFSv4 minor versions below 3; future protocol changes require care. `ff_layout_prepare_ds` records errors and layoutreturn side effects during connection setup, so transient connection failures can affect global layout state. Read availability only needs one usable DS, while RW availability needs all mirrors, which must remain consistent with write mirroring semantics.

Test signals: GETDEVICEINFO decode with IPv4/IPv6 multipath and multiple versions, unsupported version rejection, DS connect success/failure, localio probe fallback, merged overlapping DS errors, `LAYOUTERROR` status encoding, no-MDS-fallback read/write behavior, and module parameter effects on DS RPC timeout/retransmission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayoutdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/fs_context.c -->
## sources/distributed-fs/ceph-client/fs/nfs/fs_context.c

Purpose: implements the Linux mount API plumbing for NFS and NFSv4. It parses text and legacy binary mount options into `struct nfs_fs_context`, validates protocol/address/security combinations, selects the protocol module and filesystem type, creates the NFS superblock tree, duplicates/free contexts, and declares `nfs`/`nfs4` filesystem types.

Important APIs and functions: key parser data includes `enum nfs_param`, `nfs_fs_parameters`, version/protocol/security/xprtsec lookup tables, and readdirplus/write/local-lock/fatal-neterror enums. Main functions are `nfs_fs_context_parse_param`, `nfs_parse_source`, `nfs23_parse_monolithic`, `nfs4_parse_monolithic`, `nfs_fs_context_parse_monolithic`, `nfs_fs_context_validate`, `nfs_get_tree`, `nfs_fs_context_dup`, `nfs_fs_context_free`, and `nfs_init_fs_context`. Public filesystem objects are `nfs_fs_type` and `nfs4_fs_type`.

Control flow: `nfs_init_fs_context` allocates defaults or seeds a remount context from the existing server. The VFS invokes `.parse_param` for text options; the large switch updates flags, sizes, timeouts, address strings, auth flavors, TLS key serials, cache options, protocol family selectors, lock/write/readdirplus policy, and sloppy handling. Legacy `sys_mount` data is translated by `.parse_monolithic` into the same context. Before mounting, validation checks source presence, minor-version rules, migration constraints, address/protocol-family consistency, UDP/xprtsec legality, default ports, source `host:path` parsing, NFS version module availability, and fs_type correction. `nfs_get_tree` then calls the version-specific `try_get_tree` unless marked internal.

State and persistence behavior: state is per-fs_context until superblock creation. It owns allocated strings for source-derived hostname/export path, client/mount host strings, `fscache_uniq`, mount filehandle, optional clone fattr, selected module reference, and transport security fields. Remount contexts copy current server settings and network namespace. Free and dup paths must maintain module refs and deep-copy or clear owned pointers.

Dependencies and integration points: integrates with Linux `fs_context`, `fs_parser`, SunRPC transports and address parsing, TLS handshake key verification, NFS version module registry, NFS superblock creation, NFS reconfigure, and optional NFSv4 support. It controls options consumed later by `fscache.c`, inode behavior, transport setup, mount daemon use for v2/v3, and security mount option setup in root acquisition.

Risks: the parser has many interacting flags, so regressions can silently change mount semantics. Address-family validation must match `proto=` and `mountproto=` choices. TLS key serial verification depends on `CONFIG_KEYS`. Legacy binary mount parsing includes compatibility and SELinux context handling. Duplicating contexts intentionally clears pointer fields after `kmemdup`; missing a pointer would cause double-free or stale reference. UDP support is conditional and always invalid for NFSv4.

Test signals: text mounts across v2/v3/v4/v4.1/v4.2, IPv4/IPv6 bracketed sources, `proto=`/`mountproto=` mismatch rejection, `xprtsec=tls/mtls` with TCP and non-TCP transports, `fsc` and `nofsc`, `lookupcache`, `local_lock`, `rdirplus`, `nconnect`/`max_connect` bounds, legacy binary v2/v3/v4 mount data, remount/reconfigure, and module autoload/version-unavailable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/fs_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/fscache.c -->
## sources/distributed-fs/ceph-client/fs/nfs/fscache.c

Purpose: connects the NFS client to the Linux fscache/netfs caching infrastructure. It creates per-superblock cache volumes, per-inode cookies, manages cache use on open/release, and implements netfs read issue/completion glue over NFS pageio.

Important APIs and functions: cache volume/key routines include `nfs_fscache_get_super_cookie`, `nfs_fscache_release_super_cookie`, `nfs_fscache_get_client_key`, and `nfs_append_int`. Inode/file routines are `nfs_fscache_init_inode`, `nfs_fscache_clear_inode`, `nfs_fscache_open_file`, and `nfs_fscache_release_file`. Netfs integration includes `nfs_netfs_read_folio`, `nfs_netfs_readahead`, `nfs_netfs_init_request`, `nfs_netfs_free_request`, `nfs_netfs_issue_read`, `nfs_netfs_initiate_read`, `nfs_netfs_folio_unlock`, `nfs_netfs_read_completion`, and `const struct netfs_request_ops nfs_netfs_ops`.

Control flow: a mounted NFS server with fscache enabled builds a volume key from NFS version, address, fsid, mount/server flags, sizes, attribute timers, auth flavor, and optional uniquifier. Regular inode initialization binds a filehandle-indexed cookie with auxiliary coherency data. File open calls use the cookie and invalidate on write opens. Netfs read requests retain the NFS open context, create an NFS pageio descriptor, add folios from the requested xarray range, complete pageio, and use a per-subrequest refcount so only the last split RPC terminates the netfs subrequest.

State and persistence behavior: fscache volume and cookie state persists in the local cache backend, keyed by generated strings and filehandles. Auxiliary coherency data stores mtime, ctime, and NFSv4 change attribute. Runtime state includes `netfs_inode(inode)->cache`, `nfss->fscache`, `nfss->fscache_uniq`, and temporary `nfs_netfs_io_data` objects. Cache invalidation updates auxdata and file size before calling fscache.

Dependencies and integration points: depends on fscache, netfs, NFS pageio/read completion, NFS open contexts from `inode.c`, NFS mount/server settings from `fs_context.c`, and trace/iostat infrastructure. The header provides no-op stubs when `CONFIG_NFS_FSCACHE` is disabled, so callers can remain unconditional.

Risks: volume key construction has a fixed maximum; overflow falls through to no volume without surfacing most errors. The NFS pageio layer may split one netfs request into several RPC completions, making the refcount/termination contract critical. Cache coherency depends on correct auxdata updates and invalidation during writes/truncation. `PG_private_2` use is marked deprecated but still participates in folio release/unlock behavior.

Test signals: fscache mount option with and without uniquifier, IPv4/IPv6 cache key generation, duplicate volume key `-EBUSY`, regular vs non-regular inode cookie creation, read-only open enabling cache, write open invalidation, readahead/read_folio cache hit/miss behavior, split RPC completion, EOF tail clearing, and operation with `CONFIG_NFS_FSCACHE=n` stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/fscache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/fscache.h -->
## sources/distributed-fs/ceph-client/fs/nfs/fscache.h

Purpose: declares the NFS fscache/netfs interface and provides compile-time stubs when filesystem cache support is disabled.

Important APIs and types: defines `struct nfs_fscache_inode_auxdata`, the coherency record persisted with cached inode data; `struct nfs_netfs_io_data`, the bridge object used to terminate netfs subrequests once all NFS RPC fragments complete; inline refcount helpers `nfs_netfs_get` and `nfs_netfs_put`; `nfs_netfs_inode_init`; exported fscache routines; netfs read entry points; folio release and invalidation helpers; fscache state string helper; and setters that pass netfs state between pageio descriptors and pgio headers.

Control flow: when `CONFIG_NFS_FSCACHE` is enabled, callers initialize netfs state in each NFS inode, acquire/release superblock and inode cookies, use/unuse cookies on open/close, and route read_folio/readahead through netfs. `nfs_netfs_put` is the key completion gate: the final reference clamps transferred bytes to the requested subrequest length, stores the error, calls `netfs_read_subreq_terminated`, and frees the bridge object. When disabled, functions become no-ops or `-ENOBUFS` returns while preserving call sites.

State and persistence behavior: auxdata mirrors inode mtime/ctime and NFSv4 change_attr into fscache coherency metadata. Invalidation is non-sleeping and passes auxdata plus current i_size. The enabled path records cookie state in `NFS_I(inode)->netfs`; disabled stubs intentionally persist nothing.

Dependencies and integration points: includes swap, NFS mount/version headers, fscache, and iversion. It references `nfs_netfs_ops` implemented in `fscache.c`, NFS server/client version data, and netfs/fscache folio release APIs. It is used from inode allocation/clear, open/close, cache invalidation, and pageio read paths.

Risks: the header encodes different behavior under configuration flags, so build coverage must include both enabled and disabled fscache. Completion clamping in `nfs_netfs_put` protects against pageio overread warnings; regressions here would show as netfs accounting errors. `nfs_fscache_release_folio` waits on deprecated private state only when allowed by reclaim context.

Test signals: allmodconfig and fscache-disabled builds, netfs subrequest split/completion refcounts, invalidation auxdata for NFSv3 vs NFSv4, folio release under kswapd and non-`__GFP_FS`, and pageio propagation of `pg_netfs` between descriptor and header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/fscache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/getroot.c -->
## sources/distributed-fs/ceph-client/fs/nfs/getroot.c

Purpose: obtains the root inode and dentry for an NFS mount after the superblock and mount context have been prepared.

Important APIs and functions: `nfs_get_root` is the external entry point. `nfs_superblock_set_dummy_root` installs an invisible dummy root dentry on the superblock. It also uses `nfs_alloc_fattr_with_label`, protocol `getroot`, `nfs_fhget`, `d_obtain_root`, `security_sb_set_mnt_opts`, `security_sb_clone_mnt_opts`, and `nfs_setsecurity`.

Control flow: `nfs_get_root` duplicates the mount source for dentry private data, allocates root fattrs, asks the protocol ops to getattr the mount root filehandle, converts the filehandle/fattrs to an inode, ensures the superblock has a dummy root, obtains the actual root dentry, attaches the source name to anonymous root dentries, applies or clones LSM mount options, adjusts the security-label capability if LSMs did not accept native labels, sets inode security from fattrs, and returns the root in `fc->root`.

State and persistence behavior: `sb->s_root` may be initialized once to a dummy dentry whose alias is removed from the inode alias list so later dentry splicing does not expose it incorrectly. `fc->root` receives a referenced root dentry. `root->d_fsdata` may own the duplicated source string. Server `has_sec_mnt_opts` and `NFS_CAP_SECURITY_LABEL` can be updated based on security setup.

Dependencies and integration points: integrates mount context state from `fs_context.c`, server/protocol operations, inode construction in `inode.c`, VFS dentry/root helpers, and Linux security hooks. Clone mounts use the parent superblock security options and require the cloned root to be a directory.

Risks: error unwinding must free fattrs/source strings and drop `fc->root` when security setup fails. The dummy root alias manipulation is subtle but protects unmount/shrinker assumptions. Security-label capability is modified based on LSM output flags, so mount behavior can differ by active LSM configuration. Clone data with a non-directory root returns `-ESTALE`.

Test signals: successful NFS root mount, failed protocol getroot, inode creation failure, dentry allocation failure, clone mount from a parent superblock, LSM context and native-label mounts, non-directory clone roots, and dentry alias/shrinker behavior during unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/getroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/inode.c -->
## sources/distributed-fs/ceph-client/fs/nfs/inode.c

Purpose: provides core NFS inode, attribute-cache, open-context, pagecache revalidation, fattr/fhandle allocation, per-net setup, workqueue, and module initialization logic for the Linux NFS client.

Important APIs and functions: exported inode helpers include `nfs_fhget`, `nfs_ilookup`, `nfs_getattr`, `nfs_setattr`, `nfs_setattr_update_inode`, `nfs_revalidate_inode`, `nfs_refresh_inode`, `nfs_post_op_update_inode`, `nfs_post_op_update_inode_force_wcc`, `nfs_clear_invalid_mapping`, `nfs_revalidate_mapping`, `nfs_alloc_inode`, `nfs_free_inode`, `nfs_clear_inode`, `nfs_evict_inode`, `nfs_sync_inode`, `nfs_sync_mapping`, `nfs_set_cache_invalid`, `nfs_zap_acl_cache`, and `nfs_setsecurity`. Open/lock context APIs include `alloc_nfs_open_context`, `get_nfs_open_context`, `put_nfs_open_context`, `nfs_get_lock_context`, `nfs_put_lock_context`, `nfs_file_set_open_context`, `nfs_file_clear_open_context`, and `nfs_find_open_context`.

Control flow: `nfs_fhget` maps filehandles and fattrs into inode-cache entries using `iget5_locked`; new inodes get mode-specific ops, mapping ops, timestamps, ownership, file size, link count, security labels, cache validity, fscache state, and regular/dir private initialization. Existing inodes are refreshed. Attribute reads go through `nfs_getattr`, which filters statx masks, flushes writes when needed, decides whether cached attributes are stale, optionally revalidates, and fills `kstat`. `nfs_setattr` handles delegated timestamp shortcuts, flushes dirty data, sends protocol setattr, truncates pagecache when needed, and refreshes attributes. Revalidation fetches server attrs unless delegations/pNFS state make it unnecessary. Attribute update paths compare generation counters and change attributes to avoid stale RPC replies, apply weak cache consistency, invalidate data/access/ACL/xattr caches, and manage out-of-order change gaps.

State and persistence behavior: `struct nfs_inode` holds fileid, filehandle, cache validity bits, attribute timeout and generation counters, open-file list, access/ACL/xattr state, write/commit counters, out-of-order change tracking, pNFS layout state, delegation state, and netfs/fscache state. Cache invalidation uses release/acquire barriers around `cache_validity` and serializes data invalidation with `NFS_INO_INVALIDATING`. Attribute timeout backs off up to server max when revalidation succeeds and resets on detected changes. Open contexts pin dentries, credentials, superblock active refs, lock contexts, localio handles, and optional pNFS thresholds until RCU free.

Dependencies and integration points: ties together protocol ops, pNFS, fscache/netfs, NFS access and ACL caches, VFS inode/pagecache/statx APIs, writeback/direct I/O, NFSv4 delegations/security labels/layouts, lockd-style locking contexts, proc/sysfs/pernet registration, keyring support, workqueues, and filesystem registration. `init_nfs_fs` orders subsystem initialization and unwinds in reverse on failure.

Risks: attribute coherency is the central risk: stale/out-of-order RPC replies, local writeback, delegations, pNFS layoutcommit, and server change-attribute semantics all interact. Data invalidation must avoid races where one task clears invalid bits before another invalidates mappings. Open context refcounts and RCU list removal protect mmap/writeback credentials; mistakes can leak refs or use freed contexts. `nfs_update_inode` can mark inodes stale on fileid/type changes and must avoid invalidating data caused by local writers. Module init/exit ordering must match allocation dependencies.

Test signals: filehandle lookup and type/fileid mismatch, regular/dir/symlink/special inode initialization, statx with force/dont-sync and dio alignment fields, close-to-open revalidation, delegated atime/mtime updates, setattr truncate and chmod/chown, weak cache consistency after writes, pNFS layoutcommit outstanding attrs, pagecache invalidation races under concurrent reads/writes, fscache invalidation, open/close context lifetime, lock context reuse, NFS stale handling, per-net proc registration, and init failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/inode.c -->
