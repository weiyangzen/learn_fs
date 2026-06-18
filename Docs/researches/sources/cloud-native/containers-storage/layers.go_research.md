# sources/cloud-native/containers-storage/layers.go

## Purpose
`layers.go` implements the containers/storage layer store: in-memory indexing, persistent metadata, graph-driver integration, mount tracking, diff/apply operations, big data, deletion, garbage collection, and digest lookup for container image layers.

## Important Types and APIs
`Layer` is the persistent layer record with ID, names, parent, metadata, SELinux mount label, created time, compressed/uncompressed/TOC digests and sizes, compression type, UID/GID sets, flags, ID maps, read-only status, location, and big-data names. `layerLocations` splits metadata among stable `layers.json`, image-store `layers.json`, and `volatile-layers.json`. `roLayerStore` and `rwLayerStore` define the read/write store interfaces used by the broader storage package. `layerStore` owns locks, JSON paths, layer indexes, digest maps, mount indexes, and the graph `drivers.Driver`.

## Locking and Control Flow
The store uses a process-level `sync.RWMutex` nested under file locks from `pkg/lockfile`. `startWriting` takes the layer lock and in-process write lock, then reloads if needed. `startReading` takes read locks, checks whether on-disk layer or mount state changed, and can temporarily upgrade through a serialized reload path. `multipleLockFile` allows the primary layer directory and optional image store to be locked together.

`load` reads each configured JSON file, assigns layer locations, rebuilds indexes, reserves SELinux labels, loads mountpoints, recovers stale tempdirs, resolves duplicate names by removing conflicting names, and cleans incomplete layers when the store is writable. `saveLayers` records the lockfile write before atomically writing the selected JSON files; volatile layer metadata is written with `NoSync`. `saveMounts` separately records and writes `mountpoints.json`.

## Layer Creation and Persistence
`newLayerStore` creates directories, obtains lockfiles, configures JSON paths, loads metadata, and returns a writable store. `newROLayerStore` uses a read-only lockfile and only stable/volatile metadata under the layer directory. `create` validates ID/name uniqueness, handles template-layer metadata copying, reserves SELinux labels, writes an incomplete layer record before creating driver data, stores big data, creates or clones graph-driver layers, applies a diff or staged directory if supplied, updates digest maps, clears the incomplete flag, and saves final metadata. This incomplete-flag protocol is the crash-recovery anchor.

## Mounts, Deletion, and Cleanup
`Mount`, `unmount`, `Mounted`, and `ParentOwners` maintain mount counts and paths in `mountpoints.json` under `mountsLockfile`. Source comments explicitly identify locking bugs where `Diff` can reach `Mount`/`unmount` while the layer store is only read-locked for btrfs/zfs fallback getters. `internalDelete` marks the layer incomplete, creates a `tempdir.TempDir`, asks the driver for deferred removal, stages tar-split and big-data paths into the tempdir, removes indexes, and returns cleanup functions. `deferredDelete` unmounts first, calls `internalDelete`, saves metadata, and expects callers to run cleanup outside locks. `Wipe` deletes known layers newest-first and then removes driver leftovers.

## Diff, Apply, and Digest Behavior
`Changes` delegates to `driver.Changes` after resolving parent/layer IDs and ID mappings. `Diff` normally delegates to driver diff unless reconstructing a tar stream from tar-split metadata, or returning an additional-layer blob. It can recompress according to requested or recorded compression. `applyDiffWithOptions` peeks compression, computes compressed and uncompressed digests/sizes, captures tar-split metadata, logs UID/GID sets, applies the diff through the driver, writes tar-split data, updates layer fields and digest maps, and saves. Staged-differ paths use `DriverWithDiffer` outputs and can update TOC digest, metadata, flags, tar-split, and big data.

## Dependencies and Integration Points
The file integrates with graph drivers, `archive`, `idtools`, `lockfile`, `mount`, `selinux`, `tar-split`, `pgzip`, `digest`, `tempdir`, `ioutils`, and package-level helpers for names and errors. It is one of the central persistence layers for containers/storage and is consumed through the store APIs elsewhere in the package.

## Risks and Edge Cases
Major risks include the documented read-lock mutation path in `Diff`, metadata consistency across multiple JSON locations, incomplete-layer recovery failures, cleanup functions that must be run even on error, and stale mount information becoming obsolete immediately after load. Volatile metadata trades durability for speed. Digest maps must stay synchronized on update/delete; this file updates compressed and uncompressed maps in several paths but `deleteInDigestMap` only removes compressed and uncompressed entries, leaving TOC-map cleanup as a detail to watch.

## Test Signals
The included `layers_test.go` only validates `layerLocations` bit/index conversion. Most behavior in this file must be covered by broader store and driver tests outside this subset. The code itself contains detailed invariants and comments that serve as strong design signals, especially around lock ordering, incomplete flags, and cleanup obligations.
