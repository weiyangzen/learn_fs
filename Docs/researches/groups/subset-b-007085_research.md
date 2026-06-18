# subset-b-007085 GlusterFS EC heal, heald, helpers, and inode read research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heal.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heal.c

## Purpose
Implements the erasure-code translator self-heal engine. It decides whether an inode needs metadata, entry/name, or data repair; selects recoverable source bricks from EC version/dirty/size xattrs; repairs stale or missing directory entries; rebuilds file fragments by reading healthy fragments and writing sinks; adjusts persistent pending xattrs after success; exposes explicit heal and heal-info entry points; and throttles background heal tasks.

## Important APIs, types, and functions
The public heal entry points are `ec_heal()`, `ec_fheal()`, `ec_get_heal_info()`, `ec_launch_replace_heal()`, and `ec_heal_inodelk()`. Shared helpers include `ec_mask_to_char_array()`, `ec_char_array_to_mask()`, `ec_adjust_versions()`, and `ec_wind_xattrop_parallel()`. Metadata repair is centered on `ec_heal_metadata_find_direction()`, `__ec_heal_metadata_prepare()`, `__ec_heal_metadata()`, and `__ec_removexattr_sinks()`. Entry repair uses `ec_heal_entry_find_direction()`, `__ec_heal_entry_prepare()`, `ec_heal_name()`, `__ec_heal_name()`, `ec_delete_stale_names()`, `ec_delete_stale_name()`, `ec_create_name()`, and `ec_heal_names()`. Data repair uses `ec_heal_data_find_direction()`, `__ec_heal_data_prepare()`, `__ec_heal_mark_sinks()`, `__ec_heal_trim_sinks()`, `ec_rebuild_data()`, `ec_restore_time_and_adjust_versions()`, `__ec_fd_data_adjust_versions()`, and `ec_data_undo_pending()`. Block copying runs through `ec_heal_block()`, `ec_manager_heal_block()`, `ec_heal_data_block()`, `ec_heal_readv_cbk()`, and `ec_heal_writev_cbk()`. Need inspection uses `ec_heal_inspect()`, `ec_need_heal()`, `_need_heal_calculate()`, and the metadata/data/entry variants. Background queueing uses `ec_heal_throttle()`, `__ec_dequeue_heals()`, `ec_launch_heal()`, and `ec_handle_healers_done()`.

## Control flow
`ec_heal()` validates a `loc_t`, allocates an `EC_FOP_HEAL` fop, stores the partial flag and xdata, then passes it through `ec_heal_throttle()`. Foreground heals and accepted background heals are launched as synctasks via `ec_launch_heal()`, which creates a privileged self-heald frame and calls `ec_synctask_heal_wrap()`. `ec_heal_do()` performs optional name heal for a named entry, optionally inspects SHD-triggered entries to skip no-op or purge-only work, then runs data heal for regular files, entry heal for directories unless partial, and metadata heal for all inode types. It reports participant, good, bad, and pending-entry masks through the original heal callback.

Metadata heal locks enough bricks, looks up the inode on locked bricks, gets filtered xattrs, groups identical stat/xattr answers excluding EC/internal and ignored quota/security keys, and requires at least `ec->fragments` matching sources. Sinks receive source mode/uid/gid, extra xattrs are removed, source xattrs are copied, and `EC_XATTR_VERSION`/`EC_XATTR_DIRTY` are reconciled with `GF_XATTROP_ADD_ARRAY64`.

Entry heal first determines a source version set for the directory, then scans names on participating bricks. Each name is locked at the parent, looked up on all participants, grouped by GFID, and either stale variants are deleted, a missing name is recreated from the single surviving GFID group, or ambiguous multiple-GFID cases are left unresolved. Newly created entries are marked dirty so subsequent data/metadata heal can complete them.

