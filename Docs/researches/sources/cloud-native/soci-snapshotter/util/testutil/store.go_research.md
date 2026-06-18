# sources/cloud-native/soci-snapshotter/util/testutil/store.go

## Purpose
`store.go` provides a small helper for resolving the blob directory for a configured content store type.

## Important APIs, Types, and Functions
`GetContentStoreBlobPath(contentStoreType)` calls `store.GetContentStorePath(contentStoreType, "")` and appends `blobs/sha256`.

## Control Flow, State, and Persistence
The helper performs path calculation only. It does not verify directory existence or create directories.

## Dependencies and Integration Points
It depends on `path/filepath` and `github.com/awslabs/soci-snapshotter/soci/store`. It is used by shell test helpers for direct SOCI content deletion.

## Risks and Test Signals
Only SHA256 blob layout is supported. Errors from content-store path canonicalization are propagated, but missing directories are not detected here.
