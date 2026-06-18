# subset-b-009710 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_lock.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/state_lock.c

Purpose: Implements the SAL byte-range lock manager for NFS-Ganesha. It tracks in-memory lock entries per file, owner, state, export, NLM client, and blocked-lock queue, mediates all FSAL `lock_op2` calls, handles NFSv4/NLM grant and cancel lifecycles, and exposes cleanup paths for file, owner, client, export, and shutdown teardown.

Important APIs/types/functions: `state_lock_entry_t`, `state_block_data_t`, `state_cookie_entry_t`, `unknown_owner`, `state_blocked_locks`, `ht_lock_cookies`, `state_lock_init()`, `state_cleanup()`, `state_test()`, `state_lock()`, `state_unlock_locked()`, `state_unlock()`, `state_cancel()`, `state_cancel_blocked()`, `state_nlm_notify()`, `state_nfs4_owner_unlock_all()`, `state_export_unlock_all()`, `blocked_lock_polling()`, `grant_blocked_lock_upcall()`, `available_blocked_lock_upcall()`, and `state_lock_wipe()`. Internal helpers include `lock_end()`, `different_lock()`, `get_overlapping_entry()`, `merge_lock_entry()`, `subtract_lock_from_entry()`, `subtract_lock_from_list()`, `do_lock_op()`, `copy_conflict()`, `try_to_grant_lock()`, `cancel_blocked_lock()`, and grant-cookie table helpers.

Control flow: A lock request enters `state_lock()` with the object state lock already held. It first checks duplicate blocked requests and export-owner conflicts, scans the file lock list for conflicting or already-covered ranges, handles immediate grants or NFSv4 nonblocking cancellation of an existing blocked request, then chooses `FSAL_OP_LOCK`, `FSAL_OP_LOCKB`, or a local blocked result. It creates a provisional `state_lock_entry_t`; on FSAL success it merges adjacent/overlapping same-owner ranges and inserts the entry, on conflict it removes the entry, and on block it attaches caller-owned `state_block_data_t`, chooses async/poll/internal block type, inserts into the file list, and appends to `state_blocked_locks`. Unlocks cancel overlapping blocked locks, subtract the unlocked range from owned granted entries with split fragments when needed, issue `FSAL_OP_UNLOCK`, then retry grants for newly unblocked waiters. Test requests first use Ganesha's list for conflicts and then call FSAL `LOCKT` only if needed.

State and persistence behavior: Lock state is process-resident and protected by the per-object `st_lock`, `blocked_locks_mutex`, owner mutexes, export rwlocks, and atomic refcounts. Entries hold references to the owner, optional `state_t`, export, and object; they update SAL metrics as holders/waiters. The `lock_clientid_hint` on `state_file` is a transient optimization that records a single NFSv4 clientid, a mixed sentinel, or zero when the lock list empties. Grant cookies are stored in `ht_lock_cookies` and removed when grants complete, cancel, or release. No durable lock persistence is written here; recovery semantics are delegated to surrounding state/recovery modules and FSAL lock records.

Dependencies and integration points: Depends on FSAL object operations, export readiness/context switching, NFSv4 owner/client records, optional NLM and 9P owner support, Ganesha hash tables/lists/pools/logging, LTTng tracepoints, SAL metrics, and async state scheduling. FSAL capability checks (`fso_lock_support`, `fso_lock_support_async_block`, `fso_lock_full_control`) decide whether operations are passed through, converted, skipped, polled, or locally granted. NLM integration adds NSM client lock/share cleanup and global cancel paths; NFSv4 integration handles lease-time polling, grant availability, stale clientid unlock skips, and owner cleanup.

Risks: Range arithmetic around `UINT64_MAX` and zero-length "to EOF" locks is correctness-critical. List membership and refcount transitions are complex, especially when cookies, upcalls, cancel, unlock, export teardown, and polling race. The cookie hash functions are simple sum-based functions with TODO notes and may be weak under adversarial or high-volume cookie sets. `state_nlm_notify()` comments explicitly call out a vulnerability/race if a second SM_NOTIFY arrives while a local `newlocks` list is in use. Some fatal cleanup loops depend on repeated progress under memory pressure or stale exports. The file assumes callers respect lock ordering: per-file state lock for file list edits, `blocked_locks_mutex` for blocked list edits, and owner/export locks around their lists.

Test signals: Exercise overlapping read/write conflicts, same-owner merge/downgrade/upgrade, zero-length EOF ranges, split unlocks, duplicate blocking requests, nonblocking NFSv4 cancellation of a blocked request, async FSAL grant and available upcalls, grant cookie add/find/complete/release/cancel, export cleanup, NLM SM_NOTIFY/FREE_ALL with state counters, stale clientid unlock skip, and disabled-lock FSALs. Sanitizer and stress tests should focus on lock/cookie refcount races and list deletion while polling/upcalls are pending.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_misc.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/state_misc.c

Purpose: Provides miscellaneous SAL state utilities: state error stringification and conversion to FSAL/NFS status spaces, state-owner identity comparison/display, owner refcount/hash-cache lifecycle, file-wide state wipe, export-wide state release, and server id selection.

