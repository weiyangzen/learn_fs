# Research: subset-b-007131

Grouped research for GlusterFS POSIX storage translator files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-common.c -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-common.c

## Purpose
`posix-common.c` owns the lifecycle and option surface of the `storage/posix` translator. It validates the brick export directory, initializes persistent POSIX translator state, creates the hidden GFID handle hierarchy, starts background janitor/fsync/health/disk-space services, handles runtime reconfiguration, exposes statedump data, and tears the translator down.

## Important APIs, Types, And Functions
- `posix_priv(xlator_t *this)` writes statedump fields from `struct posix_private`, notably `base_path`, `base_path_length`, and atomic read/write maxima.
- `posix_notify()` forwards `GF_EVENT_PARENT_UP` as `GF_EVENT_CHILD_UP` and handles parent-down cleanup when graph shutdown starts.
- `mem_acct_init()` initializes translator memory accounting with `gf_posix_mt_end`.
- `posix_reconfigure()` applies settable volume options to an existing `struct posix_private`.
- `posix_init()` is the main constructor for `storage/posix`.
- `posix_fini()` is the destructor.
- `posix_options[]` declares the translator's volume options and defaults.
- Local helpers include `delete_posix_diskxl()`, `posix_set_owner()`, `set_gfid2path_separator()`, `set_batch_fsync_mode()`, Darwin-only `set_xattr_user_namespace_mode()`, and helpers for `.glusterfs/unlink`.

## Control Flow
Initialization starts by rejecting subvolumes, requiring a `directory` option, clearing process umask, and verifying the export path is an existing directory. It allocates `struct posix_private`, records the base path, reads filesystem block size, initializes fd arrays, derives hostname, and verifies xattr support depending on `mandate-attribute`.

Volume identity is enforced through `trusted.glusterfs.volume-id`. The export root GFID is verified as the GlusterFS root GFID or created as `trusted.gfid` on first use. ACL support is probed. The code may `chdir()` into the brick when base path length plus POSIX path requirements could exceed filesystem path capacity.

After core validation, `posix_init()` initializes locks, atomics, option fields, and open fds. It opens the brick directory as `mount_lock`, creates/opens `.glusterfs` and each first-level hash directory fd in `arrdfd[256]`, calls `posix_handle_init()`, sets up trash/landfill with `posix_handle_trash_init()`, and creates/clears the `.glusterfs/unlink` directory. It then enables optional AIO/io_uring, disk reserve checking, health checking, janitor timers, context janitor, and the fsync aggregation thread.

Reconfiguration re-reads options through `GF_OPTION_RECONF`, updates ownership, fsync mode and delay, gfid2path behavior, node pathinfo behavior, link-count xattrs, AIO/io_uring, disk reserve and related thread registration, health checking, landfill purge, creation masks, hardlink limits, FIPS checksum mode, and ctime mode.

Shutdown cancels health, janitor, disk-space, and fsync threads/timers, closes `.glusterfs` directory fds, closes `mount_lock`, releases strings and locks, and frees `struct posix_private`.

## State And Persistence Behavior
Persistent state on the brick includes `trusted.glusterfs.volume-id`, root `trusted.gfid`, the `.glusterfs` GFID handle hierarchy, `.glusterfs/landfill`, and `.glusterfs/unlink`. Runtime state in `struct posix_private` includes base path metadata, directory fds for hashed GFID lookup, locks, condition variables, janitor/fsync/health/disk-space thread handles, disk reserve thresholds, create masks, ctime mode, `gfid2path` configuration, `update_pgfid_nlinks`, and `max_hardlinks`.

The hidden directory is intentionally reserved for translator housekeeping. It is created with restrictive permissions and then used by handle code and entry operations to map GFIDs to backend paths.

## Dependencies And Integration Points
This file integrates with `posix-handle.c` through `posix_handle_init()` and `posix_handle_trash_init()`, with async I/O through `posix_aio_on/off()` and `posix_io_uring_on/off()`, with background services through `posix_spawn_*` helpers, with Gluster eventing through `gf_event()`, and with xlator option parsing through `GF_OPTION_INIT` and `GF_OPTION_RECONF`.

It depends heavily on Gluster wrappers such as `sys_*`, `gf_msg`, `gf_thread_create`, `gf_tw_del_timer`, `dict_get*`, and `GF_ATOMIC_*`.

