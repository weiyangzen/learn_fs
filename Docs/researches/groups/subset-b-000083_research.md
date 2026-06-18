# Research Report: subset-b-000083

Work item `subset-b-000083` covers selected containers/storage packages under `pkg/chunked`, `pkg/config`, `pkg/directory`, `pkg/dmesg`, `pkg/fileutils`, `pkg/fsutils`, `pkg/fsverity`, `pkg/homedir`, `pkg/idmap`, `pkg/idtools`, and `pkg/ioutils`. Each section below preserves the source path as its title and is bounded with the required split markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/filesystem_linux.go -->
## sources/cloud-native/containers-storage/pkg/chunked/filesystem_linux.go

Purpose: Linux-only fd-oriented filesystem helpers for the chunked differ. The file keeps extraction under a target root using `openat2(RESOLVE_IN_ROOT)` when available, a securejoin fallback otherwise, and helpers for hard links, symlinks, directories, sparse holes, metadata/xattr ownership application, whiteouts, and an in-memory seekable wrapper over an `io.ReaderAt`.

Important APIs/types/functions: `fileMetadata` embeds `minimal.FileMetadata` and adds chunk slices plus `skipSetAttrs`; `splitPath`, `openFileUnderRoot`, `openOrCreateDirUnderRoot`, `doHardLink`, `copyFileContent`, `setFileAttrs`, `safeMkdir`, `safeLink`, `safeSymlink`, `whiteoutHandler`, `seekableFile.GetBlobAt`, and `newSeekableFile`. `skipOpenat2` caches kernel lack of `openat2`.

Control flow: paths are normalized with `internal/path.CleanAbsPath`; file opens first try `openat2`, fall back only on `ENOSYS`, and create missing parents for `O_CREAT`. `setFileAttrs` chooses descriptor versus path mode, forces symlink operations through path-based syscalls, applies chown, base64-decoded xattrs except ignored SELinux labels, timestamps, then chmod. Copying prefers a hard link when allowed, otherwise creates a new file and delegates copy acceleration to `drivers/copy.CopyRegularToFile`.

State and persistence: creates directories/files/symlinks/hardlinks under the checkout root, mutates xattrs, ownership, times, modes, device whiteouts, and sparse file size. `skipSetAttrs` prevents hard-link dedupe from changing shared inode metadata. `skipOpenat2` is process-global. `seekableFile` owns and closes the wrapped reader.

Dependencies and integration points: used by `storage_linux.go` extraction, whiteout conversion, composefs flat paths, and tar metadata staging. Depends on `unix`, `/proc/self/fd`, `archive.TarOptions`, `securejoin`, `tar-split`, and storage path helpers.

Risks: fallback root containment relies on procfs target prefix checking and securejoin semantics; hard-link dedupe deliberately skips metadata changes; xattr values must be valid base64; `setFileAttrs` ignores `ENOSYS`/`ENOTSUP` for xattr/time/chmod operations; symlink tests intentionally show link targets may point outside root but opening remains root-confined.

Test signals: `filesystem_linux_test.go` covers section reads, hard-link replacement, sparse holes, root-confined mkdir/link/symlink/open, copy versus hard-link inode behavior, and path normalization. No full end-to-end `ApplyDiff` test is in this file. Local test execution was blocked because `go` is not installed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/filesystem_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/filesystem_linux_test.go -->
## sources/cloud-native/containers-storage/pkg/chunked/filesystem_linux_test.go

Purpose: Linux unit tests for the fd-safe filesystem primitives used by chunked layer extraction.

Important APIs/types/functions: defines `nopCloser`, `createTempFile`, and tests `newSeekableFile.GetBlobAt`, `doHardLink`, `appendHole`, `safeMkdir`, `safeLink`, `safeSymlink`, `openOrCreateDirUnderRoot`, `copyFileContent`, and `splitPath`.

Control flow: each test builds temporary roots and file descriptors, exercises helper behavior, then verifies by reading through `openFileUnderRoot`, `Fstat`, inode comparison, file size seeking, or expected normalized path pairs. Privilege-sensitive chown calls are bypassed with `archive.TarOptions{IgnoreChownErrors:true}`.

State and persistence: tests create real temporary files, directories, hard links, symlinks, and sparse holes. The suite checks whether hard-link dedupe returns nil destination file and preserves inode identity, while copy mode creates a distinct inode.

Dependencies and integration points: test coverage targets `filesystem_linux.go`; uses `testify`, `syscall`, `archive.TarOptions`, and `minimal.FileMetadata`. It validates assumptions consumed later by `storage_linux.go`.

Risks: tests use Linux filesystem semantics and may require symlink/hardlink support. They exercise helper primitives but do not validate whiteout handler, xattr application, `openat2` ENOSYS fallback, or fs-verity flows.

Test signals: the case table for `splitPath` is broad and important because many *at syscalls receive its base name. Local execution was not possible because `go` is unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/filesystem_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/internal/minimal/compression.go -->
## sources/cloud-native/containers-storage/pkg/chunked/internal/minimal/compression.go

Purpose: minimal, dependency-light zstd:chunked format definitions and manifest writing logic shared with consumers that should not import graph-driver code.

Important APIs/types/functions: `ZstdWriter`, `CreateZstdWriterFunc`, `TOC`, `FileMetadata`, chunk/file type constants, annotation keys, `GetType`, `TarSplitData`, `WriteZstdChunkedManifest`, `ZstdWriterWithLevel`, `ZstdChunkedFooterData`, `footerDataToBlob`, `timeIfNotZero`, and `NewFileMetadata`.

Control flow: `WriteZstdChunkedManifest` marshals a TOC with entries and tar-split digest, compresses it with caller-provided zstd writer, records checksum and position annotations, writes the compressed manifest and tar-split bytes as zstd skippable frames, then writes a binary footer frame. `NewFileMetadata` converts tar headers to JSON metadata and base64-encodes PAX xattrs.

State and persistence: writes zstd skippable frames to a destination stream and mutates the caller-provided metadata map with manifest/tar-split annotations. It does not read files or maintain global mutable state beyond constants.

Dependencies and integration points: consumed by chunked compressor and differ manifest readers/writers. Integrates with `archive.PaxSchilyXattr`, `jsoniter`, `klauspost/compress/zstd`, OCI digest parsing, and `tar-split` tar types.

Risks: callers must pass valid offsets that reflect bytes already written; `RegularFile` chunk metadata invariants are documented but not enforced here; digest security depends on annotation consumers verifying the compressed manifest digest; footer is explicitly not read by this implementation.

Test signals: `compression_test.go` checks binary footer round trip and magic validation. `zstdchunked_test.go` exercises manifest generation and reading through higher-level chunked code. Local test execution was blocked by missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/internal/minimal/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/internal/minimal/compression_test.go -->
## sources/cloud-native/containers-storage/pkg/chunked/internal/minimal/compression_test.go

Purpose: validates the binary footer layout emitted by `footerDataToBlob`.

Important APIs/types/functions: `TestGenerateAndReadFooter` and local helper `readFooterDataFromBlob`, which decodes the little-endian footer fields and checks `ZstdChunkedFrameMagic`.

Control flow: builds a `ZstdChunkedFooterData`, serializes it, asserts `FooterSizeSupported`, decodes all seven uint64 fields, validates the magic suffix, and compares with the original struct.

State and persistence: no filesystem or persistent state; all data is in memory.

Dependencies and integration points: directly protects the footer contract used by zstd:chunked writers. It uses `testify/assert`, `encoding/binary`, and the package constants.

