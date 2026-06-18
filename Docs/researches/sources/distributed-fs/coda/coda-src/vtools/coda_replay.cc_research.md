# sources/distributed-fs/coda/coda-src/vtools/coda_replay.cc

## Purpose

`coda_replay.cc` replays or lists Coda closure streams encoded as tar-like records with Coda-specific operations in the tar `linkflag` field. It can execute the stream, list it without changes, or reject deprecated stripping behavior.

## Important APIs, Types, and Functions

Global flags `rflag`, `sflag`, `tflag`, `vflag`, `hflag`, and `trailers` drive mode. `main()` requires exactly one of replay/list/deprecated strip mode and reads from stdin or a named file. `ValidateHeader()` parses octal metadata, validates operation kind, logs records under verbose/list modes, detects trailers, and verifies checksum. `HandleRecord()` applies operations for `STOREDATA`, `LINK`, `SYMLINK`, `STORESTATUS`, `REMOVE`, `RENAME`, `MKDIR`, and `RMDIR`. Helpers `checksum()`, `makeprefix()`, `setmode()`, `setowner()`, `setlength()`, `settimes()`, `readblock()`, `writeblock()`, and `usage()` implement tar-block I/O and filesystem effects.

## Control Flow

The tool reads 512-byte headers until two empty trailer records are seen. Every header is validated before handling. In replay mode, data records create parent directories, redirect `stdout` to the target file, copy full tar blocks, close the file, and apply metadata. Other operations call POSIX link, symlink, truncate, chmod, chown, utimes, unlink, rename, mkdir, or rmdir. In list mode, it validates and logs but helper functions suppress mutations because they check `rflag`.

## State and Persistence Behavior

Replay mode mutates the current filesystem tree according to the stream: creates directories/files/links, removes names, renames paths, changes mode/owner/timestamps, and truncates status-only records. There is no checkpointing or rollback. Non-harsh mode logs some failures and continues; harsh mode exits on supported errors.

## Dependencies and Integration Points

It depends on `coda_replay.h` for the tar header layout and operation constants, and POSIX file APIs. It is used by Coda repair/reintegration closure workflows that need non-tar operations represented in otherwise tar-like streams.

## Risks

Input paths are trusted and can write outside the intended directory if the stream contains absolute paths or `..`. `STOREDATA` writes whole 512-byte blocks and does not call `setlength()`, so non-block-aligned file sizes can retain tar padding unless upstream formats avoid this. It uses `freopen()` on global `stdout`, making error handling and further diagnostics fragile. UID/GID and octal size parsing use `uint32_t`, limiting large sizes. `makeprefix()` modifies the path buffer in place. There is no symlink traversal protection, atomicity, or replay transaction boundary.

## Test Signals

Tests should feed synthetic blocks for every `linkflag`, bad checksums, malformed operation codes, one and two trailer records, non-multiple-of-512 data sizes, harsh versus non-harsh failures, path traversal inputs, metadata changes, and list mode no-op behavior.
