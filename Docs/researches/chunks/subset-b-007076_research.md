# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-common.c lines 8293-11618

## Scope

This chunk covers the middle-late DHT common FOP implementation for GlusterFS. It starts in the tail of `dht_link_cbk()` and then implements hard-link retry during migration, file create placement and parent-layout validation, distributed directory creation, distributed directory removal, entry locks, IPC fan-out for upcall targeting, inode context cleanup, child event notification, layout/rebalance helper routines, release cleanup, pass-through directory/xattr helpers, and a final directory-layout error checker.

The code is control-plane-heavy for DHT: it decides which child translator gets a file FOP, when to create linkto files, when to refresh or validate directory layout xattrs, how to guard namespace changes with entry/inode locks, and when to fan operations out to every subvolume. It also owns several callbacks that merge per-child status and attributes before unwinding the original Gluster FOP stack.

## Purpose

The main purpose of this chunk is to keep DHT's distributed namespace coherent while handling namespace-mutating operations:

- `link` and `create` place files on the cached/hashed subvolume, create linkto files when data is placed elsewhere, and retry or redirect when rebalance migration flags indicate phase 1 or phase 2 movement.
- `mkdir` creates a new directory on all DHT subvolumes, sets the hashed subvolume as metadata server, writes/validates parent layout information, and self-heals the new directory layout.
- `rmdir` removes a distributed directory from all subvolumes while optionally scanning for stale linkto files, deleting valid linkfiles, protecting the namespace with locks, and restoring layout state after partial failures.
- Entry locks and file-entry locks are routed to the cached subvolume for the target inode/fd.
- `dht_notify()` aggregates child up/down/connecting events, starts rebalance worker state when all children have reported, handles rebalance status/stop commands, and marks cache-invalidation upcalls that need an explicit lookup.
- Pass-through helpers implement a special single-child mode for mkdir/getxattr/fgetxattr while hiding internal DHT xattrs from normal clients.

## Important APIs, Types, and Functions

### Link and create

- `dht_link_cbk()` is entered before this chunk and continues here. The visible tail preserves first-call return state in `local->stbuf`, `local->preparent`, `local->postparent`, and `local->inode`, records rebalance metadata with `dht_set_local_rebalance()`, checks migration phase flags, and either invokes `dht_link2()`/rebalance checks or unwinds the link result after stripping phase-one flags.
- `dht_link2()` is the second-stage link handler used by rebalance checks. If the current DHT layer is not migrating, it returns the original result. If the chosen target subvolume is the already-created linkfile subvolume, it treats the operation as successful. Otherwise it sets `local->call_cnt = 2` and winds the link to the migration target.
- `dht_link_linkfile_cbk()` runs after `dht_linkfile_create()` for hard links whose new name hashes to a different subvolume than the source data. On success it winds the real link to `local->linkfile.srcvol`; on failure it unwinds the original link FOP.
- `dht_link()` validates inputs, initializes `dht_local_t`, finds the cached subvolume for the old path and hashed subvolume for the new path, stores `newloc` in `local->loc2`, refs `xdata`, and either creates a linkto file on the hashed subvolume or directly winds `link` to the cached subvolume.
- `dht_create_cbk()` records create failures, handles `GF_PREOP_CHECK_FAILED` parent-layout mismatch by building a parent loc and taking a create layout lock, sets fd context with `dht_fd_ctx_set()`, presets file layout with `dht_layout_preset()`, optionally heals linkfile attrs, and unwinds after releasing parent layout locks.
- `dht_create_linkfile_create_cbk()` continues a create after a linkto file has been created on the hashed subvolume. It strips internal linkto keys from `local->params` and winds the real `create` to `local->cached_subvol`.
- `dht_create_wind_to_avail_subvol()` chooses whether the hashed subvolume can accept the file. If full, it asks `dht_free_disk_available_subvol()` for an alternate data subvolume and creates a linkto file when the alternate differs. It also controls whether `GF_PREOP_PARENT_KEY` and the parent disk layout are included in the create params.
- `dht_build_parent_loc()` builds a parent `loc_t` from `child->parent` or by looking up `child->pargfid` in `this->itable`.
- `dht_create_do()`, `dht_create_finish()`, `dht_create_lock_cbk()`, and `dht_create_lock()` implement the retry path when create sees a stale parent layout or a decommissioned hashed subvolume. They lock the parent layout, refresh it, reselect the hashed child from the refreshed layout, retry create, and unlock via a copied frame.
- `dht_set_parent_layout_in_dict()` extracts the parent layout range for the current hashed subvolume and stores it in the create params under `conf->xattr_name`, with `GF_PREOP_PARENT_KEY` pointing to that layout xattr name.
- `dht_create()` is the public create FOP. It updates disk-usage info, initializes local state, handles debug `dht_filter_loc_subvol_key()` forced-placement requests, detects hashed subvolumes that are decommissioned, triggers parent-layout refresh if needed, and otherwise delegates to `dht_create_wind_to_avail_subvol()`.

