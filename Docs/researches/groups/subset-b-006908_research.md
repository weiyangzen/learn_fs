# subset-b-006908 research

## sources/distributed-fs/ceph/src/mds/CDir.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CDir.h -->
# sources/distributed-fs/ceph/src/mds/CDir.h

## Purpose
`CDir.h` declares `CDir`, the MDS cache object for one directory fragment. A `CDir` is owned by a `CInode`, keyed by `dirfrag_t`, and stores cached dentries plus the per-fragment `fnode_t` statistics that are committed to metadata objects. It is the boundary object for directory authority, import/export, freezing, fetch/commit, scrub, bloom-filter lookup hints, and fragment split/merge.

## Important APIs, Types, And State
The class inherits `MDSCacheObject` and `Counter<CDir>`, so it participates in common cache object state, waiters, authority, pins, and dumping. Important nested types are `dentry_key_map`, `dentry_key_set`, `fnode_ptr`, `dentry_commit_item`, `freeze_tree_state_t`, and `scrub_info_t`. `dentry_commit_item` is the commit staging structure for null, remote, and primary dentries; it carries key, snap range, inode data, xattrs, old inode map, snaprealm data, symlink text, features, damage flags, and alternate names.

Major public APIs include `lookup`, `add_null_dentry`, `add_primary_dentry`, `add_remote_dentry`, `link_*_inode`, `unlink_inode`, `remove_dentry`, `split`, `merge`, `fetch`, `fetch_keys`, `commit`, `mark_complete`, `mark_dirty`, `mark_clean`, `encode_export`, `decode_import`, `freeze_tree`, `freeze_dir`, `unfreeze_tree`, `unfreeze_dir`, and scrub methods. Accessors expose the owning inode, frag id, auth state, fnode versions, dentry counts, and stats.

State is represented by many explicit bits. Important bits include completeness, frozen/freezing tree and dir states, committing, fetching, creating, import/export bounds, active importing/exporting, fragmenting, sticky pinning, dirty dirfragtree, bad fragment, open-file-table tracking, and auxiliary subtree. Masks define which bits survive export/import/fragment operations.

## Control Flow And Persistence
The normal data path is: a `CInode` opens or locates a `CDir`; dentries are inserted, linked, unlinked, or loaded; mutations project an `fnode_t`; journal callbacks pop projected fnode state; dirty fragments are committed via OMAP operations. Fetch methods load full fragments or selected keys from backing metadata objects. Commit helpers encode fnode headers, dentry records, stale removals, and primary inode payloads.

`fnode` is held through shared immutable pointers, with `project_fnode` creating mutable copies for mutations. This mirrors `CInode` projected metadata and lets log events share stable snapshots. `pre_dirty`, `_mark_dirty`, `mark_dirty`, and `mark_clean` coordinate versioning, log segment membership, and dirty pins. `_encode_base` and `_decode_base` serialize first snap, fnode, replication mode, and replica list data for import/export or metadata movement.

## Dependencies And Integration Points
`CDir` depends tightly on `CInode`, `CDentry`, `MDCache`, `MDSContext`, `Mutation`, `LogSegmentRef`, `MDSCacheObject`, `snap.h`, and Ceph buffer encoding. It is a friend of migrator, discovery, balancer, cache, and commit/fetch context classes. `CInode` uses `CDir` for dirfrag ownership, scatter-stat accounting, auth-pin propagation, export pinning, freezing checks, and path construction. `Locker` and `MDCache` integrate with `lock_caches_with_auth_pins`, dir auth pins, waiters, and subtree authority.

## Risks
The highest-risk behavior is state coupling: fragment dirtyness, auth pins, freeze states, projected fnode queues, and import/export masks must stay synchronized. Losing or double-clearing pins can deadlock migration or trim active metadata. Bloom filters are intentionally not serialized, so callers that enable them must maintain accuracy until `mark_complete` deletes them. Split/merge and subtree auth transitions must preserve dentry waiters and stat accounting. Bad-fragment paths must register damage consistently so scrub and recovery do not trust corrupted metadata.