Risks: the decoder helper lives only in the test because production code currently does not read the footer; tests do not cover manifest compression, annotations, or tar-split digest.

Test signals: good regression signal for footer field order, supported size, and magic bytes. Local execution was blocked because the Go toolchain is absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/internal/minimal/compression_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/internal/path/path.go -->
## sources/cloud-native/containers-storage/pkg/chunked/internal/path/path.go

Purpose: tiny path-normalization helper package for chunked extraction and composefs-style flat file storage.

Important APIs/types/functions: `CleanAbsPath` and `RegularFilePathForValidatedDigest`.

Control flow: `CleanAbsPath` prefixes input with `/` and calls `filepath.Clean`, collapsing `.` and `..` into a root-confined absolute logical path. `RegularFilePathForValidatedDigest` requires a SHA256 digest and maps its encoded hex to `<first-two>/<rest>`.

State and persistence: stateless string transformation only.

Dependencies and integration points: used by `filesystem_linux.go` and `storage_linux.go` to sanitize TOC names/link targets and to derive flat composefs backing paths. Depends on `opencontainers/go-digest`.

Risks: `RegularFilePathForValidatedDigest` trusts the caller to provide a validated digest; it assumes SHA256 encoding has enough length for slicing. `CleanAbsPath` is logical normalization and not sufficient alone for filesystem containment, so fd-based opens still matter.

Test signals: `path_test.go` has broad path-cleaning examples and a SHA512 rejection case. Local test execution was blocked by missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/internal/path/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/internal/path/path_test.go -->
## sources/cloud-native/containers-storage/pkg/chunked/internal/path/path_test.go

Purpose: unit tests for chunked internal path normalization and digest-based regular-file path generation.

Important APIs/types/functions: `TestCleanAbsPath` and `TestRegularFilePathForValidatedDigest`.

Control flow: table-driven tests feed empty, relative, absolute, repeated slash, `.` and `..` paths into `CleanAbsPath`. Digest tests parse a valid SHA256 and a SHA512 and assert path generation or error.

State and persistence: no persistent state; all tests are pure.

Dependencies and integration points: validates helpers used by fd-safe filesystem operations and flat output mapping in `storage_linux.go`.

Risks: tests do not check malformed digest strings directly because parsing is done before calling the helper; they also do not validate OS-specific path separator differences.

Test signals: strong signal for traversal normalization; local execution was blocked because `go` is unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/internal/path/path_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/storage.go -->
## sources/cloud-native/containers-storage/pkg/chunked/storage.go

Purpose: platform-neutral public contracts and errors for chunked blob access and fallback signaling.

Important APIs/types/functions: `ImageSourceChunk`, `ImageSourceSeekable`, `ErrBadRequest`, `ErrFallbackToOrdinaryLayerDownload`, and `newErrFallbackToOrdinaryLayerDownload`.

Control flow: callers pass chunk offset/length requests to `ImageSourceSeekable.GetBlobAt`, receiving separate stream and error channels. Fallback errors wrap a root cause and remain detectable through `errors.As`/`Unwrap`.

State and persistence: no state; defines wire-like contracts between image sources and differs.

Dependencies and integration points: implemented by image source adapters, `seekableFile`, and tests; consumed heavily by `storage_linux.go` for range fetches and fallback decisions.

Risks: dual-channel API is awkward and requires careful draining; `storage_linux.go` adds `getBlobAt` to normalize it. `ErrBadRequest` drives request-merging retry behavior.

Test signals: behavior is indirectly tested in `storage_linux_test.go` and `filesystem_linux_test.go`. No direct tests in this file; local execution unavailable due to missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/storage_linux.go -->
## sources/cloud-native/containers-storage/pkg/chunked/storage_linux.go

Purpose: Linux implementation of chunked partial layer application. It chooses a zstd:chunked, eStargz, or conversion differ, reads TOC metadata, stages filesystem entries, deduplicates content from prior layers or OSTree repos, range-fetches missing chunks, records fs-verity digests, and returns graph-driver differ output.

Important APIs/types/functions: `chunkedDiffer`, `pullOptions`, `parsePullOptions`, `NewDiffer`, `getProperDiffer`, `makeConvertFromRawDiffer`, `makeZstdChunkedDiffer`, `makeEstargzChunkedDiffer`, `ApplyDiff`, `mergeTocEntries`, `retrieveMissingFiles`, `storeMissingFiles`, `mergeMissingChunks`, `getBlobAt`, `copyAllBlobToFile`, `makeEntriesFlat`, `findFileInOtherLayers`, `findFileInOSTreeRepos`, `recordFsVerity`, and `stagedFileGetter`.

Control flow: `NewDiffer` requires partial images and a graph driver supporting staged differs, then dispatches by TOC annotations. zstd:chunked readers require tar-split unless unpredictable content is explicitly allowed; eStargz requires that same insecure opt-out. `ApplyDiff` is one-shot: optional raw-to-zstd conversion first validates the compressed digest, then parses the generated manifest; entries are merged with following `TypeChunk` records; IDs may be remapped; directories/symlinks/hardlinks are created; regular files are copied from cache/OSTree when possible; remaining chunks are merged into bounded range requests, fetched, decompressed or hole-punched, hashed, and attributed.

State and persistence: mutates the destination root with files, dirs, xattrs, whiteouts, hardlinks, holes, override xattrs, and fs-verity state. Maintains per-differ zstd/gzip readers, tar-split file ownership, layer cache reference, copy buffer, fs-verity digest map, and one-shot `used` guard. Output BigData stores manifest and chunked-layer metadata; Artifacts include TOC and fs-verity digests.

Dependencies and integration points: central integration point with `storage.Store`, graph drivers, `archive.TarOptions`, `idtools`, `fsverity`, tar-split, eStargz, zstd/gzip, OCI digests, layer cache helpers, compression helpers, securejoin, and fd-safe filesystem helpers.

Risks: high-complexity security path involving TOC trust, digest validation, fd containment, whiteout conversion, and ID mapping. The boolean expression in `maybeDoIDRemap` depends on operator precedence and may be easy to misread. `useHardLinks` dedupe skips metadata changes by design. Full uncompressed digest reconstruction is expensive but needed for consistency unless insecure opt-out is enabled. Concurrent copy workers write into a shared result slice by unique indexes; correct job indexing is essential.

Test signals: `storage_linux_test.go` focuses on `getBlobAt` stream/error channel normalization and `typeToOsMode`; `zstdchunked_test.go` validates manifest generation/read integration. There is no focused unit test for `ApplyDiff`, request merging, fs-verity, OSTree dedupe, ID remap, or whiteout behavior in the selected files. Local `go test` could not run because `go` is not installed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/storage_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/storage_linux_test.go -->
## sources/cloud-native/containers-storage/pkg/chunked/storage_linux_test.go

Purpose: tests selected utility behavior from the Linux chunked storage implementation.

Important APIs/types/functions: `mockImageSource`, `mockReadCloser`, `TestGetBlobAtNormalOperation`, `TestGetBlobAtMaxStreams`, `TestGetBlobAtWithErrors`, `TestGetBlobAtMixedStreamsAndErrors`, and `TestTypeToOsMode`.

Control flow: mock image sources return preloaded stream and error channels. Tests consume the normalized `getBlobAt` channel, verify stream contents, over-return detection, error forwarding, mixed stream/error handling, stream close behavior, and tar type to `os.FileMode` conversion.