### Mkdir

- `dht_mkdir_selfheal_cbk()` finishes directory self-heal, sets the fixed directory stat fields, persists the new layout in inode context on success, updates inode/parent time caches, and unwinds `mkdir`.
- `dht_mkdir_cbk()` handles mkdir responses from non-hashed subvolumes. It merges layout entries and iatts under `frame->lock`, treats `EEXIST` as a likely race with lookup self-heal, marks filled subvolumes as `ENOSPC` in the layout, and on the last response unlocks namespace state and runs `dht_selfheal_new_directory()`.
- `dht_mkdir_helper()` is the retry continuation after parent-layout refresh. It extracts the parent disk layout for the new hashed subvolume, detects loops where the layout did not change after a failed attempt, stores preop layout validation keys in params, and winds `mkdir` to the hashed subvolume.
- `dht_mkdir_hashed_cbk()` processes the first mkdir response from the hashed subvolume. On `GF_PREOP_CHECK_FAILED` it creates a stub and calls `dht_handle_parent_layout_change()`. On success it removes parent preop keys, merges layout and attrs, sets the inode MDS subvolume to the hashed subvolume, then winds mkdir to every other subvolume.
- `dht_mkdir_guard_parent_layout_cbk()` runs after parent-layout/namespace guard locking. It writes the internal MDS xattr marker into params and winds mkdir to the hashed subvolume.
- `dht_mkdir()` validates the required `gfid-req`, initializes a new layout with commit hash derived from `conf->lookup_optimize`, creates a mkdir stub, and asks `dht_guard_parent_layout_and_namespace()` to protect parent layout and namespace before creation.

### Rmdir

- `dht_rmdir_selfheal_cbk()` is used after partial rmdir failures. It destroys the heal frame, fixes parent stats, and unwinds the main frame with the original rmdir result.
- `dht_rmdir_hashed_subvol_cbk()` handles rmdir on the hashed subvolume after non-hashed subvolumes have been processed. It records errors, triggers self-heal restore for partial failures, updates parent time cache on clean completion, unlocks namespace state, and unwinds.
- `dht_rmdir_unlock()` unlocks both namespace entry locks and parent-layout inode locks. It uses a copied frame for inode unlocks so the main operation can continue unwinding independently.
- `dht_rmdir_cbk()` handles rmdir on non-hashed subvolumes. It treats `ENOENT`/`ESTALE` as ignorable, marks self-heal needed for other failures, tracks whether any subvolume succeeded, and when done either starts self-heal restore, winds rmdir to the hashed subvolume, or unwinds failure/success.
- `dht_rmdir_lock_cbk()` runs after namespace protection is acquired and winds rmdir to every non-hashed subvolume.
- `dht_rmdir_do()` selects the hashed subvolume, special-cases one-child DHT, initializes namespace protection, and delegates actual deletion to the callbacks above.
- `dht_rmdir_readdirp_done()`, `dht_rmdir_readdirp_do()`, `dht_rmdir_opendir_cbk()`, and `dht_rmdir_readdirp_cbk()` implement the optional stale-linkfile cleanup scan used when `rmdir_optimize` is disabled and the caller did not pass flags. They open the directory on all subvolumes, repeatedly issue `readdirp`, and only proceed to rmdir once all scans finish or record a failure.
- `dht_rmdir_is_subvol_empty()` inspects `readdirp` entries. Non-dot entries that are not linkfiles make the directory non-empty. Linkfiles are validated by lookup: invalid/self-pointing linkfiles are looked up on their own subvolume for unlink, while linkfiles pointing elsewhere first verify the cached target is absent.
- `dht_rmdir_lookup_cbk()`, `dht_rmdir_cached_lookup_cbk()`, and `dht_rmdir_linkfile_unlink_cbk()` are the validation/unlink chain for stale linkfiles encountered during the pre-rmdir scan.
- `dht_rmdir()` initializes rmdir local state and fd, chooses the optimized direct path by default, or builds an xattr request for linkto metadata and starts opendir on every subvolume for the full scan path.

