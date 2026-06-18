# subset-b-007077 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-common.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-common.h

## Purpose

`dht-common.h` is the shared contract for GlusterFS's DHT/distribute translator. It defines the in-memory layout model, per-call local state, inode and fd context, rebalance/migration metadata, disk-usage state, lock wrappers, DHT xattr keys, and the FOP/helper prototypes consumed by the DHT implementation files. The header is the coordination point between lookup/layout code, disk-space placement, linkfile handling, migration checks, read/write forwarding, directory self-heal, and translator lifecycle code.

## Important APIs, Types, and Functions

The central types are `dht_layout_entry_t`, `dht_layout_t`, `dht_inode_ctx_t`, `dht_local_t`, `dht_du_t`, `gf_defrag_info_t`, `dht_conf_t`, `dht_migrate_info_t`, and `dht_fd_ctx_t`. `dht_layout_t` stores hash ranges, commit hashes, generation, spread count, and a refcounted variable-length `list[]`. `dht_inode_ctx_t` persists an inode's cached layout, time cache, lock subvolume, and directory MDS subvolume. `dht_local_t` is the large per-frame scratchpad for locations, xattrs, cached/hashed subvolumes, self-heal, linkfile, rebalance, locks, counters, and retry state.

Important macros include `DHT_STACK_UNWIND`, `DHT_STACK_DESTROY`, `DHT_UPDATE_TIME`, `IS_DHT_MIGRATION_PHASE1`, `IS_DHT_MIGRATION_PHASE2`, `DHT_STRIP_PHASE1_FLAGS`, `check_is_linkfile`, `layout_is_sane`, and the DHT xattr constants such as `GF_XATTR_FIX_LAYOUT_KEY`, `GF_XATTR_FILE_MIGRATE_KEY`, `DHT_FILE_MIGRATE_DOMAIN`, `DHT_LAYOUT_HEAL_DOMAIN`, and `DHT_ENTRY_SYNC_DOMAIN`. The declared APIs span layout allocation/search/merge/extract, hash calculation, linkfile creation, disk-usage refresh, subvolume selection, fd/inode context handling, migration checks, directory self-heal, xattr heal, lock routing, all file/dir FOP entry points, and lifecycle hooks.

## Control Flow and Integration

Most DHT FOPs allocate `dht_local_t` with `dht_local_init`, derive cached or hashed subvolumes from inode layout, wind one or more child FOPs, then unwind through `DHT_STACK_UNWIND`, which also wipes the local state. Layout lookup and self-heal flows use `dht_layout_merge`, `dht_layout_normalize`, and self-heal callbacks. File migration flows use the rebalance fields in `dht_local_t`, `dht_migrate_info_t` in inode ctx slot 1, and `dht_fd_ctx_t` on fd contexts to know whether an fd has been opened on the destination. Directory operations integrate with namespace/layout lock domains and MDS xattrs.

## State and Persistence Behavior

Persistent distributed state is stored mostly as trusted xattrs: directory layout, commit hash, linkto target, migration flags, MDS markers, and debug/status keys. Runtime state is split across translator config (`dht_conf_t`), inode contexts (`dht_inode_ctx_t` plus migration info), fd contexts (`dht_fd_ctx_t`), and call-frame local state. `dht_layout_t` is refcounted unless marked `preset`; `DHT_STACK_UNWIND` and `dht_local_wipe` are therefore part of the memory-safety contract. `vol_commit_hash`, layout `commit_hash`, `gen`, `subvolume_status`, and `subvol_up_time` connect topology changes to lookup/migration behavior.

## Dependencies and Risks

The header depends on GlusterFS frame, inode, fd, dict, syncop, lock, refcount, ACL, XDR, and DHT message/memtype headers. Risks concentrate around aliasing and ownership: `dht_dir_transaction_t` intentionally has a lock wrapper first because cleanup casts into nested variants; layout refs must not be freed for preset layouts; `dht_local_t` stores many owned dicts/locs/refs; and migration phase mode bits must be stripped before returning attrs to upper layers. Tests should exercise layout xattr parsing, refcount lifecycle, DHT unwind cleanup, fd/inode context migration updates, directory MDS routing, and nested DHT migration where `we_are_not_migrating(ret)` passes migration mode bits upward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-diskusage.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-diskusage.c

## Purpose

`dht-diskusage.c` maintains per-subvolume free-space and free-inode telemetry and chooses substitute placement targets when the hashed target is too full. It supports create/migration placement decisions and emits warnings/events when bricks cross configured disk or inode thresholds.

