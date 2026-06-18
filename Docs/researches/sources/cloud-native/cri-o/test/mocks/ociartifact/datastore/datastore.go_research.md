# sources/cloud-native/cri-o/test/mocks/ociartifact/datastore/datastore.go

## Purpose
Generated GoMock for OCI artifact datastore implementation.

## Important APIs, Types, And Functions
`MockImpl` covers image-name candidate resolution, image source creation/closing, docker/layout reference creation, blob reads, manifest layer info, normalized name parsing, and `io.ReadAll`.

## Control Flow
All datastore operations delegate to GoMock expectations.

## State And Persistence
No actual artifact or blob persistence.

## Dependencies And Integration Points
Supports tests for CRI-O OCI artifact fetching, especially seccomp/profile artifact paths. Imports containers/image references, manifests, image sources, and GoMock.

## Risks And Test Signals
Does not validate registry, layout, blob cache, or manifest behavior. It only verifies caller interactions and returned data handling.