Data heal opens the file on live bricks, locks the inode in the self-heal domain, reads version/dirty/size via fxattrop and fstat, chooses a source group with matching data version and logical EC size, optionally validates on-disk fragment size, marks sinks with `EC_SELFHEAL_BIT`, trims oversized sinks, then rebuilds data in aligned windows. Each window takes an fd inodelk, reads from source fragments with `ec_readv()`, writes decoded/reconstructed data to bad fragments with `ec_writev()`, and updates `heal->good`/`heal->bad` based on callback masks. After copying, the code relocks, revalidates, restores time fields, and subtracts pending version/dirty/size deltas.

Heal-info does a fast unlocked lookup/xattr inspection. If the result is ambiguous, it repeats under locks with a thorough on-disk size check, then returns a small dictionary with `"heal-info"` set to `"heal"` or `"no-heal"`.

## State and persistence behavior
The durable state repaired here is stored in brick xattrs: `EC_XATTR_VERSION`, `EC_XATTR_DIRTY`, `EC_XATTR_SIZE`, and `EC_XATTR_CONFIG`; stale index entries are purged with a zero dirty xattrop. `ec_adjust_versions()` and `__ec_fd_data_adjust_versions()` subtract per-brick pending deltas so sources and healed sinks converge. Dirty xattrs are only erased when every brick is represented by a source or healed sink, otherwise heal reports partial progress and leaves pending state. Directory entry creation writes requested GFIDs and EC config for regular files. Runtime state includes `ec_heal_t` masks, offsets, sync barrier, lock, and fd; per-inode `heal_count`; and `ec_t` background healer lists/counters.

## Dependencies and integration points
This file is tightly coupled to `ec-common` fop scheduling/combining, `ec-locks` lock reuse and inode size tracking, `ec-method` decode/write geometry, `ec-helpers` dict/loc/mask helpers, `ec-inode-read.c` for explicit `trusted.ec.heal` getxattr callbacks, `ec-inode-write.c` for write-path heals, and `ec-heald.c` for SHD sweeps. It uses Gluster syncop and cluster-syncop APIs for lookup, xattr, setattr, create, unlink, directory scans, inode locks, fd locks, open/fstat/ftruncate, and GFID-to-path operations. It also depends on EC quorum fields such as `ec->nodes`, `ec->fragments`, `ec->redundancy`, `ec->xl_up`, `ec->self_heal_window_size`, and `ec->shd.iamshd`.

## Risks and test signals
Important risks are incorrect quorum thresholds (`<= ec->fragments` versus recoverable counts), source selection when versions match but data differs, stale dictionary mutation during xattr cleanup, partial heal leaving dirty/index state inconsistent, unbounded or duplicate background heals if `heal_count` accounting slips, lock ordering between parent/name/data/metadata phases, overflow in stripe size adjustments, and ambiguous multi-GFID directory entries. Tests should cover regular-file heal with one and multiple bad fragments, sink trimming, source on-disk-size mismatch, metadata-only divergence, directory stale-name deletion, missing name recreation for directories/symlinks/regular files, multiple GFID conflict, partial directory heal, SHD no-op purge-index path, shutdown cancellation, foreground blocking versus tiebreaker background locks, heal-info under active locks, and replace-brick wake-up of index healers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heald.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heald.c

## Purpose
Implements the EC self-heal daemon worker side: per-subvolume index healers, full-sweep healers, management-operation dispatch, thread initialization, wakeups, and teardown. It turns CLI/management SHD operations and dirty-index entries into explicit `EC_XATTR_HEAL` getxattr calls on the EC xlator.

## Important APIs, types, and functions
Public functions are `ec_xl_op()`, `ec_selfheal_daemon_init()`, `ec_shd_index_healer_wake()`, and `ec_selfheal_daemon_fini()`. Locality and naming helpers are `ec_shd_is_subvol_local()` and `ec_subvol_name()`. Thread lifecycle is handled by `ec_shd_healer_init()`, `ec_shd_healer_spawn()`, `ec_shd_full_healer_spawn()`, `ec_shd_index_healer_spawn()`, `ec_shd_healer_wait()`, and `__ec_shd_healer_wait()`. Index healing uses `ec_shd_index_inode()`, `ec_shd_index_sweep()`, `ec_shd_index_heal()`, and `ec_shd_index_purge()`. Full traversal uses `ec_shd_full_sweep()` and `ec_shd_full_heal()`. `ec_shd_selfheal()` performs the actual explicit heal request and updates SHD attempted/completed counters. `ec_heal_op()` maps management heal operations to per-brick status strings and worker spawns.

