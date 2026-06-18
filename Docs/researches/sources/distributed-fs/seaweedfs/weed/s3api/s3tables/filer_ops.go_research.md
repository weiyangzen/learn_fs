# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/filer_ops.go

## Purpose
This file centralizes low-level filer operations used by the S3 Tables handler to create/delete directories and manipulate extended attributes that hold table bucket, namespace, table, policy, metadata, and tag state.

## Important APIs and functions
`ErrAttributeNotFound` distinguishes missing extended attributes from missing entries or transport errors. Methods on `S3TablesHandler` include `createDirectory`, `ensureDirectory`, `deleteEntryIfExists`, `setExtendedAttribute`, `getExtendedAttribute`, `deleteExtendedAttribute`, `deleteDirectory`, and `entryExists`.

## Control flow and state behavior
`createDirectory` splits a path, builds a directory `Entry` with current mtime/crtime and mode `0755 | os.ModeDir`, and calls `filer_pb.CreateEntry`. `ensureDirectory` looks up a path and creates it only on `filer_pb.ErrNotFound`. Extended attribute setters and deleters perform lookup, mutate the entry's `Extended` map, and call `filer_pb.UpdateEntry`. `getExtendedAttribute` wraps missing attributes with `ErrAttributeNotFound`. Recursive deletion uses `DeleteEntry` with data deletion and ignored recursive errors. `entryExists` is a simple lookup boolean.

## Dependencies and integration points
The file depends on `filer_pb` helpers/RPCs and `splitPath` from `utils.go`. Higher-level handlers use these methods to persist metadata under `s3_constants.DefaultBucketsPath` and table object bucket paths.

## Risks and edge cases
Extended-attribute updates are read-modify-write without compare-and-swap, so concurrent tag/policy/metadata mutations can overwrite each other. `deleteEntryIfExists` relies on `DoRemove` behavior despite the name saying it ignores missing errors. Recursive deletion with ignored recursive errors may hide partial cleanup details. Directory creation does not ensure parent directories unless callers do so.

## Test signals
No direct tests in this subset target these helpers, but S3 Tables handler tests elsewhere exercise them through bucket/namespace/table/policy/tag flows.
