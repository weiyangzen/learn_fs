# sources/cloud-native/containers-storage/pkg/archive/archive.go

## Purpose
`archive.go` is the main tar/archive utility implementation for containers/storage. It detects and applies compression, creates and extracts tar streams, preserves metadata, handles whiteouts, maps IDs, prevents archive breakouts, supports copy helpers, and exposes archiver constructors used by storage and copy code.

## Important Types and APIs
`Compression` supports uncompressed, bzip2, gzip, xz, and zstd detection/handling. `WhiteoutFormat` distinguishes AUFS and overlay whiteouts. `TarOptions` controls include/exclude patterns, compression, ID maps, chown override, whiteout conversion, copy-pass mode, force-mask extraction, source-dir inclusion, rebasing, rootless/userns behavior, and fixed timestamps. `Archiver` packages `Tar`, `Untar`, ID mappings, and chown options. `TarModifierFunc` powers `ReplaceFileTarWrapper`.

## Compression and Tar Creation
`DetectCompression` checks magic bytes. `DecompressStream` wraps a pooled buffered reader and supports gzip, bzip2, xz, zstd, and uncompressed streams, using external `pigz` or `zstd` filters when available. `CompressStream` supports uncompressed, gzip, and zstd output; bzip2 and xz writing return explicit unsupported errors. `TarWithOptions` starts a pipe and writes through `tarWithOptionsTo`, which walks requested include roots, applies exclude patterns, optional rebasing, hardlink tracking, xattrs, file flags, ID mapping, whiteout conversion, and compression.

## Extraction Control Flow and Safety
`Untar` and `UntarUncompressed` call `untarHandler`, which normalizes options and optionally decompresses. `Unpack` iterates tar headers, cleans names, applies excludes, creates parent directories, checks relative path scope, prevents directory/non-directory overwrites when requested, remaps IDs, runs whiteout conversion, and calls `extractTarFileEntry`. `extractTarFileEntry` creates regular files, dirs, devices, fifos, hardlinks, symlinks, or ignores PAX global headers; it rejects hardlink/symlink targets outside the extraction root, applies chown/chmod/timestamps, restores xattrs except ignored SELinux labels, writes override xattrs for force-mask mode, and defers directory flags/times until the end.

## Copy and Temporary Archive Helpers
`Archiver.TarUntar`, `UntarPath`, `CopyWithTar`, and `CopyFileWithTar` compose tar and untar for filesystem copying. `CopyFileWithTar` streams one file through a pipe, enforces `NoOverwriteDirNonDir`, and propagates writer errors. `NewTempArchive` stores a source stream in a temp file and deletes it after the full read. Chown-aware helper factories optionally tee archive data to a hasher. `TarPath` returns an ID-mapped tar producer.

## State and Persistence
Most operations are streaming and avoid persistent state. Persistent effects are extracted files, temp archive files, restored xattrs/file flags, and optional container override xattrs. Pooled buffers must be returned correctly; tar writers/readers and compressors must be closed to flush and surface errors.

## Dependencies and Integration Points
The file depends on Go tar/compression/filepath APIs, `fileutils`, `idtools`, `pools`, `promise`, `system`, `unshare`, `logrus`, `pgzip`, and `xz`. Platform hooks come from `archive_unix.go`, `archive_windows.go`, `archive_linux.go`, `archive_bsd.go`, version-gated files, zstd support, file flags, and filter helpers. `layers.go` uses this package for diff compression/detection, tar-split replay, whiteouts, and layer change export.

## Risks and Edge Cases
Security-sensitive risks include path traversal, symlink/hardlink breakout, xattr restoration under user namespaces, device creation, directory/non-directory overwrite behavior, and races when archiving a concurrently mutating tree. `TarWithOptions` logs and skips transient stat/add failures to keep archives valid, which can omit files. `ReplaceFileTarWrapper` mutates the supplied mods map. `remapIDs` has platform-specific behavior, including Darwin override xattr parsing. `NewTempArchive` only deletes after EOF or read error, so callers that never drain or close may leave temp files until external cleanup.

## Test Signals
The archive tests cover compression detection, unsupported compressors, tar/untar round trips, include/exclude/rebase behavior, overwrite errors, sockets, hardlinks, special devices, xattrs, security breakout attempts, temp archive idempotent close, tar replacement, timestamp determinism, and writer error propagation. Linux/Unix/Windows platform tests add whiteout and path behavior coverage.