State and persistence: in-memory channels/readers only; no filesystem mutations.

Dependencies and integration points: validates helper behavior used by `copyAllBlobToFile` and missing-chunk fetch paths. Uses `testify`.

Risks: does not test real range requests, `ErrBadRequest` retry/merge behavior, partial extraction, cache dedupe, or graph-driver integration.

Test signals: good channel-draining regression coverage. Local execution unavailable because the Go toolchain is missing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/storage_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/storage_unsupported.go -->
## sources/cloud-native/containers-storage/pkg/chunked/storage_unsupported.go

Purpose: non-Linux fallback implementation of `NewDiffer`.

Important APIs/types/functions: `NewDiffer` with `//go:build !linux`.

Control flow: ignores the detailed inputs and returns `ErrFallbackToOrdinaryLayerDownload` wrapping "format not supported on this system".

State and persistence: none.

Dependencies and integration points: preserves API availability for non-Linux builds while directing callers to ordinary layer download. Depends on storage and graphdriver interfaces only for signature compatibility.

Risks: callers that require partial images must treat the fallback wrapper correctly; no conversion path exists on unsupported platforms.

Test signals: no direct tests selected. Behavior is simple but depends on build tags.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/storage_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/toc/toc.go -->
## sources/cloud-native/containers-storage/pkg/chunked/toc/toc.go

Purpose: extracts a TOC digest from image annotations for either eStargz or zstd:chunked layers without importing eStargz package code.

Important APIs/types/functions: `tocJSONDigestAnnotation` and `GetTOCDigest`.

Control flow: checks for both eStargz and zstd:chunked annotation keys, rejects ambiguous dual presence, parses whichever digest is present, or returns nil when neither exists.

State and persistence: stateless annotation-map inspection.

Dependencies and integration points: used by `storage_linux.go` after conversion and by callers wanting a format-neutral TOC digest. Depends on `minimal.ManifestChecksumKey` and OCI digest parsing.

Risks: nil digest is a valid "not present" result and must not be confused with parse success. Duplicate annotations are treated as hard error to avoid ambiguity.

Test signals: `toc_test.go` covers valid eStargz annotation, invalid digest, and no annotation. It does not cover the dual-annotation error or zstd key explicitly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/toc/toc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/toc/toc_test.go -->
## sources/cloud-native/containers-storage/pkg/chunked/toc/toc_test.go

Purpose: unit tests for format-neutral TOC digest extraction.

Important APIs/types/functions: `TestGetTOCDigest` with valid, invalid, and empty annotation cases.

Control flow: constructs annotation maps and checks digest pointer content, error behavior, and nil result.

State and persistence: pure in-memory tests.

Dependencies and integration points: protects `toc.GetTOCDigest` consumers in chunked conversion and manifest handling.

Risks: missing tests for zstd:chunked annotation and conflict handling leave two branches uncovered.

Test signals: basic digest parsing regression signal; local execution blocked because `go` is unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/toc/toc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/zstdchunked_test.go -->
## sources/cloud-native/containers-storage/pkg/chunked/zstdchunked_test.go

Purpose: Linux integration-style tests for zstd:chunked manifest writing and reading plus tar type conversion.

Important APIs/types/functions: `seekable`, `someFiles`, `TestGenerateAndParseManifest`, and `TestGetTarType`.

Control flow: builds a tar stream from sample metadata, produces tar-split data, compresses it, writes a zstd:chunked manifest with annotations, parses annotation offsets, serves the manifest/tar-split frames through a mock seekable source, calls `readZstdChunkedManifest`, and compares decoded TOC JSON. The tar type test checks both chunked `typeToTarType` and minimal `GetType`.

State and persistence: all data is in buffers except temporary directory passed to manifest reader.

Dependencies and integration points: connects `minimal.WriteZstdChunkedManifest`, `toc.GetTOCDigest`, zstd compression, tar-split, and manifest reader code outside the selected files.

Risks: sample metadata is small and does not cover chunk arrays, zeros chunks, xattrs, or large tar-split frames. The mock requires exactly two range requests, so it tests one expected read shape.

Test signals: good end-to-end signal for annotation offset math and TOC digest round-trip. Local execution unavailable because `go` is missing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/zstdchunked_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/config/config.go -->
## sources/cloud-native/containers-storage/pkg/config/config.go

Purpose: storage option TOML structs and graph-driver option flattening.

Important APIs/types/functions: `AufsOptionsConfig`, `BtrfsOptionsConfig`, `OverlayOptionsConfig`, `VfsOptionsConfig`, `ZfsOptionsConfig`, `OptionsConfig`, and `GetGraphDriverOptions`.

Control flow: `GetGraphDriverOptions` switches on driver name and emits `driver.key=value` strings. Driver-specific nested fields generally override legacy/common top-level fields; unknown drivers return no options.

State and persistence: no persistence; struct tags map config file TOML into memory.

Dependencies and integration points: used by storage configuration parsing to pass driver options for aufs, btrfs, overlay/overlay2, vfs, and zfs. `ForceMask` mixes top-level `os.FileMode` with overlay-specific string option.

Risks: option precedence is manual and can drift as config fields change. `ForceMask` formatting with `%s` on `os.FileMode` relies on its `String` method, which may not produce an octal-like config value. Boolean-like options are strings in many places, so validation must happen downstream.

Test signals: `config_test.go` covers precedence and emitted substrings for all supported switch cases. Local execution blocked by missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/config/config_test.go -->
## sources/cloud-native/containers-storage/pkg/config/config_test.go

Purpose: tests graph-driver option emission and precedence.

Important APIs/types/functions: `searchOptions`, `TestAufsOptions`, `TestBtrfsOptions`, `TestOverlayOptions`, `TestVfsOptions`, and `TestZfsOptions`.

Control flow: creates `OptionsConfig` values with top-level and driver-specific fields, calls `GetGraphDriverOptions`, and searches output strings for expected fragments.

State and persistence: pure in-memory tests.

Dependencies and integration points: validates config-to-driver option handoff for storage drivers.

Risks: assertions use substring matching and sometimes only check non-empty output, so exact key/value formatting and ordering are only partially constrained. Some failure messages have stale wording.

Test signals: broad option precedence coverage; no validation of TOML decoding. Local tests could not run because `go` is not installed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/directory/directory.go -->
## sources/cloud-native/containers-storage/pkg/directory/directory.go

Purpose: platform-neutral directory utilities shared by OS-specific usage implementations.

Important APIs/types/functions: `DiskUsage` and `MoveToSubdir`.

Control flow: `MoveToSubdir` lists entries in `oldpath` and renames every entry except the target subdirectory into `oldpath/subdir/<name>`.

State and persistence: mutates directory layout via `os.Rename`. Does not create the subdir itself; caller must ensure it exists.

Dependencies and integration points: paired with `Usage`/`Size` implementations in OS-specific files. Used for store layout migrations.

Risks: rename can fail across filesystems or if destination entries exist. There is no rollback, so partial migrations can occur.

Test signals: `directory_test.go` covers moving four files into an existing subdirectory and usage accounting. Local execution unavailable due to missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/directory/directory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/directory/directory_test.go -->
## sources/cloud-native/containers-storage/pkg/directory/directory_test.go

Purpose: validates directory usage accounting and `MoveToSubdir`.

Important APIs/types/functions: tests for empty/nonempty files and directories, nested directory accounting, migration into subdir, non-existing directory errors, and `expectSizeAndInodeCount`.

