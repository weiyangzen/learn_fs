# Research: subset-b-007079

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-rename.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-rename.c

## Purpose
Implements DHT rename for distributed GlusterFS volumes. It handles directory rename fan-out across all bricks, regular-file rename across hashed/cached subvolumes, linkto-file creation/removal, changelog rename tracking, quota-accounting suppression, and namespace/inode locking needed to make rename race-tolerant during lookup self-heal and rebalance.

## Important APIs and Functions
- `dht_rename`: public FOP entry. Resolves source/destination hashed and cached subvolumes, initializes `dht_local_t`, logs the operation, and dispatches to directory or file logic.
- `dht_rename_dir`, `dht_rename_dir_do`, `dht_rename_dir_cbk`: protect source/destination namespaces, verify destination emptiness when needed, perform the hashed-subvolume rename, fan out to remaining subvolumes, and reverse successful subvolume renames when a later subvolume fails.
- `dht_rename_lock`, `dht_rename_lock_cbk`, `dht_rename_file_protect_namespace`: acquire backward-compatible migration inodelks plus ordered namespace locks, then re-lookup source and destination before mutating.
- `dht_rename_create_links`, `dht_do_rename`, `dht_rename_unlink`, `dht_rename_cleanup`: create linkto/hardlink prerequisites, perform the actual backend rename, remove old data/linkto files, or roll back partial link creation.
- `dht_pt_rename`: pass-through rename for single-subvolume/pass-through mode while still marking changelog rename metadata for non-directories.

## Control Flow
The entry path first validates locations and derives `src_hashed`, `src_cached`, `dst_hashed`, and optionally `dst_cached`. Directory renames are all-brick namespace operations: DHT checks every subvolume is up, orders locks by hashed subvolume name and parent/name identity, optionally reads the destination directory to enforce non-empty semantics, renames on `dst_hashed`, and then renames on every other subvolume. Failure after partial success triggers reverse renames on subvolumes that already succeeded.

Regular-file rename is a linkfile-aware state machine. It takes inodelks on the source cached file and possibly destination cached file, then entry/namespace locks. After locks, it revalidates source and destination because rebalance or another rename may have changed cached placement or GFID. If source became a linkfile or GFID changed, the operation fails with an ENOENT-style path. Otherwise DHT creates a destination linkto file and/or hardlink when the cached and hashed subvolumes differ, performs the backend rename on either `src_cached` or `dst_hashed`, and cleans obsolete source data, source linkto, and overwritten destination data.

## State and Persistence
Persistent effects are backend `rename`, `link`, `unlink`, and linkto xattr operations on child xlators. The file adds request xdata such as `GLUSTERFS_MARKER_DONT_ACCOUNT_KEY`, `GF_FORCE_REPLACE_KEY`, `GLUSTERFS_INTERNAL_FOP_KEY`, and `DHT_CHANGELOG_RENAME_OP_KEY`. Runtime state lives in `dht_local_t`: cached/hashed subvol pointers, lock wrappers, `ret_cache`, `linked`, `added_link`, merged iatts, xattr request/response dictionaries, and copied destination loc.

## Dependencies and Integration Points
Depends on DHT common layout/cache helpers, `dht-lock` namespace/inodelk wrappers, linkfile creation/heal helpers, dict/xdata APIs, inode/link loc handling, and child xlator FOP vectors. It integrates with lookup self-heal, rebalance migration locks (`DHT_FILE_MIGRATE_DOMAIN`), changelog marker handling, quota/marker accounting, and the main DHT `fops.rename` registration in `dht.c`.

## Risks
- Rename correctness depends on lock ordering and complete unlock cleanup; failure to wind unlocks logs stale-lock warnings and then unwinds anyway.
- Directory fan-out rollback is best effort; reverse rename can also fail and leave divergent directories.
- Linkfile failures are intentionally sometimes non-critical, so stale linkto files may remain until lookup/rebalance heals them.
- `DHT_MARKER_DONT_ACCOUNT` can allocate a dict through a macro argument and changes ownership expectations; callers must unref carefully.
- Destination cached changes are handled by re-lookup, but races with concurrent rename/unlink still depend on downstream errno behavior.

