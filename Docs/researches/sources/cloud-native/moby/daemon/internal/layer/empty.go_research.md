## sources/cloud-native/moby/daemon/internal/layer/empty.go

Purpose: Defines the canonical empty layer implementation and digest.

Important APIs/types: `DigestSHA256EmptyTar` is the sha256 digest of a 1024-byte empty tar stream. `EmptyLayer` is a singleton `*emptyLayer`. `IsEmpty(diffID)` checks for the empty layer digest.

Control flow: `TarStream` creates an in-memory tar writer, closes it to emit an empty tar, and returns a read closer. `TarStreamFrom` only supports an empty parent ID. Metadata, parent, size, diff size, chain ID, and diff ID methods return fixed empty-layer values.

State and persistence: No mutable persistence. The digest value is part of image/layer compatibility semantics and is used to avoid adding empty history layers to RootFS.

Dependencies and integration: Used by image child creation and layer APIs as a no-content layer.

Risks: The digest must remain aligned with the tar writer output. `TarStreamFrom` returns a generic error for non-empty parent.

Test signals: `empty_test.go` verifies IDs, nil parent, zero sizes, empty metadata, and tar digest.
