<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/containers.go -->
# sources/cloud-native/containers-storage/containers.go

- Purpose: Implements the JSON-backed container metadata store for containers/storage.
- Important APIs/types: `Container`, `rwContainerStore`, `containerStore`, `copyContainer`, label/mount option accessors, lock methods, `newContainerStore`, lookup/name/metadata/big-data methods, create/delete/wipe, and garbage collection.
- Control flow: Store construction creates directories and lock file, loads stable and volatile JSON files, builds ID/layer/name/trunc indexes, resolves duplicate names by saving when holding a write lock, and serves reads/writes under a process RW lock plus cross-process lockfile.
- State and persistence: Stable containers live in `containers.json`; volatile containers live in `volatile-containers.json` in `runDir` when transient mode is enabled. Big data is stored as files under per-container data directories, with sizes and digests tracked in metadata. Saves use atomic file writes and lockfile write records.
- Dependencies and integration: Uses ID mapping validation, string ID generation, truncindex lookup, lockfile last-write detection, logrus, digest calculation, and store helper functions shared with images/layers.
- Risks: Concurrent readers must reload carefully when on-disk state changes; duplicate name cleanup requires write lock; volatile data is less durable by design; big-data keys map to filenames and must be validated.
- Test signals: Unit/integration tests for create/get/lookup/delete, transient store behavior, big-data size/digest backfill, lock/reload behavior, and GC of orphan datadirs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/containers.go -->
