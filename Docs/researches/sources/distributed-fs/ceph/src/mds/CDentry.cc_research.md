# sources/distributed-fs/ceph/src/mds/CDentry.cc

## Purpose
This file implements `CDentry`, the MDS cache object for a directory entry. A dentry links a name and snap interval in a `CDir` to either a primary inode, a remote inode reference, or a null/negative entry. It manages projected linkage during metadata mutations, dirty tracking, authority pins, client leases, export/import state, lock-state encoding, remote-link encoding, path formatting, dump output, and corruption checks.

## Important APIs, Types, and Functions
Constructors create null or remote dentries with hash, snap range, alternate name, locks, and dirty-list items. `operator<<`, `print()`, and `dump()` expose debug and admin state. `authority()` delegates to the containing `CDir`. `pre_dirty()`, `_mark_dirty()`, `mark_dirty()`, `mark_clean()`, and `mark_new()` synchronize dentry versions and dirty membership with the parent dir and log segment.

Linkage APIs include `link_remote()`, `unlink_remote()`, `push_projected_linkage()`, `push_projected_linkage(CInode*)`, and `pop_projected_linkage()`. Projected primary linkage preserves dirty rstat state while pushing/popping projected inode parent state. `add_client_lease()`, `remove_client_lease()`, and `remove_client_leases()` manage intrusive client lease records and SimpleLock lease counters. `encode_remote()` and `decode_remote()` serialize remote dentries, including v2 alternate names. `scrub()` and `check_corruption()` detect invalid snap ranges and optionally mark damage or abort to avoid committing newly corrupt metadata.

## Control Flow
Dirtying a dentry starts by asking the parent dir for a projected version, then `mark_dirty()` records the committed dentry version, marks the dentry dirty, inserts it into both the dir dirty list and log segment dirty list, and marks the dir dirty. Cleaning removes the dirty state, list items, and dirty pin. Projected linkage follows a two-phase mutation flow: push a future linkage before the mutation is committed, use projected readers when locks allow it, then pop to apply the change by calling `CDir::link_remote_inode()` or `CDir::link_primary_inode()`.

Authority pins are delegated upward. `auth_pin()` pins the dentry and increments nested auth pins on the containing `CDir`; `auth_unpin()` reverses that and may unblock freezes. Waiters for unfreeze or single-auth are redirected to the dir, while other waiters stay on the dentry.

Client lease removal erases the lease from both per-session and global lists, updates the dentry lock's client lease count, drops the lease pin when the last lease goes away, and asks `Locker` to re-evaluate gathers if the lock became gatherable.

## State and Persistence Behavior
Durable dentry state includes name, snap range, first/version fields, linkage type, remote inode/type, primary inode store through the parent dir commit path, and alternate name. Runtime state includes lock objects, version lock, projected linkage list, dirty-list membership, LRU position, auth pins, client leases, batch ops, reintegration id, and corruption-loaded marker. Export/import encoding captures snap first, state, versions, locks, and replicas; import restores auth, dirty pins, replica pins, and nonce behavior.

## Dependencies and Integration Points
`CDentry` is tightly integrated with `CDir`, `CInode`, `MDCache`, `Locker`, `LogSegment`, `SnapClient`, `SnapRealm`, MDS locks, client sessions, memory pools, and MDS damage reporting. It is manipulated by dir fetch/commit, rename/link/unlink, scatterlock, cache trimming, exports/imports, and scrub.

## Risks and Test Signals
High-risk areas are projected linkage ordering, dirty version invariants, auth pin balance, remote parent registration, client lease cleanup, snap range corruption, and export/import state masks. Tests should cover primary/remote/null transitions, projected pop after rename/link/unlink, dirty and clean list membership, lease add/remove with lock gather, corrupt `first > last` handling, remote encode/decode v1/v2, and scrub detection of invalid snap intervals.