## Risks And Edge Cases
- Partial initialization has a large cleanup surface: fd arrays, `mount_lock`, `base_path`, `trash_path`, and background thread state must be released on every failure path.
- Reconfiguring disk reserve deletes/recreates disk-space tracking state; races here can affect shutdown and reserve enforcement.
- The xattr mandate check treats lack of xattr support as fatal unless explicitly allowed.
- Hidden handle directory creation and fd caching are required for later entry operations; failures make the brick unusable.
- `posix_create_unlink_dir()` deletes an existing unlink directory at startup; if stale open-fd tracking is incorrect, this can affect cleanup semantics.
- Several options change persistent metadata behavior (`gfid2path`, `update-link-count-parent`, `ctime`, create masks), so mixed-version or mid-run changes need regression coverage.

## Test Signals
Useful tests should cover first-brick initialization, volume-id mismatch, missing or wrong root GFID, no-xattr backends with `mandate-attribute` on/off, `.glusterfs` creation, all 256 hash fd opens, reconfigure toggles for AIO/io_uring/gfid2path/disk reserve/health check, hidden directory protection through entry ops, failed partial init cleanup, and shutdown under live janitor/disk-space/fsync activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-entry-ops.c -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-entry-ops.c

## Purpose
`posix-entry-ops.c` implements namespace-mutating and namespace-resolving FOPs for the POSIX storage translator: lookup, mknod, mkdir, unlink, rmdir, symlink, rename, link, create, and put. It bridges Gluster inode/GFID semantics to backend filesystem paths, xattrs, hidden GFID handles, ctime metadata, DHT linkfile behavior, and pre/post parent attribute reporting.

## Important APIs, Types, And Functions
- `posix_lookup()` resolves named and nameless locations, fills iatt/xattrs, heals GFIDs, handles stale GFID handles, and supports special unlinked-file lookup.
- `posix_mknod()`, `posix_mkdir()`, `posix_symlink()`, and `posix_create()` create entries, set ownership/modes/ACLs/xattrs/GFIDs, update ctime, and unwind parent attrs.
- `posix_unlink()` and helper `posix_unlink_gfid_handle_and_entry()` remove entries and GFID handles, with open-fd preservation through `.glusterfs/unlink`.
- `posix_rmdir()` removes directories or moves them to landfill/trash depending on flags.
- `posix_rename()` handles replacement semantics, GFID handle updates, pgfid/gfid2path xattr migration, victim handle cleanup, and parent ctime updates.
- `posix_link()` creates hardlinks while respecting `max_hardlinks`, pgfid link-count xattrs, and optional gfid2path xattrs.
- `posix_put()` sequences create/write/fsetxattr/flush through syncops.
- Local helpers manage gfid2path xattrs, ACL xattrs, DHT stale linkto removal, non-linkto unlink skipping, symlink-handle matching, and link-count response xdata.

## Control Flow
Every public FOP validates core arguments and then translates Gluster locs to backend paths using `MAKE_ENTRY_HANDLE()` or `MAKE_INODE_HANDLE()`. Most mutating operations take pre-operation parent stats, perform the backend syscall, set or adjust metadata, take post-operation parent stats, update ctime/parent ctime, and unwind through `STACK_UNWIND_STRICT`.

`posix_lookup()` blocks direct lookup of `.glusterfs` and NetBSD `.attribute`, supports nameless lookups through GFID handles, can check `.glusterfs/unlink` when `GF_UNLINKED_LOOKUP` is requested, heals GFID metadata when a named lookup lacks an inode GFID, fills requested xattrs, performs cloudsync maintenance, optionally clears external-write protection, initializes parent-GFID link-count xattrs, and returns postparent attributes.

Create-like paths validate requested GFIDs via `GFID_NULL_CHECK_AND_GOTO`, enforce disk reserve via `DISK_SPACE_CHECK_AND_GOTO`, apply create masks and forced mode bits, honor parent SGID, optionally replace stale DHT linkto files when `GF_FORCE_REPLACE_KEY` is present, set ACL xattrs, set entry xattrs, set `trusted.gfid`, update ctime, and roll back created filesystem entries/GFID xattrs on failure.

