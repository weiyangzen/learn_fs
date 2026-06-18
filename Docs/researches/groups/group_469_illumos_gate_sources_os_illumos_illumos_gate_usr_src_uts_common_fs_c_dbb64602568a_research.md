# Group Research: group_469_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_c_dbb64602568a

Scope verified against `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_sym.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_sym.c

This file implements ctfs symbolic-link vnodes for `/system/contract/all/<ctid>`. The symlink points from the aggregate `all` contract directory back to the typed contract directory, using a target of the form `../<type>/<id>`.

Key routines:
- `ctfs_create_symnode()` creates a GFS file vnode, marks it `VLNK`, stores the contract pointer, formats and stores the symlink target string, and takes a contract hold.
- `ctfs_sym_getattr()` reports a read-only symlink with size equal to the symlink target length and timestamps derived from the contract creation time.
- `ctfs_sym_readlink()` returns the prebuilt target through `uiomove()`.
- `ctfs_sym_inactive()` releases the held contract and frees the symlink string and node storage after `gfs_file_inactive()` confirms teardown.

The vnode operation table exposes open, close, getattr, readlink, read-only access, and inactive handling. Directory operations are rejected with `fs_notdir`; ioctl is invalid.

Integration points are `gfs_file_create()`, `ctfs_ops_sym`, `contract_hold()`, `contract_rele()`, `ctfs_common_getattr()`, and standard VOP dispatch through `ctfs_tops_sym`.

Primary correctness concerns are lifetime symmetry between `contract_hold()` and `contract_rele()`, and keeping `ctfs_sn_size` consistent with the allocated symlink string length.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_sym.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_tdir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_tdir.c

This file implements ctfs per-contract-type directories, such as `/system/contract/<type>`. Each directory contains fixed control entries and dynamically enumerated contract ID directories.

Static entries are:
- `bundle`
- `pbundle`
- `template`
- `latest`

Key routines:
- `ctfs_create_tdirnode()` creates a GFS directory with the static entry table plus custom inode, readdir, and lookup callbacks.
- `ctfs_tdir_getattr()` reports a read-only directory, link count based on fixed entries, and size based on fixed entries plus the contract count for the type.
- `ctfs_tdir_do_inode()` maps each fixed entry index into a ctfs type-file inode.
- `ctfs_tdir_do_readdir()` enumerates contract IDs visible in the vnode’s zone by using `contract_type_lookup()` and emits numeric directory names.
- `ctfs_tdir_do_lookup()` parses a numeric name, resolves the matching contract with `contract_type_ptr()`, creates a contract directory vnode, and releases the contract reference after vnode creation.

The implementation is zone-aware through `VTOZONE(vp)->zone_uniqid`. It depends on `ct_types[gfs_file_index(vp)]` to map the GFS file index to a contract type.

The vnode operation table delegates readdir and lookup to generic GFS helpers and marks the directory read/search-only. Correctness depends on contract lookup/release balance and numeric-name parsing rejecting suffixes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_tdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_tmpl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_tmpl.c

This file implements ctfs template vnodes for `/system/contract/<type>/template`. A template vnode owns a contract template object used by the `ct_tmpl_*` user interfaces.

Key routines:
- `ctfs_create_tmplnode()` creates a GFS file vnode and initializes its `ctfs_tmn_tmpl` with the contract type’s default template constructor.
- `ctfs_tmpl_open()` only accepts `FREAD | FWRITE | FOFFMAX`; any other open mode returns `EINVAL`.
- `ctfs_tmpl_getattr()` reports a zero-length regular file with mode `0666` and filesystem mount-time timestamps.
- `ctfs_tmpl_ioctl()` dispatches `CT_TACTIVATE`, `CT_TCLEAR`, `CT_TCREATE`, `CT_TSET`, and `CT_TGET`.
- `ctfs_tmpl_inactive()` frees the held contract template and node storage.

The ioctl path copies parameters with `ctparam_copyin()`, calls `ctmpl_set()` or `ctmpl_get()`, and handles copyout for `CT_TGET`. `CT_TCREATE` creates a contract from the template and returns the new contract ID via `rvalp`.

The vnode table exposes read-write access and ioctl support while rejecting directory operations. The main risk area is memory ownership for `ct_kparam_t.ctpm_kbuf`; `CT_TSET` always frees after `ctmpl_set()`, while `CT_TGET` frees only on `ctmpl_get()` error and otherwise transfers through copyout handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_tmpl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dcfs/dc_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dcfs/dc_vnops.c

This file implements `dcfs`, a layered pseudo filesystem that presents UFS fiocompressed files as transparently decompressed read-only regular files. UFS detects compressed files and calls `decompvp()` to obtain a shadow dcfs vnode.

Major components:
- Module registration for filesystem type `dcfs`.
- A vnode operation table for open, close, read, getattr, setattr, access, fsync, inactive, fid, seek, frlock, realvp, getpage, putpage, map, addmap, and delmap.
- `dcnode` allocation, recycling, hash-table lookup by subordinate vnode, and small LRU retention for nodes with cached pages.
- Decompression block handling through zlib-compatible `z_uncompress()` and a per-block-size kmem cache.

Control flow:
- `decompvp()` checks whether a shadow vnode already exists, validates the compressed header, reads the full block map, allocates a `dcnode`, holds the subordinate vnode, initializes decompression buffer cache state, and inserts the node into `dctable`.
- `dc_read()` reads through `segmap`; actual decompression occurs in page-fault/page-cache paths.
- `dc_getpage()` rounds the requested range to compression-block boundaries and calls `dc_getblock()` per block.
- `dc_getblock()` first tries cached pages and falls back to `dc_getblock_miss()`.
- `dc_getblock_miss()` reads compressed bytes from the subordinate vnode, decompresses into destination pages, zero-fills EOF slack, and validates decompressed size.
- `dc_putpage()` only supports invalidation/free/dontneed style cleanup; dirty pages are treated as impossible and forced out with error handling.
- `dc_map()`, `dc_addmap()`, and `dc_delmap()` support read mappings and track mapped page count for mandatory-lock checks.

The filesystem is intentionally read-only at the dcfs layer. Write attempts in `dc_getpage()` panic, and `dc_putapage()` also panics if a dirty page path is reached.

Important dependencies include vnode/VFS APIs, VM page APIs, `segmap`, `pvn_*` helpers, zlib wrapper functions, compressed file header definitions in `sys/fs/decomp.h`, and subordinate filesystem VOPs.

Risk areas:
- Header validation and block-map sizing are critical because compressed metadata drives later reads.
- Dirty-page paths are asserted impossible; any future write-like behavior would need explicit design.
- `dctable_lock` protects both hash and LRU operations, so lock ordering with vnode locks matters in inactive/recycle paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dcfs/dc_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_comm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_comm.c

This file implements kernel-side communication between `/dev` filesystem code and user-level `devfsadmd`/`devfsadm` services. It handles door setup, daemon startup requests, wait coordination, and registration of the daemon’s door pathname.

Key routines:
- `sdev_devfsadm_lockinit()` and `sdev_devfsadm_lockdestroy()` initialize global synchronization.
- `sdev_wait4lookup()` waits for lookup or readdir completion, either while devfsadm is running or while an in-kernel callback/plugin lookup is active.
- `sdev_unblock_others()` clears lookup/read flags and broadcasts waiters.
- `sdev_start_devfsadmd()` emits a sysevent requesting daemon startup.
- `sdev_open_upcall_door()` waits for the daemon to register a door filename and opens it with `door_ki_open()`.
- `sdev_ki_call_devfsadmd()` performs the kernel door upcall, with retry behavior for `EINTR`, `EAGAIN`, and limited rebinding on `EBADF`.
- `sdev_devfsadm_revoked()` detects shutdown or revoked door handles.
- `sdev_devfsadmd_thread()` launches asynchronous full device configuration.
- `devname_filename_register()` is called from user/kernel control plumbing to install the door filename and wake waiters.

The global `devfsadm_state` bitset coordinates “running”, “has run”, and stop/run outcomes. Per-node lookup locks coordinate callers blocked on specific `sdev_node` creation.

Primary integration points are sysevents, kernel doors, `/dev` lookup state macros, and the task/thread path used by `sdev_subr.c`.

Risks include timeout behavior during daemon startup, stale/revoked door state, and ensuring every blocked lookup path eventually clears flags and broadcasts waiters.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_comm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ipnetops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ipnetops.c

This file implements vnode overrides for the dynamic `/dev/ipnet` directory. Entries represent IP network interfaces known to the `ipnet` module and are scoped by the current zone.

Key routines:
- `devipnet_fill_vattr()` builds character-device attributes with mode `0666`, device number, and current timestamps.
- `devipnet_validate()` checks whether an existing sdev node still maps to a live `ipnet` device in the current zone and whether its minor number is current.
- `devipnet_create_rvp()` is the lookup callback used by `devname_lookup_func()` to create a node when `ipnet_if_getdev()` succeeds.
- `devipnet_lookup()` delegates dynamic creation to `devname_lookup_func()` and asserts expected real-vnode behavior for character nodes.
- `devipnet_filldir_entry()` creates missing cached entries while walking ipnet interfaces.
- `devipnet_filldir()` upgrades the directory lock, prunes invalid/stale ready nodes, and walks the current zone’s interfaces.
- `devipnet_readdir()` fills on first offset, then delegates output formatting to `devname_readdir_func()`.

The vnode operation table overrides lookup and readdir, and rejects create/remove/mkdir/rmdir/symlink/security-attribute mutation.

The main dependencies are `ipnet_if_getdev()`, `ipnet_walk_if()`, sdev cache helpers, zone ID lookup, and generic `/dev` readdir/lookup helpers.

Correctness concerns are zone scoping, stale minor detection, and avoiding deletion of nodes that still have vnode references.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ipnetops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ncache.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ncache.c

This file implements the `/dev` negative lookup cache. The cache records names for which implicit reconfiguration failed, preventing repeated expensive `devfsadm` attempts for known-missing devices. It persists through `/etc/devices/devname_cache`.

Major state:
- Tunables for entry expiration, maximum entries, reconfiguration delay, verbose logging, cache disable flags, and read/write disable flags.
- `sdev_boot_state`, `sdev_reconfig_boot`, global `sdev_ncache`, and the nvfile handle for persistent storage.
- `sdev_cache_ops`, which binds nvfile callbacks to `/etc/devices/devname_cache`.

Key routines:
- `sdev_ncache_init()` creates the in-memory list.
- `sdev_ncache_setup()` registers the persistent cache file, reads it unless disabled, processes stored entries, and advances device state.
- `sdev_ncache_unpack_nvlist()` and `sdev_ncache_pack_list()` translate between nvlist storage and internal path/expiration arrays.
- `sdev_ncache_process_store()` loads stored paths into the live negative cache, respecting maximum-entry limits.
- `sdev_ncache_write()` snapshots the live cache to nvfile state and wakes the nvfile flush daemon.
- `sdev_ncache_write_complete()` handles completion and schedules another write if the cache dirtied again during a write.
- `sdev_devstate_change()`, `sdev_state_sysavail()`, and `sdev_state_boot_complete()` manage boot-state transitions, delayed completion, expiration-count decrement, and write enablement.
- `sdev_lookup_filter()` checks whether a failed lookup should avoid reconfiguration.
- `sdev_lookup_failed()` adds eligible failed lookups to the cache.
- `sdev_nc_node_exists()` and `sdev_nc_path_exists()` remove entries when a node/path exists.
- `sdev_nc_free_bootonly()` clears store-sourced entries during reconfiguration boot when reset is enabled.

The cache is protected by both an rwlock for list traversal/mutation and a mutex for dirty/write flags. The backing nvfile has its own lock; the code documents and follows a specific lock ordering during writes.

Risk areas:
- Lock ordering between nvfile lock, negative-cache rwlock, and flag mutex.
- Correctly excluding dynamic, non-global, and `SDEV_NO_NCACHE` nodes.
- Boot-state timing, because cache writes are intentionally delayed until the system is sufficiently available.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ncache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_netops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_netops.c

This file implements vnode overrides for `/dev/net`, where entries represent active network datalinks using vanity names.

Key routines:
- `devnet_validate()` checks that a cached node still corresponds to a current datalink and that non-global-zone access is allowed by `zone_check_datalink()`.
- `devnet_create_rvp()` opens a datalink via `dls_devnet_open()`, obtains its device number, and prepares character-device attributes.
- `devnet_lookup()` handles `.`, `..`, cache lookup, stale attribute refresh, dynamic creation, and stores a `dls_dl_handle_t` in `sdev_private` while the node is active.
- `devnet_filldir_datalink()` creates or refreshes cache entries while walking datalinks.
- `devnet_filldir()` prunes invalid ready nodes, then enumerates global or zone-visible datalinks depending on mount context.
- `devnet_readdir()` fills on offset zero and delegates output to `devname_readdir_func()`.
- `devnet_inactive_callback()` closes the held datalink handle and marks attributes invalid.
- `devnet_inactive()` delegates common inactive handling to `devname_inactive_func()`.

The vnode table overrides lookup, readdir, and inactive, and rejects mutation operations.

Important dependencies include DLS management APIs, zone datalink walking, sdev node/cache helpers, and spec vnode conversion through `sdev_to_vp()`.

Risk areas include keeping `sdev_private` handle lifetime balanced, refreshing stale device numbers after detach/reattach, and matching global-zone versus non-global-zone visibility rules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_netops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_plugin.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_plugin.c

This file implements the dynamic directory plugin interface for sdev. It lets kernel subsystems register `/dev/<name>` dynamic directories backed by in-kernel state, instead of hard-coding all such directories in sdev itself.

Core concepts:
- A plugin provides `spo_validate`, `spo_filldir`, and `spo_inactive`.
- The plugin interface exposes context helpers for vnode type, path, name, minor number, and global flag.
- Plugins may create child directories and character/block nodes through `sdev_plugin_mkdir()` and `sdev_plugin_mknod()`.
- A global plugin list maps `/dev` paths to plugin vnode ops, flags, and validators.
- Legacy `vtab` dynamic directories are registered as legacy plugins.

Key routines:
- `sdev_plugin_register()` validates the name and ops, ensures a unique global `/dev` entry, inserts the plugin, and creates its top-level directory.
- `sdev_plugin_unregister()` removes the plugin, walks all sdev mounts to stale matching directories, waits for plugin node count to drain, then frees the plugin.
- `sdev_plugin_vop_lookup()` and `sdev_plugin_vop_readdir()` validate existing entries, call `spo_filldir()`, and delegate lookup/readdir formatting to common sdev helpers.
- `sdev_plugin_vop_inactive_cb()` calls `spo_inactive()` only when a node is truly zombie and decrements the plugin’s active node count.
- `sdev_get_vop()` selects plugin vnode ops and flags for a node based on its `/dev` path.
- `sdev_get_vtor()` returns either a legacy validator or the generic plugin validator.
- `sdev_plugin_nodeready()` attaches non-legacy plugin state to new nodes and increments node count.
- `sdev_plugin_init()` creates caches/locks, registers legacy vtab entries, and builds plugin vnode ops.

Lock ordering is explicitly documented: `sdev_plugin_lock` precedes per-plugin locks, and once plugin locks are held the code must not acquire sdev node holds or contents locks.

Risk areas:
- Plugin unregister is guarded by `sdev_plugin_unregister_allowed` because detach-context use can deadlock or return busy.
- `sdev_match()` path matching for `SDEV_SUBDIR` plugins is central to routing.
- Plugin callbacks execute with blocking allowed and with sdev contents locks held in the wrapper paths, so callback behavior must respect API restrictions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_plugin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_profile.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_profile.c

This file implements `/dev` namespace profiles for non-global-zone sdev instances. Profiles define which global `/dev` names appear in a zone, which names are excluded, which symlinks are created, and which global devices are mapped under alternate names.

Profile rule types:
- Include
- Exclude
- Map
- Symlink

Key routines:
- `prof_getattr()` obtains attributes from the shadow backing store, creates shadow directories as needed, or derives default device attributes from devfs/global vnode state.
- `prof_mknode()` creates profile-visible sdev nodes and applies glob patterns to newly created directories.
- `prof_make_dir()` creates/intersects profile directories with corresponding global `/dev` directories.
- `prof_lookup_globaldev()` looks up a device in the global `/dev` origin and creates a visible node under the local name.
- `prof_make_symlinks()`, `prof_make_maps()`, and `prof_make_names()` materialize profile rules into directory contents.
- `prof_name_matched()` evaluates include/exclude and directory-glob rules.
- `walk_dir()` reads a directory and applies a callback to each non-dot entry.
- `prof_zone_matched()` applies a final zone-property check for `SDEV_ZONED` directories.
- `prof_filldir()` rebuilds directory contents when generation counters or build flags indicate stale contents.
- `process_rule()` parses paths and installs rules at the correct directory level.
- `sdev_process_profile()` consumes the packed profile nvlist entries.
- `prof_lookup()` performs lookup within a profiled directory, triggering `prof_filldir()` on cache miss.
- `devname_profile_update()` copies in the packed nvlist, finds the matching mounted sdev instance by mount point, and applies the profile.

The file depends on nvlist profile formats from libdevinfo/modctl, global `/dev` origins in `sdev_origins`, sdev cache/node helpers, pathname traversal, and devfs default attribute lookup.

Risk areas:
- Profile updates depend on first nvpair being `SDEV_NVNAME_MOUNTPT`.
- Include/exclude glob rules can recurse through existing directory contents.
- Global-zone peeking into zone `/dev` has a noted limitation for `SDEV_ZONED` property checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_profile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ptsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ptsops.c

This file implements vnode overrides for `/dev/pts`, where entries represent allocated pseudo-terminal subsidiary devices.

Key routines:
- `devpts_getvnodeops()` returns the global `/dev/pts` vnodeops pointer.
- `devpts_strtol()` safely parses a numeric minor name and rejects malformed names such as `4foo` or negative values.
- `devpts_validate()` checks that the pts driver is attached, the minor is valid for the current zone, and cached uid/gid attributes match PTMS ownership.
- `devpts_create_rvp()` builds character-device attributes for a valid pty minor and zone.
- `devpts_prunedir()` validates ready children and removes invalid/stale unreferenced nodes.
- `devpts_lookup()` delegates dynamic creation to `devname_lookup_func()` and asserts that sdev nodes do not expose a realvp in a way that would break namefs fattach protections.
- `devpts_create()` allows open/create semantics to find existing nodes but rejects creation of missing nodes with `EROFS`.
- `devpts_readdir()` prunes on first offset and delegates formatting to `devname_readdir_func()`.
- `devpts_set_id()` updates PTMS owner state when uid/gid changes.
- `devpts_setattr()` uses common `devname_setattr_func()` with uid/gid callback protocol.

The vnode table overrides lookup, create, readdir, and setattr, while rejecting remove/mkdir/rmdir/symlink/security-attribute operations.

Important dependencies are PTMS APIs, sdev validators, common lookup/readdir/setattr helpers, and namefs behavior around fattach.

Risk areas include pty minor reuse, zone ownership validation, and the documented security assumption that `VOP_REALVP()` on the sdev node returns `ENOSYS`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ptsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_subr.c

This file provides the shared implementation for the illumos `/dev` filesystem: node allocation, attribute handling, directory cache operations, lookup/readdir algorithms, persistent backing-store integration, rename/cleanup, modctl helper operations, generic setattr, and inactive teardown.

Major exported/default state:
- Prototype vattrs for directory, symlink, block, and character nodes.
- `sdev_node_cache`.
- `devtype`.
- Legacy dynamic directory table `vtab` for `pts`, `vt`, `zvol`, `zcons`, `net`, `ipnet`, `lofi`, and `rlofi`.

Node lifecycle:
- `sdev_node_cache_init()` and `sdev_node_cache_fini()` manage the kmem cache.
- `sdev_nodeinit()` allocates an `sdev_node`, names/path it, initializes vnode state, inherits flags, and sets initial state.
- `sdev_nodeready()` transitions a node to `SDEV_READY`, initializes directory AVL state, symlink target, plugin state, non-global origin, attributes, and optional persistent shadow vnode.
- `sdev_mkroot()` builds the filesystem root node and marks global `/dev` roots as global/persistent.
- `sdev_nodedestroy()` releases backing vnode, attributes, names, symlink target, profile nvlists, origins, AVL state, locks, and returns the node to the cache.
- `devname_inactive_func()` handles vnode inactive callbacks, destroying zombie nodes only when the final reference drops.

Directory cache and mutation:
- `sdev_findbyname()`, `sdev_direnter()`, `sdev_dirdelete()`, `sdev_cache_update()`, and `sdev_cache_lookup()` implement the in-core AVL directory cache.
- `sdev_stale()` recursively marks cached children stale/zombie and sets rebuild state.
- `sdev_cleandir()` recursively removes children, optionally enforcing deletion of busy nodes, and cleans persistent backing-store entries.
- `sdev_rnmnode()` implements rename by validating hierarchy constraints, handling symlink targets, replacing existing destinations, recursively moving directory contents, creating a fresh destination node, and updating timestamps.

Lookup and directory fill:
- `devname_lookup_func()` is the central lookup path. It checks `.`, `..`, cache entries, backing store, dynamic callbacks, implicit devfsadm reconfiguration, negative cache filtering, validators, stale recreation, and spec vnode conversion.
- `sdev_call_dircallback()` creates dynamic symlink or vattr-based nodes from directory-specific callbacks.
- `sdev_call_devfsadmd()` coordinates implicit reconfiguration through devfsadmd.
- `sdev_filldir_from_store()` populates cache entries from the persistent backing directory.
- `sdev_filldir_dynamic()` pre-creates dynamic legacy directories under global `/dev`.
- `devname_readdir_func()` is the common readdir formatter; it optionally triggers devfsadm for browse reads, waits for rebuilds, fills from backing store, emits `.`, `..`, and ready cached entries, and applies validators.
- `add_dir_entry()` is a small dirent construction helper.

Persistence and attributes:
- `sdev_shadow_node()` creates or finds a persistent backing-store vnode for a node.
- `devname_backstore_lookup()` wraps lookup in the backing store.
- `sdev_vattr_merge()` overlays sdev inode/link/type/rdev information onto vattrs.
- `sdev_getdefault_attr()` returns default vattr templates.
- `sdev_update_timestamps()` writes timestamp changes to a vnode.
- `devname_setattr_func()` implements common setattr logic, using backing-store setattr when available, creating a shadow node for persistent or non-dynamic metadata changes, or updating in-memory attributes with policy checks.

Modctl helpers:
- `sdev_modctl_lookup()` resolves a path through global root, follows symlinks and mountpoints, and returns only the persisted vnode underlying `/dev`.
- `sdev_modctl_readdir()` lists persisted directory contents for module-control callers.
- `sdev_modctl_readdir_free()` frees returned lists.
- `sdev_modctl_devexists()` checks whether a persisted device path exists.

Important dependencies include VFS/vnode operations, specfs `specvp()`, AVL trees, sdev plugin hooks, devfsadm communication, negative cache helpers, backing-store filesystem VOPs, PTMS/net/ipnet validators through `vtab`, and zone/profile state.

Risk areas:
- Locking is complex: parent directory contents locks, child contents locks, vnode locks, lookup locks, and backing-store VOP calls interact across many paths.
- `SDEV_INIT`, `SDEV_READY`, and `SDEV_ZOMBIE` transitions are central to avoiding duplicate construction and dangling visible nodes.
- Persistent backing-store cleanup errors are intentionally logged but often not propagated.
- `devname_lookup_func()` has many early exits; reference release and negative-cache updates must stay balanced.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vfsops.c

This file implements VFS/module operations for the illumos `/dev` filesystem.

Global state:
- `sdev_origins`, the mount info for the global `/dev` origin.
- `sdev_lock`, used for mount/unmount/rename synchronization.
- `sdev_taskq`, lazily created on first mount.
- `devmajor`, `devminor`, and linked-list `sdev_mntinfo` for mounted instances.
- `sdev_stale_attrvp`, a debug aid for stale attribute vnodes after remount.

Module and init flow:
- `_init()` initializes global lock, node cache, devfsadm locks, and installs the filesystem module.
- `_fini()` always returns `EBUSY`; the global `/dev` instance keeps the module loaded.
- `devinit()` registers VFS ops, creates default vnode ops, allocates a unique device major, initializes the plugin subsystem, and initializes the negative cache.

Mount flow:
- `sdev_mount()` checks mount privileges and mountpoint validity, copies mount arguments, resolves the attribute backing directory, lazily creates the taskq, and handles either remount or fresh mount.
- On remount, it stales existing nodes, replaces mount args and root attribute vnode, and updates mount time.
- On fresh mount, it allocates a unique dev_t, creates the root node with `sdev_mkroot()`, initializes `sdev_data`, inserts it into the mount list, and configures ACL flavor.
- For non-global instances, the root origin is set to the global `/dev` root.
- For the global instance, it sets up the negative cache and pre-fills dynamic root entries.

Unmount flow:
- `sdev_unmount()` enforces unmount/device privileges, rejects forced unmount, refuses to unmount the global instance, checks root vnode references, clears directory contents, destroys the root node, removes mount info from the linked list, and frees mount args/data.

Other VFS operations:
- `sdev_root()` returns the mounted root vnode with a hold.
- `sdev_statvfs()` returns synthetic filesystem stats suitable for a pseudo `/dev` filesystem.
- `sdev_find_mntinfo()` finds a mounted instance by root name and takes a root vnode hold.
- `sdev_mntinfo_rele()` releases that hold.
- `sdev_mnt_walk()` iterates all mounted instances under `sdev_lock`.

Important dependencies include module/VFS registration, `sdev_subr.c` node helpers, plugin initialization, negative-cache setup, profile update lookup by mount info, and backing attribute directory behavior.

Risk areas are remount stale-state handling, global versus non-global mount distinction, lifetime of root/origin holds, and linked-list consistency under `sdev_lock`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vfsops.c -->