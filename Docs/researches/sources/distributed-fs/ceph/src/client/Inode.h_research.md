# sources/distributed-fs/ceph/src/client/Inode.h

## Purpose
`Inode.h` declares the central client metadata-cache inode, its capability records, cap-snapshot records, flags, directory/object-cache state, fscrypt fields, delegation list, and helper APIs.

## Important APIs, Types, and Functions
`Cap` represents an MDS-issued cap for one inode/session. `CapSnap` snapshots dirty inode state for snapshot flushing. `Inode` stores identity (`ino`, `snapid`, fake ino), stat metadata, layout, size/truncate/time fields, recursive stats, xattrs, inline data, fscrypt metadata/context, directory cache (`Dir*`, frag trees/maps), caps/auth cap, dirty/flushing lists, snap realm, cap refs, object cache set, parent dentries, symlink, waiters, delegations, unsafe ops, active Fhs, and dir pin. Helpers cover path construction, refs, open refs, cap accounting, valid size, directory opening, async errors, dumping, charmap metadata, delegation, dirty caps, fscrypt inheritance, and effective size.

## Control Flow
MDS reply trace insertion populates/updates `Inode`. Dentries and file handles hold refs. Cap grants/revokes update `caps`, `auth_cap`, and wanted/dirty state. File IO checks caps and object cache state through this inode. Snapshot handling links it to a `SnapRealm` and may create `CapSnap` entries. Directory operations allocate `Dir` lazily and use frag maps for MDS targeting.

## State and Persistence Behavior
The inode mirrors persisted MDS metadata and OSD file layout, but the object itself is a transient cache record. Dirty caps, flushing tids, inline data, xattrs, fscrypt fields, and cap snaps represent local modifications pending MDS acknowledgement. `ObjectCacher::ObjectSet` ties file data cache/writeback to this inode.

## Dependencies and Integration Points
It depends on Ceph/MDS types, `ObjectCacher`, `MetaSession`, `UserPerm`, `Delegation`, `FSCrypt`, `InodeRef`, and request messages. `Client` is a friend-like owner through direct access and orchestrates most state transitions.

## Risks and Edge Cases
This is a dense ownership hub: raw pointers, intrusive refs, xlist items, object cache membership, and session cap lists must all be unwound in the right order. Directory hardlink assumptions are asserted. Cap ref and open mode maps default-insert entries in several helpers. Fscrypt is included unconditionally by this header but protected in parts by Linux guards, so platform compile coverage matters.

## Test Signals
Trace insertion/update, cap grant/revoke/import/export, dirty cap and cap snap flushing, inode ref/drop trimming, directory cache open/close, object cache cleanup, delegation lifecycle, file lock state, quota/charmap metadata, fscrypt metadata, and fake inode mapping.
