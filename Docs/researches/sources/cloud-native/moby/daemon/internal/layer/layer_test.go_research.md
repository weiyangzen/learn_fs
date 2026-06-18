## sources/cloud-native/moby/daemon/internal/layer/layer_test.go

Purpose: Provides broad integration-style tests for the concrete layer store using the vfs graphdriver.

Important helpers: `newVFSGraphDriver`, `newTestStore`, `createLayer`, `FileApplier`, `testFile`, `initWithFiles`, `getCachedLayer`, metadata assertions, `tarFromFiles`, `assertLayerDiff`, and `assertReferences`.

Important tests: `TestMountAndRegister` verifies creating a layer and mounting a child RW layer. `TestLayerRelease` checks recursive deletion only after all children/references release. `TestStoreRestore` verifies restoring layers and mounts from layerdb, duplicate mount name conflict, repeated mount/unmount, RW release, and final parent cleanup. `TestTarStreamStability` confirms registered layer tar streams remain stable even if graphdriver content is later modified. `TestRegisterExistingLayer` confirms duplicate registration returns references to the same underlying layer. `TestTarStreamVerification` corrupts tar-split metadata and expects verification failure.

Control flow and state: Tests create real temp graphdriver data, write files, register tar streams, manipulate driver state, and inspect internal maps/reference sets.

Dependencies and integration: Exercises graphdriver/vfs, archive packing, tar-split reconstruction, digest verification, and reference counting.

Risks covered: Restore, deduplication, recursive release, tar reproducibility, and metadata corruption. Several tests skip Windows due to known graphdriver differences.

Persistence: Strongly exercises layerdb plus graphdriver temp filesystem state.