## Test Signals
Useful test signals include directory fetch/commit round trips, split and merge under active waiters, auth import/export with dirty and boundary fragments, scrub detecting local stat mismatch, damage injection on dentry/header decode, freeze/unfreeze with nested auth pins, and replica rejoin with preserved exported mask bits. Assertions around ref counts, dirty counters, projected fnode emptiness, and dirfrag leaf membership are also important runtime guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CDir.h -->

## sources/distributed-fs/ceph/src/mds/CInode.cc
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CInode.cc -->
# sources/distributed-fs/ceph/src/mds/CInode.cc

## Purpose
`CInode.cc` implements Ceph MDS cached inode behavior. It covers inode store serialization, projected metadata mutation, dirfrag management, lock-state replication, scatter-stat accounting, snaprealm copy-on-write, client capability issuance, auth pinning and freezing, backtrace and root inode persistence, import/export, scrub validation, export pin policies, and inodestat/cap message encoding.

## Important APIs And Control Flow
The file starts with `CInodeCommitOperation::update`, which writes parent backtrace xattrs and, for current pools, layout and symlink xattrs. `CInode` construction wires all lock objects and list items; destruction closes dirfrags and snaprealms and asserts that projected snapnodes, notable caps, subtree roots, exporting dirs, and batch ops are gone.

Projection is central. `project_inode` clones the current projected inode, optionally clones xattrs and prepares a projected snapnode, then registers the projection with a mutation. `pop_and_dirty_projected_inode` pops the oldest projected node after journaling, installs inode/xattrs/snaprealm state, marks the inode dirty, dirties parent backtrace when needed, and re-evaluates export pins if layout or pin policy changed.

Dirfrag flow includes `pick_dirfrag`, `get_dirfrags_under`, `get_or_open_dirfrag`, `add_dirfrag`, `close_dirfrag`, and sticky-dir pin propagation. Opened fragments must remain leaves in `dirfragtree`; `verify_dirfrags` and `force_dirfrags` enforce this. Path APIs walk primary or projected parents, with trimmed paths avoiding expensive long-path logging.

Persistence flow is split between inode objects and backtraces. `store` writes base/system inode data into `.inode` objects. `fetch` reads both legacy xattr and `.inode` formats and decodes whichever exists. `build_backtrace`, `_store_backtrace`, `store_backtrace`, and `_stored_backtrace` update object parent xattrs in the current and old data pools, handling deleted-pool `ENOENT` specially. `flush` gathers parent backtrace and inode/parent-dir commits.

Lock replication uses per-lock encode/decode helpers for auth, link, dirfrag tree, file, nest, xattr, snap, flock, and policy locks. Scatter locks (`filelock`, `nestlock`, `dirfragtreelock`) exchange inode-level summaries plus per-dirfrag stats. `start_scatter`, `finish_scatter_update`, `finish_scatter_gather_update`, and `finish_scatter_gather_update_accounted` reconcile dirfrag stats into inode totals and journal accounted stat updates.

Snap logic opens and closes `SnapRealm`, projects srnodes, records past parents, copies old inode intervals via `cow_old_inode`, purges stale old inode state, and selects old inode intervals for snapped lookups. Client capability flow uses `add_client_cap`, `remove_client_cap`, `reconnect_cap`, `export_client_caps`, `get_caps_allowed_*`, `get_caps_issued`, `get_caps_wanted`, and loner selection to map lock states and client features to issued caps.

`encode_inodestat` is the client reply bridge. It selects stable versus projected inode fields based on client xlocks/loner status, selects old inode data for snapshots, optionally emits inline data and xattrs, creates caps when allowed, and supports both newer tuple-based reply encoding and legacy feature-gated encoding. `encode_cap_message` similarly chooses projected or stable fields for asynchronous cap updates.

## State And Persistence Behavior
Important persistent state includes `inode_t`, xattrs, symlink, dirfragtree, snap blob, old inode map, oldest snap, damage flags, root inode objects, dentry-embedded inode stores, and object backtrace xattrs. Important transient state includes pins, waiters, projected nodes, snaprealm objects, dirfrags, locks, client caps, MDS cap wants, dirty list items, freeze flags, ephemeral pins, scrub info, and validation shadow inodes.

Import/export encodes base inode state, exported state bits, popularity vectors, replicas, boundary dirfrag stats, full lock state, and file locks. Import restores auth state, dirty pins, replicas, boundary stats when valid, and locks. Export completion masks local-only state and clears popularity and loner state.

