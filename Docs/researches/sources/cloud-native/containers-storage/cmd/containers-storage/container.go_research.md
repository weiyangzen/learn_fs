<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/container.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/container.go

- Purpose: Implements per-container inspection and big-data operations.
- Important functions: `container`, `listContainerBigData`, `getContainerBigData`, `getContainerBigDataSize`, `getContainerBigDataDigest`, `setContainerBigData`, `getContainerDir`, `getContainerRunDir`, and `containerParentOwners`.
- Control flow: Resolve container by ID/name, call storage APIs for metadata, big data, directory paths, or parent ownership chain, and write human or raw output.
- State and persistence: `setContainerBigData` writes big-data files and updates container JSON metadata through the store; read commands are non-mutating.
- Dependencies and integration: Relies on `storage.Store` container APIs and command flags for data file path/output selection.
- Risks: Raw big-data output can be binary; setting data from files mutates persistent store state.
- Test signals: CLI tests over create-container, data set/get, and path commands.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/container.go -->