## Important APIs, Types, and Functions

`dht_du_info_cbk` consumes child `statfs` results and updates `conf->du_stats[]` with available percent, bytes, inode percent, chunk count, total/available blocks, and fragment size. `dht_get_du_info` periodically refreshes all child subvolumes using root-gfid `statfs` calls and `GF_INTERNAL_IGNORE_DEEM_STATFS`; `dht_get_du_info_for_subvol` refreshes one indexed child. `dht_is_subvol_filled` checks `min_free_disk` and `min_free_inodes` against either percent or absolute bytes depending on `conf->disk_unit_percent`. `dht_free_disk_available_subvol`, `dht_subvol_with_free_space_inodes`, and `dht_subvol_maxspace_nonzeroinode` select usable alternatives.

## Control Flow

Refresh starts from `dht_get_du_info`, which copies the caller frame, initializes a DHT local, sets a statfs request dict, then winds `statfs` to each child. Each callback updates only the slot whose `prev` cookie matches `conf->subvolumes[i]`, decrements `local->call_cnt`, and destroys the copied frame on the last callback. Placement selection loads the parent directory layout, locks `conf->subvolume_lock`, first searches for a child satisfying both free-space and inode minimums, then falls back to the maximum-space child with nonzero inodes. Candidate filtering rejects ignored rebalance source, layout-error children, and decommissioned bricks.

## State and Persistence Behavior

The file updates only runtime state in `dht_conf_t`: `du_stats[]`, `last_stat_fetch`, and rate-limited per-child `du_stats[i].log` counters. No on-disk layout or file metadata is written here. Space calculations are derived from child `struct statvfs`; inode-free percent is set to 100 when `f_files` is zero to represent dynamically allocated inode filesystems.

## Dependencies and Integration Points

It depends on DHT config/layout helpers, Gluster frame winding, `statfs`, dict APIs, logging, and `gf_event` for `EVENT_DHT_DISK_USAGE` and `EVENT_DHT_INODES_USAGE`. It integrates with create/rebalance placement through `dht_free_disk_available_subvol` and with layout code because candidates must be present and healthy in the relevant directory layout.

## Risks and Test Signals

Important edge cases include stale `du_stats` when refresh frames cannot be allocated, integer truncation in percent computations, division by block size when deriving 1 MiB chunks, absolute-vs-percent threshold confusion, and the subtle use of `i` after unlocking in `dht_is_subvol_filled`. Candidate selection currently chooses a child when either inode percent or space is greater than the running maximum, so tests should cover mixed inode/space pressure. Test signals include mocked `statfs` results, threshold event emission, decommissioned-brick exclusion, layout-error exclusion, refresh throttling by `refresh_interval`, dynamic-inode filesystems, and create fallback to hashed subvol when no alternative qualifies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-diskusage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-hashfn.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-hashfn.c

## Purpose

`dht-hashfn.c` computes the stable name hash that maps directory entries into DHT layout ranges. It also implements optional filename munging so rsync-style temporary names or administrator-specified regex patterns hash as their intended final names.

## Important APIs, Types, and Functions

`dht_hash_compute` is the exported entry point declared by `dht-common.h`. It accepts a DHT hash type, filename, and output pointer. `dht_hash_compute_internal` currently supports `DHT_HASH_TYPE_DM` and `DHT_HASH_TYPE_DM_USER`, both delegated to `gf_dm_hashfn` from `<glusterfs/hashfn.h>`. `dht_munge_name` applies a compiled `regex_t`, copies capture group 1 into a caller-provided buffer, and returns the new NUL-inclusive length when munging succeeds.

## Control Flow

The public function validates `name`, allocates a stack buffer sized to the original string, locks `priv->lock`, and first tries `priv->extra_regex` when valid, then `priv->rsync_regex` when valid and the extra regex did not match. On a successful capture, it hashes the captured name; otherwise it hashes the original name. The final hash call uses `len - 1` because the DM hash receives a byte length without the terminating NUL.

## State and Persistence Behavior

This file does not persist state. It reads runtime DHT config fields `extra_regex_valid`, `extra_regex`, `rsync_regex_valid`, and `rsync_regex` under `conf->lock`. The resulting hash affects persistent file placement indirectly because it selects layout ranges and therefore child subvolumes for future creates/lookups.

## Dependencies and Integration Points