## Dependencies And Integration Points
The implementation is coupled to `CDir`, `CDentry`, `Capability`, `SnapRealm`, `MDCache`, `MDSRank`, `MDLog`, `Locker`, `MDBalancer`, `Mutation`, `EUpdate`, `Objecter`, `InoTable`, `DamageTable`, `OpenFileTable`, `MClientCaps`, and `MClientReply`. It relies on Ceph buffer encoding, feature bits, object operations, gather contexts, MDS finishers, logger counters, and config gates such as scatter verification, backtrace verification, and ephemeral export pin policies.

## Risks
The main risk is sequencing. Projected inode state must be popped only after journal safety; otherwise clients or replicas can see state that is not durable. Scatter-stat reconciliation intentionally trusts dirfrags in repair paths but must preserve versions and avoid counting stale/frozen fragments. Capability issuance must respect stale sessions, quiesce locks, client feature support, snaprealm mismatches, and exporting caps. Backtrace persistence spans old pools and can encounter deleted pools. Freeze/auth-pin propagation is deadlock-sensitive. Import/export masks must not drop durable dirty or pin policy state.

## Test Signals
Strong tests include encode/decode round trips for `InodeStore`, bare stores, lock states, export/import payloads, and capability export/import structs; mutation tests for projected inode/xattr/snaprealm pop order; persistence tests for root inode store/fetch and backtrace update across pool changes; MDS recovery/rejoin tests for lock state and scatter dirty flags; cap tests for stale sessions, loner changes, quiesce masks, inline-data and pool namespace feature gating; scrub tests for bad backtraces, dirty directories, damaged dirfrags, and repair mode; export-pin tests for explicit, distributed ephemeral, and random ephemeral policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CInode.cc -->

## sources/distributed-fs/ceph/src/mds/CInode.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CInode.h -->
# sources/distributed-fs/ceph/src/mds/CInode.h

## Purpose
`CInode.h` declares the backing store and cached runtime interface for CephFS MDS inodes. `InodeStoreBase` holds serializable inode data without full cache behavior. `InodeStore` and `InodeStoreBare` support encoded standalone and embedded inode forms. `CInode` adds MDS cache-object behavior: lock objects, dirfrags, parent links, snaprealms, caps, freezing, persistence, validation, import/export, and policy controls.

## Important APIs, Types, And State
`InodeStoreBase` defines mempool-backed pointer types for `inode_t`, xattrs, and old inode maps, plus allocators, encode/decode helpers, JSON decode, dentry hash selection, and dirfrag picking. `CInodeCommitOperation` and `CInodeCommitOperations` package objecter mutations for backtrace and layout/symlink xattrs.

`CInode::validated_data` captures scrub validation results for backtrace, inode data, and raw stats. `CInode::scrub_info_t` tracks scrub/uninline progress, queued fragments, scrub headers, and dirty scrub stamps. `projected_inode` and private `projected_const_node` represent copy-on-write projected metadata used between mutation start and journal completion.

The class declares many pins (`PIN_DIRFRAG`, `PIN_CAPS`, `PIN_FREEZING`, `PIN_FROZEN`, `PIN_DIRTYRSTAT`, `PIN_EXPORTINGCAPS`, etc.), state bits (`STATE_FREEZING`, `STATE_FROZEN`, `STATE_AMBIGUOUSAUTH`, `STATE_DIRTYPARENT`, `STATE_DIRTYRSTAT`, `STATE_REPAIRSTATS`, `STATE_CLIENTWRITEABLE`, ephemeral pin bits, and others), export masks, and wait masks. Lock members include `quiescelock`, `versionlock`, `authlock`, `linklock`, `dirfragtreelock`, `filelock`, `xattrlock`, `snaplock`, `nestlock`, `flocklock`, and `policylock`.

## Control Flow And Persistence
The declaration exposes the complete lifecycle: construct with `MDCache`, open or add dirfrags, project inode/xattr/snaprealm state, journal and pop projections, mark dirty and clean, store/fetch base inode objects, store/fetch backtraces, flush pending state, encode/decode stores, encode/decode lock state, export/import cache state, and validate on-disk state.

