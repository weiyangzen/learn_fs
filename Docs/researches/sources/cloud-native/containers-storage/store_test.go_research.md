# sources/cloud-native/containers-storage/store_test.go

Purpose: broad smoke and regression tests for the public `Store` façade.

Important APIs/types/functions: `newTestStore`, `TestStore`, `TestWithSplitStore`, `TestStoreMultiList`, and `TestStoreDelete`.

Control flow: `newTestStore` creates temp run/graph roots, defaults to `vfs`, and supplies single-ID uid/gid maps. `TestStore` and `TestWithSplitStore` call most public methods against missing IDs to assert expected errors or empty success paths. `TestStoreMultiList` creates a layer/image/container and verifies selective listing counts. `TestStoreDelete` creates two images/containers and an unused layer, deletes them, and verifies the store returns to the initial state.

State/persistence: uses temporary storage roots and the vfs driver; creates and deletes real storage metadata and layer directories. Calls `Shutdown` and `Free` to release store state.

Dependencies/integration: depends on `pkg/reexec`, `idtools`, OCI digest, and testify. Exercises top-level integration with graph drivers and store metadata implementations.

Risks: many assertions are smoke-level and only check error presence, not specific error types. `reexec.Init()` is called inside some tests rather than `TestMain`, which is adequate for these paths but less comprehensive than unshare tests. Concurrency and additional read-only stores are not deeply covered.

Test signals: useful guard that the public API remains callable, split image stores initialize, `MultiList` is consistent, and delete operations clean up created objects.
