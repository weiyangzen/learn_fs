# sources/cloud-native/stargz-snapshotter/fusemanager/fusestore.go

## Purpose
Persists fuse mount information in BoltDB so the fuse manager can restore mount tracking after reinitialization.

## Important APIs, Types, And Functions
`fuseInfo` stores root, mountpoint, labels, and service config. `storeFuseInfo` creates or opens `fuse-info-bucket` and stores JSON by mountpoint. `removeFuseInfo` deletes a mountpoint key. `restoreFuseInfo` scans the bucket and remounts each stored entry through `fm.mount`.

## Control Flow
Mount stores an entry after `fm.mount` succeeds. Unmount deletes the entry after filesystem unmount succeeds. `Init` calls `restoreFuseInfo`, which reads all stored JSON values and remounts through the current filesystem, skipping already-present mountpoints indirectly through `fm.mount`.

## State And Persistence
Durable state is a BoltDB bucket keyed by mountpoint. Values are JSON-serialized `fuseInfo`. Although root and config are stored, restore currently only uses mountpoint and labels.

## Dependencies And Integration
Depends on bbolt, JSON encoding, `service.Config`, and `Server.mount`. It is opened and closed by `NewFuseManager`/`Close` in `service.go`.

## Risks And Test Signals
Risks include stale entries after failed unmount/store errors being ignored by callers, restore using current config rather than stored config, and loss of store on `Server.Close` because the file is removed. Tests in this subset do not directly assert store/restore behavior.
