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
