# sources/cloud-native/cri-o/internal/ociartifact/store.go

## Purpose
Implements CRI-O's OCI artifact store: pull validation, main and read-only additional store support, listing, status lookup, removal, blob mount path discovery, and artifact pinning.

## Important APIs and Control Flow
`NewStore` creates the main `<root>/artifacts` libartifact store, opens additional read-only artifact stores, stores an injectable manifest `Impl`, and initializes pinned regexps atomically. `Pull` first calls `EnsureNotContainerImage`, skips pulling when the artifact already exists in an additional store, otherwise pulls into the main store. `EnsureNotContainerImage` fetches the root manifest, resolves manifest lists for the current platform, parses the selected manifest, and returns `ErrIsAnImage` when manifest/config media types match standard container images and no OCI `artifactType` is present. `List` reads additional stores first, then main store, wraps artifacts with root/pinning metadata, and deduplicates by reference with additional stores winning. `Status` checks additional stores before main. `Remove` only removes from the main writable store. `BlobMountPaths` opens the artifact's OCI layout, resolves local blob paths for layers, and names mountable blobs from OCI title or ModelPack filepath annotations. `SetPinnedImageRegexps`, `isArtifactPinned`, and `RootPath` round out the API.

## State, Persistence, Dependencies, and Integration
Artifacts persist under `<root>/artifacts`; additional stores are read-only and force-pinned. Uses libartifact/libimage, containers/image manifest/layout/types, OCI image spec, ModelPack annotations, atomic regex pointer reloads, and CRI-O logging. `Artifact.CRIImage` turns these objects into CRI image-like records.

## Risks and Test Signals
Classification depends on MIME type and OCI artifactType interpretation; unusual images/artifacts can be misclassified. Additional store errors are warned and skipped for list/status. Deduplication by `Reference()` may collapse `unknown` references. Pinning regexps match both reference and canonical name. No tests for this file are included in the listed subset, so edge cases are under-covered here.
