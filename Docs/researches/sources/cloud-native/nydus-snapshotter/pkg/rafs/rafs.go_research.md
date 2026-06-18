# Research: sources/cloud-native/nydus-snapshotter/pkg/rafs/rafs.go

This file defines RAFS instance state and an in-memory cache. `Cache` is a mutex-protected map from snapshot ID to `*Rafs`, with add/remove/get/list/head/locked-list/set methods. `RafsGlobalCache` is initialized at package init. `Rafs` is persisted as the per-snapshot filesystem record, including sequence, image ID, daemon ID, filesystem driver, snapshot ID/dir, underlying cache files, mountpoint, and annotations.

`NewRafs` creates the snapshot directory under `config.GetSnapshotsRootDir`, initializes annotations and underlying files, adds the instance to the global cache, and returns it. Methods expose annotations, snapshot dir, fs driver fallback, fscache workdir, mountpoint, shared fusedev relative mountpoint, and bootstrap path lookup. `BootstrapFile` prefers `fs/image/image.boot` and falls back to legacy `fs/image.boot`.

State is both memory and persistent manager-store data. Integration points include filesystem mount/umount, daemon RAFS caches, fscache annotations, manager recovery, metrics, and bootstrap validation. Risks include global mutable cache, deep-copy list behavior, typo `SetIntances`, pointer sharing after `CloneRafsInstances`, directory creation side effects, and no direct tests in this subset.
