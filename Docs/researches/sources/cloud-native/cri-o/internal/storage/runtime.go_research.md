# sources/cloud-native/cri-o/internal/storage/runtime.go

Purpose: implements CRI-O's storage-backed runtime service for creating, starting, stopping, deleting, and inspecting pod sandbox/container filesystem records in containers/storage.

Important APIs/types/functions: defines error sentinels for invalid pod/container IDs and names; `ContainerInfo`; `RuntimeServer`; `RuntimeContainerMetadata`; `SetMountLabel`; internal `runtimeContainerMetadataTemplate`; `createContainerOrPodSandbox`; public methods `CreatePodSandbox`, `CreateContainer`, `DeleteContainer`, `SetContainerMetadata`, `GetContainerMetadata`, `StartContainer`, `StopContainer`, `GetWorkDir`, `GetRunDir`, and `GetRuntimeService`.

Control flow: creation validates pod/container names, resolves the image config through containers/image storage transport, builds JSON metadata, calls `CreateContainer`, then adds a layer name and resolves persistent/run directories. A defer deletes partially created containers if later steps fail. `CreatePodSandbox` first resolves the pause image locally and pulls it with optional auth if missing. Start loads metadata and mounts with the stored mount label. Stop unmounts, treating missing containers/layers as already gone in selected paths. Delete removes the storage container and best-effort deletes mapped parent layers.

State and persistence: writes `RuntimeContainerMetadata` JSON into containers/storage container metadata, stores container names and layer names, mutates ID mapping options with mappings assigned by storage, and returns work/run directory paths. `CreatedAt`, `Pod`, `Privileged`, image identity, labels, namespace, UID, and attempt become durable metadata.

Dependencies/integration: depends on containers/image storage transport/types, containers/storage, OCI image-spec `v1.Image`, CRI-O internal logging, `ImageServer`, `StorageTransport`, `StorageImageID`, and `RegistryImageReference`. Upper layers use the `RuntimeServer` interface to manage CRI pod sandboxes and workload containers.

Risks: metadata JSON is a compatibility surface; field/tag changes affect stored containers. Creation cleanup is best effort and may leave partial artifacts if deletion fails. `CreatePodSandbox` uses `context.Background()` for pulls instead of the service context. Error normalization is inconsistent by method: some unknown containers are nil, some become `ErrInvalidContainerID`. `SetContainerMetadata` marshals `&metadata`, a pointer to pointer, which currently works through JSON dereferencing but is easy to misread.

Test signals: `runtime_test.go` covers directory lookup, start/stop/delete errors, metadata read/write, create success/failure cleanup, and pause image pulling with default or provided auth file.