Important APIs/types/functions: Global state includes `cached_open_owners`, `cached_open_owners_lock`, `state_owner_pool`, and debug-only `state_owners_all`. Exported routines include `state_err_str()`, `state_error_convert()`, `nfs4_Errno_state()`, `nfs3_Errno_state()`, `state_unlock_err_ok()`, `state_owner_type_to_str()`, `different_owners()`, `display_owner()`, `_inc_state_owner_ref()`, `_dec_state_owner_ref()`, `free_state_owner()`, `get_state_owner_hash_table()`, `uncache_nfs4_owner()`, `get_state_owner()`, `hold_state_owner_ref()`, `state_wipe_file()`, `state_release_export()`, and `get_unique_server_id()`.

Control flow: Error conversion maps FSAL major codes into SAL state codes and then into protocol-specific NFSv4/NFSv3 status values, logging unexpected or internal-only cases. Owner lookup uses the owner-type-specific hash table, latches it, increments an existing owner unless its refcount reached zero, or allocates/copies/initializes a new owner and inserts it under the same latch. Refcount decrement removes the owner from its hash table if the count reaches zero, then dispatches to NLM/NFSv4/9P-specific free paths and releases pool memory. File wipe locks the object state, calls lock/share/NFSv4-state wipe routines, and unlocks. Export release sets an operation context for the export and runs lock, NFSv4 state, and NLM share cleanup.

State and persistence behavior: Owner objects are in-memory pooled objects keyed in per-protocol hash tables. The cached-open-owner list retains NFSv4 open owners using an extra reference until refreshed or uncached. Refcounts are atomic and use `atomic_inc_unless_0_int32_t()` where a racing free is possible. No persistent state is written; cleanup coordinates transient in-memory state and delegates protocol-specific persistence/recovery elsewhere.

Dependencies and integration points: Integrates with NLM, 9P, and NFSv4 owner compare/display/free functions, Ganesha hash tables, display buffers, logging, LTTng state tracepoints, FSAL object state, and export context helpers. `state_wipe_file()` directly invokes `state_lock_wipe()`, optional `state_share_wipe()`, and `state_nfs4_state_wipe()`. `state_release_export()` relies on `state_export_unlock_all()`, `state_export_release_nfs4_state()`, and optional `state_export_unshare_all()`.

Risks: Error conversion defaults can hide new FSAL errors as generic `STATE_FSAL_ERROR` unless maintained. Owner key hashing uses the copied `state_owner_t` structure; fields that are pointers or mutable must remain consistent with the compare functions. `_dec_state_owner_ref()` expects careful latch release behavior and can log critical errors if hash state diverges from refcount state. Cached owner uncache must not run while `so_mutex` can be destroyed. File/export cleanup relies on callers not already holding `st_lock` in incompatible contexts.

Test signals: Unit-test FSAL-to-state and state-to-NFS mappings, especially lock/share/grace/stale cases. Stress owner lookup/free with duplicate keys and racing decrefs, cache refresh/uncache of NFSv4 open owners, `hold_state_owner_ref()` against zero refcounts, file wipe ordering, and export release with NLM enabled and disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_share.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/state_share.c

Purpose: Implements NLM share reservation management when `_USE_NLM` is enabled. It maintains counted share access/deny modes, reopens files with FSAL share-deny flags, and removes share state from owner, NSM client, file, and export lists.

Important APIs/types/functions: `remove_nlm_share()`, `state_nlm_share()`, `state_share_wipe()`, and `state_export_unshare_all()`. It operates on `state_t`, `state_owner_t`, `state_nlm_client_t`, `state_nlm_share`, `fsal_openflags_t`, and FSAL access masks.

Control flow: `state_nlm_share()` locks object state, updates per-mode access/deny counters for share or unshare, recomputes union access/deny masks, and exits early if the union did not change. If unshare removes the last access mode, it removes all share list memberships and lets the state reference close the file. Otherwise it builds FSAL open flags, performs `test_access()`, calls `fsal_reopen2()` to apply open/share-deny mode, and, for a first active share, links the state into the owner, NSM client, file, and export share lists. Wipe/export cleanup iterate those lists and call `state_nlm_share(..., OPEN4_SHARE_ACCESS_ALL, OPEN4_SHARE_DENY_ALL, ..., unshare=true)`.

State and persistence behavior: Share reservations are in-memory counted state associated with the `state_t`. The active share keeps a `state_t` reference and NSM client reference, and list nodes connect it to owner/client/file/export cleanup paths. No durable persistence is performed here; NLM recovery interactions are through NSM client state and cleanup callbacks.

Dependencies and integration points: Depends on FSAL `test_access` and `fsal_reopen2`, export manager locks, NLM owner/client/NSM structures, SAL state references, and the object `STATELOCK`. Integrates with `state_wipe_file()`, `state_nlm_notify()`, and export release cleanup.

Risks: Counter underflow is guarded only by logging when unshare does not match an existing count; callers can still request mismatched unshares. `remove_nlm_share()` assumes list membership is valid and must be called exactly once for active shares. `state_nlm_share()` unlock path must handle FSAL errors after local counters were tentatively changed, so share counter consistency depends on this path being called with valid protocol sequencing. Export cleanup loops use an error limit and fatal on repeated failure.

Test signals: Cover repeated share/unshare counts, `OPEN4_SHARE_ACCESS_ALL` and `OPEN4_SHARE_DENY_ALL`, final unshare closing/removing state, access-denied and share-denied FSAL reopen failures, reclaim flags, file wipe, NSM client cleanup, and export unshare-all under stale object references.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/state_share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/avl/CMakeLists.txt

Purpose: Defines the build target for the embedded `avltree` object library used by Ganesha's tree data structures.

