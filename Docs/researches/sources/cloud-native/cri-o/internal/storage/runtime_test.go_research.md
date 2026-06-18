# sources/cloud-native/cri-o/internal/storage/runtime_test.go

Purpose: mock-based behavioral tests for `RuntimeServer` methods in `internal/storage/runtime.go`.

Important APIs/types/functions: constructs mocks for containers/storage `Store`, CRI-O `ImageServer`, and `StorageTransport`; tests `GetRunDir`, `GetWorkDir`, `StopContainer`, `StartContainer`, `GetContainerMetadata`, `SetContainerMetadata`, `DeleteContainer`, `CreateContainer`, and `CreatePodSandbox`.

Control flow: each spec establishes expected store/transport call order with gomock and `mockutils.InOrder`, invokes the service, and asserts error/value outcomes. Helper sequences model local-image resolution and pause-image resolution/pull paths.

State and persistence: no real storage is used. Tests assert metadata-dependent behavior through mock JSON strings, `Container` structs, directory return values, and ID mapping/image IDs.

Dependencies/integration: uses Ginkgo/Gomega, gomock, generated mocks under `test/mocks`, CRI-O storage reference and image ID types, containers/storage types, and a shared `testManifest` from suite setup.

Risks: strict ordered mocks can make harmless implementation refactors noisy. The suite has broad error coverage but does not inspect the exact metadata JSON written by creation, mapped-layer cleanup, or all unknown-container idempotency branches.

Test signals: verifies invalid pod/container inputs, cleanup after late creation failures, pause-image pull copy options including `AuthFilePath`, and translation of unknown storage errors to CRI-O sentinel errors in selected methods.
