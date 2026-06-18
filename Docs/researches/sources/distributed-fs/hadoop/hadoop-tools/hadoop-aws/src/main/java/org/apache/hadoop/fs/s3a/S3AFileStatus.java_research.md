# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AFileStatus.java

## Purpose

`S3AFileStatus` is the S3A-specific `FileStatus` implementation used for object and pseudo-directory metadata. It extends Hadoop's `FileStatus` with S3-specific eTag and version id fields and a tri-state "empty directory" marker so listing, rename, delete, auditing, and located-status conversion can reason about S3's directory emulation.

## Important APIs, Types, and Functions

- `public class S3AFileStatus extends FileStatus implements EtagSource`: exposes S3 eTag through the standard `EtagSource` interface.
- Directory constructors:
  - `S3AFileStatus(boolean isemptydir, Path path, String owner)`
  - `S3AFileStatus(Tristate isemptydir, Path path, String owner)`
- File constructor: `S3AFileStatus(long length, long modification_time, Path path, long blockSize, String owner, String eTag, String versionId)`.
- Package-private combined constructor: creates either file or directory status and calls the modern `FileStatus` superclass constructor with owner/group set to owner and directory flags.
- `static fromFileStatus(FileStatus source, Tristate isEmptyDirectory, String eTag, String versionId)`: converts a generic status into S3A status while preserving file metadata and adding S3 metadata.
- `isEmptyDirectory()` and `setIsEmptyDirectory()`: expose/update the tri-state directory emptiness marker.
- `getETag()` and `getEtag()`: deprecated S3A spelling plus standard interface spelling.
- `getVersionId()` and `setVersionId()`: expose/update S3 object version id.
- `getModificationTime()`: returns current time for directories and the stored modification time for files.
- `equals()` and `hashCode()`: explicitly defer to `FileStatus`, preserving path-based semantics.
- `toString()`: appends empty-directory, eTag, and version id information to the base status string.

## Control Flow

Construction splits along directory versus file paths. Directory statuses carry length, modification time, and block size as zero and use `Tristate` to represent empty, non-empty, or unknown emptiness. File statuses carry object length, object last-modified time, block size, eTag, and version id.

`fromFileStatus()` branches on `source.isDirectory()`. Directory conversion creates a directory status and does not preserve eTag/version id because pseudo-directories do not represent normal S3 object metadata in the same way. File conversion preserves length, modification time, path, block size, owner, eTag, and version id.

`getModificationTime()` intentionally changes directory behavior at read time: directories report `System.currentTimeMillis()` to avoid ecosystem components treating stale marker object timestamps as old directories.

## State and Persistence Behavior

The class is serializable through `FileStatus` and adds mutable fields:

- `Tristate isEmptyDirectory`
- `String eTag`
- `String versionId`

It does not perform persistence itself. The fields mirror S3 object/listing/head metadata created elsewhere. `setVersionId()` and `setIsEmptyDirectory()` allow later operations to refine status metadata without reconstructing the object.

Directory modification time is intentionally non-stable because it returns the current local time on each call. This affects consumers that cache or compare directory status values.

## Dependencies and Integration Points

- `S3AUtils.createFileStatus()` and `createUploadFileStatus()` build instances from S3 metadata.
- `S3AFileSystem.innerGetFileStatus()`, `s3GetFileStatus()`, rename, delete, listing, and content-summary paths use `S3AFileStatus` to distinguish files, empty directories, non-empty directories, and unknown states.
- `Listing` creates iterators of `S3AFileStatus` from S3 object listings and common prefixes.
- `S3ALocatedFileStatus` copies eTag, version id, and empty-directory state and can convert back to `S3AFileStatus`.
- `DirMarkerTracker`, marker tools, audit managers, mkdir operations, and rename/delete operations inspect status metadata.
- `EtagSource` lets public APIs access eTags without relying on the deprecated `getETag()` method.

## Risks and Edge Cases

- Directory modification time is dynamic by design. Code expecting stable directory mtimes can see changing values across calls.
- Equality and hash code come from `FileStatus`, so eTag, version id, and empty-directory state do not affect equality. This is useful for path identity but risky for metadata-sensitive caches.
- `fromFileStatus()` drops eTag/version id for directories. If a directory marker object's own metadata matters, it must be carried elsewhere.
- `toString()` has nested `String.format()` calls that effectively place eTag and version id inside the formatted empty-directory suffix. This is diagnostic only but worth checking when changing it.
- Mutable `versionId` and `isEmptyDirectory` can diverge from actual S3 state if reused after object changes.

## Test Signals

Signals include:

- `TestS3AResourceScope`, which constructs directory and file statuses and verifies executable/scope behavior.
- `ITestS3AFileOperationCost`, which verifies `isEmptyDirectory()` for root, empty directories, non-empty directories, and file status probes.
- `TestS3AGetFileStatus`, which covers status creation from S3 object and listing metadata.
- Located-status tests and code paths through `S3ALocatedFileStatus` should preserve eTag/version id/empty-directory fields.
- Rename and mkdir integration tests indirectly validate the tri-state empty-directory behavior because overwrite and parent checks depend on it.