Important APIs/types/functions: Sets `avltree_STAT_SRCS` to `avl.c`, `bst.c`, `rb.c`, and `splay.c`; creates `add_library(avltree OBJECT ...)`; applies `add_sanitizers(avltree)`; sets `COMPILE_FLAGS "-fPIC"`; and, when `USE_LTTNG` is enabled, adds dependency on `gsh_trace_header_generate` and includes generated trace file properties.

Control flow: During CMake configure/generate, this file collects the four C source files into an object library so other targets can consume the compiled objects. Sanitizer instrumentation and PIC compilation are configured immediately on the target.

State and persistence behavior: No runtime state or persistence; build metadata only.

Dependencies and integration points: Depends on top-level sanitizer helper macros and optional LTTng generation state. The object library likely feeds shared/static Ganesha targets that need tree implementations without producing a standalone installed library here.

Risks: Forced `-fPIC` through `COMPILE_FLAGS` can interact awkwardly with toolchain-level flags. If `USE_LTTNG` generated property files are absent or stale, configure/build can fail. The file does not install headers or library artifacts directly.

Test signals: Configure with and without `USE_LTTNG`, with sanitizer options enabled, and verify downstream targets link object files from all four sources.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/avl.c -->
# sources/user-network-fs/nfs-ganesha/src/avl/avl.c

Purpose: Implements an intrusive AVL tree with parent pointers, cached first/last nodes, size/height accounting, and optional parent/balance bit packing on 64-bit pointer platforms.

Important APIs/types/functions: Exports `avltree_next()`, `avltree_prev()`, `avltree_size()`, `avltree_inf()`, `avltree_sup()`, `avltree_do_insert()`, `avltree_remove()`, `avltree_replace()`, and `avltree_init()`. Internal helpers manage parent/balance access, first/last traversal, `rotate_left()`, `rotate_right()`, and child assignment.

Control flow: Lookup-like infimum/supremum walks use the user comparator. Insertion initializes the node, links it under the located parent, updates cached first/last, walks back to the nearest unbalanced ancestor updating balances, then applies single or double rotations. Removal chooses a successor, relinks children/parent, updates first/last and size, then walks upward applying AVL delete rebalancing until height stabilizes. Replace rewires parent/child caches and copies the old node payload into the replacement.

State and persistence behavior: Tree state lives entirely in caller-provided `struct avltree` and embedded nodes. It stores no allocations and performs no persistence. On suitable platforms, low parent pointer bits encode balance, so node alignment is an implicit state invariant.

Dependencies and integration points: Uses `avltree.h` for node/tree layouts and comparator types. Consumers must embed `avltree_node` in their own objects and provide a strict comparator.

Risks: Intrusive replacement copies the whole node struct and requires callers to ensure the replacement's container state remains valid. Packed parent/balance mode depends on pointer alignment and `UINTPTR_MAX == UINT64_MAX`. Comparator instability or duplicate handling mistakes can corrupt tree ordering. `avltree_replace()` has a comment expressing skepticism about replacing a non-tree/rootless node and increments size in that branch.

Test signals: Insert ascending/descending/random keys, duplicate insert path through higher-level caller, delete leaf/one-child/two-child/root nodes, first/last maintenance, inf/sup edge cases, replace root and non-root, 32-bit fallback layout, and invariant checks for height/balance after randomized operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/avl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/bst.c -->
# sources/user-network-fs/nfs-ganesha/src/avl/bst.c

Purpose: Implements an intrusive threaded binary search tree with cached first/last nodes and optional thread-bit packing in pointer low bits.

Important APIs/types/functions: Exports `bstree_first()`, `bstree_last()`, `bstree_next()`, `bstree_prev()`, `bstree_lookup()`, `bstree_insert()`, `bstree_remove()`, `bstree_replace()`, and `bstree_init()`. Internal helpers distinguish child links from predecessor/successor threads.

Control flow: `do_lookup()` walks by comparator and returns matching node or insertion parent/side. Insert initializes the node and attaches it with predecessor/successor threads. Iteration follows real child links to subtree extremes or thread links. Removal handles leaf, one-child, and two-child cases, updating threads and cached endpoints. Replace finds the parent when needed, rewires parent/root and adjacent thread references, then copies the old node into the new node.

State and persistence behavior: Intrusive in-memory tree only; no allocation or persistence. Thread markers are either explicit booleans or low-bit pointer tags depending on platform support.

Dependencies and integration points: Includes `avltree.h` for shared tree declarations. Consumers own node storage and comparator behavior.

Risks: The tree is unbalanced, so ordered insertions can degrade to linear lookup/remove. Low-bit tagging requires pointer alignment. Removal calls `do_lookup(node, tree, ...)` and assumes comparator identity locates the actual node. Thread updates are easy to break around first/last and two-child removal.

Test signals: Verify inorder iteration after each insert/remove, first/last changes, removal of root/leaf/one-child/two-child nodes, replacement preserving threads, duplicate insert return, and pathological sorted insertion performance expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/bst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/rb.c -->
# sources/user-network-fs/nfs-ganesha/src/avl/rb.c

Purpose: Implements an intrusive red-black tree with parent pointers, cached first/last nodes, and optional parent/color bit packing.

Important APIs/types/functions: Exports `rbtree_first()`, `rbtree_last()`, `rbtree_next()`, `rbtree_prev()`, `rbtree_lookup()`, `rbtree_insert()`, `rbtree_remove()`, `rbtree_replace()`, and `rbtree_init()`. Internal helpers manage color/parent access, rotations, lookup, and child assignment.

