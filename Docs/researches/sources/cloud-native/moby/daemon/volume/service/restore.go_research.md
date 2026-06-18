# sources/cloud-native/moby/daemon/volume/service/restore.go

## Purpose
Restores volume store in-memory state and plugin driver references from persisted metadata at daemon startup.

## Important APIs, Types, And Functions
`(s *VolumeStore) restore()` reads all `volumeMetadata` and repopulates names, labels, options, refs, and driver refcounts.

## Control Flow
The method reads metadata in a Bolt view, then launches one goroutine per metadata entry. Entries with a known driver call `lookupVolume`; missing volumes are queued for metadata removal, communication errors are logged. Entries without driver probe via `getVolume` and update metadata with the discovered driver. Existing volumes increment driver refcount through `CreateDriver` and are cached under global lock with empty refs. After workers complete, stale metadata is removed in one update transaction.

## State And Persistence
Reads and may update/remove entries in `metadata.db`. Rebuilds in-memory caches and plugin references, but does not restore per-container refs.

## Dependencies And Integration Points
Called by `NewStore`. Depends on Bolt metadata helpers, driver store, lookupVolume, and logging.

## Risks
Concurrent goroutines call store methods and metadata updates; lock ordering must avoid deadlocks. Errors from `CreateDriver` are ignored. Restored refs are empty by design, so live restore must reattach runtime references separately.

## Test Signals
`restore_test.go` verifies labels/options survive shutdown and new store initialization.
