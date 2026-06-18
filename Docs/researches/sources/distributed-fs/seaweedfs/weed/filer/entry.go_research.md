# sources/distributed-fs/seaweedfs/weed/filer/entry.go

## Purpose
This file defines SeaweedFS filer metadata objects: file attributes and entries. It provides conversion to and from protobuf entries and helper methods for size, timestamps, cloning, S3 expiration/version markers, and full-entry wrappers.

## Important APIs, Types, and Functions
- `Attr` stores times, mode, ownership, MIME, TTL, user/group names, symlink target, MD5, file size, device, and inode.
- `Entry` embeds `util.FullPath` and `Attr`, plus extended metadata, chunks, hard-link fields, inline content, remote entry, quota, and WORM timestamp.
- Methods include `Attr.IsDirectory`, `Entry.Size`, `Entry.Timestamp`, `Entry.ShallowClone`, `ToProtoEntry`, `ToExistingProtoEntry`, `ToProtoFullEntry`, `GetChunks`, `IsExpireS3Enabled`, `IsS3Versioning`, and `GetS3ExpireTime`.
- Conversion functions: `FromPbEntryToExistingEntry`, `FromPbEntry`, and `maxUint64`.

## Control Flow and State
`ToExistingProtoEntry` populates a protobuf entry, reusing existing attribute storage if present. `FromPbEntryToExistingEntry` decodes protobuf attributes and assigns chunks, extended metadata, hard links, content, remote entry, quota, computed file size, and WORM timestamp. `Size` returns the maximum of chunk total size, recorded file size, and inline content length.

## State and Persistence Behavior
`Entry` is the in-memory representation that filer stores serialize and persist. Chunks reference volume-server data; extended fields carry S3 and SeaweedFS metadata; TTL and WORM fields influence lifecycle semantics.

## Dependencies and Integration Points
It integrates with `filer_pb.Entry`, `filer_pb.FullEntry`, S3 constants, `util.FullPath`, and helper functions such as `EntryAttributeToPb`, `PbToEntryAttribute`, `FileSize`, and `TotalSize` defined elsewhere.

## Risks and Edge Cases
- `ShallowClone` shares slices, maps, and pointers, so callers must not mutate shared fields unexpectedly.
- `Timestamp` returns creation time for directories and modification time for files.
- `Size` can report inline content length or file-size metadata even when chunks differ.
- S3 expiration falls back from mtime to crtime and uses TTL seconds directly.

## Test Signals
Tests in this set indirectly cover entry serialization through `entry_codec_atime_test.go`, backend stores, and chunk tests. Additional tests should cover shallow clone sharing, size precedence, proto reuse, and S3 marker helpers.
