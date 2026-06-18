# sources/cloud-native/cri-o/internal/ociartifact/impl.go

## Purpose
Abstracts manifest retrieval and platform-specific manifest-list resolution for the OCI artifact store.

## APIs and Behavior
`Impl` defines `ChooseInstance` for selecting a manifest digest from a multi-image list and `GetManifestFromRef` for fetching manifest bytes and MIME type, optionally for a selected instance digest. `defaultImpl` delegates to containers/image `manifest.List.ChooseInstance` and `ImageReference.NewImageSource().GetManifest`.

## Integration, Risks, and Tests
Used by `Store.EnsureNotContainerImage` to distinguish OCI artifacts from ordinary images before pulling. The abstraction makes manifest classification testable. Risks are mostly external-reference I/O errors and platform selection mismatches. Direct tests are outside this subset.