Control flow: Insert performs normal BST insertion, colors the new node red, updates endpoint caches, then repairs red-black properties with recoloring and at most two rotations before forcing the root black. Removal selects successor if needed, transplants nodes, preserves successor color, handles easy red/single-red-child cases, and otherwise performs the standard double-black fixup with sibling recoloring/rotation. Iterators use parent links and subtree extremes.

State and persistence behavior: In-memory intrusive state only. Color may be stored in the low bit of the parent word, so alignment is part of the data representation.

Dependencies and integration points: Uses `avltree.h` shared declarations. Consumers supply stable comparators and node storage.

Risks: Delete fixup assumes sibling pointers exist in cases where red-black invariants require them; corrupted trees can crash. Replacement copies node memory and must be used only when callers manage embedded container implications. There is no explicit size field, unlike AVL. Packed parent/color mode can fail on unusual pointer representations.

Test signals: Randomized insert/delete with red-black invariant validation, endpoint iteration checks, root removal, replacement, duplicate insertion, and builds on platforms with and without `UINTPTR_MAX`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/rb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/splay.c -->
# sources/user-network-fs/nfs-ganesha/src/avl/splay.c

Purpose: Implements an intrusive top-down threaded splay tree, optimizing repeated access by rotating searched keys near or to the root.

Important APIs/types/functions: Exports `splaytree_first()`, `splaytree_last()`, `splaytree_next()`, `splaytree_prev()`, `splaytree_lookup()`, `splaytree_insert()`, `splaytree_remove()`, `splaytree_replace()`, and `splaytree_init()`. Internal helpers manage thread/link tagging, subtree extremes, rotations, and `do_splay()`.

Control flow: `do_splay()` performs top-down splaying with temporary left/right assembly roots until it finds the key or closest terminal position, then reassembles the tree with the chosen root. Lookup splays and returns root only on exact match. Insert splays around the new node's key, then attaches the previous root and one side subtree under the new node while updating first/last. Remove splays the target to root, then joins left and right subtrees. Replace splays the old node, asserts it is root, and copies node contents into the replacement.

State and persistence behavior: Intrusive volatile state only; no allocation. Threaded predecessor/successor pointers are encoded either with low-bit tags or explicit booleans.

Dependencies and integration points: Uses shared declarations from `avltree.h`; callers provide comparators and node storage.

Risks: `splaytree_remove()` and `splaytree_replace()` assert the target is present after splaying, so misuse is fatal in debug and corrupting in release. Splay trees have amortized bounds but individual operations can be expensive. Thread tagging has the same alignment assumptions as `bst.c`.

Test signals: Access locality tests showing root changes, randomized insert/lookup/remove with inorder validation, endpoint maintenance, missing-key lookup leaving nearest root, replacement, and 32-bit/no-tag builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/avl/splay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/bsd10.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/bsd10.cmake

Purpose: FreeBSD 10.1-oriented build preset that narrows the build to VFS-like support by disabling several optional FSALs and services.

Important APIs/types/functions: Sets `USE_FSAL_PROXY_V4`, `USE_FSAL_CEPH`, `USE_FSAL_GPFS`, `_MSPAC_SUPPORT`, `USE_9P`, and `USE_DBUS` to `OFF`, then emits a status message.

Control flow: Included by the top-level build when the BSD 10.1 configuration is selected; variables influence later `goption`, `find_package`, and subdirectory decisions.

State and persistence behavior: CMake cache/configuration state only.

Dependencies and integration points: Integrates with top-level option handling and platform-specific dependency discovery, especially avoiding unsupported Linux-centric dependencies on FreeBSD.

Risks: The comment says only VFS FSAL, but the file relies on defaults for any options not explicitly disabled. Future FSAL options may need explicit handling to preserve the minimal preset.

Test signals: Configure on FreeBSD-like and Linux hosts with this preset and verify disabled FSALs are not discovered or built.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/bsd10.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/debian.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/debian.cmake

Purpose: Debian package-oriented preset that enables DBus and admin tools for a DPKG build.

Important APIs/types/functions: Sets `USE_DBUS ON`, `USE_ADMIN_TOOLS ON`, and emits `Building DPKG`.

Control flow: Included during configure before dependent package and subdirectory logic evaluate these options.

State and persistence behavior: CMake configuration variables only.

Dependencies and integration points: Enables DBus/admin-tool build paths, implying later discovery of DBus-related dependencies and inclusion of admin utilities.

Risks: It does not force package generator selection itself; packaging behavior depends on surrounding CPack/debian logic. Missing DBus dependencies can make this preset fail or disable functionality depending on option-required handling.

Test signals: Configure a Debian packaging build and verify admin tools and DBus-dependent targets are present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/debian.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/everything.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/everything.cmake

Purpose: Broad feature preset intended to enable most optional build paths.

Important APIs/types/functions: Enables `PROXYV4_HANDLE_MAPPING`, `USE_DBUS`, `USE_CB_SIMULATOR`, `USE_FSAL_XFS`, `USE_FSAL_CEPH`, `USE_FSAL_RGW`, `USE_FSAL_GLUSTER`, and `USE_TOOL_MULTILOCK`.

Control flow: These variables are consumed by later option tests, dependency discovery, and target inclusion, making this a high-dependency configure mode.

State and persistence behavior: CMake configuration state only.

Dependencies and integration points: Pulls in optional FSALs, DBus, callback simulator, and multilock tool integration. It relies on the relevant `Find*.cmake` modules to locate dependencies or disable/fail features.

