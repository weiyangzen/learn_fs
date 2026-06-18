# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/OpenFileSupport.java

## Purpose
`OpenFileSupport` centralizes S3A `openFile()` option handling so `S3AFileSystem` does not directly contain all builder parsing, status conversion, split/range handling, and read-policy defaults. It converts `OpenFileParameters` and filesystem defaults into an `OpenFileInformation` value used to build `S3AReadOpContext` for later stream creation.

## Important APIs and Types
- `OpenFileSupport(...)` stores immutable defaults: `ChangeDetectionPolicy`, default readahead, username, default buffer size, async drain threshold, and default `S3AInputPolicy`.
- `applyDefaultOptions(S3AReadOpContext)` applies default input policy, change detection, async drain threshold, and readahead to a read context.
- `prepareToOpenFile(Path, OpenFileParameters, long)` is the core parser for builder options and optional supplied status.
- `openSimpleFile(int)` creates the equivalent options for legacy `open(path, bufferSize)`.
- Nested `OpenFileInformation` is a fluent mutable value object with getters, `with...` setters, and `applyOptions(S3AReadOpContext)`.

## Control Flow
`prepareToOpenFile()` first rejects S3 Select when mandatory and logs once when optional, then validates mandatory option keys against `InternalConstants.S3A_OPENFILE_KEYS`. If the caller supplied a `FileStatus`, it verifies filename equality, rejects directories, extracts length/modification time plus S3A eTag/version metadata where available, and creates an `S3AFileStatus` using the target path. It then parses split start/end, file length, read policy, buffer size, async drain threshold, and readahead through `FSBuilderSupport`. If a length is known but no status was supplied, it builds a minimal status with unknown modification time and no eTag/version. The result is built as `OpenFileInformation`.

## State and Persistence
The support object is immutable after construction. `OpenFileInformation` is mutable during fluent setup but returned as the per-open state container. No persistent storage is modified; it only influences future S3 GET/HEAD behavior and stream configuration.

## Dependencies and Integration Points
It depends on Hadoop open-file option keys, S3A constants (`READAHEAD_RANGE`, `ASYNC_DRAIN_THRESHOLD`, `INPUT_FADVISE`), `S3AInputPolicy`, `S3AFileStatus`, `S3ALocatedFileStatus`, `ChangeDetectionPolicy`, and S3 Select constants. Integration is with S3A file opening, change detection, and stream factories through `S3AReadOpContext`.

## Risks and Edge Cases
Supplied status validation intentionally compares only final filename, not full path, so callers must avoid passing stale status for a different object with the same basename. Split-start greater than split-end is reset to zero with a warning, which prevents invalid ranges but may hide bad caller options. Minimal status from `FS_OPTION_OPENFILE_LENGTH` lacks eTag/version metadata, so change detection cannot use those fields. S3 Select is explicitly unsupported and mandatory use fails.

## Test Signals
Tests should cover mandatory-key rejection, optional vs mandatory S3 Select handling, supplied `S3AFileStatus` and `S3ALocatedFileStatus` metadata propagation, directory status rejection, split reset behavior, option precedence between standard open-file read policy and `INPUT_FADVISE`, and `applyOptions()` propagation into `S3AReadOpContext`.