## Test Signals
No direct unit test appears in this subset. Indirect signals come from DHT rename, rebalance, linkto, quota/changelog, and directory self-heal regressions. High-value tests would cover cross-subvolume rename with existing destination, directory partial failure rollback, source migration between lock and lookup, stale linkto replacement via `GF_FORCE_REPLACE_KEY`, and pass-through changelog tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-selfheal.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-selfheal.c

## Purpose
Implements DHT directory self-heal and layout repair. It refreshes on-disk directory layouts from child subvolumes, detects holes/overlaps/missing directories/down bricks, creates missing directory copies, heals attributes and selected xattrs, recomputes hash ranges, writes layout xattrs, and updates rebalance commit hashes.

## Important APIs and Functions
- `dht_refresh_layout` / `dht_refresh_layout_cbk`: lookup every subvolume with DHT layout xattr requested, merge results into `selfheal.refreshed_layout`, then decide whether repair is needed.
- `dht_should_heal_layout` and `dht_should_fix_layout`: policy predicates for normal self-heal versus fix-layout, considering holes, overlaps, missing dirs, down/misc errors, commit hash changes, decommissioned bricks, and weighted/equal distribution.
- `dht_selfheal_layout_lock`: acquires layout-domain inodelks on all subvolumes, or only the hashed subvolume for new directories, before refreshing and writing layouts.
- `dht_selfheal_dir_mkdir`, `dht_selfheal_dir_mkdir_lookup_*`, `dht_selfheal_dir_mkdir_cbk`: protect namespace, re-lookup to avoid racing rmdir, create missing directories with requested GFID/internal context, and continue to attr/xattr healing.
- `dht_selfheal_layout_new_directory`, `dht_fix_layout_of_directory`, `dht_selfheal_layout_maximize_overlap`: compute new hash ranges, optionally weighted by disk usage, randomized by GFID, and adjusted to maximize overlap with old ranges.
- `dht_dir_heal_xattrs`, `dht_dir_attr_heal`, `dht_update_commit_hash_for_layout`: sync user/quota/MDS xattrs, mode/uid/gid, and commit-hash layout xattrs.

## Control Flow
Normal directory self-heal starts with a merged layout and iatt state from lookup. It links the inode, copies MDS attrs/xattrs when needed, rejects repair if bricks are down or anomalies are unrecoverable, sorts by subvolume name, computes a fix when holes/overlaps/missing entries exist, and calls `dht_selfheal_dir_mkdir`. Missing directory creation first takes namespace protection on the hashed/MDS subvolume, re-lookups all children under lock, creates only entries still missing or forced, then heals attrs and layout xattrs.

Layout xattr healing writes a 4-int disk-layout blob (`conf->xattr_name`) to each participating subvolume and writes 0-0/dummy layouts to non-participating subvolumes so stale overlaps are removed. A refresh pass sorts on-disk layout and either invokes the healer or swaps in the refreshed layout and finishes. Commit-hash update is a rebalance-only path that locks local subvolumes, updates `layout->list[j].commit_hash`, extracts disk layout blobs, sets xattrs, then unlocks.

## State and Persistence
Persistent state is stored as trusted DHT layout xattrs, MDS xattrs, quota/user xattrs, directory attrs, GFIDs, and commit hashes on child bricks. Runtime state lives in `local->selfheal`: current/refreshed layout refs, anomaly counters, forced mkdir, callbacks, healer predicate, plus `need_attrheal`, `need_xattr_heal`, MDS buffers, and lock wrappers.