Control flow: creates temporary directory trees, writes small files, calls `Usage`, compares expected size and inode count, and verifies renamed entries after `MoveToSubdir`.

State and persistence: uses real temporary files and directories.

Dependencies and integration points: covers Unix and Windows `Usage` contracts at a behavioral level, although expected inode counts depend on the active OS implementation.

Risks: no hard-link test despite Unix implementation deduping by inode. `MoveToSubdir` test does not cover destination collision or partial rename failure.

Test signals: basic filesystem behavior coverage; local execution blocked by absent `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/directory/directory_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/directory/directory_unix.go -->
## sources/cloud-native/containers-storage/pkg/directory/directory_unix.go

Purpose: non-Windows implementation of directory size and inode usage accounting.

Important APIs/types/functions: `Size` and `Usage`.

Control flow: `Usage` walks with `filepath.WalkDir`, ignores disappeared children, errors on missing root, deduplicates visited inode numbers from `syscall.Stat_t`, skips directory sizes, and sums regular/non-directory file sizes. `Size` returns `Usage.Size`.

State and persistence: read-only traversal; no persistent mutation.

Dependencies and integration points: used by storage accounting code and tests. Depends on Unix `Stat_t` being present in `FileInfo.Sys()`.

Risks: inode dedupe uses inode number alone without device ID, which can undercount if a walk crosses devices with overlapping inode numbers. Directory sizes are ignored intentionally. Concurrent deletion is tolerated for children but not root.

Test signals: directory tests cover basic size/count cases but not hard links or cross-device walks. Local execution unavailable because `go` is missing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/directory/directory_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/directory/directory_windows.go -->
## sources/cloud-native/containers-storage/pkg/directory/directory_windows.go

Purpose: Windows implementation of directory usage accounting.

Important APIs/types/functions: `Size` and `Usage`.

Control flow: `Usage` walks the tree, increments inode count for every entry, skips directory sizes, sums file sizes, ignores disappeared children, and errors on missing root. `Size` calls `Usage` but returns `0, nil` on error.

State and persistence: read-only traversal.

Dependencies and integration points: fulfills package API for Windows builds.

Risks: `Size` suppresses errors from `Usage`, unlike Unix; this may hide missing or inaccessible paths. Inode count is really entry count, not unique inode count.

Test signals: shared directory tests exercise behavior when run on Windows, but no Windows-specific error suppression test is selected.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/directory/directory_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/dmesg/dmesg_linux.go -->
## sources/cloud-native/containers-storage/pkg/dmesg/dmesg_linux.go

Purpose: Linux helper to read recent kernel log messages.

Important APIs/types/functions: `Dmesg(size int) []byte`.

Control flow: allocates a byte slice of requested size and calls `SYS_SYSLOG` with action `3` (`SYSLOG_ACTION_READ_ALL`), returning bytes read or an empty slice on syscall error.

State and persistence: read-only kernel log access; no package state.

Dependencies and integration points: useful for diagnostics in storage/kernel error paths. Depends on `golang.org/x/sys/unix` and unsafe pointer syscall usage.

Risks: calling with `size == 0` would take `&b[0]` and panic; permissions or kernel restrictions often make syslog reads fail, returning empty bytes without error detail.

Test signals: `dmesg_linux_test.go` only logs output and has no assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/dmesg/dmesg_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/dmesg/dmesg_linux_test.go -->
## sources/cloud-native/containers-storage/pkg/dmesg/dmesg_linux_test.go

Purpose: smoke test for the Linux dmesg helper.

Important APIs/types/functions: `TestDmesg`.

Control flow: calls `Dmesg(512)` and logs the returned bytes as a string.

State and persistence: read-only kernel log access through the function under test.

Dependencies and integration points: minimal diagnostic coverage for `dmesg_linux.go`.

Risks: no assertions means permission failures, empty output, or unexpected content do not fail the test. It does not cover the zero-size panic risk.

Test signals: weak smoke signal only; local execution blocked by missing Go toolchain.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/dmesg/dmesg_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/exists_freebsd.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/exists_freebsd.go

Purpose: FreeBSD-specific fast existence checks.

Important APIs/types/functions: `Exists` and `Lexists`.

Control flow: `Exists` uses `unix.Faccessat` with follow behavior. `Lexists` uses `AT_SYMLINK_NOFOLLOW`, and falls back to `os.Lstat` on `EINVAL` for older FreeBSD kernels lacking that flag.

State and persistence: read-only filesystem checks.

Dependencies and integration points: used by generic file utilities and idtools directory creation. Errors are wrapped as `os.PathError` except the Lstat fallback.

Risks: FreeBSD fallback returns raw `os.Lstat` errors, so error shape differs from faccessat path. Access checks use `F_OK` only, not permissions.

Test signals: shared `exists_test.go` compares behavior against `os.Stat`/`os.Lstat` when run on FreeBSD.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/exists_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/exists_test.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/exists_test.go

Purpose: behavioral tests and benchmarks for `Exists` and `Lexists`.

Important APIs/types/functions: `TestExist`, `BenchmarkExists`, and `BenchmarkStat`.

Control flow: creates a temp directory, working symlink, and dangling symlink; compares `Exists` with `os.Stat` and `Lexists` with `os.Lstat`, including error type and Linux errno equality. Benchmarks compare faccess-based helpers with stat calls.

State and persistence: creates temporary symlinks and directories.

Dependencies and integration points: validates platform-specific existence helpers that are used by file utilities and idtools.

Risks: symlink creation may not be available or permitted on some platforms. One assertion compares `pathErr1.Path` to itself, so it does not actually validate path equality between errors.

Test signals: good coverage for follow versus no-follow semantics; local execution blocked by missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/exists_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/exists_unix.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/exists_unix.go

Purpose: Unix non-Windows, non-FreeBSD fast existence checks.

Important APIs/types/functions: `Exists` and `Lexists`.

Control flow: calls `unix.Faccessat(AT_FDCWD, path, F_OK, AT_EACCESS)` for follow mode and adds `AT_SYMLINK_NOFOLLOW` for link-object checks. Errors are wrapped as `os.PathError`.

State and persistence: read-only.

Dependencies and integration points: used throughout packages that need existence checks without full stat overhead.

Risks: `AT_EACCESS` checks using effective IDs; behavior may differ from `os.Stat` in unusual permission situations. Not used on FreeBSD because of compatibility handling.

Test signals: shared tests compare against `os.Stat`/`os.Lstat` and benchmarks evaluate performance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/exists_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/exists_windows.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/exists_windows.go

Purpose: Windows implementation of existence checks.

Important APIs/types/functions: `Exists` and `Lexists`.

Control flow: wraps `os.Stat` for follow behavior and `os.Lstat` for no-follow behavior.

State and persistence: read-only.

Dependencies and integration points: keeps fileutils API portable.

Risks: Windows symlink semantics and permission requirements differ from Unix; no fast faccess equivalent is used.

Test signals: shared tests apply when symlink support is available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/exists_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/fileutils.go

Purpose: file utility package for ignore-style pattern matching, file copying, symlink canonicalization, and create-if-missing helpers.

Important APIs/types/functions: `PatternMatcher`, `NewPatternMatcher`, `Matches`, `MatchesResult`, `IsMatch`, `Pattern`, `Pattern.compile`, package-level `Matches`, `CopyFile`, `ReadSymlinkedDirectory`, `ReadSymlinkedPath`, and `CreateIfNotExists`.

Control flow: patterns are trimmed, cleaned, marked as exclusions on `!`, syntax-checked with `filepath.Match`, lazily compiled to regex with special `**` handling, and evaluated in order where later matches override earlier state. Copying cleans paths, no-ops on identical clean path, removes existing destination, creates new destination, and streams bytes. Symlink readers resolve absolute paths through `EvalSymlinks`; directory variant rejects non-directories. `CreateIfNotExists` creates dirs recursively or parent dirs plus a file.

State and persistence: pattern regexes are cached in `Pattern.regexp` and are not concurrency-safe. `CopyFile` and `CreateIfNotExists` mutate the filesystem; symlink functions read filesystem metadata.

Dependencies and integration points: used by idtools and broader storage code for pattern exclusion and basic file operations. Depends on `logrus` for debug messages.

Risks: matcher methods are documented non-concurrent because lazy regex caching mutates patterns. `CreateIfNotExists` silently returns nil for non-NotExist errors from `Exists`, which can hide permission errors. Copy removes destination before ensuring creation succeeds.

Test signals: `fileutils_test.go` has extensive pattern matrix coverage plus copy, symlink-directory, and create-if-missing tests. Local execution blocked by missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_darwin.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_darwin.go

Purpose: Darwin implementation of process file-descriptor count.

Important APIs/types/functions: `GetTotalUsedFds`.

Control flow: resolves current PID, runs `lsof -p <pid>`, trims output, splits by lines, and subtracts one header line.

State and persistence: spawns an external process and reads its output; no persistent mutation.

Dependencies and integration points: diagnostic helper for resource usage on macOS.

Risks: requires `lsof` in PATH; failure returns `-1`. Line-counting assumes standard `lsof` output with one header.

Test signals: no direct selected tests for this platform-specific implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_solaris.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_solaris.go

Purpose: Solaris placeholder for process file-descriptor count.

Important APIs/types/functions: `GetTotalUsedFds`.

Control flow: always returns `-1`.

State and persistence: none.

Dependencies and integration points: keeps package portable where implementation is unsupported.

Risks: callers must treat `-1` as unsupported/unknown.

Test signals: no direct selected tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_solaris.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_test.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_test.go

Purpose: comprehensive tests for copy helpers, symlink resolution, create-if-missing, and Docker/gitignore-like pattern matching.

Important APIs/types/functions: tests for `CopyFile`, `ReadSymlinkedDirectory`, `Matches`, `NewPatternMatcher`, `MatchesResult`, `CreateIfNotExists`, and helper tables `matchesTestCase`/`matchTests`.

Control flow: uses temp files for copy/create cases, fixed `/tmp` paths for symlink directory tests, and large table-driven pattern matrices for `*`, `**`, character classes, exclusions, malformed patterns, match counts, and platform-specific escaping.

State and persistence: creates and removes files, directories, and symlinks. Some symlink tests use hard-coded `/tmp` names rather than `t.TempDir`.

Dependencies and integration points: validates behavior needed by ignore/exclusion consumers and file operations in storage utilities.

Risks: hard-coded `/tmp` paths can collide with parallel runs or pre-existing files. Pattern tests rely on filepath behavior that differs on Windows and conditionally skip escape cases.

Test signals: strong for pattern semantics and basic copy/create helpers; no direct tests for `ReadSymlinkedPath`. Local execution unavailable because `go` is missing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_unix.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_unix.go

Purpose: Linux/FreeBSD implementation of process file-descriptor count.

Important APIs/types/functions: `GetTotalUsedFds`.

Control flow: reads `/proc/<pid>/fd` and returns the number of directory entries; logs and returns `-1` on failure.

State and persistence: read-only `/proc` inspection.

Dependencies and integration points: diagnostics/resource tracking helper. Depends on procfs availability even on FreeBSD build tag.

Risks: environments without procfs return `-1`; logging an error on unsupported procfs may be noisy.

Test signals: no direct selected tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_windows.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_windows.go

Purpose: Windows placeholder for process file-descriptor count.

Important APIs/types/functions: `GetTotalUsedFds`.

Control flow: always returns `-1`.

State and persistence: none.

Dependencies and integration points: portable API stub.

Risks: callers must handle unsupported value.

Test signals: no direct selected tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/fileutils_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/reflink_linux.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/reflink_linux.go

Purpose: Linux helper to clone file contents with CoW reflink when possible, falling back to byte copy.

Important APIs/types/functions: `ReflinkOrCopy`.

Control flow: calls `unix.IoctlFileClone(dst, src)`; on success returns nil, otherwise runs `io.Copy(dst, src)` and returns copy error.

State and persistence: mutates destination file contents/extent references.

Dependencies and integration points: used where fast copy or CoW clone is beneficial. Depends on Linux clone ioctl support and current file offsets.

Risks: fallback starts copying from the current source offset and destination offset; callers must position files correctly. It ignores the reflink error cause by design.

Test signals: no direct selected tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/reflink_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/reflink_unsupported.go -->
## sources/cloud-native/containers-storage/pkg/fileutils/reflink_unsupported.go

Purpose: non-Linux fallback for reflink-or-copy.

Important APIs/types/functions: `ReflinkOrCopy`.

Control flow: directly calls `io.Copy(dst, src)`.

State and persistence: writes destination file contents.

Dependencies and integration points: portable implementation for platforms without Linux file clone ioctl.

Risks: same offset assumptions as Linux fallback; no CoW optimization.

Test signals: no direct selected tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fileutils/reflink_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fsutils/fsutils_linux.go -->
## sources/cloud-native/containers-storage/pkg/fsutils/fsutils_linux.go

Purpose: Linux filesystem feature detection for directory entry `d_type` support.

Important APIs/types/functions: `SupportsDType`, `locateDummyIfEmpty`, and `iterateReadDir`.

Control flow: if target directory is empty, creates a temporary dummy file so at least one dirent is visited. It reads raw dirents with `unix.ReadDirent`, stops early on `DT_UNKNOWN`, and reports whether all visited entries exposed known type values.

State and persistence: may create and remove a temporary dummy file in the checked directory.

Dependencies and integration points: used by storage drivers that need reliable d_type support. Depends on unsafe casting of raw dirent buffers.

Risks: requires write permission on empty directories; failure to create dummy file makes feature detection fail. Dirent parsing trusts `Reclen` values from the kernel.

Test signals: no selected tests for this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fsutils/fsutils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fsverity/fsverity_linux.go -->
## sources/cloud-native/containers-storage/pkg/fsverity/fsverity_linux.go

Purpose: Linux fs-verity enablement and digest measurement helpers.

Important APIs/types/functions: `verityDigest`, `EnableVerity`, and `MeasureVerity`.

Control flow: `EnableVerity` issues `FS_IOC_ENABLE_VERITY` with SHA256 and 4096 block size, accepting `EEXIST` as success. `MeasureVerity` issues `FS_IOC_MEASURE_VERITY` into a fixed 64-byte buffer and returns hex digest bytes up to reported size.

State and persistence: enabling verity permanently changes file metadata/state on supporting filesystems; measuring is read-only.

Dependencies and integration points: used by `chunkedDiffer.recordFsVerity`. Depends on Linux ioctls, read-only file descriptors for enablement, and `x/sys/unix` constants.

Risks: kernel/filesystem support varies; digest buffer size is fixed at 64; callers decide whether unsupported errors are fatal. Enablement errors are wrapped with path description.

Test signals: no direct selected tests; behavior is indirectly referenced by chunked storage but not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fsverity/fsverity_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fsverity/fsverity_unsupported.go -->
## sources/cloud-native/containers-storage/pkg/fsverity/fsverity_unsupported.go

Purpose: non-Linux stub for fs-verity helpers.

Important APIs/types/functions: `EnableVerity` and `MeasureVerity`.

Control flow: both return formatted unsupported errors.

State and persistence: none.

Dependencies and integration points: keeps fsverity package importable on unsupported platforms.

Risks: callers must gate or tolerate unsupported errors; required fs-verity mode cannot work off Linux.

Test signals: no direct selected tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/fsverity/fsverity_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/homedir/homedir.go -->
## sources/cloud-native/containers-storage/pkg/homedir/homedir.go

Purpose: cross-platform XDG data/cache home helpers built on platform-specific home directory lookup.

Important APIs/types/functions: `GetDataHome` and `GetCacheHome`.

Control flow: returns `XDG_DATA_HOME`/`XDG_CACHE_HOME` when set, otherwise uses `Get()` and appends `.local/share` or `.cache`; errors if neither env nor home is available.

State and persistence: reads environment only; no directory creation.

Dependencies and integration points: used by storage config/runtime path selection. Depends on platform-specific `Get`.

Risks: does not validate whether env-provided paths are absolute despite XDG expectations. Empty `Get()` causes an error.

Test signals: selected homedir tests only validate `Get` and shortcut string, not data/cache helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/homedir/homedir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/homedir/homedir_test.go -->
## sources/cloud-native/containers-storage/pkg/homedir/homedir_test.go

Purpose: basic tests for platform home directory lookup and shell shortcut string.

Important APIs/types/functions: `TestGet` and `TestGetShortcutString`.

Control flow: calls `Get`, asserts non-empty absolute path, then calls `GetShortcutString` and asserts non-empty string.

State and persistence: reads environment/user lookup only.

Dependencies and integration points: smoke coverage for platform-specific homedir implementations.

Risks: tests do not cover XDG data/cache/config/runtime helpers, sticky runtime behavior, permissions, or symlink resolution.

Test signals: weak smoke signal; local execution blocked by missing Go toolchain.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/homedir/homedir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/homedir/homedir_unix.go -->
## sources/cloud-native/containers-storage/pkg/homedir/homedir_unix.go

Purpose: Unix home, config, runtime directory, and sticky runtime-file helpers.

Important APIs/types/functions: `Key`, `Get`, `GetShortcutString`, `StickRuntimeDirContents`, `stick`, `isWriteableOnlyByOwner`, `GetConfigHome`, and `GetRuntimeDir`.

Control flow: `Get` delegates to `unshare.HomeDir`. `GetConfigHome` is cached with `sync.Once`, uses `XDG_CONFIG_HOME` or resolves `$HOME/.config`, creates it, and verifies ownership. `GetRuntimeDir` uses `XDG_RUNTIME_DIR`, `/run/user/<uid>`, or a temp fallback, requiring owner-only write permissions. `StickRuntimeDirContents` absolute-normalizes paths under runtime dir and chmods sticky bit.

State and persistence: reads env, creates config/runtime directories, chmods files, and caches config/runtime results process-wide.

Dependencies and integration points: rootless storage path selection and runtime file retention. Depends on `unshare`, filesystem ownership from `syscall.Stat_t`, and logrus.

Risks: `sync.Once` caches env-derived paths and errors, so tests or callers changing env after first call will not affect results. Runtime dir prefix check is string-based after `Abs`, not `EvalSymlinks` for each file. Directory creation can fail in restricted environments.

Test signals: selected tests only smoke `Get` and shortcut; no coverage for config/runtime/sticky behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/homedir/homedir_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/homedir/homedir_windows.go -->
## sources/cloud-native/containers-storage/pkg/homedir/homedir_windows.go

Purpose: Windows home/config/runtime directory helpers.

Important APIs/types/functions: `Key`, `Get`, `GetConfigHome`, `GetShortcutString`, `StickRuntimeDirContents`, and `GetRuntimeDir`.

Control flow: uses `USERPROFILE` or `os.UserHomeDir`; config home is `<home>/.config`; sticky operation is a no-op; runtime dir is `<data home>/containers/storage`.

State and persistence: reads environment; does not create directories in this file.

Dependencies and integration points: portable homedir API for Windows storage paths.

Risks: `GetConfigHome` can return `.config` relative to empty home if lookup fails; runtime dir depends on `GetDataHome` and can fail if home lookup fails.

Test signals: shared homedir tests validate non-empty absolute `Get` and shortcut when run on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/homedir/homedir_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idmap/idmapped_utils.go -->
## sources/cloud-native/containers-storage/pkg/idmap/idmapped_utils.go

Purpose: Linux helpers to create ID-mapped bind mounts using another process's user namespace and to spawn a helper user namespace process.

Important APIs/types/functions: `CreateIDMappedMount` and `CreateUsernsProcess`.

Control flow: `CreateIDMappedMount` opens `/proc/<pid>/ns/user`, clones the source mount with `open_tree`, sets `MOUNT_ATTR_IDMAP` with the user namespace fd, creates target directory, then moves the cloned mount to target. `CreateUsernsProcess` calls `clone(CLONE_NEWUSER|SIGCHLD)`, makes the child pause until killed, writes `uid_map` and `gid_map`, and returns pid plus cleanup function.

State and persistence: creates target directories, attaches mounts, spawns/kills a process, and writes `/proc/<pid>/{uid,gid}_map`.

Dependencies and integration points: works with `idtools.IDMap` and storage drivers needing idmapped mounts. Depends on modern Linux mount APIs and architecture-specific clone argument ordering for s390x.

Risks: requires kernel support and sufficient privileges; `gid_map` writes can require setgroups handling in some contexts; cleanup must be called to avoid lingering paused helper process. Partial failures call cleanup after map write errors.

Test signals: no selected tests directly cover idmapped mount creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idmap/idmapped_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idmap/idmapped_utils_unsupported.go -->
## sources/cloud-native/containers-storage/pkg/idmap/idmapped_utils_unsupported.go

Purpose: non-Linux stubs for ID-mapped mount utilities.

Important APIs/types/functions: `CreateIDMappedMount` and `CreateUsernsProcess`.

Control flow: both return unsupported errors; process creation returns `-1, nil, error`.

State and persistence: none.

Dependencies and integration points: portable API surface for packages that import idmap.

Risks: callers must handle unsupported errors or gate by platform/capability.

Test signals: no direct selected tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idmap/idmapped_utils_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools.go -->
## sources/cloud-native/containers-storage/pkg/idtools/idtools.go

Purpose: core UID/GID mapping, subordinate ID parsing, ownership helpers, containers override xattr formatting/parsing, safe chown wrappers, and mapping contiguity checks.

Important APIs/types/functions: `IDMap`, `IDPair`, `IDMappings`, `MkdirAllAs`, `MkdirAs`, `MkdirAllAndChown`, `MkdirAndChown`, `MkdirAllAndChownNew`, `GetRootUIDGID`, `RawToContainer`, `RawToHost`, `NewIDMappings`, `NewIDMappingsFromMaps`, `RootPair`, `ToHost`, `ToHostOverflow`, `ToContainer`, `parseSubidFile`, `FormatContainersOverrideXattrDevice`, `GetContainersOverrideXattr`, `parseOverrideXattr`, `SetContainersOverrideXattr`, `SafeChown`, `SafeLchown`, and `IsContiguous`.

Control flow: mapping functions linearly find containing ranges. `NewIDMappings` reads subordinate ranges and sorts them into contiguous container ID maps. Overflow mapping substitutes kernel overflow UID/GID if a target cannot map. Override xattrs encode uid/gid/mode/type/device as colon-separated text and parse it back. Darwin safe chown stores requested metadata in `user.containers.override_stat` before chowning to current user/group; other platforms avoid no-op chown and wrap EINVAL with subuid/subgid guidance.

State and persistence: reads `/etc/subuid`, `/etc/subgid`, `/proc/sys/kernel/overflow{uid,gid}`; caches overflow IDs; mutates ownership and xattrs through `SafeChown`, `SafeLchown`, and xattr setters.

Dependencies and integration points: used across archive extraction, chunked force-mask handling, storage namespace setup, and idmapped mount utilities. Depends on `system` xattr/stat helpers, `os/user`, and platform-specific `readSubuid/readSubgid`.

Risks: range matching is linear and assumes non-overlapping maps; `IsContiguous` sorts the provided slice in place through slice aliases, mutating caller order. Subid parsing treats malformed matching files as fatal. Darwin xattr override behavior differs substantially from Linux ownership semantics.

Test signals: `idtools_test.go` covers mapping, overflow, root pair detection, contiguity, override xattr parse/format, and device parsing. Unix tests cover mkdir/chown behavior and subid parsing. Local execution blocked by missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_supported.go -->
## sources/cloud-native/containers-storage/pkg/idtools/idtools_supported.go

Purpose: optional Linux+cgo+libsubid backend for subordinate ID lookup.

Important APIs/types/functions: `readSubid`, `readSubuid`, `readSubgid`, and `onceInit`.

Control flow: rejects username `ALL`, optionally resolves username to numeric UID string, initializes libsubid once, calls UID or GID range lookup by name then numeric UID fallback, converts C ranges to Go `ranges`, and frees C allocations.

State and persistence: initializes libsubid process state and reads system subordinate ID databases through the library.

Dependencies and integration points: selected by build tags `linux && cgo && libsubid`; replaces file parser backend in `idtools_unsupported.go`.

Risks: C string from `C.CString("storage")` passed to `subid_init` is not freed in the visible code; ABI compatibility handled with preprocessor aliases but still depends on libsubid availability. `ALL` is unsupported here, which affects helpers that scan all ranges.

Test signals: no selected tests target libsubid backend specifically.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_supported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_test.go -->
## sources/cloud-native/containers-storage/pkg/idtools/idtools_test.go

Purpose: unit tests for core ID mapping and override-xattr formatting/parsing.

Important APIs/types/functions: `TestToHost`, `TestToHostOverflow`, `TestGetRootUIDGID`, `TestIsContiguous`, `TestParseOverrideXattr`, `TestFormatContainersOverrideXattrDevice`, and `TestParseDevice`.

Control flow: constructs in-memory maps, verifies translation and overflow IDs, tests root ID extraction error cases, checks contiguous and non-contiguous maps, parses xattr strings into `Stat`, formats many mode/type/device combinations, and validates device parser error handling.

State and persistence: mostly pure; overflow tests may read cached `/proc/sys/kernel/overflow*` through code under test.

Dependencies and integration points: covers behavior used by archive/chunked force-mask and namespace remapping.

Risks: no tests for `SafeChown`, xattr system calls, `NewIDMappings`, or malformed subid files here. `IsContiguous` mutation of input order is not asserted.

Test signals: strong pure-function coverage; local execution unavailable because `go` is missing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_unix.go -->
## sources/cloud-native/containers-storage/pkg/idtools/idtools_unix.go

Purpose: Unix implementation of directory creation with ownership, access checks, passwd/group lookup with getent fallback, and command execution helpers.

Important APIs/types/functions: `mkdirAs`, `CanAccess`, `accessible`, `LookupUser`, `LookupUID`, `LookupGroup`, `LookupGID`, `getentUser`, `getentGroup`, `callGetent`, and package globals `entOnce/getentCmd`.

Control flow: `mkdirAs` identifies missing path components, requires absolute paths for recursive creation, creates directories, and chowns only required components depending on `chownExisting`. Lookup functions first use moby/sys/user local file lookup, then call `getent` if available, parsing passwd/group output and mapping exit codes to user-facing errors.

State and persistence: creates directories and changes ownership. Caches resolved `getent` path with `sync.Once`. Spawns external `getent` process.

Dependencies and integration points: backs public mkdir/chown helpers in `idtools.go` and user/group lookups in storage setup. Depends on `fileutils.Exists`, `system.Stat`, `moby/sys/user`, and `utils_unix.go` command helpers.

Risks: `callGetent` returns `fmt.Errorf("")` when no getent exists, an unhelpful empty error. `mkdirAs` only records missing ancestors before creation; concurrent filesystem changes can alter chown behavior. Absolute path requirement applies only to recursive creation.

Test signals: `idtools_unix_test.go` covers mkdir ownership behavior and relative path rejection; no selected tests for getent fallback or access checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_unix_test.go -->
## sources/cloud-native/containers-storage/pkg/idtools/idtools_unix_test.go

Purpose: Unix tests for mkdir-and-chown helpers and subid parser comment/blank-line handling.

Important APIs/types/functions: `TestMkdirAllAs`, `TestMkdirAllAndChownNew`, `TestMkdirAs`, `TestParseSubidFileWithNewlinesAndComments`, plus helpers `buildTree`, `readTree`, and `compareTrees`.

Control flow: builds temporary directory trees with specified ownership, calls public mkdir helpers, reads ownership recursively with `unix.Stat`, and compares expected maps. The parser test writes a synthetic subuid file with comments/blank lines and verifies only the requested range is returned.

State and persistence: creates temp trees and performs real `os.Chown`, which may require privileges or be affected by user namespace mappings.

Dependencies and integration points: validates `mkdirAs` behavior used by storage directory creation.

Risks: ownership tests can be environment-sensitive in rootless or restricted CI. No tests for group/user lookup fallback.

Test signals: strong for ownership semantics; local execution unavailable because `go` is missing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_unsupported.go -->
## sources/cloud-native/containers-storage/pkg/idtools/idtools_unsupported.go

Purpose: default subordinate ID backend when libsubid-specific backend is not selected.

Important APIs/types/functions: `readSubuid` and `readSubgid`.

Control flow: delegates to `parseSubidFile` for `/etc/subuid` and `/etc/subgid`.

State and persistence: reads system files only.

Dependencies and integration points: active for most non-`linux+cgo+libsubid` builds, including Linux without libsubid. Used by `NewIDMappings` and user range helpers.

Risks: depends on direct file readability and parser behavior; no NSS/libsubid integration in this path.

Test signals: `idtools_unix_test.go` covers `parseSubidFile` with a synthetic file, not the hard-coded system file paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_windows.go -->
## sources/cloud-native/containers-storage/pkg/idtools/idtools_windows.go

Purpose: Windows implementations for ownership-related helpers where UID/GID semantics are unsupported.

Important APIs/types/functions: `mkdirAs` and `CanAccess`.

Control flow: `mkdirAs` ignores ownership arguments and calls `os.MkdirAll`; `CanAccess` always returns true.

State and persistence: may create directories; no ownership changes.

Dependencies and integration points: enables public idtools APIs to compile on Windows.

Risks: behavior is intentionally semantic mismatch with Unix; callers relying on ownership/access enforcement must gate platform behavior.

Test signals: no selected Windows-specific tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/idtools_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/parser.go -->
## sources/cloud-native/containers-storage/pkg/idtools/parser.go

Purpose: parses CLI/config ID map triplets into `IDMap` slices.

Important APIs/types/functions: `parseTriple` and `ParseIDMap`.

Control flow: each non-empty map spec is split on `:`, must contain a multiple of three fields, each triple parses as uint32 container ID, host ID, and size, then converts to int with an extra guard on 32-bit builds.

State and persistence: pure parsing; no filesystem or global state.

Dependencies and integration points: used where user-provided uidmap/gidmap strings configure namespace mappings.

Risks: all parse failures collapse to the same standard malformed error, so details are hidden. Multiple triplets can be packed into one string, which callers must understand. Does not validate overlap or zero size.

Test signals: `parser_test.go` covers valid maps, malformed numbers, oversized values, and wrong field counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/parser_test.go -->
## sources/cloud-native/containers-storage/pkg/idtools/parser_test.go

Purpose: tests ID map string parsing for Unix builds.

Important APIs/types/functions: `TestParseIDMap`.

Control flow: table-driven cases call `ParseIDMap` with valid triplets, multiple entries, malformed fields, oversized values, and wrong colon structure, asserting error presence.

State and persistence: pure in-memory tests.

Dependencies and integration points: protects CLI/config parsing for ID mappings.

Risks: does not assert exact returned `IDMap` values for success cases, only absence of error. Does not cover packed multi-triplet single strings or zero-size mappings.

Test signals: basic validation signal; local execution blocked by missing `go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/usergroupadd_linux.go -->
## sources/cloud-native/containers-storage/pkg/idtools/usergroupadd_linux.go

