# sources/cloud-native/cri-o/test/mocks/containers/image/v5/types.go

## Purpose
Generated GoMock for `go.podman.io/image/v5/types.ImageCloser`.

## Important APIs, Types, And Functions
`MockImageCloser` covers lifecycle, config/manifest/blob metadata, layer info, inspect, signatures, size, encryption support, references, and updated-image helpers.

## Control Flow
Each method delegates to GoMock and extracts typed return values.

## State And Persistence
No image persistence; state is held in expectations.

## Dependencies And Integration Points
Supports CRI-O image-related unit tests without opening real image sources. Imports OCI image spec, Docker reference, and containers/image types.

## Risks And Test Signals
Validates interactions with image objects but not actual manifest parsing, blob reads, or close semantics. Must be regenerated on upstream interface changes.