## Control flow
Initialization allocates `index_healers` and `full_healers` arrays sized by `ec->nodes`, initializes each mutex/condition pair, and records the subvolume id. A spawn either signals an existing worker or creates a new `ecshd` thread, then sets `rerun`. Worker loops wait until rerun, timeout, shutdown, SHD enablement, and EC up state allow work. Index workers obtain the brick's xattrop index directory GFID from the root, resolve it to an inode, and scan the directory concurrently. Each UUID-named index entry is converted to a path/inode and healed through `syncop_getxattr(EC_XATTR_HEAL)`; stale ENOENT/ESTALE entries are unlinked from the index directory. Full workers heal the root first, then walk the entire brick namespace with `syncop_ftw()` and heal each entry with a non-null GFID.

Management calls arrive through `ec_xl_op()`, which reads `"xl-op"` and the xlator id from input, writes per-child status keys to output, and for full/index heal starts workers only for connected, local bricks while reporting remote/down states.

## State and persistence behavior
Runtime state lives in `ec->shd`: enabled flag, timeout, max thread count, wait queue length, per-subvolume `subvol_healer` arrays, `running`, `rerun`, mutexes, conditions, and threads. SHD stats increment attempted and completed counts. Persistent effects are indirect: explicit heal getxattrs mutate EC xattrs and data through `ec-heal.c`, while index purge removes stale entries from brick xattrop index directories. `EC_XATTR_HEAL_NEW` returned from directory heals forces another index sweep when new dirty entries may have been generated.

## Dependencies and integration points
Depends on `ec-heal.c` through the `EC_XATTR_HEAL` interface and on `ec-heald.h` declarations. It uses Gluster syncop helpers for locality checks, getxattr, inode find, GFID-to-path, unlink, multithreaded directory scans, and full tree walks. It integrates with management op enums `GF_SHD_OP_HEAL_FULL` and `GF_SHD_OP_HEAL_INDEX`, `protocol-common.h`, the xattrop index `GF_XATTROP_INDEX_GFID`, and `GF_CLIENT_PID_SELF_HEALD`.

## Risks and test signals
Risks include incorrect local-brick detection causing duplicate or missing work, stale index entries not purged when GFID resolution fails differently than ENOENT/ESTALE, worker threads sleeping indefinitely if rerun/condition signaling is lost, teardown destroying cond/mutex objects while threads still run, and fragile parsing of heal completion strings. Tests should exercise management output for local/remote/down bricks, index sweep stale-entry purge, directory heal causing `EC_XATTR_HEAL_NEW` rerun, full sweep cancellation/cleanup, disabled SHD wait behavior, shutdown wakeup, and stats increments only on completed heals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heald.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heald.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heald.h

## Purpose
Declares the EC self-heal daemon interface used outside `ec-heald.c`: management operation dispatch, daemon lifecycle, and index-healer wakeup after replacement or new dirty-index work.

## Important APIs, types, and functions
`ec_xl_op(xlator_t *this, dict_t *input, dict_t *output)` handles SHD management requests such as full and index heals. `ec_selfheal_daemon_init(xlator_t *this)` allocates and initializes per-brick healer objects. `ec_shd_index_healer_wake(ec_t *ec)` wakes index healer threads for currently up bricks. `ec_selfheal_daemon_fini(xlator_t *this)` tears down SHD healer objects.

## Control flow
The EC translator initializes SHD structures during xlator startup, accepts management operations through `ec_xl_op()`, wakes index workers when dirty index processing should resume, and finalizes worker synchronization objects on shutdown when running as self-heald.