### Locks, IPC, lifecycle, and pass-through helpers

- `dht_entrylk()` and `dht_fentrylk()` route entry locks to the cached subvolume for the inode or fd. A TODO warns that sending `entrylk` to cached subvol can result in stale locks in the referenced bug.
- `dht_ipc()` fans `GF_IPC_TARGET_UPCALL` to all subvolumes after setting a DHT layout xattr marker in `xdata`; other IPC operations are forwarded only to `FIRST_CHILD(this)`. `dht_ipc_cbk()` treats `ENOTCONN` as non-fatal and unwinds success if any child succeeds or all failures are only disconnects.
- `dht_forget()` removes DHT inode context, unreferences any saved layout, and frees `dht_inode_ctx_t`.
- `dht_notify()` tracks child events in `conf->last_event`, `conf->subvolume_status`, and `conf->subvol_up_time`, updates disk-usage info on child up, handles assert-no-child-down termination, services rebalance status/stop/detach commands, sets explicit lookup on layout/linkfile cache-invalidation upcalls, starts the defrag thread once all children have reported, and conditionally propagates events through `default_notify()`.
- `dht_inode_ctx_layout_get()` safely refs and returns the layout from inode context under `inode->lock`.
- `dht_log_new_layout_for_dir_selfheal()` builds a debug log string with each layout entry's subvolume, error, hash range, and commit hash.
- `dht_migration_get_dst_subvol()` stores the current hashed subvolume into `local->rebalance.target_node`.
- `dht_set_local_rebalance()` snapshots stbuf/pre/post buffers and `xdata` into `local->rebalance` for later migration-phase replay.
- `dht_release()` destroys fd context via `dht_fd_ctx_destroy()`.
- `dht_pt_mkdir()`, `dht_pt_getxattr()`, and `dht_pt_fgetxattr()` are pass-through variants that operate on `FIRST_CHILD(this)`. The getxattr callbacks remove DHT internal layout/MDS/commit-hash and selected trusted internal xattrs before unwinding to clients.
- `dht_dir_layout_error_check()` reads a directory layout and returns success if any layout entry has `err == 0`; otherwise it returns the first recorded layout error.

## Control Flow

The create path is a placement decision followed by optional guarded retry. `dht_create()` initializes local state and chooses a hashed subvolume from the current parent layout. Forced subvolume debug placement can bypass normal min-free/decommission checks, but still creates a linkto file if the forced subvolume differs from the hash. Normal create detects decommissioned hashed subvolumes and parent-layout mismatch errors; both cases move the child loc into `local->loc2`, build a parent loc in `local->loc`, take a layout inode lock with `dht_create_lock()`, refresh the layout, restore the child loc in `dht_create_do()`, and retry placement. The callback sets fd/inode layout context only after the child create succeeds.

The create data-placement branch is controlled by `dht_create_wind_to_avail_subvol()`. When the hashed subvolume is not filled, the file is created there. When it is filled, DHT asks for an available data subvolume. If that alternate is different, DHT creates a linkto file on the hashed subvolume and then creates the real file on the alternate. Parent layout validation is included in params only when no parent layout lock has been taken; after a guarded retry the stale preop key is removed to avoid failing against an intentionally changed disk layout.

