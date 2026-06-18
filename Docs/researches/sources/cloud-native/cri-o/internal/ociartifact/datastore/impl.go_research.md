# sources/cloud-native/cri-o/internal/ociartifact/datastore/impl.go

## Purpose
Defines an abstraction layer over image-reference, OCI layout, blob, and short-name operations for the OCI artifact data store.

## Important APIs and Behavior
`Impl` exposes parsing, docker/layout reference construction, image source creation/closing, manifest layer enumeration, blob retrieval, reader draining, and candidate resolution. `defaultImpl` delegates to containers/image docker/reference/layout APIs and manifest helpers. `CandidatesForPotentiallyShortImageName` rejects short names and requires fully qualified artifact names, returning a tag-normalized candidate.

## Integration, Risks, and Tests
`datastore.Store` uses this interface for test injection and all external I/O. Rejecting short names is a security/clarity choice for artifacts. `store_test.go` mocks this interface for pull reference error paths.
