# sources/cloud-native/cri-o/internal/ociartifact/libartifact_store.go

## Purpose
Defines a small interface around `libartifact.ArtifactStore` so CRI-O artifact store logic can be tested and can access the underlying system context.

## APIs and Integration
`LibartifactStore` includes `Remove`, `List`, `Pull`, `Inspect`, and `SystemContext`. `artifactStore` embeds `*libartifact.ArtifactStore` and exposes its `SystemContext` field via a method. `Store.NewStore` wraps the main and additional stores with this interface.

## Risks and Tests
The interface is straightforward but central to testability and additional-store behavior. Any libartifact API change must be mirrored here. No direct tests in this subset.