## Dependencies and Integration Points
Uses DHT layout parsing/sorting/anomaly helpers, namespace and inodelk wrappers, synchronous FOP helpers for background attr/xattr heal, dict APIs, GFID/inode APIs, `dht_common_mark_mdsxattr`, and volume options from `dht_conf_t` such as `dir_spread_cnt`, `do_weighting`, `randomize_by_gfid`, `du_stats`, `decommissioned_bricks`, and local subvolumes. It is called from lookup/mkdir/fix-layout/rebalance paths.

## Risks
- Some comments note non-layout xattr healing remains secondary and may not run when layout is otherwise well-formed.
- Repair is skipped when subvolumes are down, leaving layout anomalies until later.
- Weighted layout depends on current `du_stats`; missing or uneven stats switch behavior and can alter placement.
- Several paths continue after failures with logged errors, so partial xattr or attr heal can remain.
- `dht_selfheal_layout_maximize_overlap` uses stack allocation proportional to old*new layout count.

## Test Signals
The unit tests in this subset only cover `dht_layout_new`; this file needs broader regression coverage through directory lookup/mkdir/fix-layout/rebalance tests. Important signals include layout hole/overlap repair, add-brick 0-0 layout clearing, decommissioned brick exclusion, MDS xattr heal, root directory attr behavior, forced restore, and commit-hash update under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-selfheal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-shared.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-shared.c

## Purpose
Provides shared DHT translator lifecycle, options, state dumping, reconfiguration, decommission handling, regex initialization, rebalance setup, and method-table initialization used by distribute, NUFA, and switch variants.

## Important APIs and Functions
- `dht_priv_dump` and `dht_inodectx_dump`: statedump hooks for translator private state and per-inode layout state.
- `dht_fini`: releases layouts, subvolume arrays/status, DU stats, decommission state, xattr-name strings, regexes, locks, pools, and private config.
- `mem_acct_init`: initializes DHT memory accounting.
- `dht_reconfigure`: updates runtime options including lookup behavior, min-free thresholds, layout spread, readdir optimization, migration/durability, rebalance stats/throttle, decommissioned bricks, regexes, weighting, and readdirp.
- `dht_init`: allocates `dht_conf_t`, initializes locks/pools, parses rebalance options, discovers subvolumes/local subvolumes, initializes layouts, xattr names, regexes, methods, and reachable-leaf mapping.
- `dht_options`: declares the volume option table exported as `options`.

## Control Flow
Initialization validates child presence, allocates `dht_conf_t`, optionally builds `gf_defrag_info_t` for rebalance commands, parses base options, initializes child subvolume arrays and optional local-subvolume lists, parses decommissioned bricks, compiles rsync/extra hash regexes, initializes file/dir layouts, creates local and lock pools, derives xattr keys from `xattr-name`, stores `this->private`, then initializes subvolume range and DHT method callbacks. Any error frees partially allocated state.

Reconfiguration mirrors a subset of init: it validates boolean/string options, updates thresholds and flags in place, adjusts active defrag thread count/stats, parses or clears decommissioned bricks, recompiles regexes under `conf->lock`, and updates weighting/readdirp. Dump functions take `subvolume_lock` when walking mutable subvolume state.

## State and Persistence
All state is in-memory translator state except child xattrs used by other files. `dht_conf_t` holds subvolume lists, status arrays, layouts, generation, DU stats, decommissioned brick pointers, regex objects, xattr key strings, lock pools, defrag queues, option flags, and method callbacks. Reconfigure changes affect future placement/lookup/heal behavior without persisting by itself.

## Dependencies and Integration Points
Depends on libglusterfs dict/options/statedump/mem-pool/logging APIs, DHT layout/subvolume initialization helpers, defrag/rebalance structures, regex library, and child translator graph traversal. `dht.c`, `nufa.c`, and `switch.c` all reuse this init/fini/reconfigure/options surface.

## Risks
- Error cleanup is manual and not identical to `dht_fini`; future allocations can leak unless added to both paths.
- Reconfigure mutates live fields while operations may be active; only regex updates take `conf->lock`.
- Decommission parsing fails on unknown brick names and keeps stateful counters that must be reset exactly.
- `dht_priv_dump` uses `TRY_LOCK`; dump output can be skipped under contention.
- Rebalance pattern parsing stores pointers into duplicated strings owned by list nodes, making ownership subtle.