Risks: "Everything" is not exhaustive if newer options are added. It can expose dependency skew and optional API compatibility issues, especially Ceph/RGW/Gluster/XFS.

Test signals: Full dependency CI configure, package build, and smoke tests for all enabled FSAL/tool targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/everything.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/gpfs.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/gpfs.cmake

Purpose: GPFS/VFS/pNFS-oriented preset with DBus enabled and unrelated FSALs disabled.

Important APIs/types/functions: Sets `CMAKE_PREFIX_PATH "/usr/"`, enables `USE_FSAL_GPFS`, `USE_FSAL_VFS`, `USE_FSAL_PROXY_V4`, and `USE_DBUS`, disables `USE_FSAL_CEPH`, `_MSPAC_SUPPORT`, and `USE_9P`.

Control flow: Included at configure time to bias dependency lookup and feature selection toward GPFS and VFS targets.

State and persistence behavior: CMake variables/cache behavior only.

Dependencies and integration points: Integrates with GPFS, VFS, proxy v4, pNFS, and DBus build logic; disables Ceph/MSPAC/9P to avoid incompatible or unneeded dependencies.

Risks: Hard-coding `CMAKE_PREFIX_PATH` can override user/toolchain expectations. GPFS headers/libraries may be proprietary or platform-specific and require strict environment setup.

Test signals: Configure/build in a GPFS SDK environment and verify GPFS, VFS, proxy v4, and DBus targets while Ceph/9P are absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/gpfs.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/rpmbuild.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/rpmbuild.cmake

Purpose: RPM build preset placeholder that announces an RPM-oriented configuration.

Important APIs/types/functions: Emits `message(STATUS "Building RPM")`; it sets no feature variables itself.

Control flow: Included by external build selection; the top-level/default options and RPM packaging files carry the actual build behavior.

State and persistence behavior: No state beyond a CMake status message.

Dependencies and integration points: Depends entirely on surrounding RPM build scripts/spec logic and default options.

Risks: The comment says "Turn on everything" but the file does not set options, so it can be misleading and may not match RPM packager expectations.

Test signals: Compare RPM preset configure output and enabled options against the RPM spec or packaging policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/rpmbuild.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/vfs_only.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/vfs_only.cmake

Purpose: Minimal VFS-focused preset with DBus enabled and several non-VFS features disabled.

Important APIs/types/functions: Disables `USE_FSAL_PROXY_V4`, `USE_FSAL_CEPH`, `USE_FSAL_GPFS`, `_MSPAC_SUPPORT`, and `USE_9P`; enables `USE_DBUS`.

Control flow: Included during configure to shape later option/dependency decisions.

State and persistence behavior: CMake configuration state only.

Dependencies and integration points: Keeps the build near VFS plus DBus, reducing optional FSAL dependency discovery.

Risks: As with other presets, future FSALs not explicitly disabled may still be enabled by defaults. DBus remains enabled despite the "vfs only" name, so a truly minimal build may require additional overrides.

Test signals: Configure and verify only expected VFS/DBus targets are built; run with missing Ceph/GPFS deps to ensure they are not required.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/build_configurations/vfs_only.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/cpack_config.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/cpack_config.cmake

Purpose: Defines common CPack metadata and source/binary package generator settings for NFS-Ganesha.

Important APIs/types/functions: Sets `CPACK_PACKAGE_NAME`, `CPACK_PACKAGE_VERSION`, `CPACK_PACKAGE_VENDOR`, `CPACK_PACKAGE_DESCRIPTION_SUMMARY`, Debian maintainer, RPM component behavior, ignored component groups, `CPACK_GENERATOR`, `CPACK_SOURCE_GENERATOR`, source ignore patterns, and `CPACK_SOURCE_PACKAGE_FILE_NAME`.

Control flow: Included by top-level packaging configuration before `include(CPack)` so these variables control generated TGZ/source packages and package metadata.

State and persistence behavior: Packaging configuration state only; generated archives are produced by CPack outside this file.

Dependencies and integration points: Uses `GANESHA_VERSION` from the surrounding build. Integrates with CPack Debian/RPM/TGZ generators but sets both binary and source generators to TGZ here.

Risks: Maintainer and package metadata can drift from distro-specific package files. `CPACK_SOURCE_IGNORE_FILES` prepends git-related ignores while preserving prior ignore patterns, so ordering and regex escaping matter.

Test signals: Run `cpack` and source package generation, inspect archive name/version, metadata, and ignored files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/cpack_config.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/gitdesc_from_path.sh -->
# sources/user-network-fs/nfs-ganesha/src/cmake/gitdesc_from_path.sh

Purpose: Extracts a git description fragment from a path-like input, used by build/version tooling.

Important APIs/types/functions: Shell pipeline assigns `res` by stripping everything through `_desc_` and removing a trailing `-[0-9]*.[0-9]*.[0-9]*` pattern; prints `NO-GIT` when empty, otherwise prints the result.

Control flow: One positional argument is transformed through `sed`; output is a single line.

State and persistence behavior: Stateless shell utility; no files are modified.

Dependencies and integration points: Depends on `/bin/sh` plus `sed`. Likely called from CMake/version scripts when deriving metadata from generated archive paths.

Risks: `$1` is unquoted in `echo $1`, so whitespace, glob characters, or leading options can be mangled. Pattern matching is specific to archive naming conventions and may return unexpected strings if `_desc_` appears multiple times.