Unlink and rename flows are more stateful. Unlink may refuse to remove open files when DHT requests it, may skip non-linkto entries, may open the file to preserve fdstat/background unlink behavior, adjusts pgfid/gfid2path xattrs for multi-link files, unlinks or moves GFID handles depending on open fd count, returns block/link-count xdata, and updates parent ctime. Rename updates old/new parent stats, detects target victims, locks per-inode pgfid state, migrates pgfid/gfid2path xattrs, cleans up overwritten victim handles, recreates directory symlink handles, and reports victim link/block data where requested.

## State And Persistence Behavior
The file mutates backend namespace entries, `trusted.gfid`, ACL xattrs, Gluster entry-create xattrs, ctime metadata xattrs, parent-GFID hardlink count xattrs (`PGFID_XATTR_KEY_PREFIX`), gfid2path xattrs (`GFID2PATH_XATTR_KEY_PREFIX`), DHT linkto xattrs, `.glusterfs` GFID handles, `.glusterfs/unlink` temporary links for open deleted files, and `.glusterfs/landfill` directory moves.

Runtime state includes fd contexts (`struct posix_fd`), inode ctx pgfid locks, inode open-fd counts, inode unlink flags, and xdata request/response dictionaries. The code frequently uses backend xattrs as durable coordination state for upper translators and healing.

## Dependencies And Integration Points
This file depends on `posix-handle.h` macros/functions for path construction and GFID handle manipulation, `posix-gfid-path.h` for gfid2path virtual xattr behavior, `posix-metadata.h` for ctime, Gluster dict/xdata keys for DHT/AFR/cloudsync/trash semantics, syscall wrappers for backend operations, and inode/fd context helpers from the POSIX translator.

Upper translators integrate through xdata keys such as `GF_GFIDLESS_LOOKUP`, `GF_UNLINKED_LOOKUP`, `GF_FORCE_REPLACE_KEY`, `DHT_SKIP_OPEN_FD_UNLINK`, `DHT_SKIP_NON_LINKTO_UNLINK`, `DHT_IATT_IN_XDATA_KEY`, `GET_LINK_COUNT`, `GF_GET_FILE_BLOCK_COUNT`, and preop layout/check keys.

## Risks And Edge Cases
- Namespace operations have multi-step persistence with limited rollback. Failures after backend creation but before all xattrs/GFID handles are set can leave inconsistent metadata.
- `posix_put()` explicitly notes missing atomicity and rollback for create/write/xattr/flush.
- `posix_rename()` combines two inode pgfid locks, replacement cleanup, and GFID handle mutation; lock ordering and failure after rename are high-risk.
- gfid2path and pgfid xattr updates are optional but persistent; disabling/enabling options mid-run can leave mixed metadata.
- Unlink must distinguish no-open-fd deletion from open-fd preservation; incorrect fd counts or unlink flags can orphan or prematurely remove data.
- Hardlink behavior must stay below `max_hardlinks` and `MAX_GFID2PATH_LINK_SUP` for gfid2path metadata.
- Hidden `.glusterfs` and NetBSD `.attribute` protection must remain intact for lookup/mkdir/rmdir.
- Several helper calls intentionally allow unlink to continue on absent pgfid/gfid2path xattrs; tests should assert intended tolerance.

## Test Signals
Regression coverage should include named and nameless lookup, stale GFID handle cleanup, lookup of `.glusterfs`, GFID heal, mkdir with duplicate GFID, create/mknod with internal DHT linkfile behavior, stale linkto replacement, ACL xattr propagation, parent SGID inheritance, pgfid link-count update on create/link/unlink/rename, gfid2path add/remove/rename/link limits, unlink with open fds and background unlink, rmdir landfill moves, rename over files and directories, max-hardlink enforcement, ctime updates, preop layout/check failures, and put failure paths after each syncop step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-entry-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-gfid-path.c -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-gfid-path.c

## Purpose
`posix-gfid-path.c` implements support for the virtual `glusterfs.gfidtopath` style xattr. It detects internal gfid2path xattr names and resolves stored parent-GFID/basename metadata back into user-visible paths.

## Important APIs, Types, And Functions
- `posix_is_gfid2path_xattr(const char *name)` returns true for xattr names with `GFID2PATH_XATTR_KEY_PREFIX`.
- `posix_get_gfid2path(xlator_t *this, inode_t *inode, const char *real_path, int *op_errno, dict_t *dict)` populates `GFID2PATH_VIRT_XATTR_KEY` in a response dict.
- Static `gf_posix_xattr_enotsup_log` throttles repeated unsupported-xattr warnings.
- The implementation uses `MAX_GFID2PATH_LINK_SUP`, `posix_resolve_dirgfid_to_path()`, `sys_llistxattr()`, `sys_lgetxattr()`, `dict_set_dynstr()`, and `dict_set_dynptr()`.

