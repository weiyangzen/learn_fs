# sources/cloud-native/soci-snapshotter/ztoc/testutil.go

## Purpose
`ztoc/testutil.go` supplies a helper that builds a temporary gzip tar, builds a zTOC for it, and returns both the zTOC and an in-memory section reader over the compressed bytes.

## Important APIs, Types, and Functions
`BuildZtocReader(t, ents, compressionLevel, spanSize, opts...)` uses testutil tar builders, writes to a temp file, builds a zTOC with `NewBuilder("test")`, removes the temp file, and returns the section reader.

## Control Flow, State, and Persistence
The function writes a temp archive to disk because the builder needs a filename, then removes it before returning. The returned section reader is backed by the in-memory tar data, so extraction tests do not depend on the temp file after construction.

## Dependencies and Integration Points
It depends on bytes/io/os/testing and `util/testutil`. It is used by ztoc tests for gzip header edge cases.

## Risks and Test Signals
The `testing.T` parameter is unused except for signature consistency. Errors during temp creation or zTOC build are propagated.
