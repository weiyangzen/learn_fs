# sources/cloud-native/moby/daemon/volume/service/store.go

## Purpose
Core metadata-backed volume store handling driver lookup, creation, removal, listing, reference counting, filtering, restore, and cache consistency.

## Important APIs, Types, And Functions
`VolumeStore` owns per-name locks, global maps (`names`, `refs`, `labels`, `options`), driver store, Bolt DB, and event logger. `volumeWrapper` adds labels/options/scope/cached path/live restore. Important methods include `NewStore`, `Find`, `list`, `Create`, `checkConflict`, `create`, `Get`, `getVolume`, `Remove`, `Release`, `CountReferences`, `purge`, and `Shutdown`.

## Control Flow
`NewStore` initializes maps, opens metadata DB if root is set, creates the bucket, and restores metadata. `Find` interprets `By` filters, lists drivers in parallel, merges cached volumes from failed drivers, and removes cross-driver name conflicts. `Create` normalizes/locks the name, validates with the platform parser, checks cached conflict/staleness, probes existing volumes when driver unspecified, acquires driver ref, creates through the driver if needed, records labels/options/empty refs, and persists metadata. `Get` uses metadata/driver hints/cache/all-driver probing, updates missing driver metadata, and attaches optional references. `Remove` rejects referenced volumes, resolves the latest volume, removes via driver, purges metadata/cache on success or forced purge, and emits destroy events. `Release` removes refs under locks.

## State And Persistence
Persistent state is Bolt metadata; driver backends own actual volumes. In-memory state caches names, refs, labels, options, and plugin refs. `purge` deletes metadata and releases driver refs.

## Dependencies And Integration Points
Used by `VolumesService` and `MountPoint` consumers. Integrates driver store/plugin refs, mount parser volume-name validation, bbolt metadata, event logging, and error wrappers.

## Risks
Lock ordering between per-name locks and globalLock is critical. Plugin driver refcounts must balance create/remove/purge/error paths. Metadata can become stale relative to external plugins, so conflict checks and purge behavior are delicate. `Shutdown` assumes `db` is non-nil.

## Test Signals
Store tests cover create/remove/list/restore, driver filters, references, stale refs, plugin dereference on error, get with reference, and filter function behavior.