Purpose: Linux helper to create a system user/group and subordinate UID/GID ranges for namespace remapping.

Important APIs/types/functions: `AddNamespaceRangesUser`, `addUser`, `createSubordinateRanges`, `findNextUIDRange`, `findNextGIDRange`, `findNextRangeStart`, and `wouldOverlap`.

Control flow: chooses `adduser` or `useradd` once, creates the user, runs `id` and parses UID/GID, checks whether subuid/subgid ranges already exist, finds the next non-overlapping range starting at 100000, and uses `usermod -v/-w` to add ranges.

State and persistence: mutates host user/group databases and subordinate ID files through system commands; caches selected user creation command.

Dependencies and integration points: supports automatic namespace user setup. Depends on external commands, delayed regexp, and subordinate range readers.

Risks: highly host-distribution dependent and requires privileges. `wouldOverlap` treats range endpoints inclusively and may be conservative/off by one around adjacent ranges. No locking around subuid/subgid allocation, so concurrent invocations can race.

Test signals: no selected tests directly exercise user creation or range allocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/usergroupadd_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/usergroupadd_unsupported.go -->
## sources/cloud-native/containers-storage/pkg/idtools/usergroupadd_unsupported.go

Purpose: non-Linux stub for namespace range user creation.

Important APIs/types/functions: `AddNamespaceRangesUser`.

