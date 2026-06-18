## sources/cloud-native/moby/daemon/internal/layer/empty_test.go

Purpose: Tests the empty layer singleton.

Important test: `TestEmptyLayer` checks chain ID, diff ID, parent, size, diff size, metadata, tar stream creation, and digest of the produced tar stream.

Control flow and state: Copies the tar stream into a canonical digest hash and compares it to `DigestSHA256EmptyTar`.

Dependencies and integration: Uses `io.Copy` and OpenContainers digest. It exercises the `Layer`-like methods on `EmptyLayer`.

Risks covered: Accidental changes to the empty tar representation or fixed metadata. It does not test `TarStreamFrom` error behavior or `IsEmpty`.

Persistence: None.