The mkdir flow is deliberately hashed-subvolume-first. `dht_mkdir()` creates a fresh layout, guards parent layout and namespace through a stub, marks the hashed subvolume as MDS in params, and winds mkdir to the hashed subvolume. Only after the hashed mkdir succeeds does `dht_mkdir_hashed_cbk()` wind mkdir to the remaining subvolumes. Once all responses have arrived, DHT unlocks namespace state and self-heals the directory layout. Parent-layout mismatch during hashed mkdir is retried through `dht_mkdir_helper()`, which includes loop detection using the previously seen parent disk layout.

The rmdir flow deletes non-hashed subvolumes before the hashed subvolume. `dht_rmdir_do()` protects the namespace, winds rmdir to non-hashed children, and only after they finish does `dht_rmdir_cbk()` optionally wind to the hashed child. This ordering preserves the hashed subvolume until distributed cleanup is almost complete. If some subvolume failed after another succeeded, the code starts `dht_selfheal_restore()` on a copied frame before unwinding the original rmdir result.

The non-optimized rmdir path inserts a preflight cleanup loop before actual rmdir. It opens the directory on each subvolume, spawns separate readdirp frames per subvolume, scans all entries, and only accepts dot entries and linkfiles. For each linkfile, it verifies whether the linkfile is stale and safe to unlink; non-linkfile entries make the directory `ENOTEMPTY`. Readdirp may be repeated because one `readdirp` response may not contain every entry.

Event notification control flow is aggregation-based. Child up/down/connecting events update per-subvolume status but may be hidden until every child has reported at least once. Once all children have reported, the code computes one aggregate event, starts defrag once if configured, and then begins propagating child events normally. Rebalance control commands return directly from the notify handler after inspecting `rebalance-command` and mutating/querying `conf->defrag`.

## State and Persistence Behavior

This chunk mutates several layers of DHT state:

- In-flight per-FOP state in `dht_local_t`: cached/hashed subvolumes, alternate locs (`loc2`), fd, params, flags/mode/umask, layout locks, MDS subvolume, rebalance snapshots, pre/post parent stats, merged stbuf, op result, and self-heal frames.
- Inode and fd context: successful create sets fd context and file layout; mkdir sets directory layout and MDS subvolume in inode context; `dht_forget()` deletes inode context and unreferences layout; `dht_release()` destroys fd context.
- On-disk xattrs and params: parent layout preop validation uses `GF_PREOP_PARENT_KEY` and `conf->xattr_name`; mkdir writes the internal MDS xattr key; pass-through xattr reads strip DHT internal layout, MDS, commit hash, quota, and pgfid xattrs for normal clients.
- Linkto files: link/create may create linkfiles on hashed subvolumes when real data resides elsewhere. Rmdir cleanup can delete stale/invalid linkfiles discovered by readdirp.
- Directory layouts: mkdir allocates and self-heals a new directory layout across children; rmdir may restore layout after partial failure; `dht_log_new_layout_for_dir_selfheal()` reports layout ranges for debugging.
- Cluster status state: `dht_notify()` updates `conf->gen`, `conf->subvolume_status[]`, `conf->last_event[]`, `conf->subvol_up_time[]`, and defrag status/command fields.

Persistent backend effects happen through child translator FOPs (`create`, `mkdir`, `rmdir`, `link`, `unlink`, `lookup`, `opendir`, `readdirp`, xattrs) and through DHT-managed layout/linkto xattrs sent in params. The code often stores only the request-side state locally, then relies on lower translators such as POSIX to validate or persist the supplied layout xattrs.

## Dependencies and Integration Points

This chunk depends on Gluster's stack-wind callback model: every public FOP validates inputs, initializes `frame->local` with `dht_local_init()`, winds one or more child FOPs with `STACK_WIND` or `STACK_WIND_COOKIE`, decrements outstanding calls through `dht_frame_return()`, and finishes with `DHT_STACK_UNWIND()`.