Test signals: Inputs with no desc, with `_desc_<hash>-1.2.3`, with spaces, and with unusual suffixes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/gitdesc_from_path.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/githead_from_path.sh -->
# sources/user-network-fs/nfs-ganesha/src/cmake/githead_from_path.sh

Purpose: Extracts a git head/hash-like token from a path-like input.

Important APIs/types/functions: Splits `$1` on underscores and hyphens, filters tokens containing `git`, strips the literal `git`, and prints `NOT-GIT` if no token remains.

Control flow: Single shell pipeline using `sed`, `grep`, and `sed`; emits one or more matching stripped tokens depending on input.

State and persistence behavior: Stateless utility; no persistence.

Dependencies and integration points: Depends on `/bin/sh`, `sed`, and `grep`. Used by build/version extraction paths.

Risks: Unquoted `$1` can be word-split or glob-expanded. Multiple `git` tokens can produce multi-line output. The parser accepts any token containing `git`, not just structured version metadata.

Test signals: Paths with `git<sha>`, no git marker, multiple git-like segments, and whitespace.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/githead_from_path.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/goption.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/goption.cmake

Purpose: Provides custom option macros that distinguish defaulted options from explicit user requests, allowing missing dependencies to be optional or required depending on command-line intent.

Important APIs/types/functions: `goption(OPTNAME DESC DEFVAL)` stores cache value `DEFAULT_ON` or `DEFAULT_OFF` with allowed strings `ON OFF`. `gopt_test(OPTNAME)` normalizes the option to `ON`/`OFF` and sets `${OPTNAME}_REQUIRED` to empty for defaults or `REQUIRED` for explicit user settings.

Control flow: Callers define options with `goption`, then call `gopt_test` before `find_package` or custom dependency checks. Later code uses `${OPTNAME}_REQUIRED` to decide fatal vs warning/disable behavior.

State and persistence behavior: CMake cache variables are mutated and sometimes forced. The default sentinel values persist until `gopt_test` normalizes them.

Dependencies and integration points: Central to FSAL/feature option handling throughout the CMake tree, especially optional dependencies.

Risks: Macro conditionals rely on dynamic variable expansion and string matches; malformed cache values can lead to surprising branches. The example comment has a duplicated `elseif (USE_FSAL_TEST_REQUIRED)` where an `else` was probably intended. Cache forcing explicit values can surprise repeated configure runs.

Test signals: Configure with omitted option, `-DOPT=ON`, `-DOPT=OFF`, invalid string, and dependency missing to verify required/default behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/goption.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/maintainer_mode.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/maintainer_mode.cmake

Purpose: Defines strict maintainer/debug compiler flags and validates allowed `CMAKE_BUILD_TYPE` values.

Important APIs/types/functions: Sets `CMAKE_CXX_FLAGS_MAINTAINER`, `CMAKE_C_FLAGS_MAINTAINER`, linker flag cache entries, derived Debug flags with `-g`, allowed build type list, cache documentation for `CMAKE_BUILD_TYPE`, default Debug selection, and `USE_UNWIND`/`USE_UNWIND_ENRICHED_BT` defaults when build type is empty.

Control flow: Included during configure; it forces cache values for maintainer/debug flags, defaults empty build type to Debug, and sends an error if the selected build type is outside the allowed list.

State and persistence behavior: Mutates CMake cache aggressively with `FORCE`; no runtime state.

Dependencies and integration points: Interacts with compiler warning support, unwind/backtrace options, and all targets via global C/CXX/linker flags.

Risks: Forced `-Werror` in maintainer flags can break builds on newer compilers or third-party headers. Defaults an empty build type to Debug, which differs from some CMake conventions. Shared linker Debug flags use `CMAKE_EXE_LINKER_FLAGS_MAINTAINER`, likely intentional but worth verifying.

Test signals: Configure each allowed build type, invalid build type, empty build type, GCC/Clang warning compatibility, and builds with/without unwind dependencies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/maintainer_mode.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindASan.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindASan.cmake

Purpose: Sanitizer module for AddressSanitizer support on targets that opt into sanitizer helpers.

Important APIs/types/functions: Defines option `SANITIZE_ADDRESS`, candidate compiler flags, incompatibility check with thread/memory sanitizers, includes `sanitize-helpers`, finds optional `asan-wrapper`, and defines `add_sanitize_address(TARGET)`.

Control flow: If ASan is enabled, compiler flags are probed through `sanitizer_check_compiler_flags`; target calls add the selected flags via `sanitizer_add_flags`.

State and persistence behavior: CMake option/cache state only.

Dependencies and integration points: Integrates with shared sanitizer helper macros and target-level `add_sanitizers` usage.

Risks: Mutually exclusive sanitizer checks only cover thread/memory, not all possible sanitizer conflicts. Wrapper discovery depends on `CMAKE_MODULE_PATH`.

Test signals: Configure ASan on/off, with TSan/MSan conflict, and compile a sanitized target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindASan.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCEPHFS.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCEPHFS.cmake

Purpose: Finds CephFS headers/libraries and detects optional libcephfs API capabilities that control FSAL_CEPH feature macros.

