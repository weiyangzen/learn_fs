<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/images.go -->
# sources/cloud-native/containers-storage/images.go

## Purpose
`images.go` implements the persistent image metadata store: image records, names, name history, top layers, mapped top layers, metadata, big-data blobs, digest indexes, locking, reload, save, garbage collection, and read-only/read-write views.

## Important APIs, Types, And Functions
`Image` is the stored record. `roImageStore` and `rwImageStore` define internal store capabilities. `imageStore` owns the lockfile, directory, in-process lock, `images` slice, truncation index, and lookup maps. Key functions include `newImageStore`, `newROImageStore`, `startReading`, `startWriting`, `reloadIfChanged`, `load`, `Save`, `create`, `updateNames`, `Delete`, `Get`, `Images`, `ByDigest`, `SetBigData`, `BigData*`, flag setters, mapped-layer setters, `GarbageCollect`, and `Wipe`.

## Control Flow
Callers acquire read or write locks before using store methods. Reads first use the on-disk lockfile `LastWrite` state to decide whether to reload. If a read reload detects duplicate image names that a writable save could repair, it upgrades through a write lock path and retries. `load` reads `images.json`, rebuilds indexes, recomputes digests from explicit image digest and manifest-like big data names, removes duplicate names from older records when writable, and saves repaired state. `create` validates ID/name uniqueness, appends a record, saves metadata, then writes requested big-data items. `updateNames` applies set/add/remove operations, transfers names away from conflicting images, appends name history, and saves. `Delete` updates every index, saves, and removes the image data directory.

## State And Persistence
Persistent state is `images.json`, `images.lock`, and per-image data directories containing big-data files named through the big-data basename helper. In-memory state mirrors the JSON plus indexes by full/truncated ID, name, and digest. The store uses atomic writes for JSON and big data. `GarbageCollect` removes unreferenced ID-looking directories after crashes.

## Dependencies And Integration Points
The file depends on lockfile, ioutils atomic writes, string IDs, string utilities, truncindex, digest validation, and package-level helpers such as `dedupeStrings`, `applyNameOperation`, `makeBigDataBaseName`, and map/slice copy helpers from neighboring files. Higher-level storage operations use these interfaces for image lifecycle and lookup.

## Risks And Edge Cases
Lock ordering is subtle: the filesystem lock must be held before the in-process lock, and reload upgrades must avoid stale `LastWrite` assumptions. Read-only stores cannot repair duplicate names and return `ErrDuplicateImageNames`. Big data writes happen after the image JSON record is saved, so partial creation cleanup must use `Delete`. Digest indexes depend on valid digest strings and manifest key naming. Methods often require the caller to have already locked correctly; misuse can race or panic.

## Test Signals
`images_test.go` covers name history and conflict transfer semantics. Other image store behaviors are likely covered elsewhere; this subset does not directly test reload upgrade, duplicate-name repair, big data persistence, garbage collection, or read-only errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/images.go -->
