# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioning.go

## Purpose

This is the core S3 object versioning implementation, storing versions in hidden `.versions` directories and maintaining cached latest-version metadata.

## Important APIs, Types, and Functions

Important types include `S3ListObjectVersionsResult`, `VersionListEntry`, `ObjectVersion`, `versionListItem`, and `versionCollector`. Important functions include delete marker creation, version listing, recursive collection, specific/latest version reads, version deletion, latest pointer pre-roll, retry helpers, stale pointer clear/heal, list handler, cached list entry recovery, and owner extraction.

## Control Flow

Versioned writes create files under `object.versions/` and update latest metadata. Delete markers are version files tagged as delete markers; suspended deletes use a fixed `null` marker. Listing recursively finds `.versions`, explicit directory markers, regular/null objects, and prefixes, then emits interleaved S3 XML entries. Reads use cached latest pointers and self-heal missing/stale pointers by rescanning. Deleting the latest pre-rolls the pointer before blob removal, then tears down or repairs `.versions` as needed.

## State and Persistence Behavior

Persistent state spans regular entries, `.versions` child entries, and `.versions` directory extended metadata: version ids, latest ids/files, cached size/mtime/ETag/owner/delete-marker, delete marker flags, storage class, owner, and noncurrent timestamps. Mutations use filer `mkFile`, `updateEntry`, `rm`, `rmObject`, list, and get operations with bounded retry on load-bearing pointer updates.

## Dependencies and Integration Points

The file depends on filer listing/ETag helpers, version id generation/comparison, S3 constants/errors, logging, gRPC status codes, lifecycle metadata, versioned finalize helpers, IAM owner lookup, and optional heal queues. It integrates with PUT, GET/HEAD, DELETE, ListObjectVersions, regular listing, lifecycle, remote storage, and copy flows.

## Risks and Edge Cases

High-risk areas include multi-page version directories, mixed old/new id formats, delete markers as latest, stale pointers, orphan entries, missing extended metadata, concurrent writers, transient filer failures, and null/pre-versioning object semantics.

## Test Signals

Self-heal tests cover selector semantics and filename fallback. More integration tests are needed for real filer PUT/DELETE/LIST flows and concurrency.