Important APIs/types/functions: Consumes optional `CEPH_PREFIX`; sets `CEPHFS_INCLUDE_DIR`, `CEPHFS_LIBRARY_DIR`, `CEPHFS_LIBRARY`, `CEPHFS_LIBRARIES`, and feature variables such as `USE_FSAL_CEPH_MKNOD`, `USE_FSAL_CEPH_SETLK`, `USE_FSAL_CEPH_LL_LOOKUP_ROOT`, `USE_FSAL_CEPH_LL_DELEGATION`, `USE_FSAL_CEPH_LL_SYNC_INODE`, `USE_CEPH_LL_FALLOCATE`/related fallocate variables, `USE_FSAL_CEPH_ABORT_CONN`, `USE_FSAL_CEPH_RECLAIM_RESET`, `USE_FSAL_CEPH_GET_FS_CID`, `USE_FSAL_CEPH_REGISTER_CALLBACKS`, `USE_FSAL_CEPH_LOOKUP_VINO`, `USE_FSAL_CEPH_STATX`, and nonblocking/zerocopy toggles.

Control flow: Prefix hints are searched first with `NO_DEFAULT_PATH`; fallback searches use default paths. The module verifies `ceph_ll_lookup` to accept the library, clears include/library cache on failure, then runs many `check_library_exists()` and `check_symbol_exists()` probes to enable or disable feature-specific compile definitions. It finishes with `FIND_PACKAGE_HANDLE_STANDARD_ARGS`.

State and persistence behavior: CMake cache and feature variables only. It may unset cached include/library dirs when a required symbol is missing.

Dependencies and integration points: Requires CMake library/symbol check modules, libcephfs, `cephfs/libcephfs.h`, and FSAL_CEPH source conditionals that consume the feature variables.

Risks: There is a variable inconsistency around fallocate (`USE_CEPH_FALLOCATE` vs `USE_CEPH_LL_FALLOCATE`). `CEPHFS_LIBRARIES` is set even when the library is missing. Some messages mention different symbol names than checked. API probes are numerous and need maintenance as Ceph evolves.

Test signals: Configure against old and new Ceph versions, with `CEPH_PREFIX`, without Ceph, and verify generated config headers/compile definitions match available symbols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCEPHFS.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCUnit.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCUnit.cmake

Purpose: Finds CUnit library and headers for C unit test builds.

Important APIs/types/functions: Consumes `CUNIT_PREFIX`; sets `CUNIT_LIBRARIES` from library `cunit` and `CUNIT_INCLUDE_DIR` from `CUnit/Basic.h`; uses `find_package_handle_standard_args`.

Control flow: Searches library and include path, then reports success only if both are present.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Test targets using CUnit consume the discovered include/library variables.

Risks: Library name casing and platform package naming can vary. It searches `${CUNIT_PREFIX}` directly for libraries but `${CUNIT_PREFIX}/include` for headers, which may miss lib/lib64 under a prefix.

Test signals: Configure tests with system CUnit, custom prefix, and missing library/header combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCUnit.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCaps.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCaps.cmake

Purpose: Finds Linux capabilities support through libcap and `sys/capability.h`.

Important APIs/types/functions: Consumes `CAPS_PREFIX`; finds library `cap` into `CAPS`, checks `cap_set_proc` into `HAVE_SET_PROC`, finds `CAPS_INCLUDE_DIR`, and sets `CAPS_LIBRARIES` only when the function check passes.

Control flow: Library symbol availability gates the final library variable, then `find_package_handle_standard_args` requires both `CAPS_LIBRARIES` and include dir.

State and persistence behavior: CMake cache/check variables only.

Dependencies and integration points: Used by privilege/capability handling code that needs libcap.

Risks: `check_library_exists(cap cap_set_proc "" HAVE_SET_PROC)` does not use the found `CAPS` path, so custom prefixes may fail symbol checks if not on default linker paths. The intermediate library variable is named `CAPS`, while consumers likely use `CAPS_LIBRARIES`.

Test signals: Configure with system libcap, custom prefix, header-only missing lib, and lib path not in default linker search.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindCaps.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindEPOLL.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindEPOLL.cmake

Purpose: Detects epoll support, with FreeBSD-based platforms treated as supported via emulation.

Important APIs/types/functions: Uses `BSDBASED`, `check_include_files("sys/epoll.h" EPOLL_HEADER)`, `check_function_exists(epoll_create EPOLL_FUNC)`, and `FIND_PACKAGE_HANDLE_STANDARD_ARGS(EPOLL ...)`.

Control flow: If `BSDBASED` is true, sets `EPOLL_FOUND ON` and returns. Otherwise it requires both header and function checks.

State and persistence behavior: CMake check result variables only.

Dependencies and integration points: Event-loop/network code conditions on `EPOLL_FOUND`.

Risks: The documented `EPOLL_PATH_HINT` is not used. `check_function_exists` may need libraries on unusual platforms. FreeBSD emulation is assumed without validating the emulation header/API here.

Test signals: Configure on Linux, FreeBSD, and a non-epoll Unix; verify generated feature decisions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindEPOLL.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindExecInfo.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindExecInfo.cmake

Purpose: Finds `execinfo.h` and libexecinfo for backtrace support on platforms where it is separate.

Important APIs/types/functions: Sets `EXECINFO_INCLUDE_DIR`, `EXECINFO_LIBRARY`, and `EXECINFO_FOUND`; emits status or fatal error based on find mode.

Control flow: Simple header/library search, manual found handling, and optional fatal if required.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Backtrace/unwind diagnostics may consume these variables.

Risks: Required-variable name uses `ExecInfo_FIND_REQUIRED` while the module file is `FindExecInfo.cmake`; CMake package-name casing can make this brittle. It does not use `FindPackageHandleStandardArgs`.

