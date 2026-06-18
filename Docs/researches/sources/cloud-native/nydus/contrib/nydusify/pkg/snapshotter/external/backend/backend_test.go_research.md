# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/backend_test.go

Purpose: validates external backend metadata struct sizes and chunk offset splitting.

Important APIs under test: `Header`, `ChunkMeta`, `ObjectMeta`, and `SplitObjectOffsets`.

Control flow and state: `TestLayout` asserts the unsafe sizes of header and metadata structs match the on-disk layout assumptions. `TestSplitObjectOffsets` covers non-positive chunk size, zero total size, divisible totals, and final partial chunk offsets.

Dependencies and integration points: `unsafe.Sizeof`, reflect comparison, and testify require.

Risks and test signals: layout tests guard accidental struct changes that would break binary metadata compatibility. They do not validate `ChunkOndisk` size or object encoding details.