Control flow: returns `-1, -1` and an unsupported error.

State and persistence: none.

Dependencies and integration points: portable API stub for non-Linux builds.

Risks: callers must handle unsupported platforms.

Test signals: no direct selected tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/usergroupadd_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/utils_unix.go -->
## sources/cloud-native/containers-storage/pkg/idtools/utils_unix.go

Purpose: Unix command lookup and execution helpers for idtools.

Important APIs/types/functions: `resolveBinary` and `execCmd`.

Control flow: `resolveBinary` uses `exec.LookPath`, resolves symlinks, and only accepts a binary whose resolved basename matches the requested name. `execCmd` splits an argument string on spaces and runs the command with combined stdout/stderr output.

State and persistence: spawns external commands; no persistent mutation by itself.

Dependencies and integration points: used by getent fallback and user/group creation.

Risks: `strings.Split(args, " ")` cannot represent quoted arguments or embedded spaces. Symlink basename enforcement rejects wrapper symlinks with different final names.

Test signals: no selected direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/idtools/utils_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/buffer.go -->
## sources/cloud-native/containers-storage/pkg/ioutils/buffer.go

Purpose: small fixed-capacity buffer used internally by `BytesPipe`.

Important APIs/types/functions: `errBufferFull`, `fixedBuffer`, `Write`, `Read`, `Len`, `Cap`, `Reset`, and `String`.