Directory behavior is expressed through `dirfrags`, `dirfragtree`, subtree root counters, sticky dir refs, nested dirfrag queries, fragment verification, and split/merge support through `CDir`. Snapshot behavior is expressed through `first`, `last`, `old_inodes`, `oldest_snap`, snaprealm open/close/project methods, old inode copy-on-write, and stale snap data purge.

Client capability behavior is declared through the `client_caps` map, MDS cap wants, loner cap selection, add/remove/reconnect/export cap operations, allowed/issued/wanted cap calculations, client writeable tracking, and reply/message encoders. Freeze/auth behavior is declared through `can_auth_pin`, `auth_pin`, `auth_unpin`, `freeze_inode`, `unfreeze_inode`, and frozen auth-pin helpers.

## Dependencies And Integration Points
This header is a central MDS include. It depends on Ceph metadata types, lock classes, `Capability`, `ScrubHeader`, `inode_backtrace_t`, `flock`, `MDSCacheObject`, `Context`, `Counter`, mempool containers, and `LogSegmentRef`. It forward-declares many peers to reduce include pressure: `CDir`, `CDentry`, `MDCache`, `Session`, `SnapRealm`, `MutationImpl`, `MDRequestImpl`, `EMetaBlob`, and message/object operation classes.

## Risks
`CInode.h` exposes many friend classes and mutable state containers, so invariants are distributed across MDS subsystems. The RCU-like immutable pointer model requires callers to project before mutation and pop in journal order. State masks must match migration semantics. Cap counters must stay aligned with `OpenFileTable` and `SnapRealm` membership. Raw pointers to parents, dirfrags, snaprealms, and file-lock state require careful ownership and teardown.

## Test Signals
Header-level coverage should be reflected in dencoder tests for `InodeStore`/`InodeStoreBare`, compile coverage for lock type arrays, unit or integration tests around projection and dirty marking, cap add/remove accounting, snap old-inode interval lookup, dirfrag leaf verification, freeze/auth-pin behavior, and scrub validation result dumping. Static assertions are absent, so runtime assertions and MDS integration tests are the main guardrail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CInode.h -->

## sources/distributed-fs/ceph/src/mds/CMakeLists.txt
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/mds/CMakeLists.txt

## Purpose
This CMake file defines the `mds` static library for Ceph's Metadata Server implementation. It collects the MDS source files that implement server request handling, metadata cache objects, journaling, migration, balancing, locks, snap handling, sessions, metrics, quiesce logic, and related common components.

## Important Build APIs And Targets
The file sets `mds_srcs` with local MDS implementation files including `Capability.cc`, `MDSDaemon.cc`, `MDSRank.cc`, `Server.cc`, `Mutation.cc`, `MDCache.cc`, `CDentry.cc`, `CDir.cc`, `CInode.cc`, lock classes, snap classes, table clients/servers, scrub, damage, metrics, and quiesce components. It also includes shared sources from `src/common`, `src/osdc`, and `src/mgr` such as `TrackedOp.cc`, `MemoryModel.cc`, `Journaler.cc`, and `MDSPerfMetricTypes.cc`.

The build creates `add_library(mds STATIC ${mds_srcs})`. It links privately against `legacy-option-headers`, `Boost::url`, profiler libraries, `osdc`, and `${LUA_LIBRARIES}`. It adds the Lua include directory privately with `target_include_directories(mds PRIVATE "${LUA_INCLUDE_DIR}")`.

## Control Flow And Integration
There is no runtime control flow in this file, but it is the compilation integration point for the MDS implementation. Adding `Capability.cc` and `CInode.cc` here ensures their object code is part of the static library consumed by the Ceph MDS daemon. The local list makes source membership explicit rather than using globbing, so adding a new `.cc` file in `src/mds` requires updating this list.

## State And Persistence Behavior
The file does not define persistent state directly. Its choices affect which persistence implementations are compiled into the MDS library: inode store/backtrace persistence from `CInode.cc`, directory OMAP persistence from `CDir.cc`, journal behavior from `MDLog.cc` and `journal.cc`, and table persistence through `InoTable.cc`, `MDSTable*`, and snap table sources.

## Dependencies And Risks
The target depends on external imported targets and variables being configured by parent CMake files. Missing Lua variables, profiler targets, Boost URL, or `osdc` linkage will break MDS builds. Because the file uses private linkage/includes, consumers of `mds` should not rely on Lua headers or these private libraries leaking transitively. The explicit source list is easy to audit but has omission risk when new implementation files are added.

