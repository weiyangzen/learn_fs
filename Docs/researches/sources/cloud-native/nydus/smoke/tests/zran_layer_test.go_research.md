# sources/cloud-native/nydus/smoke/tests/zran_layer_test.go

## Purpose
This suite verifies zran/OCI-reference layer packing and mounting for gzip and non-gzip OCI blobs with cache compression and prefetch combinations.

## Important APIs, Types, And Functions
`ZranTestSuite.TestMakeLayers` iterates `gzip`, `cache_compressed`, and `enable_prefetch`. `testMakeLayers` prepares a context, creates a lower texture layer, packs it with `PackRef` to produce original OCI and RAFS blob digests, merges with `OCIRef=true`, asserts the merge returns the original OCI digest, sets the bootstrap path, and verifies the mount.

## Control Flow
For each scenario the test builds a lower layer, packs the OCI-reference RAFS blob, merges it into a bootstrap that references original OCI content, then mounts through `nydusd` and compares the file tree.

## State And Persistence
Temporary state includes source layer, OCI blob, RAFS blob, bootstrap, cache, and mount directory. The gzip flag changes how the original OCI blob is stored.

## Dependencies And Integration Points
It depends on `texture.MakeLowerLayer`, `tool.Layer.PackRef`, `tool.MergeLayers`, `snapshotter-converter`, and `tool.Verify`. It exercises Nydus zran/OCI reference mode in builder and runtime.

## Risks
The texture layer includes special files and large random data, requiring host support. The expected digest assertion differs from native mode: the returned digest must be the original OCI digest, not the RAFS blob digest.

## Test Signals
Signals are correct merge digest accounting and successful mounted file-tree verification for all gzip/cache/prefetch combinations.