Control flow: writes copy into `buf[pos:cap(buf)]` without extending length, advances `pos`, and returns `errBufferFull` when capacity is exhausted. Reads copy unread bytes from `lastRead:pos`, advances `lastRead`, and never returns EOF. Reset zeroes positions and shrinks slice length to zero.

State and persistence: in-memory mutable positions and backing slice only.

Dependencies and integration points: buffer pooling in `bytespipe.go` relies on capacity and reset behavior.

Risks: because slice length remains zero while data is written into capacity, direct use of `buf` requires slicing by capacity/positions; this is intentional but non-idiomatic. `Read` returns `0, nil` at exhaustion.

Test signals: `buffer_test.go` covers capacity, length after reads, string of unread data, full writes, and reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/buffer_test.go -->
## sources/cloud-native/containers-storage/pkg/ioutils/buffer_test.go

Purpose: unit tests for `fixedBuffer`.

Important APIs/types/functions: `TestFixedBufferCap`, `TestFixedBufferLen`, `TestFixedBufferString`, `TestFixedBufferWrite`, and `TestFixedBufferRead`.

Control flow: constructs buffers with fixed capacity, writes/reads known byte sequences, checks capacity/length/string behavior, and validates `errBufferFull` when capacity is exhausted.

State and persistence: in-memory only.