## Control Flow
For directories, `posix_get_gfid2path()` resolves the directory GFID directly through `posix_resolve_dirgfid_to_path()` using the brick base path and stores the resulting path string in the dict.

For non-directories, it lists all xattrs on `real_path`. It first attempts an 8 KiB stack buffer and falls back to a size-query plus heap allocation on `ERANGE`. Unsupported xattrs produce an occasional warning; other list failures are logged as errors. The function scans the NUL-separated xattr list, filters names through `posix_is_gfid2path_xattr()`, fetches each matching xattr value, parses the first 36 bytes as a parent GFID string, treats the substring at offset 37 as the basename, resolves parent GFID plus basename to a path, and accumulates paths in `paths[]`.

If no gfid2path xattr is found, it returns `ENODATA`. If matching xattrs are found but no value can be resolved, it errors. Otherwise it concatenates resolved paths with `priv->gfid2path_sep` and stores the joined value as `GFID2PATH_VIRT_XATTR_KEY`.

## State And Persistence Behavior
The file reads persistent gfid2path xattrs created by entry operations. Each xattr key is a prefixed hash, and each value is encoded as `parent-gfid/basename`. The returned virtual xattr is not persisted by this file; it is synthesized into a dict for the caller. Heap-owned strings are transferred to dict ownership on success and freed on error.

## Dependencies And Integration Points
Entry operations create and remove gfid2path xattrs. This file is consumed by xattr filling logic elsewhere in the POSIX translator when callers request the virtual path xattr. It relies on `struct posix_private` for `base_path` and `gfid2path_sep`, Gluster dict ownership conventions, GF memory allocators, and backend xattr wrappers.

## Risks And Edge Cases
- `paths` is sized to `MAX_GFID2PATH_LINK_SUP`, but the scan increments `i` for every matching xattr without an obvious bounds check; a file with more matching xattrs than the supported maximum risks array overflow.
- Xattr value parsing assumes at least 37 bytes and a `parent-gfid/basename` layout; malformed values can produce incorrect parse/resolution behavior.
- The initial 8 KiB xattr buffers handle common cases, but very large xattr sets require the ERANGE path.
- `dict_set_dynptr()` receives `bytes` rather than `bytes + 1`; callers must treat the value length correctly even though the buffer is NUL-terminated.
- Error handling intentionally reports `ENODATA` when no gfid2path xattr exists, which differs from returning an empty path.