Test signals: Configure on glibc where execinfo may not require a separate library, FreeBSD with libexecinfo, and required missing cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindExecInfo.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindGTest.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindGTest.cmake

Purpose: Finds GoogleTest libraries and headers for C++ test targets.

Important APIs/types/functions: Consumes `GTEST_PREFIX`; finds `gtest` and `gtest_main` into `GTEST`/`GTEST_MAIN`, finds `gtest/gtest.h`, sets `GTEST_LIBRARIES`, and uses standard package handling.

Control flow: Search variables are resolved, then package success requires `GTEST_LIBRARIES` and `GTEST_INCLUDE_DIR`.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Test targets link `${GTEST_LIBRARIES}` and include `${GTEST_INCLUDE_DIR}`.

Risks: Some modern GTest installs provide CMake package targets instead of raw libraries, and library names may be debug-suffixed. The module requires both gtest and gtest_main even if a target supplies its own main.

Test signals: Configure with distro GTest, source-built prefix, missing `gtest_main`, and target linking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindGTest.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindGperftools.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindGperftools.cmake

Purpose: Finds gperftools profiler support.

Important APIs/types/functions: Consumes `Gperftools_ROOT_DIR`; finds `profiler` library into `GPERFTOOLS_PROFILER`, finds `gperftools/heap-profiler.h`, sets `GPERFTOOLS_LIBRARIES`, and uses `find_package_handle_standard_args`.

Control flow: Hinted library/header searches populate variables, then standard args report package status.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Profiling or allocator-related build options can link the profiler library.

Risks: Comments mention tcmalloc but only profiler is searched. It does not find `tcmalloc` or `tcmalloc_and_profiler`, so allocator use is handled elsewhere or unsupported by this module.

Test signals: Configure with gperftools installed/missing, custom root, and profile-enabled target linking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindGperftools.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindJeMalloc.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindJeMalloc.cmake

Purpose: Finds jemalloc headers and library.

Important APIs/types/functions: Consumes CMake or environment `JEMALLOC_ROOT_DIR`; searches common prefixes, finds `jemalloc.h` under `include/jemalloc`, finds library `jemalloc`, sets `JEMALLOC_LIBRARIES` and `JEMALLOC_INCLUDE_DIRS` on success.

Control flow: Root hints and platform prefixes feed `FIND_PATH`/`FIND_LIBRARY`; standard package args determine `JEMALLOC_FOUND`.

State and persistence behavior: CMake cache variables only.

Dependencies and integration points: Optional allocator selection can include/link jemalloc using the exported variables.

Risks: Header search only uses `include/jemalloc`, which may miss installs exposing `jemalloc/jemalloc.h` differently unless include usage matches. Environment variable import can surprise hermetic builds.

Test signals: Configure with system jemalloc, custom root/env root, missing header/library, and allocator-enabled link.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindJeMalloc.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindKrb5.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindKrb5.cmake

Purpose: Finds Kerberos 5 and requested krb5-config components, producing include directories and ordered libraries for RPCSEC_GSS/GSSAPI-related builds.

Important APIs/types/functions: Consumes `KRB5_PREFIX` and `KRB5_FIND_COMPONENTS`; finds `krb5-config`, runs it for `--cflags` and `--libs`, parses `-I`, `-L`, and `-l` flags, appends `gssapi_krb5`, finds each library, and sets `KRB5_FOUND`, `KRB5_INCLUDE_DIRS`, and `KRB5_LIBRARIES`.

Control flow: If `krb5-config` is missing, marks not found. If present, command execution results must be zero before include/library parsing proceeds. Each parsed library is resolved with hinted and default searches; any missing library clears found state. Final status or fatal messaging depends on find options.

State and persistence behavior: CMake cache/library variables only.

Dependencies and integration points: Security/authentication build paths consume Kerberos headers and libraries, especially GSSAPI.

Risks: It unconditionally prepends `"${KRB5_PREFIX}/include"` even when prefix is unset. It always appends `gssapi_krb5`, which may be MIT-specific and wrong for Heimdal. Existing `KRB5_LIBRARIES` is not cleared before accumulation in repeated configure scenarios.

Test signals: Configure with MIT Kerberos, Heimdal, custom prefix, component lists such as `gssapi`, missing `krb5-config`, and repeated reconfigure after changing prefix.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindKrb5.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLSB_release.cmake -->
# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLSB_release.cmake

Purpose: Finds the `lsb_release` executable and captures distribution metadata into CMake variables.

Important APIs/types/functions: Sets `LSB_RELEASE_EXECUTABLE`, `LSB_RELEASE_VERSION_SHORT`, `LSB_RELEASE_ID_SHORT`, `LSB_RELEASE_DESCRIPTION_SHORT`, `LSB_RELEASE_RELEASE_SHORT`, and `LSB_RELEASE_CODENAME_SHORT`; strips quotes from description; uses standard package handling.

Control flow: If executable is found, runs `lsb_release` with `-vs`, `-is`, `-ds`, `-rs`, and `-cs` and stores stripped outputs. Package success requires only the executable.

State and persistence behavior: Configure-time detection variables only.

Dependencies and integration points: Packaging or distro-specific configuration can consume release metadata.

Risks: Execute results are not checked individually, so command failures can leave empty metadata while the package is considered found. Non-LSB systems may lack the command despite having `/etc/os-release`.

Test signals: Configure on Debian/RHEL/Ubuntu, container images without `lsb_release`, and systems with quoted descriptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLSB_release.cmake -->
