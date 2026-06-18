<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/ensurehello.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/ensurehello.go

## Purpose
Downloads a known `hello-world` OCI archive and imports it into a temporary containerd content store for tests.

## Important APIs, Types, And Functions
- `HelloArchiveURL` and `HelloArchiveDigest` define the fixture source and expected archive digest.
- `EnsureHello(ctx)` downloads, verifies, gunzips, imports the OCI index, and returns descriptor plus content store.

## Control Flow
HTTP GET streams through a SHA256 tee into a gzip reader, creates a temp local content store, imports the index with `archive.ImportIndex`, then compares the downloaded gzip digest to the expected digest.

## State And Persistence
Creates a temporary content store directory. The caller receives the store but not an explicit cleanup callback in this function.

## Dependencies And Integration Points
Depends on network access to GitHub releases, Go gzip, containerd local content store, and OCI archive import helpers.

## Risks And Edge Cases
Network availability and remote fixture stability affect tests. Temp directories can leak if callers do not clean them. Digest verifies the compressed archive, not each imported object independently.

## Test Signals
Successful return includes a descriptor, usable content store, and digest match. Failures identify download, gzip, import, or digest mismatch problems.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/ensurehello.go -->