## Test Signals
No direct tests in this subset. Expected coverage should come from volume-option parsing, rebalance, decommission/remove-brick, statedump, and translator init tests. Useful targeted tests would validate xattr-name derivation, reconfigure decommission add/remove, invalid child names, regex `"none"`, throttle parsing, and cleanup after partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht.c

## Purpose
Defines the exported xlator API for the standard DHT "distribute" translator. It binds GlusterFS FOP vectors, dump callbacks, callbacks, options, lifecycle hooks, and pass-through behavior into `xlator_api`.

## Important APIs and Types
- `dht_pt_fops`: reduced pass-through FOP set used when DHT is effectively pass-through, preserving mkdir layout creation, xattr access, and rename changelog tracing.
- `fops`: main DHT operation table covering lookup, create/mknod, directory ops, rename, locks, inode read/write ops, xattrs, allocation, discard, and zerofill.
- `dumpops`: maps private and inode-context statedump callbacks to shared DHT dump functions.
- `cbks`: registers `dht_release` and `dht_forget`; `releasedir` is intentionally commented.
- `xlator_api`: exported translator descriptor with `dht_init`, `dht_fini`, `dht_notify`, `dht_reconfigure`, `mem_acct_init`, options, identifier `"distribute"`, and maintained category.

## Control Flow
There is no algorithmic runtime logic here beyond dispatch registration. GlusterFS loads this module, reads `xlator_api`, invokes lifecycle hooks, and routes FOPs through the function pointers. The pass-through table is available for the single-child/shrunk-volume case where only a small subset of DHT-specific behavior should remain active.

## State and Persistence
The file owns no mutable state. Persistent behavior is indirect through the selected FOP implementations in other DHT files. The table selection determines which functions can mutate layouts, linkfiles, locks, xattrs, and backend data.

## Dependencies and Integration Points
Includes `dht-common.h` and references nearly every DHT FOP implementation. It integrates with the translator loader ABI via `xlator_api_t`, with shared options from `dht_options`, and with pass-through logic used after remove-brick/shrink workflows.

## Risks
- Missing or mismatched FOP assignments silently change translator behavior.
- The commented lookup/readdir pass-through entries document a known dangling-linkto tradeoff for 1x volumes.
- Pass-through rename is deliberately retained for changelog tracing; removing it would affect changelog consumers.

## Test Signals
Coverage is mostly integration-level: mounting a distribute volume and exercising each FOP verifies the dispatch table. Specific tests should confirm pass-through mode still creates layouts on mkdir, exposes xattrs, and traces rename while not unexpectedly handling lookup/readdir in the reduced table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/nufa.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/nufa.c

## Purpose
Implements the NUFA DHT variant, which prefers a local brick for lookup/create/mknod while retaining DHT layout, linkfile, and common FOP behavior. If no local subvolume can be found, it downgrades selected FOPs back to standard DHT behavior.

## Important APIs and Functions
- `nufa_lookup` / `nufa_local_lookup_cbk`: fresh lookup starts on the configured local subvolume; revalidates use cached layout subvolumes like DHT.
- `nufa_create` and `nufa_mknod`: choose the local subvolume unless it is full, then fall back to a free subvolume; create linkfiles when placement differs from the hashed subvolume.
- `nufa_find_local_brick`, `nufa_find_local_subvol`: locate a local child by `local-volume-name` or by matching local host/remote-host.
- `nufa_to_dht`: rewires lookup/create/mknod to normal DHT when local selection fails.
- `nufa_init`: calls shared `dht_init`, determines local volume selection mode, and configures fallback.

