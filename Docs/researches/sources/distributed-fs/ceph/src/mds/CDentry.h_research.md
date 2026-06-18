# sources/distributed-fs/ceph/src/mds/CDentry.h

## Purpose
This header defines the `CDentry` cache object and `ClientLease` records used by CephFS MDS directory cache. It describes dentry state flags, pin types, linkage representation, versioning, authority operations, exporting/importing, locking, leases, and serialization helpers.

## Important APIs, Types, and Functions
`ClientLease` is an intrusive set/list node keyed by client id and linked into both session and global lease lists. `CDentry::linkage_t` distinguishes primary, remote, and null entries and stores a primary `CInode *` or remote inode/type. `CDentry` inherits from `MDSCacheObject`, `LRUObject`, and `Counter<CDentry>`.

State flags include new, fragmenting, purging, bad remote ino, stray evaluation, purge pinned, bottom LRU, and stray notify-ref. Pin constants include inode pin, fragmenting, purging, and scrub parent. Public APIs cover waiter routing, key construction, corruption checks, name/alternate name accessors, projected linkage, refcount LRU hooks, auth pins, remote links, path construction, version dirtying/cleaning, export/import, lock-state encode/decode, client leases, dump/print, and remote dentry serialization.

## Control Flow
The header exposes the dentry mutation model: direct linkage is durable/current, `projected` holds pending mutation state, and `use_projected()` selects the projected view for clients allowed by the lock or mutation. Export/import methods inline the state-mask and pin transitions used during migration. `first_get()` and `last_put()` bind object references to LRU pinning.

## State and Persistence Behavior
Persistent fields are the name, alternate name, hash, snap interval, linkage, and versions as committed through `CDir`. Lock state and replica state can be encoded for MDS replication/migration. Runtime-only fields include `dir`, projected list, LRU state, lease maps, dirty items, batch ops, auth pins inherited from `MDSCacheObject`, and reintegration request id.

## Dependencies and Integration Points
It depends on MDS cache base classes, lock classes, log segment refs, Ceph buffer types, intrusive containers, CDir/CInode forward declarations, and session/locker types. It is one of the central types shared by MDS cache, request handling, locker, migrator, stray manager, and scrub code.

## Risks and Test Signals
The API is easy to misuse if callers read `linkage` directly instead of projected linkage during locked mutations. State and pin constants must stay aligned with import/export masks and debug dump code. Tests should validate projected/current view selection, LRU pin hooks, encode/decode of export and lock state, and lease map uniqueness by client.
