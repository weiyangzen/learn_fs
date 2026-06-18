## sources/cloud-native/moby/daemon/internal/layer/layer_store.go

Purpose: Implements the concrete graphdriver-backed layer store for immutable layers and mutable mounts.

Important APIs/types: `maxLayerDepth`, `layerStore`, `StoreOptions`, `NewStoreFromOptions`, `newStoreFromGraphDriver`, `Driver`, `loadLayer`, `loadMount`, `applyTar`, `Register`, `registerWithDescriptor`, `Get`, `Map`, `Release`, `CreateRWLayer`, `GetRWLayer`, `GetMountID`, `ReleaseRWLayer`, `saveMount`, `initMount`, `getTarStream`, `assembleTarTo`, `Cleanup`, `DriverStatus`, `DriverName`, and the `naiveDiffPathDriver` fallback.

Control flow: Initialization creates graphdriver and layerdb store, lists layer/mount metadata, recursively loads read-only layers, increments parent reference counts, and restores mounts. Registering a layer retains the parent, creates a graphdriver cache ID, starts metadata transaction, applies tar through tar-split metadata capture, computes diff/chain IDs, stores metadata, deduplicates against existing chain IDs, commits transaction, and returns a retained reference. Release removes a reference, decrements reference counts recursively, renames metadata to `-removing`, removes graphdriver data, then deletes metadata. RW layer creation locks by name, retains parent, optionally creates an init layer, creates graphdriver read-write layer, persists mount metadata, and returns a reference. RW release removes graphdriver layers and mount metadata, then releases parent. Tar stream reconstruction reads tar-split metadata and graphdriver diff files, then verifies through `ro_layer.go`.

State and persistence: In-memory maps `layerMap` and `mounts` plus reference maps/counts are protected by locks. Durable state is graphdriver data and layerdb metadata. Cleanup removes orphaned `-removing` layerdb entries and delegates driver cleanup.

Dependencies and integration: Central integration with graphdriver, layer metadata store, tar-split asm/storage, digest identity chain IDs, string IDs, user ID mapping, and daemon logging.

Risks: Reference-count invariants are strict and can panic on impossible states. Deduplication sets a cleanup error to remove the just-created duplicate graphdriver layer while returning the existing reference. Register writes/driver operations span several systems and must clean up on every failure. `Map` exposes underlying `*roLayer` values, not new references, so callers must not release them as retained references.

Test signals: `layer_test.go`, `mount_test.go`, `layer_unix_test.go`, and `migration_test.go` cover registration, restore, release, tar stability, duplicate registration, tar verification, mount behavior, and migration.