Dependencies and integration points: protects assumptions used by `BytesPipe` buffer pooling and flow control.

Risks: tests do not cover `io.ErrShortWrite` branch or direct reset reuse from pools.

Test signals: solid coverage for normal internal buffer behavior; local execution blocked by missing Go toolchain.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/buffer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/bytespipe.go -->
## sources/cloud-native/containers-storage/pkg/ioutils/bytespipe.go

Purpose: dynamically buffered in-memory `io.ReadWriteCloser` pipe with reusable fixed-size buffer slices and backpressure.

Important APIs/types/functions: constants `maxCap`, `minCap`, `blockThreshold`; `ErrClosed`; global `bufPools`; `BytesPipe`; `NewBytesPipe`; `Write`; `CloseWithError`; `Close`; `Read`; `returnBuffer`; and `getBuffer`.

Control flow: writes append to the last fixed buffer, allocate geometrically larger buffers up to `maxCap`, and block while total buffered bytes exceed `blockThreshold`. Reads wait for data or close error, drain buffers in order, return empty buffers to size-specific sync pools, and broadcast waiters. Close sets `closeErr` to supplied error or EOF and wakes readers/writers.

State and persistence: in-memory synchronized queue, condition variable, close state, total buffered length, and process-global sync.Pool map keyed by capacity.

Dependencies and integration points: used where producer/consumer byte streaming needs elastic buffering without retaining peak allocations permanently.

Risks: `Read` uses a single `Cond.Wait` instead of a loop before checking close/data, so spurious wakeups could return `0, nil`. Writers blocked on threshold wake on reads or close. Global pools are guarded for map access but pooled buffers retain allocated memory by size class.

Test signals: `bytespipe_test.go` exists outside the required output list and covers reads, writes, random chunks, and benchmarks. Local package tests could not run because `go` is unavailable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/ioutils/bytespipe.go -->
