# sources/distributed-fs/seaweedfs/weed/s3api/s3api_remote_storage_test.go

## Purpose

This test file documents and verifies behavior for remote-only entries, remote cache paths, versioned source ids, local-cache detection, and CopyObject from remote-only sources.

## Important APIs, Types, and Functions

Tests cover `filer_pb.Entry.IsInRemoteOnly`, streaming classification logic, versioned remote path construction, `resolvedSourceVersionId`, `cachedEntryHasLocalData`, and remote-only copy detection.

## Control Flow

Cases distinguish remote-only entries, cached remote entries, local chunks, zero-byte remote entries, corrupt no-chunk positive-size entries, empty files, version/null path construction, latest-version id fallback, local data hits from chunks/content, and the copy inline-branch bug shape.

## State and Persistence Behavior

All state is synthetic `filer_pb.Entry` data. The tested persistent contracts are remote-entry metadata, chunk/content presence, `.versions/v_<id>` cache paths, and version id extended metadata.

## Dependencies and Integration Points

The file depends on `filer.FileSize`, `filer_pb.Entry`, `RemoteEntry`, S3 constants, and remote streaming/copy helpers.

## Risks and Edge Cases

Risks include treating remote-only objects as corrupt, mishandling zero-byte remote objects, building wrong versioned cache paths, losing latest version id, and creating copy destinations with size but no data.

## Test Signals

The tests are strong unit signals for classification and path construction; configured remote-storage integration tests remain needed.
