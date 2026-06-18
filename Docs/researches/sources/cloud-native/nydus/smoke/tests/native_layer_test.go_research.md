# sources/cloud-native/nydus/smoke/tests/native_layer_test.go

## Purpose
This suite validates native layer packing, merging, mounting, overlay semantics, chunkdict use, parent bootstrap merge behavior, repeatable builds, multiple compressors/fs versions/cache modes, and amplify I/O settings.

## Important APIs, Types, And Functions
Constants name matrix parameters shared by other tests. `checkDigests` compares digest slices order-insensitively. `NativeLayerTestSuite.TestMakeLayers` builds a broad Cartesian matrix over daemon version, compressor, fs version, chunk size, cache type/compression, RAFS mode, prefetch, batch, encryption, amplify I/O, and dedup DB, with skip rules for unsupported combinations. `TestAmplifyIO` narrows the matrix around `AmplifyIO`. `TestMergeLayerWithParentBootstrap` verifies parent-bootstrap merge returns only new upper digest and mounts correct overlay content. `testMakeLayers` is the large scenario implementation for chunkdict, lower, upper, base, and parent-bootstrap flows.

## Control Flow
The main implementation creates a chunkdict layer and bootstrap, packs lower and upper layers using that dictionary, asserts repeated packing yields identical digests, merges and mounts lower and overlay layers, then builds base layers and merges later layers with `ParentBootstrapPath` and `ChunkDictPath` pointing at the base bootstrap. Each stage verifies expected blob digest sets and mounted file trees.

## State And Persistence
All test artifacts live in a temporary workdir: source directories, blobs, cache, bootstraps, and optional CAS DB path. File-tree state is recorded in `tool.Layer.FileTree` and then mutated by `Overlay` to model merged layer behavior.

## Dependencies And Integration Points
It depends on `snapshotter-converter` pack/merge APIs, `texture` layer builders, `tool.Verify`/`tool.Nydusd`, and versioned `nydusd` resolution. It exercises builder output determinism, chunkdict metadata, parent bootstrap reuse, and runtime mount compatibility.

## Risks
The matrix is large and may be expensive. Some options such as `/tmp/cas.db` are shared paths that can carry cross-test state if parallel tests collide. Texture layers create special files and set capabilities, requiring privileges and host support. Skip logic is critical for avoiding unsupported combinations.

## Test Signals
Digest equality checks prove merge result accounting and repeatable builds. `tool.Verify` proves mounted metadata/content match expected synthetic trees after lower, overlay, and parent-bootstrap merges.