Core DHT dependencies include `dht_layout_get()`, `dht_layout_new()`, `dht_layout_merge()`, `dht_layout_set()`, `dht_layout_unref()`, `dht_subvol_get_hashed()`, `dht_subvol_get_cached()`, `dht_is_subvol_filled()`, `dht_free_disk_available_subvol()`, `dht_linkfile_create()`, `dht_linkfile_subvol()`, `check_is_linkfile()`, `dht_iatt_merge()`, `dht_set_fixed_dir_stat()`, `dht_inode_ctx_*()` helpers, `dht_selfheal_*()` helpers, and rebalance helpers such as `dht_rebalance_complete_check()` and `dht_rebalance_in_progress_check()`.

Locking integrates with DHT namespace and layout locks: `dht_guard_parent_layout_and_namespace()`, `dht_handle_parent_layout_change()`, `dht_protect_namespace()`, `dht_unlock_namespace()`, `dht_unlock_entrylk_wrapper()`, `dht_lock_new()`, `dht_blocking_inodelk()`, `dht_unlock_inodelk()`, and lock-array copy/reset/free helpers.

Gluster framework dependencies include `call_frame_t`, `xlator_t`, `loc_t`, `fd_t`, `inode_t`, `dict_t`, `gf_dirent_t`, `struct iatt`, uuid helpers, `GF_CALLOC`/`GF_FREE`, `dict_set_*`/`dict_del`, frame copying/destruction, `gf_msg*` logging, `gf_thread_create()`, and event constants such as `GF_EVENT_CHILD_UP`, `GF_EVENT_VOLUME_DEFRAG`, and `GF_EVENT_UPCALL`.

Integration points outside the chunk include earlier getxattr helpers for `dht_vgetxattr_subvol_status()`, earlier setxattr/remove/rebalance code that consumes `local->rebalance`, lower child translators that implement actual file-system operations, md-cache clients that act on `UP_EXPLICIT_LOOKUP`, and rebalance/defrag code driven from `conf->defrag`.

## Risks and Edge Cases

- `dht_create_cbk()` contains a duplicate `local = frame->local;` assignment. It is harmless but shows this area has callback complexity and should be watched during refactors.
- `dht_create_wind_to_avail_subvol()` assumes `local->params` is valid when setting or deleting parent layout keys. Public `dht_create()` does `dict_ref(params)` without validating `params`, so callers must follow the expected FOP contract.
- Parent-layout retry correctness depends on moving `local->loc` and `local->loc2` exactly once through the refresh path. Lost or stale loc state can retry create against the wrong path or parent.
- Parent-layout validation is skipped after locks are held by deleting `GF_PREOP_PARENT_KEY`. This is intentional for shrink/rebalance races, but it means lower translators no longer validate that exact preop layout once DHT has taken responsibility.
- `dht_set_parent_layout_in_dict()` unrefs `parent_layout` even when `dht_layout_get()` may have failed; correctness depends on `dht_layout_unref(NULL)` being safe.
- `dht_mkdir_helper()` detects a retry loop by comparing the last parent disk layout. If a layout changes back to the same serialized range for the hashed subvolume, this could be reported as a loop even though other metadata changed.
- `dht_mkdir_hashed_cbk()` removes parent validation keys from `local->params` after hashed mkdir succeeds. Reusing the same params dict for other subvolumes is intentional, but accidental sharing with callers would be risky if the dict contract changed.
- `dht_mkdir_cbk()` converts `EEXIST` to success for likely self-heal races. If an incompatible pre-existing directory exists, the later layout set/self-heal must catch it.
- Rmdir has complicated success semantics. `ENOENT` and `ESTALE` are ignored on child rmdir, partial success can trigger self-heal restore, and the hashed subvolume is deleted last. Tests must verify that a failed non-hashed child does not accidentally delete the last useful namespace copy without restore.
- The non-optimized rmdir path creates many copied frames and lookup/unlink calls for linkfiles. Memory allocation failure during this scan degrades to `ENOTEMPTY` and adjusts `call_cnt` under `frame->lock`; races between already-returned callbacks and loop cleanup are explicitly handled but fragile.
- `dht_rmdir_cached_lookup_cbk()` treats finding the file on the cached target as `ENOTEMPTY`; stale linkfile cleanup therefore depends on correct linkfile target resolution from xattrs.
- `dht_entrylk()` has an explicit TODO that routing locks to the cached subvolume can create stale locks. Lock routing remains a known risk for rename/migration/cache changes.
- `dht_ipc()` mutates the caller-supplied `xdata` by setting `conf->xattr_name`. If the dict is shared by upper layers, this side effect is observable.
- `dht_notify()` uses a static `run_defrag` flag inside the function. That prevents rebalance thread restart after graph switches as intended, but it is process-global rather than per-translator instance.
- `dht_notify()` may terminate the process on child down when `assert_no_child_down` is set. This is correct for rebalance mode but high impact if configuration or event routing is wrong.
- Cache-invalidation upcalls force explicit lookup when DHT layout xattrs change or stat mode indicates a linkfile. Missing this flag would leave md-cache clients with stale DHT routing state.
- `dht_dir_layout_error_check()` does not check whether `dht_layout_get()` returned NULL before dereferencing `layout->cnt`.

