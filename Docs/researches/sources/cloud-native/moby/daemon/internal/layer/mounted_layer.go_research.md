## sources/cloud-native/moby/daemon/internal/layer/mounted_layer.go

Purpose: Implements `RWLayer` references for mutable container layers.

Important APIs/types: `mountedLayer` stores name, graphdriver mount ID, optional init ID, parent `roLayer`, store pointer, and active RW references. Methods implement `cacheParent`, `TarStream`, `Name`, `Parent`, `Size`, `Changes`, `Metadata`, `getReference`, `hasReferences`, `deleteReference`, `retakeReference`. `referencedRWLayer` embeds `mountedLayer` and implements `Mount`, `Unmount`, and `ApplyDiff`.

Control flow: RW operations delegate to the graphdriver using `mountID` and `cacheParent`, where `cacheParent` prefers init layer over parent layer. `getReference` creates a wrapper and records it under a mutex. `deleteReference` ensures release is balanced and returns `ErrLayerNotRetained` for unknown references. `retakeReference` restores a reference after failed deletion. `Metadata` ensures an `ID` key defaults to the user-visible mount name.

State and persistence: Reference map is in-memory. Durable mount metadata is handled by `layer_store.go`/`filestore.go`; graphdriver stores filesystem data.

Dependencies and integration: Used by layer store RW lifecycle and container mount operations. Depends on graphdriver Diff/Get/Put/ApplyDiff/Changes/DiffSize.

Risks: Mount/unmount balance is caller-managed. `referencedRWLayer` references share the same underlying mutable layer, so concurrent filesystem modifications are graphdriver/caller responsibility. Error recovery in release depends on `retakeReference`.

Test signals: `mount_test.go` and `layer_test.go` cover mount content, size, changes, apply diff, restore, repeated mount/unmount, and release.