## Control Flow
Fresh lookup requests both layout and linkto xattrs, then probes only `conf->private`, the local subvolume. If the entry is missing and unhashed search is enabled, it falls back to `dht_lookup_everywhere`. A found regular file presets the inode layout to the local/cookie subvolume and then continues through normal DHT lookup callback. A found directory triggers all-subvolume directory lookup/merge; a linkfile follows the linkto target.

Create and mknod first refresh disk usage, compute the hashed subvolume, and set `avail_subvol` to the local child. If local is full, `dht_free_disk_available_subvol` chooses a replacement. When available and hashed differ, NUFA creates a linkto file on the hashed subvolume pointing at the available data subvolume, then creates/mknods the real object on the available subvolume.

## State and Persistence
`conf->private` stores the selected local subvolume pointer, unlike standard DHT. Persistent side effects are standard DHT object creation plus linkto xattrs when NUFA places data away from the hashed subvolume. Runtime local state uses `dht_local_t` fields for xattr requests, cached subvol, params, mode, flags, rdev, and fd.

## Dependencies and Integration Points
Reuses shared DHT init/fini/reconfigure/options, DHT lookup callbacks, layout presetting, linkfile creation, disk usage and free-space selection, and common FOPs for all operations except lookup/create/mknod. It relies on translator graph traversal and child `remote-host` options to discover locality.

## Risks
- `conf->private` is overloaded as a generic variant-private pointer and must remain a valid child xlator.
- Local-host matching can select the first local brick, which may not be the intended placement if multiple bricks are local.
- If params is NULL, some callbacks still dict_ref `params`; call-site contracts matter.
- NUFA is marked tech preview, and fallback mutates `this->fops` at init time.
- Local-first placement may fight rebalance or layout expectations, relying on linkfiles to preserve namespace correctness.

## Test Signals
No direct NUFA tests are in this subset. Useful tests would cover explicit `local-volume-name`, automatic host matching, fallback to DHT when no local subvol exists, local-full placement, linkfile creation for non-hashed placement, directory lookup merge, and linkfile target lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/nufa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/switch.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/switch.c

## Purpose
Implements the switch DHT variant, which routes files matching configured path patterns to selected child subvolumes while retaining DHT hashing, linkfiles, layouts, and common FOPs. It is a pattern-aware placement/lookup scheduler layered over DHT.

## Important APIs and Types
- `struct switch_struct`: linked-list pattern rule containing a glob pattern, eligible child array, round-robin node index, and child count.
- `set_switch_pattern`: parses `pattern.switch.case` strings like `*.jpg:child1,child2;*.mpg:child3`, validates child names, builds rule list, and adds a default `*` rule for unmentioned children.
- `get_switch_matching_subvol`: returns the hashed subvolume if it is eligible for a matching rule; otherwise picks the next eligible child round-robin.
- `switch_lookup` / `switch_local_lookup_cbk`: route fresh lookup through the pattern-selected child, then handle regular files, directories, linkfiles, and fallback search.
- `switch_create` and `switch_mknod`: place new objects on pattern-selected/free subvolumes and create linkfiles when placement differs from hash.
- `switch_fini` / `switch_init`: manage pattern rule memory around shared DHT lifecycle.

## Control Flow
Initialization calls `dht_init` then parses `pattern.switch.case`. Rule parsing builds a temporary all-child array, marks children already assigned by explicit patterns, rejects unknown child names and overlong patterns, and finally appends a default `*` rule for remaining children. Lookup revalidation follows existing layout. Fresh lookup asks for layout and linkto xattrs, computes the hash, selects a switch subvolume by `fnmatch`, and either uses normal DHT lookup on the hashed child or switch-local lookup on the selected child. Directory and linkfile handling then converge with DHT callbacks.

Create/mknod compute the hashed child, choose the matching rule child, fall back to free-space selection if filled, and either create directly on the hashed child or create a linkfile on hash then create the real object on the selected child.

## State and Persistence
`conf->private` stores the head of the switch rule linked list. Each rule mutates `node_index` for round-robin scheduling. Persistent effects are backend file creation and DHT linkto xattrs when selected placement differs from hashed placement.