Hash computation feeds `dht_layout_search`, `dht_subvol_get_hashed`, create/linkfile decisions, and any directory layout search method installed in `dht_conf_t.methods`. It depends on regex configuration established by DHT init/reconfigure and on Gluster's DM hash implementation. Nested DHT or NUFA/switch variants can rely on the same exported function unless they replace the layout-search method.

## Risks and Test Signals

Risks are concentrated in regex capture semantics and hash stability. A regex without capture group 1 or with a capture longer than the original buffer is ignored. Regex configuration changes alter placement for future operations and can increase unhashed lookups for existing files. Invalid hash type returns `-1`, which layout search logs as a hash failure. Tests should validate plain names, rsync temporary names, extra-regex precedence over rsync regex, no-capture patterns, boundary-length captures, invalid type handling, and cross-version stability of `gf_dm_hashfn` results for known names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-hashfn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-helper.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-helper.c

## Purpose

`dht-helper.c` provides the shared runtime machinery behind DHT FOP implementations: fd-context tracking, migration info, fd reopening on migration targets, subvolume selection helpers, `dht_local_t` lifecycle, attribute merging, subvolume initialization, rebalance phase checks, inode context management, path healing, lock-subvolume routing, and directory xattr-heal helpers.

## Important APIs, Types, and Functions

FD state is handled by `dht_fd_ctx_set`, `dht_fd_open_on_dst`, and `dht_fd_ctx_destroy`; migration state by `dht_inode_ctx_set_mig_info`, `dht_inode_ctx_get_mig_info`, and `dht_mig_info_is_invalid`. `dht_check_and_open_fd_on_subvol` starts a synctask that opens an fd on the cached/destination child and then resumes the original FOP through `dht_check_and_open_fd_on_subvol_complete`. General helpers include `dht_frame_return`, `dht_filter_loc_subvol_key`, `dht_deitransform`, `dht_local_init`, `dht_local_wipe`, `dht_subvol_get_hashed`, `dht_subvol_get_cached`, `dht_iatt_merge`, and `dht_build_child_loc`. Rebalance checks are split between `dht_rebalance_complete_check` and `dht_rebalance_in_progress_check`. Inode context APIs include layout get/set wrappers, time cache updates, MDS/lock subvolume slots, and migration ctx cleanup.

## Control Flow

Most callers enter through a FOP callback after detecting migration phase bits, `EREMOTE`, `ENOENT`, `ESTALE`, `EBADF`, or similar stale-fd symptoms. For complete migration, the synctask reads the source linkto xattr, performs a DHT lookup to refresh cached layout, validates GFID, resets migration info, and opens every live fd on the new destination. For in-progress migration, it reads linkto, looks up the destination directly, validates GFID, opens all inode fds on the destination, and records source/destination migration info. The completion callback invokes the saved `local->rebalance.target_op_fn` so read/write callbacks can retry against the selected child.

## State and Persistence Behavior

The file manipulates runtime state across three scopes. FD context stores the child on which a specific fd is open. Inode context stores layout, timestamps, lock subvolume, MDS subvolume, and a second ctx slot for migration info. `dht_local_t` owns transient refs to locs, dicts, fd, inode, layout, rebalance vectors/iobrefs, call stubs, and lock arrays; `dht_local_wipe` is the authoritative cleanup. Persistent state is consulted through linkto xattrs, ancestry path xattrs, and DHT layout data but not normally written here except through child open/lookups and ctx updates.

## Dependencies and Integration Points

This file integrates with `dht-inode-read.c` and `dht-inode-write.c` retry paths, with layout/hash helpers for cached and hashed subvolumes, with lock code through `dht-lock.h`, with syncop APIs for migration and path heal, and with inode/fd tables. `dht_iatt_merge` is used by directory and multi-child operations to synthesize attributes. `dht_get_lock_subvolume` stabilizes directory locks across lock/unlock by storing `lock_subvol` in inode ctx.

## Risks and Test Signals

High-risk areas are lock ordering around inode/fd lists, refcount ownership during fd-list iteration, stale migration ctx after multiple migrations, root-credential syncops, and the `dht_check_and_open_fd_on_subvol_task` path where the code comments say ENOENT/ESTALE can be tolerated but the later assignment still sets failure. Tests should cover migration phase1 and phase2 with open fds, multiple fds on one inode, fd already open on destination, nested DHT layers returning `ENODATA`, GFID mismatch, concurrent lookup changing cached subvol, directory lock/unlock after inode cache pressure, path-heal from ancestry xattr, `dht_local_wipe` leak checks, and subvolume initialization for one-child pass-through volumes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-inode-read.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-inode-read.c