## Test Signals
Primary signals are configure-time success, `mds` target compilation, full MDS unit/integration test builds, and link success for binaries that consume the static library. Build-system tests should catch missing source entries by unresolved symbols or missing behavior in MDS test targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/CMakeLists.txt -->

## sources/distributed-fs/ceph/src/mds/Capability.cc
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Capability.cc -->
# sources/distributed-fs/ceph/src/mds/Capability.cc

## Purpose
`Capability.cc` implements serialization, diagnostics, test instances, and key state transitions for `Capability`, the per-client capability record attached to a `CInode`. Capabilities track what a client wants, what the MDS has issued, what is pending after revocation, migration sequence numbers, feature compatibility flags, and revocation history.

## Important APIs And Types
Nested wire/state structs implemented here are `Capability::Export`, `Capability::Import`, and `Capability::revoke_info`. `Export` carries cap id, wanted, issued, pending, client snap follow point, issue sequence, migrate sequence, last issue stamp, and state flags. `Import` carries the cap id and issue/migration sequence needed to reattach caps after migration. `revoke_info` records caps held before a revoke, the sequence, and the last issue value.

The `Capability` constructor initializes session list membership, cap generation, stale-session handling, and client feature flags. It sets state bits when the connection lacks inline data, file layout v2 pool namespace, or quota features. `get_client`, `is_stale`, `is_valid`, `revalidate`, `mark_notable`, `maybe_clear_notable`, `set_wanted`, `encode`, `decode`, `dump`, and `generate_test_instances` provide the main behavior in this file.

## Control Flow And State Behavior
`confirm_receipt` is the key update routine. When a client acknowledges the latest sequence, it clears revokes, replaces issued caps with the client-reported caps, and intersects pending caps so the method never adds bits. If revocation is still incomplete, it records a new revoke entry and ensures the cap is notable. For older acknowledgements, it discards obsolete revoke records, updates the matching revoke's `before` field, recalculates issued caps, or reconstructs issued as `caps | pending` if no revoke entry remains. When revocation finishes, it removes the inode/session revoking list entries and may clear notable state. The return value is the set of bits actually revoked.

`set_wanted` keeps inode-level `num_caps_notable` accounting consistent when wanted caps enter or leave notable ranges. It marks the capability notable or attempts to clear it based on issued/pending/client-writeable state. Encode/decode preserve last sent sequence, last issue stamp, wanted bits, pending bits, and revoke list; decode calls `set_wanted` so inode accounting is updated and then recalculates issued caps from revoke state.

## Dependencies And Integration Points
This file depends on `Capability.h`, `CInode.h`, `SessionMap.h`, `Mutation.h`, `BatchOp.h`, Ceph buffer encoding, `Formatter`, debug logging, and capability string helpers. It is integrated with `CInode` cap maps, `Session` cap LRU/list operations, inode notable counters, open-file-table tracking through `CInode::adjust_num_caps_notable`, and migration code that exports/imports cap state.

## Persistence And Compatibility
The encode paths use Ceph versioned encoding macros. `Capability::Export` is encoded at version 3 with legacy compatibility down to version 2; the `state` field is decoded only for struct version 3 and newer. `revoke_info` and `Capability` use legacy-compatible version 2 blocks. The `generate_test_instances` methods are dencoder signals for compatibility and regression coverage.

## Risks
The main risk is incorrect revocation accounting. If `_issued`, `_pending`, `_revokes`, and notable list membership diverge, clients may retain write caps too long or the MDS may wait forever for revokes already completed. `set_wanted` relies on a valid inode pointer for notable accounting; detached or imported capabilities must be careful about when this is called. Feature flags are captured from the session connection at construction, so reconnect and import paths must preserve or refresh compatibility expectations.

## Test Signals
Important tests include dencoder round trips for `Export`, `Import`, `revoke_info`, and `Capability`; cap revoke acknowledgement cases for current and stale sequences; wanted cap transitions that increment and decrement inode notable counts; stale session construction; feature-gated state bits for old clients; and migration export/import preserving sequence and pending state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Capability.cc -->