## Dependencies and Integration Points
Uses `fnmatch`, DHT shared init/fini/options, DHT lookup callbacks, linkfile creation, disk-usage selection, child xlator names, and common DHT FOPs for all non-placement operations. `xlator_api` identifies the translator as `"switch"` and tech preview.

## Risks
- `node_index` is incremented without locking, so concurrent creates/lookups can race and skew round-robin selection.
- `set_switch_pattern` frees only part of the temporary state on some error paths; ownership is intricate.
- The parser ignores explicit `*` rules and creates its own default, which can surprise administrators.
- Pattern strings longer than 255 bytes are rejected, but rule syntax has limited validation around missing `:` pieces.
- Like NUFA, non-hashed placement depends on linkfiles and later self-heal/rebalance to keep namespace consistent.

## Test Signals
No direct switch tests are in this subset. High-value tests should cover parser success/failure, unknown child rejection, default `*` construction, round-robin among eligible children, hashed-child eligibility short-circuit, full-subvolume fallback, linkfile creation, and concurrent rule selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/unittest/dht_layout_mock.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/unittest/dht_layout_mock.c

## Purpose
Provides minimal mock/stub definitions needed to link the DHT layout unit test without pulling the full GlusterFS runtime. The stubs return neutral success values and suppress logging/xattr behavior.

## Important APIs and Functions
- `dht_hash_compute`: stubbed to return success.
- `dht_inode_ctx_layout_get` / `dht_inode_ctx_layout_set`: no-op inode context stubs.
- `dict_get_ptr` / `dict_get_ptr_and_len`: no-op dict lookup stubs.
- `_gf_log`, `_gf_log_callingfn`, `_gf_msg`: logging stubs returning success.
- `gf_uuid_unparse`: empty UUID conversion stub.

## Control Flow
There is no meaningful control flow. Every stub immediately returns 0 or does nothing. The file exists to satisfy external symbol references from the DHT layout code under test.

## State and Persistence
No state is read or written. Output parameters are not populated, so tests relying on these helpers must avoid paths where real values are required.

## Dependencies and Integration Points
Includes GlusterFS and xlator headers plus `dht-common.h`. It is linked with `dht_layout_unittest.c` and the production layout implementation selected by the unit-test build.

## Risks
- Returning success without setting output values can hide bugs if tests expand into code paths that expect populated pointers or UUID strings.
- Logging and dict APIs are not behaviorally faithful.
- The mock is tightly scoped to `dht_layout_new`; broader layout tests would need richer mocks.

## Test Signals
The paired unit test currently exercises layout allocation defaults. This mock should remain intentionally small unless additional DHT layout functions are tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/unittest/dht_layout_mock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/unittest/dht_layout_unittest.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/unittest/dht_layout_unittest.c

## Purpose
Defines a cmocka unit test for `dht_layout_new`, validating layout allocation defaults both with and without a populated DHT private config.

## Important APIs and Functions
- `helper_xlator_init`: allocates a minimal `xlator_t`, memory accounting structure, context, and per-type locks for tests.
- `helper_xlator_destroy`: destroys locks and frees the test xlator/context/accounting allocations.
- `test_dht_layout_new`: asserts invalid inputs fail, then verifies `dht_layout_new` initializes type, count, refcount, generation, and spread count.
- `main`: runs the single cmocka test group.

## Control Flow
The test first expects assert failures for NULL xlator and negative count. It then creates a test xlator with no private config and expects a layout with `DHT_HASH_TYPE_DM`, requested count, refcount 1, generation 0, and spread count 0. Next it attaches a `dht_conf_t` with `dir_spread_cnt` and `gen`, calls `dht_layout_new` again, and verifies those values are copied into the layout.

## State and Persistence
All state is in-memory test allocation. The test manually allocates/frees layouts and config, and uses lock init/destroy around the fake memory accounting records. There is no persistent output.