## Purpose

`dht-inode-read.c` implements DHT file/inode read-side and metadata FOPs: `open`, `stat`, `fstat`, `readv`, `access`, `flush`, `fsync`, `lk`, `lease`, `readlink`, `xattrop`, `fxattrop`, `inodelk`, `finodelk`, and `seek`. The common theme is forwarding operations to the cached child while detecting migration and retrying on the correct destination.

## Important APIs, Types, and Functions

The public FOPs are the DHT translator entry points declared in `dht-common.h`. Callback/retry pairs include `dht_open_cbk`/`dht_open2`, `dht_file_attr_cbk`/`dht_attr2`, `dht_readv_cbk`/`dht_readv2`, `dht_access_cbk`/`dht_access2`, `dht_flush_cbk`/`dht_flush2`, `dht_fsync_cbk`/`dht_fsync2`, `dht_lk_cbk`/`dht_lk2`, `dht_common_xattrop_cbk`/`dht_common_xattrop2`, and `dht_seek_cbk`/`dht_seek2`. Directory/non-file aggregation uses `dht_attr_cbk` and `dht_iatt_merge`. Xattrop migration support uses `dht_request_iatt_in_xdata` and `dht_read_iatt_from_xdata` to request/read mode hints from xdata.

## Control Flow

For regular files, operations initialize `dht_local_t`, cache original arguments in `local->rebalance` as needed, set `call_cnt = 1`, and wind to `local->cached_subvol`. The callback treats non-migration errors as final but handles missing files, `EREMOTE`, phase2 mode bits, phase1 mode bits, and remote-fd failures by invoking helper synctasks. Complete-migration checks refresh layout and retry on the new cached subvol; in-progress checks validate/open the destination and retry there. Directory `stat`/`fstat` fan out across all layout entries and merge attributes. Directory `access` can walk available subvolumes when one child is down or missing. Lock paths use `dht_get_lock_subvolume` to keep directory locks/unlocks on a stable child.

## State and Persistence Behavior

This file primarily consumes inode layout and fd/migration context established elsewhere. It updates fd context when `open` succeeds on the final target and relies on helper code to open fds on migrated destinations. It stores retry state in `dht_local_t`: flags, offset, size, flock, xattr dicts, pre/post attrs, and original op return. Xattrop paths create or ref request dicts and ask lower translators to return DHT mode/iatt data in xdata so migration phases can be recognized without a separate lookup.

## Dependencies and Integration Points

It depends tightly on `dht-helper.c` for `dht_rebalance_complete_check`, `dht_rebalance_in_progress_check`, `dht_check_and_open_fd_on_subvol`, fd context, lock-subvolume tracking, and attribute merge. It depends on migration mode macros from `dht-common.h`, child FOP tables, dict APIs, and DHT layout context. Sharding is explicitly mentioned as a consumer of xattrop/fxattrop on files.

## Risks and Test Signals