## Test and Validation Signals

Useful test coverage for this chunk should include:

- Hard-link tests where old and new names hash to the same subvolume, different subvolumes, missing cached subvolume, missing hashed subvolume, linkfile creation failure, and rebalance phase-one/phase-two migration retry.
- Create tests for normal hashed placement, full hashed subvolume fallback with linkto creation, forced debug subvolume placement, missing params, parent-layout preop mismatch, decommissioned hashed subvolume refresh, lock acquisition failure, layout refresh failure, fd context failure logging, and linkfile attr healing.
- Parent-layout validation tests that confirm `GF_PREOP_PARENT_KEY` and `conf->xattr_name` are set before unlocked creates and removed after guarded retries.
- Mkdir tests for missing `gfid-req`, hashed subvolume missing, parent-layout guard failure, MDS xattr set failure, hashed mkdir preop mismatch retry, retry loop detection, `EEXIST` race handling on non-hashed subvolumes, filled-subvolume `ENOSPC` layout entries, MDS inode ctx setting, and final self-heal layout persistence.
- Rmdir tests for one-child DHT, normal multi-child order with hashed subvolume last, namespace lock failure, all-child `ENOENT`/`ESTALE`, partial failure with self-heal restore, `EACCES` handling, parent time update, and unlock behavior when copied unlock frames fail allocation.
- Non-optimized rmdir tests with directories containing only dot entries, real entries, valid linkfiles whose targets still exist, stale linkfiles safe to unlink, invalid/self-pointing linkfiles, more entries than one `readdirp` buffer, opendir/readdirp failures, lookup failures, unlink failures, and memory allocation failures in copied lookup frames.
- Entry lock tests for valid cached subvolume, missing cached subvolume, fd cached lookup failure, and behavior during file migration or after layout cache invalidation.
- IPC tests for `GF_IPC_TARGET_UPCALL` fan-out to all children, non-target IPC pass-through to first child, `ENOTCONN` tolerance, mixed success/failure aggregation, and `xdata` mutation with `conf->xattr_name`.
- Notify tests for initial child-event aggregation, child-up disk-usage refresh, child-down with `assert_no_child_down`, bad child pointers, child connecting state, event propagation before and after all children report, rebalance status/detach/stop commands, defrag thread creation failure, and upcall cache invalidation setting `UP_EXPLICIT_LOOKUP`.
- Inode/fd lifecycle tests for `dht_forget()` layout unref/free, `dht_inode_ctx_layout_get()` refcounting under lock, `dht_release()` fd ctx destruction, and pass-through xattr filtering of DHT internal xattrs.

## Cross-Chunk Notes

The chunk begins in the tail of `dht_link_cbk()`, so the initial link callback setup and stale-linkto cleanup code are in the preceding chunk. The normal getxattr/setxattr/remove/xattrop implementations referenced by pass-through helpers and rebalance state are earlier in `dht-common.c`. The file continues after line 11618 with additional DHT common helpers, so final per-file synthesis should merge this with adjacent chunks before drawing whole-file conclusions about all FOP tables and initialization.