## Dependencies and Integration Points
Uses `dht-common.h`, GlusterFS logging/xlator headers, cmocka, and cmocka-pbc macros such as `REQUIRE`/`ENSURE`. It depends on `dht_layout_mock.c` to satisfy unrelated production symbols.

## Risks
- The helper appears to write `xl->mem_acct->num_types` before allocating `xl->mem_acct`, which is suspicious and may rely on header/macros or be a latent test bug.
- The destroy path uses `xl->mem_acct.rec`/`xl->mem_acct.num_types` member syntax inconsistent with earlier pointer syntax; this should be checked against the actual `xlator_t` definition.
- Coverage is narrow and does not test layout ranges, sorting, xattr extraction, merge, or anomaly detection.

## Test Signals
The only direct signal is allocation/default initialization of `dht_layout_new`. It is useful as a smoke test for layout struct initialization, but not for self-heal correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/dht/src/unittest/dht_layout_unittest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/Makefile.am

## Purpose
Top-level Automake file for the GlusterFS erasure-code/disperse cluster translator directory. It delegates the actual build to the `src` subdirectory and declares an empty cleanup variable.

## Important APIs and Functions
- `SUBDIRS = src`: tells Automake to recurse into `xlators/cluster/ec/src`.
- `CLEANFILES =`: placeholder for generated files to remove during cleanup.

## Control Flow
Automake processes this directory, then builds the implementation through `src/Makefile.am`. There is no runtime control flow.

## State and Persistence
No runtime state. Build state is limited to generated Makefile artifacts and recursive build traversal.

## Dependencies and Integration Points
Integrates with the repository Autotools build. The `src` subdirectory defines the actual `ec.la` xlator target and install hooks.

## Risks
Minimal. The file must keep `src` in `SUBDIRS`; removing it would omit the EC translator from recursive builds.

## Test Signals
Build-system signal is whether `make` descends into `xlators/cluster/ec/src` and produces the EC/disperse translator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/Makefile.am

## Purpose
Defines the Automake build for the EC/disperse translator module. It lists core EC sources/headers, conditionally adds CPU-specific dynamic code generators, sets include paths and libraries, and installs `disperse.so` as a symlink to `ec.so`.

## Important APIs and Variables
- `xlator_LTLIBRARIES = ec.la` and `xlatordir`: build/install the cluster xlator module.
- `ec_sources` / `ec_headers`: enumerate EC implementation files such as helpers, locks, read/write paths, method/galois/code layers, heal, and heald.
- `ENABLE_EC_DYNAMIC_INTEL`, `ENABLE_EC_DYNAMIC_X64`, `ENABLE_EC_DYNAMIC_SSE`, `ENABLE_EC_DYNAMIC_AVX`: configure-conditionals adding optimized generator files and headers.
- `ec_la_SOURCES`, `ec_la_LIBADD`, `ec_la_LDFLAGS`: module source list, libglusterfs dependency, and xlator module flags.
- `install-data-hook` / `uninstall-local`: maintain `disperse.so -> ec.so`.

## Control Flow
Build flow is declarative. Autotools expands conditionals based on configure results; if AVX support is enabled, `ec-code-avx.c` and `.h` are compiled into the module. Install creates a compatibility/alias symlink so the same implementation can be loaded as `disperse`.

## State and Persistence
Persistent outputs are build artifacts and installed module files/symlinks. No runtime state is defined here.