## State and persistence behavior
The header does not define state directly, but its functions operate on `ec_t`, `ec_self_heald_t`, and `struct subvol_healer` state declared in `ec-types.h`. Persistence is indirect through the daemon's heal operations and index purges.

## Dependencies and integration points
Includes `ec-types.h`, Gluster dictionaries, globals, and `xlator_t`. It is included by `ec-heal.c` for `ec_shd_index_healer_wake()` after replace-brick heal, by `ec-heald.c` for its own public definitions, and by EC translator setup/management code for lifecycle and `xl-op` routing.

## Risks and test signals
The surface is small, but ABI/API drift between this header and `ec-heald.c` would break SHD startup or management heal commands. Tests should confirm startup/fini calls are guarded by SHD mode, `ec_xl_op()` recognizes expected management operation dictionaries, and replace-brick paths can call the wake function without circular initialization problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heald.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-helpers.c

## Purpose
Provides common utility routines for the EC translator: tracing, binary mask formatting, aligned iobuf allocation, endian-safe EC xattr encode/decode helpers, `loc_t` normalization, lock-owner helpers, per-inode and per-fd context allocation, internal xattr filtering, and read-mask parsing.

## Important APIs, types, and functions
`ec_bin()` formats bitmasks for logs and heal status. `ec_fop_name()` maps negative EC pseudo-fops and normal GF fops to names. `ec_trace()` emits detailed per-fop trace state. `ec_iov_copy_to()` copies a range out of an iovec array. `ec_buffer_alloc()` allocates page-aligned, EC-word-aligned iobuf storage and attaches it to an iobref. Dictionary helpers are `ec_dict_set_array()`, `ec_dict_get_array()`, `ec_dict_del_array()`, `ec_dict_set_number()`, `ec_dict_del_number()`, `ec_dict_set_config()`, and `ec_dict_del_config()`. Location helpers are `ec_loc_parent()`, `ec_loc_update()`, `ec_loc_from_fd()`, and `ec_loc_from_loc()`, backed by `ec_loc_gfid_check()`, `ec_loc_setup_inode()`, `ec_loc_setup_parent()`, and `ec_loc_setup_path()`. Context helpers are `__ec_inode_get()`, `ec_inode_get()`, `__ec_fd_get()`, `ec_fd_get()`, `ec_inode_readmask_set()`, and `ec_inode_readmask_get()`. Xattr/read-mask helpers are `ec_is_internal_xattr()`, `ec_filter_internal_xattrs()`, `ec_is_readmask_xattr()`, and `ec_parse_read_mask()`.

## Control flow
Most functions are leaf utilities. Dict setters allocate ownership-transferred big-endian buffers and install them into Gluster dictionaries; getters validate size and convert from big-endian, including backward compatibility for older single-version EC xattrs by replicating the old value across requested slots. Config helpers pack/unpack version, algorithm, GF word size, brick count, redundancy, and chunk size into one 64-bit xattr value. Loc helpers reconcile inode, parent, path, GFID, and name fields from the best available source and reject GFID/name mismatches. Context getters allocate translator-private inode/fd structures under caller-held locks or wrapper locks, initialize heal lists, stripe cache metadata, fd status per brick, and anonymous-fd open masks. Read-mask parsing tokenizes colon-separated brick ids, validates range and minimum fragment count, and returns a bitmask.

## State and persistence behavior
The helper functions directly encode persistent EC xattr wire formats: version/dirty arrays, size numbers, and EC config are stored as big-endian binary dictionary values. `ec_dict_del_*` helpers remove decoded keys from dictionaries as part of combine/rebuild processing. In-memory state includes inode ctx `read_mask`, `heal_count`, `bad_version`, and stripe cache list, plus fd ctx open flags, fd status array, bad-version snapshot, and cached loc. `ec_filter_internal_xattrs()` removes `EC_XATTR_PREFIX` keys from user-visible dicts.