## Test Signals
Tests should request gfid2path for directories, single-link files, hardlinked files with multiple gfid2path xattrs, missing xattrs, unsupported xattr backends, ERANGE listxattr fallback, malformed/truncated xattr values, custom separators, and files exceeding `MAX_GFID2PATH_LINK_SUP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-gfid-path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-gfid-path.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-gfid-path.h

## Purpose
`posix-gfid-path.h` declares the POSIX translator interface for gfid2path virtual xattr support and defines the hardlink support limit used by the implementation.

## Important APIs, Types, And Functions
- `MAX_GFID2PATH_LINK_SUP` is defined as `500`, the supported number of gfid2path link records.
- `posix_is_gfid2path_xattr(const char *name)` identifies internal gfid2path xattr names.
- `posix_get_gfid2path(xlator_t *this, inode_t *inode, const char *real_path, int *op_errno, dict_t *dict)` resolves gfid2path metadata into a dict response.
- Included types are `int32_t`, `dict_t`, `gf_boolean_t`, and `inode_t`.

## Control Flow
The header has no executable control flow. It exposes two functions for callers that need to filter backend xattrs or synthesize the virtual gfid-to-path xattr.

## State And Persistence Behavior
The header does not mutate state. Its constant constrains how much hardlink/gfid2path state should be considered supported by implementation and entry-op code.

## Dependencies And Integration Points
The declarations integrate `posix-gfid-path.c` with xattr filling logic and with entry operations that create/remove gfid2path metadata. It depends on Gluster public headers for dict, inode, and boolean definitions.

## Risks And Edge Cases
- The `MAX_GFID2PATH_LINK_SUP` contract must match all producers and consumers; if producers allow more records than consumers safely handle, memory safety and incomplete virtual xattr results are possible.
- Callers must pass a valid `op_errno` pointer and dict with appropriate ownership expectations.

## Test Signals
Header-level test signals come from compile coverage and from behavior tests that assert the 500-link limit is consistently enforced across link creation, gfid2path xattr creation, and virtual xattr retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-gfid-path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-handle.c -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-handle.c

## Purpose
`posix-handle.c` implements the GFID handle layer for the POSIX translator. It creates and resolves `.glusterfs/<hash>/<hash>/<gfid>` handles, maps GFIDs back to paths, builds ancestry entries, initializes trash/landfill state, and maintains hardlink or symlink handles for files and directories.

## Important APIs, Types, And Functions
- `posix_resolve()` resolves a parent GFID plus basename into an inode and iatt.
- `posix_make_ancestryfromgfid()` walks directory symlink handles from a GFID back to root and builds a path and optional dirent list.
- `posix_handle_relpath()` formats relative symlink targets such as `../../xx/yy/gfid[/basename]`.
- `posix_handle_path()` returns a backend path suitable for stat of the represented object and pumps directory symlink handles to avoid `ELOOP`.
- `posix_handle_gfid_path()` returns the actual GFID handle path.
- `posix_handle_init()` creates/verifies `.glusterfs` and the root GFID handle.
- `posix_handle_trash_init()` initializes `.glusterfs/landfill` and migrates old `.landfill` state.
- `posix_handle_hard()` creates/verifies hardlink handles for regular files.
- `posix_handle_soft()` creates symlink handles for directories.
- `posix_handle_unset_gfid()` removes a GFID handle.
- `posix_create_link_if_gfid_exists()` links a new namespace path to an existing GFID handle or resurrects an unlinked-open file from `.glusterfs/unlink`.

## Control Flow
Handle initialization verifies the export path, creates `.glusterfs` if missing, records the hidden directory inode/dev, and ensures the root GFID handle points back to the export root through a symlink target of `../../..`. It uses the per-first-byte directory fd cache from `struct posix_private` and creates second-level hash directories on demand.

`posix_handle_path()` first formats the direct hidden GFID handle path. If the handle is a single-link symlink, it repeatedly reads and expands the symlink target through `posix_handle_pump()` until `lstat()` no longer fails with `ELOOP`. The pump validates internal symlink syntax through `posix_is_malformed_link()` before modifying the path buffer.

`posix_make_ancestryfromgfid()` follows directory handles upward by reading symlink targets, extracting parent GFIDs and names, stacking path components until root, then resolving back down through `posix_resolve()` and optionally appending dirents with xattrs.

Hard handles are backend hardlinks from `.glusterfs` to regular files. Soft handles are symlinks for directories that point to parent GFID plus basename. Removing a GFID handle uses `unlinkat()` against the cached hash directory fd. Creating a link for an existing GFID first tries the normal GFID handle; if absent, it checks inode ctx unlink state and links/renames from `.glusterfs/unlink`.

## State And Persistence Behavior
Persistent state includes `.glusterfs`, two-level hash directories, root GFID symlink, regular-file hardlink handles, directory symlink handles, `.glusterfs/landfill`, migrated old `.landfill` directories, and `.glusterfs/unlink` recovery targets used by entry operations. Runtime state includes cached directory fds in `priv->arrdfd`, hidden directory inode/dev, inode references, inode ctx unlink flags, and path buffers built on stack through `alloca`.

The handle layer is central to GFID stability: namespace paths may change, but GFID handles provide nameless lookup, healing, rename, unlink, and ancestry reconstruction.

## Dependencies And Integration Points
This file is called from `posix-common.c` during initialization and from `posix-entry-ops.c` during lookup, create, mkdir, unlink, rename, rmdir, and hardlink operations. It depends on `posix-inode-handle.h` macros, `posix.h`, `posix-metadata.h`, Gluster inode tables, syscall wrappers, UUID helpers, and POSIX translator private state.

## Risks And Edge Cases
- Directory symlink expansion must reject malformed internal links; bad validation can produce path corruption or traversal errors.
- `posix_make_ancestryfromgfid()` bounds ancestry by `PATH_MAX / 2`; very deep trees fail with `EINVAL`.
- Hardlink handles require inode/dev equality with the source. Mismatches indicate serious backend inconsistency.
- `posix_create_link_if_gfid_exists()` performs recovery under inode lock, but it spans link and rename operations involving `.glusterfs/unlink`; interruption can leave duplicate or stale recovery state.
- Extensive use of `alloca` makes size calculations important for long base paths and names.
- Root GFID handle verification must distinguish the export root from any stale or wrong hidden handle.

## Test Signals
Tests should cover first initialization of `.glusterfs`, existing valid and invalid root handles, regular-file hard handle creation, directory soft handle creation, malformed symlink target rejection, ELOOP pumping, ancestry reconstruction for shallow and deep paths, trash migration from old `.landfill`, GFID handle removal, create-link-if-GFID-exists for normal handles and unlinked-open recovery, and inode/dev mismatch detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-handle.h -->
# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-handle.h

## Purpose
`posix-handle.h` declares the POSIX GFID handle interface and defines macros for handle path construction, parent-GFID xattr key construction, parent-GFID link-count xattr mutation, and entry handle construction.

## Important APIs, Types, And Functions
- `HANDLE_ABSPATH_LEN(this)` computes enough space for absolute GFID handle paths.
- `MAKE_PGFID_XATTR_KEY()` builds a parent-GFID xattr key from a prefix and parent GFID.
- `SET_PGFID_XATTR`, `SET_PGFID_XATTR_IF_ABSENT`, `REMOVE_PGFID_XATTR`, `LINK_MODIFY_PGFID_XATTR`, and `UNLINK_MODIFY_PGFID_XATTR` implement big-endian link-count xattr updates.
- `MAKE_HANDLE_GFID_PATH`, `MAKE_HANDLE_RELPATH`, `MAKE_HANDLE_ABSPATH`, and `MAKE_HANDLE_ABSPATH_FD` construct handle paths or fd-relative names.
- `MAKE_ENTRY_HANDLE()` resolves a `loc_t` into parent and entry backend paths, with special handling for absolute paths and `ELOOP` expansion.
- Declared functions include `posix_handle_gfid_path()`, `posix_handle_hard()`, `posix_handle_soft()`, `posix_handle_unset_gfid()`, `posix_create_link_if_gfid_exists()`, `posix_check_internal_writes()`, `posix_disk_space_check()`, and `_fill_writev_xdata()`.

## Control Flow
The header's macro flow is significant. Parent-GFID xattr macros read, endian-convert, increment/decrement, set, or remove xattrs and jump to caller-provided labels on hard errors. `MAKE_ENTRY_HANDLE()` validates `pargfid` and `name`, rejects embedded slashes, handles absolute locs through `MAKE_REAL_PATH()` and `posix_pstat()`, otherwise tries `posix_istat()` and constructs parent/entry handle paths unless `errno == ELOOP`, in which case the caller can expand through handle logic.

## State And Persistence Behavior
The macros mutate persistent pgfid link-count xattrs on backend entries. The values are stored as big-endian 32-bit counters. Handle path macros do not persist state themselves but encode the `.glusterfs/<gfid[0]>/<gfid[1]>/<uuid>` layout used by `posix-handle.c` and entry operations.

## Dependencies And Integration Points
This header is included by entry and handle code. It relies on `posix-inode-handle.h`, `posix.h`, UUID helpers, syscall wrappers, `struct posix_private`, `loc_t`, `inode_t`, Gluster logging, and predefined xattr prefixes. Its macros assume caller-local variables such as `op_ret` and `op_errno` exist.

## Risks And Edge Cases
- The macros use `alloca`; incorrect length calculations or unexpectedly long names can exhaust stack.
- PGFID xattr macros jump to caller labels and depend on caller lock discipline. The link/unlink modify macros explicitly require a lock.
- Counter updates are read-modify-write on xattrs; missing locks or cross-process races can corrupt counts.
- `UNLINK_MODIFY_PGFID_XATTR` decrements an unsigned-ish integer path and removes the xattr at zero; underflow or missing xattr handling must be guarded by callers.
- `MAKE_ENTRY_HANDLE()` sets `op_ret` on some validation failures but mostly communicates through caller-visible variables and `errno`, making misuse easy.

## Test Signals
Compile coverage should exercise all macro call sites. Behavioral tests should validate pgfid counter creation, increment, decrement, removal at zero, absent-xattr tolerance, endian correctness, path construction for normal and absolute locs, rejection of names containing `/`, root/hidden path behavior through entry ops, and lock-protected concurrent hardlink/unlink/rename operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-handle.h -->