## Dependencies and Integration Points
Depends on libglusterfs, libxlator helper source/header, RPC/XDR include directories, generated builddir XDR headers, and configure variables such as `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, and `GLUSTERFS_LIBEXECDIR`.

## Risks
- Conditional optimized sources must match configure CPU-feature checks; compiling AVX code without the right flags would fail or produce unusable code.
- The symlink hook assumes `ec.so` is the installed module name and destination directory exists.
- Source/header lists are manual, so new EC files must be added here.

## Test Signals
Build tests should verify EC builds with each dynamic-code conditional on/off, installation creates `disperse.so`, and uninstall removes it. Runtime EC tests indirectly validate that the selected optimized generator symbols are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-avx.c -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-avx.c

## Purpose
Provides the AVX2-backed EC code generator descriptor used by the erasure-code translator. It emits vectorized 32-byte load/store/copy/xor operations through the shared Intel code-emission helpers.

## Important APIs and Functions
- `ec_code_avx_prolog`: records the loop start address in `builder->loop`.
- `ec_code_avx_epilog`: advances source/destination offsets by 32 bytes, tests loop completion against `builder->width - 1`, jumps back if needed, and emits return.
- `ec_code_avx_load` / `ec_code_avx_store`: emit memory-to-AVX and AVX-to-memory moves for linear and pointer-array layouts.
- `ec_code_avx_copy`, `ec_code_avx_xor2`, `ec_code_avx_xor3`, `ec_code_avx_xorm`: emit AVX register moves and XORs, including XOR from memory.
- `ec_code_gen_avx`: exported `ec_code_gen_t` descriptor with name `"avx"`, required flag `"avx2"`, width 32, and function pointers.

## Control Flow
The EC code builder calls the descriptor callbacks while generating encode/reconstruct routines. Linear mode computes offsets from `idx * width * bits + bit * width` against `REG_SI` plus loop offset `REG_DX`. Nonlinear mode treats `REG_SI` as a pointer table, caches the current base index in `builder->base`, loads the selected pointer into `REG_AX` when needed, then accesses `bit * width` from that base. The epilog increments `REG_DX` and `REG_DI` by 32 and loops until the width mask test is zero.

## State and Persistence
No persistent state. The functions mutate `ec_code_builder_t` code buffers/register bookkeeping (`address`, `loop`, `base`) and generate executable code used at runtime by EC methods.

## Dependencies and Integration Points
Includes `ec-code-intel.h` and uses Intel emitter helpers for AVX moves, XORs, integer ops, conditional jumps, and return. It is conditionally included by `Makefile.am` under `ENABLE_EC_DYNAMIC_AVX`, and declared through `ec-code-avx.h`.

## Risks
- Requires AVX2; runtime selection must honor `ec_code_avx_needed_flags`.
- Generated loop correctness depends on `builder->width` being 32 and compatible with the mask test.
- Nonlinear base caching must be invalidated by surrounding builder logic when source indices change unexpectedly.
- Any register convention change in `ec-code-intel` can break emitted code.

## Test Signals
Relevant tests are EC encode/decode correctness under AVX-enabled builds and CPU feature gating. Build tests should verify AVX conditional compilation; runtime tests should compare AVX output with the generic C generator across linear/nonlinear layouts and varied stripe widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-avx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-avx.h -->
# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-avx.h

## Purpose
Declares the exported AVX EC code generator descriptor for consumers that select among EC code-generation backends.

## Important APIs and Types
- Include guard `__EC_CODE_AVX_H__`.
- Includes `ec-code.h` for `ec_code_gen_t`.
- `extern ec_code_gen_t ec_code_gen_avx`: descriptor defined in `ec-code-avx.c`.

## Control Flow
There is no runtime control flow in the header. Including code can reference `ec_code_gen_avx` when the AVX backend is compiled.

## State and Persistence
No state is owned here. The extern points to a global descriptor in the implementation file.

## Dependencies and Integration Points
Used with `ec-code-avx.c` when `ENABLE_EC_DYNAMIC_AVX` adds both files to the EC module build. Higher-level EC method selection code can include this header to register or probe the AVX generator.

## Risks
- Header availability must stay synchronized with the Automake conditional and implementation symbol.
- Consumers must not reference the symbol unless the AVX source is compiled into the target.

## Test Signals
Compile/link success under AVX-enabled builds is the primary signal. Runtime EC generator selection tests should confirm the descriptor is visible only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-code-avx.h -->