## Dependencies and integration points
Used across EC read/write/heal/common/lock code. Depends on Gluster dict, inode/fd ctx, iobuf/iobref, UUID, path resolution, logging, memory types, GF endian helpers, `ec-types.h`, `ec-method.h`, and constants from `ec.h`. The read-mask helpers are called from option/xattr paths in `ec.c`; context helpers are used by open/read/write/heal code; dict helpers are central to xattr combine and self-heal state reconciliation.

## Risks and test signals
Risks include ownership mistakes for dictionary binary buffers, endian or legacy-version decode regressions, `dirname()` path mutation corner cases, accepting inconsistent `loc_t` GFIDs, anonymous fd state leaking to all subvolumes unexpectedly, stale inode read masks, and read-mask parsing accepting too few bricks. Tests should cover config pack/unpack boundaries and unsupported versions, old one-slot version xattr decode, malformed xattr lengths, parent/path/root/gfid loc combinations, fd ctx initialization for anonymous and normal fds, iobuf alignment, internal xattr filtering, and read-mask invalid tokens/ranges/fragment-count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-helpers.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-helpers.h

## Purpose
Declares EC utility APIs and inline stripe-alignment helpers shared by the EC translator implementation.

## Important APIs, types, and functions
Macros `EC_ERR()`, `EC_IS_ERR()`, and `EC_GET_ERR()` encode small negative errors as pointers. `EC_ALIGN_CHECK()` checks required memory alignment. Function declarations cover tracing, iov copying, aligned buffer allocation, dict xattr encode/decode, loc normalization, owner assignment, inode/fd context lookup, inode read-mask access, internal xattr filtering, replace-heal launch, and read-mask parsing. Inline geometry helpers are `ec_adjust_size_down()`, `ec_adjust_size_up()`, `ec_adjust_offset_down()`, and `ec_adjust_offset_up()`. `ec_is_power_of_2()` supports option/config validation.

## Control flow
The inline adjustment helpers convert user-visible logical sizes/offsets into EC stripe or fragment boundaries. Down-adjust returns the head remainder and optionally divides by `ec->fragments`. Up-adjust rounds to the next stripe/fragment boundary, returning the tail bytes needed; the size variant marks unsigned overflow by setting `UINT64_MAX` and returning a negative tail, while the offset variant clamps to `GF_OFF_MAX` on signed overflow.

## State and persistence behavior
The header itself stores no state, but its dict APIs define the persistent representation of EC xattrs and its adjustment helpers control how logical file sizes, brick fragment offsets, and heal/truncate/read sizes are interpreted throughout the translator.

## Dependencies and integration points
Included by EC heal, read, write, common, and translator setup code. It depends on `ec-types.h` for `ec_t`, `ec_config_t`, fd/inode contexts, and fop types. Its prototypes bridge source files that otherwise share no implementation unit, especially `ec-heal.c`, `ec-inode-read.c`, and `ec.c`.

## Risks and test signals
The alignment helpers are high impact: an off-by-one or overflow bug can corrupt read ranges, write ranges, heal windows, and size xattrs. Tests should cover aligned and unaligned sizes/offsets, scaled and unscaled conversions, near-`UINT64_MAX` and near-`GF_OFF_MAX` values, zero stripe edge assumptions, pointer-error macro round trips, and header/implementation signature consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-inode-read.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-inode-read.c

## Purpose
Implements EC translator inode/fd read-side fops: `access`, `getxattr`, `fgetxattr`, `open`, `readlink`, `readv`, `seek`, `stat`, and `fstat`. It dispatches operations to enough bricks, combines responses, rebuilds user-visible metadata/data from fragment geometry, filters internal EC xattrs, and exposes explicit self-heal via `trusted.ec.heal`.