Regression risk is high around retry idempotence: the same FOP must not loop indefinitely, leak request dicts, return migration mode bits to upper layers incorrectly, or operate on an fd not opened on the destination. Xattrop has a noted corruption risk if lower layers do not return the requested iatt/mode in xdata. Tests should cover read/open/stat while a file migrates through phase1 and phase2, fd migration with stale cached subvol, directory stat fanout with partial child failures, access fallback across child availability, lock/unlock on purged directory inodes, seek errors such as `ENXIO`/`EOVERFLOW`, xattrop/fxattrop with and without mode xdata, nested DHT layers, and cleanup of phase bits via `DHT_STRIP_PHASE1_FLAGS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-inode-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-inode-write.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-inode-write.c

## Purpose

`dht-inode-write.c` implements write-side and mutating inode FOPs for DHT: `writev`, `truncate`, `ftruncate`, `fallocate`, `discard`, `zerofill`, `setattr`, and `fsetattr`. It forwards regular-file operations to the cached child and preserves enough call state to retry on a migration target. For directories and other non-regular files, it fans metadata changes across layout children or routes directory MDS changes first.

## Important APIs, Types, and Functions

Each write-like operation has a callback and a second-wind helper: `dht_writev_cbk`/`dht_writev2`, `dht_truncate_cbk`/`dht_truncate2`, `dht_fallocate_cbk`/`dht_fallocate2`, `dht_discard_cbk`/`dht_discard2`, `dht_zerofill_cbk`/`dht_zerofill2`, and `dht_file_setattr_cbk`/`dht_setattr2`. Public entry points cache arguments into `local->rebalance`: iovec copies, iobrefs, offsets, sizes, flags, valid masks, and target attrs. Directory/non-file setattr aggregation uses `dht_setattr_cbk`, `dht_mds_setattr_cbk`, and `dht_non_mds_setattr_cbk`.

## Control Flow

Regular-file mutating FOPs initialize local state, wind to `local->cached_subvol`, then the callback checks for remote-fd errors, hard failures, migration phase2, and migration phase1. Phase2 or missing-file symptoms call `dht_rebalance_complete_check`; phase1 calls `dht_rebalance_in_progress_check` unless existing migration info plus fd context already identify an opened destination. The retry helpers set `call_cnt = 2` and re-wind the same operation to the destination child using the saved arguments. On second callbacks, source and destination pre/post attrs may be merged so upper layers see consistent metadata.

## State and Persistence Behavior

The file mutates child file data and metadata through child FOPs but does not itself write DHT layout xattrs. It stores transient retry data in `dht_local_t` and updates inode time cache after successful multi-child `setattr`. `writev` duplicates iovecs and refs the iobref so a retry remains valid after the original call stack advances. Phase1 writes add `GF_PROTECT_FROM_EXTERNAL_WRITES` to `xattr_req` before retrying to protect migration against concurrent external writes. Directory setattr first writes the MDS subvolume when present and then propagates to non-MDS children.

## Dependencies and Integration Points

The file depends on migration helpers, fd reopening, inode ctx migration info, DHT phase mode macros, `dht_set_local_rebalance`, and `dht_iatt_merge`. It integrates with layout/MDS metadata for directory setattr, with child storage translators for actual writes, and with upper translators that rely on correct pre/post attributes and stripped migration phase bits.

## Risks and Test Signals

Key risks are non-idempotent retry behavior for mutating operations, stale or missing duplicated write buffers, incorrect attr merging between source and destination, failure to protect phase1 external writes, and directory setattr partially applying when MDS or non-MDS children fail. Tests should cover each write FOP during phase1 and phase2 migration, fd not opened on destination, writev buffer lifetime across retry, truncation by path and fd, fallocate/discard/zerofill retry paths, regular-file setattr after complete migration, directory setattr with MDS down, non-regular multi-child setattr aggregation, and confirmation that `DHT_STRIP_PHASE1_FLAGS` runs before unwinding attrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-inode-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-layout.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-layout.c

## Purpose

`dht-layout.c` owns DHT layout allocation, lookup, refcounting, disk-xattr serialization/deserialization, layout merge, sorting, anomaly detection, normalization, mismatch checks, preset file layouts, and layout indexing. It translates between persistent on-disk directory layout xattrs and the in-memory hash range table used to route names to subvolumes.

## Important APIs, Types, and Functions

`dht_layout_new`, `dht_layout_ref`, `dht_layout_unref`, `dht_layout_get`, and `dht_layout_set` manage layout lifetime and inode attachment. `dht_layout_search` hashes a name and finds the matching range. `dht_layouts_init` creates one-entry preset file layouts for each child. `dht_disk_layout_extract` and `dht_disk_layout_extract_for_subvol` serialize a layout entry to four big-endian words: commit hash, hash type, start, and stop. `dht_layout_merge` and internal `dht_disk_layout_merge` parse child xattrs into layout entries. `dht_layout_sort`, `dht_layout_sort_volname`, `dht_layout_anomalies`, `dht_layout_missing_dirs`, `dht_layout_normalize`, `dht_dir_has_layout`, `dht_layout_dir_mismatch`, `dht_layout_preset`, and `dht_layout_index_for_subvol` implement validation and lookup helpers.

## Control Flow

Directory lookup/self-heal allocates a layout sized to child count, then calls `dht_layout_merge` once per child lookup. The merge path records child errors, handles missing xattrs as nonfatal entries, parses valid disk layouts, updates the aggregate `layout->commit_hash`, and marks it invalid if children disagree. Normalization sorts ranges, counts holes/overlaps/missing/down/misc/no-space anomalies, and returns negative for range holes/overlaps or positive counts for missing directories. Routing calls hash the basename through `dht_hash_compute` and scans the sorted or unsorted layout for a containing range.

## State and Persistence Behavior

The persistent representation is the DHT layout xattr stored per directory child. All numeric fields are big-endian on disk. Runtime layouts hold refs in inode ctx; preset file layouts belong to `conf->file_layouts` and are not freed by `dht_layout_unref`. Layout generation and commit hash connect in-memory cache validity to volume topology and rebalance completion.

## Dependencies and Integration Points

The file integrates with hash computation, inode context helpers, lookup/self-heal code, disk layout xattr names from `dht_conf_t`, and disk-usage/layout-error filtering. Directory self-heal relies on anomaly counts and mismatch detection to decide whether to fix layout xattrs. File operations rely on preset layouts to identify the cached subvolume for regular files.

## Risks and Test Signals

Risks include malformed disk layout lengths, endian mistakes, accepting zero-width/nonparticipating ranges incorrectly, stale commit hashes, preset-layout refcount misuse, sort comparator behavior for zero ranges, and mismatch checks when xattrs are absent but in-memory state says a child participates. Tests should parse/extract known layout xattrs, detect holes/overlaps/missing/down/no-space entries, validate commit-hash invalidation across disagreeing children, search boundary hashes at start/stop edges, handle user-set hash type, reject invalid hash types, verify preset file layout lifetime, and compare on-disk vs in-memory layout for self-heal decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-layout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-linkfile.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-linkfile.c

## Purpose

`dht-linkfile.c` creates, validates, resolves, and attribute-heals DHT linkfiles. Linkfiles are special regular files with `DHT_LINKFILE_MODE` plus a linkto xattr that point from a hashed location to the actual cached/target subvolume, allowing lookup and migration flows to find data that is not on the hash-selected child.

## Important APIs, Types, and Functions

`dht_linkfile_create` is the exported creation helper. It stores the caller's callback, copies the target loc, prepares gfid/internal/linkto xattrs, creates the special file as root, and winds a child `create`. `dht_linkfile_create_cbk` marks success, handles `EEXIST` by looking up the existing file with a linkto xattr request, and then dispatches the original callback. `dht_linkfile_lookup_cbk` verifies that the existing object really is a DHT linkfile. `dht_linkfile_subvol` reads the configured linkto xattr and maps the stored subvolume name to a child xlator. `dht_linkfile_attr_heal` asynchronously sets UID/GID on a newly created root-owned linkfile, using `dht_linkfile_setattr_cbk` for cleanup.

## Control Flow

Creation uses `local->params` when present or a temporary dict otherwise. It optionally sets `gfid-req`, always marks the FOP internal, stores `conf->link_xattr_name = tovol->name`, creates an fd when the caller did not provide one, and winds `create` to `fromvol` with `S_IFREG | DHT_LINKFILE_MODE`. On `EEXIST`, it sends `lookup` to confirm linkfile semantics and preserve race tolerance. Attribute heal copies the final file GFID into `local->loc`, copies the frame/local, marks the setattr internal, temporarily uses superuser credentials, and sets only UID/GID on `local->link_subvol`.

## State and Persistence Behavior

The linkfile itself is persistent child filesystem state. Its key persistent marker is the trusted DHT linkto xattr named by `conf->link_xattr_name`, whose value is a subvolume name. Creation may persist a requested GFID. Runtime state is in `local->linkfile`, `local->linked`, `local->link_subvol`, `local->fd`, and the copied frame used for async attr heal.

## Dependencies and Integration Points

This file depends on DHT config xattr names, `check_is_linkfile`, child `create`, `lookup`, and `setattr` FOPs, frame superuser helpers, dict APIs, and `DHT_MARK_FOP_INTERNAL`. It integrates with create, rename, hardlink, lookup, and rebalance paths that need linkto forwarding and with helper migration checks that resolve linkto xattrs through `dht_linkfile_subvol`.

## Risks and Test Signals

Risks include races on `EEXIST`, mismatched or stale linkto subvolume names, failure to heal root-owned UID/GID, leaking the temporary fd/dict on error, creating with the wrong GFID, and treating a normal file with linkfile mode or xattr inconsistently. Tests should cover successful linkfile creation, existing linkfile lookup validation, existing non-linkfile warning path, missing/unknown linkto target, gfid-req propagation, internal-FOP xattr presence, attr-heal success/failure, root credential use, and lookup/migration resolution from linkto xattr to child xlator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-linkfile.c -->