## Important APIs, types, and functions
Each fop has a public entry, wind callback, callback, combine helper where needed, and manager state machine. `ec_access()` uses `ec_manager_access()`. `ec_getxattr()` and `ec_fgetxattr()` use `ec_manager_getxattr()`, `ec_combine_getxattr()`, `ec_handle_special_xattrs()`, and `ec_getxattr_heal_cbk()`. `ec_open()` uses `ec_manager_open()`, `ec_combine_open()`, and `ec_open_truncate_cbk()`. `ec_readlink()` uses `ec_manager_readlink()` and `ec_combine_readlink()`. `ec_readv()` uses `ec_manager_readv()`, `ec_combine_readv()`, and `ec_readv_rebuild()`. `ec_seek()` uses `ec_manager_seek()`. `ec_stat()` and `ec_fstat()` share `ec_manager_stat()` and `ec_combine_stat()`.

## Control flow
Public fops allocate `ec_fop_data_t`, copy loc/fd/xdata/name/flags into it, then call `ec_manager()`. Managers acquire shared EC locks for query operations, dispatch to one, minimum, or all bricks depending on the operation, prepare a combined answer, invoke the user callback, reuse locks if possible, and unlock. `getxattr(EC_XATTR_HEAL)` bypasses normal getxattr dispatch and calls `ec_heal()`, then `ec_getxattr_heal_cbk()` formats a `"Good: ..., Bad: ..."` dictionary and returns pending directory-heal count in xdata. Normal getxattr/fgetxattr combines dictionaries, handles special stime xattrs where any successful answer can be accepted, and strips internal EC xattrs before returning to callers.

`open` initializes fd context, stores original flags, removes `O_APPEND` for EC offset writes, defers `O_TRUNC` into a later `ec_ftruncate()`, dispatches open to all needed bricks, and records the open mask. `readv` maps logical user offset/size to fragment offset/size using EC alignment helpers, optionally intersects dispatch mask with inode-specific or volume read mask, dispatches the minimum fragment set, combines and rebuilds iatts, decodes fragments with `ec_method_decode()`, trims head/tail back to the requested logical range and inode size, and returns a single rebuilt iovec. `seek` scales offsets between logical and fragment space and clamps results to logical file size. `stat`/`fstat` dispatch to all, combine iatts, rebuild regular-file size, and retrieve cached inode size under lock.

## State and persistence behavior
This file mostly manages transient fop state, callback lists, iobuf references, fd refs, xdata refs, and locks. It updates fd context open masks/status through `ec_update_fd_status()` and `__ec_fd_get()`. Persistent effects are limited: `open` with `O_TRUNC` triggers a write-side truncate after open; explicit heal getxattr can repair data and xattrs through `ec-heal.c`. User-visible xattr state is filtered so internal EC keys do not leak from normal getxattr responses.

## Dependencies and integration points
Depends on `ec-common` for fop allocation, dispatch, retries, answer selection, lock reuse, complete/resume/sleep, and fd status; `ec-combine` for dict/vector/iatt comparisons and EC dict combine; `ec-locks` through lock prepare helpers; `ec-method` for decode; `ec-helpers` for tracing, iobuf allocation, alignment, loc/fd/inode context, and xattr filtering; and `ec-heal.c` for explicit heal. It is wired into top-level `ec.c` FOP tables and used internally by heal and write code for reconstructive reads.

## Risks and test signals
Risks include returning mismatched dictionaries or vectors as valid, leaking internal EC xattrs, read-mask reducing available fragments below decode needs, off-by-one trimming around unaligned read heads/tails, decoding from non-word-aligned iovecs, fragment-size modulo checks rejecting valid short EOF reads, `O_TRUNC` ordering after open, stale cached inode sizes, and `seek` scaling errors near EOF. Tests should cover getxattr heal status formatting and pending count, stime partial success, node UUID list name rewrite, fgetxattr shared manager behavior, open with append/truncate flags, readv aligned/unaligned/range-at-EOF cases, read masks at volume and inode level, vector mismatch detection, stat/fstat size rebuild, and seek data/hole scaling and ENXIO handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-inode-read.c -->
