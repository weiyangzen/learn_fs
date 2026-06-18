# subset-b-009161 Research

Grouped research for restic include filtering, backup filesystem abstraction, platform filesystem metadata, Windows VSS/security handling, and FUSE file/directory nodes.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/include.go -->
# sources/sync-backup/restic/internal/filter/include.go

Purpose: Defines include-pattern configuration and match functions used by restore/filter flows. `IncludePatternOptions` wires CLI flags for case-sensitive and case-insensitive include patterns and include-file variants.

Important APIs: `IncludeByNameFunc`, `IncludePatternOptions.Add`, `Empty`, `CollectPatterns`, `IncludeByPattern`, and `IncludeByInsensitivePattern`. `CollectPatterns` reads pattern files, validates all user patterns with `ValidatePatterns`, and returns an ordered slice of matchers.

Control flow and state: Pattern state is transient and held in slices on the options struct. File-backed patterns are appended into the same in-memory include slices. `IncludeByPattern` parses once, then calls `ListWithChild` per path and returns both direct match and child-may-match. The insensitive path lowercases both patterns and candidate names.

Dependencies and integration: Depends on local filter helpers (`readPatternsFromFiles`, `ValidatePatterns`, `ParsePatterns`, `ListWithChild`), `pflag`, and restic errors. Restore code can combine returned `IncludeByNameFunc` values to prune traversal.

Risks: `warnf` is called unconditionally on `ListWithChild` errors; callers should pass a non-nil warning function. Case-insensitive matching uses Unicode/language-agnostic `strings.ToLower`, which is simple but not locale-aware. Pattern ordering appends insensitive matchers before sensitive matchers.

Test signals: `include_test.go` covers direct glob matches and case-insensitive matching for extensions and `README.md`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/include.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/include_test.go -->
# sources/sync-backup/restic/internal/filter/include_test.go

Purpose: Unit tests for include matcher behavior.

Important APIs: `TestIncludeByPattern` and `TestIncludeByInsensitivePattern` instantiate match functions from patterns `*.go` and `README.md`.

Control flow and state: Each table case builds a fresh include function and verifies only the `matched` result. `childMayMatch` is intentionally ignored here.

Dependencies and integration: Uses Go `testing` and the filter package directly. It validates behavior expected by CLI include options without involving command parsing.

Risks: Does not cover `CollectPatterns`, include-file reading, validation failures, warning callbacks, malformed patterns, or child traversal hints.

Test signals: The file itself is the primary signal: it confirms basename-oriented glob behavior and lowercased matching for uppercase file names.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/filter/include_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/const.go -->
# sources/sync-backup/restic/internal/fs/const.go

Purpose: Re-exports a portable subset of OS open flags through the `fs` package.

Important APIs: Constants `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_APPEND`, `O_CREATE`, `O_EXCL`, `O_SYNC`, `O_TRUNC`, and `O_NONBLOCK`.

Control flow and state: No runtime behavior. Values are copied from `syscall` so callers can depend on `internal/fs` rather than importing platform syscalls directly.

Dependencies and integration: Used by `FS.OpenFile`, local wrappers, reader filesystem tests, and directory read helpers. Platform-specific `const_unix.go` and `const_windows.go` add `O_NOFOLLOW`, `O_DIRECTORY`, and `sanitizeFlags`.

Risks: Constants mirror Go/syscall values; portability depends on build targets exposing equivalent constants.

Test signals: Indirectly tested by local/reader filesystem tests that pass these flags into `OpenFile`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/const.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/const_unix.go -->
# sources/sync-backup/restic/internal/fs/const_unix.go

Purpose: Provides Unix implementations of symlink/directory open flags.

Important APIs: `O_NOFOLLOW`, `O_DIRECTORY`, and `sanitizeFlags`.

Control flow and state: `sanitizeFlags` is identity on non-Windows systems because the package constants are valid OS flags.

Dependencies and integration: Consumed by `OpenFile`, `local.OpenFile`, `Readdirnames`, and tests that verify metadata-only symlink handling and FIFO directory reads.

Risks: Assumes `syscall.O_NOFOLLOW` and `syscall.O_DIRECTORY` are defined for non-Windows build targets selected by this file.

Test signals: `fs_local_test.go`, `fs_local_unix_test.go`, and `file_unix_test.go` exercise these flags through local filesystem operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/const_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/const_windows.go -->
# sources/sync-backup/restic/internal/fs/const_windows.go

Purpose: Provides Windows-safe definitions for flags used by the filesystem abstraction.

Important APIs: Invented internal `O_NOFOLLOW`, no-op `O_DIRECTORY`, and `sanitizeFlags`.

Control flow and state: `sanitizeFlags` removes the package-local `O_NOFOLLOW` bit before passing flags to Go/Windows file APIs. `O_DIRECTORY` is zero because Windows directory access is handled elsewhere.

Dependencies and integration: Lets common code compile and call `OpenFile` with Unix-like flags. Metadata-only handling in `localFile.cacheFI` interprets `O_NOFOLLOW`.

Risks: Comments note Windows `OpenFile` does not fully honor all flags. The invented flag must not leak into external APIs, hence the final sanitization step.

Test signals: Windows local metadata tests rely on symlink-follow decisions; Windows temp file and VSS tests indirectly depend on flag sanitization.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/const_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/doc.go -->
# sources/sync-backup/restic/internal/fs/doc.go

Purpose: Package documentation for `internal/fs`.

Important APIs: Declares package `fs` and describes it as an OS-independent filesystem abstraction suitable for backup.

Control flow and state: None.

Dependencies and integration: The doc anchors a package that wraps local OS files, synthetic reader-backed filesystems, metadata conversion, restore creation, and platform-specific file attributes.

Risks: Documentation is intentionally broad; behavior details live in interfaces and platform files.

Test signals: No direct tests; package-level behavior is heavily covered by `fs_*`, `node_*`, and platform tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/ea_windows.go -->
# sources/sync-backup/restic/internal/fs/ea_windows.go

Purpose: Implements Windows extended attribute encoding/decoding and low-level NT API access.

Important APIs: `extendedAttribute`, `encodeExtendedAttributes`, `decodeExtendedAttributes`, `ntStatus.Err`, `fgetEA`, `fsetEA`, `getFileEA`, `setFileEA`, and `pathSupportsExtendedAttributes`.

Control flow and state: `fgetEA` repeatedly calls `NtQueryEaFile`, doubling the buffer on insufficient-buffer/more-data errors, returning nil for `STATUS_NO_EAS_ON_FILE`. `fsetEA` encodes all attributes and calls `NtSetEaFile`. NTSTATUS values are converted to DOS errors via `RtlNtStatusToDosErrorNoTeb`.

Dependencies and integration: Uses `go-winio` for EA binary layout, `x/sys/windows`, `ntdll.dll`, and unsafe syscalls. Called by Windows node metadata backup/restore in `node_windows.go`.

Risks: Unsafe syscall signatures are architecture-sensitive and tied to Windows NT internals. `fsetEA` indexes `encodedEA[0]`; callers must avoid passing empty encoded buffers. EA support varies by volume and is checked separately.

Test signals: `ea_windows_test.go` covers binary round-trips, no-final-padding decode, truncated decode errors, real file/folder set/get, and volume support detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/ea_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/ea_windows_test.go -->
# sources/sync-backup/restic/internal/fs/ea_windows_test.go

Purpose: Windows-only tests for extended attribute serialization and NT EA operations.

Important APIs: `TestRoundTripEas`, `TestEasDontNeedPaddingAtEnd`, `TestTruncatedEasFailCorrectly`, `TestNilEasEncodeAndDecodeAsNil`, `TestSetFileEa`, `TestSetGetFileEA`, `TestSetGetFolderEA`, and `TestPathSupportsExtendedAttributes`.

Control flow and state: Tests use generated random EA values, temporary files/folders, explicit Windows handles with read/write EA rights, and cleanup helpers that close both Go files and Windows handles.

Dependencies and integration: Validates `ea_windows.go` and the `go-winio` layout against `NtSetEaFile` and `NtQueryEaFile`. Supports higher-level xattr restore tests.

Risks: Assumes the system drive supports EAs and that invalid `Z:` paths fail. Random EA value lengths avoid zero but can make failures less reproducible beyond the generated content.

Test signals: Provides strong Windows-specific confidence for EA binary layout, handle access flags, directory EA handling, and unsupported-path errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/ea_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file.go -->
# sources/sync-backup/restic/internal/fs/file.go

Purpose: Package-level filesystem helpers that wrap standard `os` operations with platform path normalization.

Important APIs: `MkdirAll`, `Remove`, `RemoveAll`, `Link`, `Lstat`, `OpenFile`, `IsAccessDenied`, `ResetPermissions`, and `Readdirnames`.

Control flow and state: Most functions call `fixpath` then `os` equivalents. `Readdirnames` opens a directory through an `FS` with `O_RDONLY|O_DIRECTORY|flags`, reads all names, closes the file, and preserves close/read errors carefully.

Dependencies and integration: Used across restore and backup paths where long Windows paths or VSS paths must be normalized. `ResetPermissions` is used by Windows encryption/attribute restore fallbacks.

Risks: `Readdirnames` must not leak open file handles on read errors. `ResetPermissions` unconditionally applies `0600`, which is a repair step rather than metadata restoration.

Test signals: `file_unix_test.go` checks FIFO directory reads do not block. `fs_local_test.go` and `node_test.go` indirectly exercise wrappers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file_unix.go -->
# sources/sync-backup/restic/internal/fs/file_unix.go

Purpose: Non-Windows path, temporary file, unsupported-feature, and chmod behavior.

Important APIs: `fixpath`, `TempFile`, `isNotSupported`, and `chmod`.

Control flow and state: `fixpath` is identity. `TempFile` creates then unlinks the file so it is removed when closed. `chmod` ignores `ENOTSUP` from filesystems that cannot apply modes.

Dependencies and integration: Used by file wrappers and restore metadata. The unlink-on-open temp file pattern avoids leaving temporary files after close on Unix-like systems.

Risks: `TempFile` depends on Unix delete-while-open semantics. `isNotSupported` only recognizes `*os.PathError` wrapping `syscall.ENOTSUP`.

Test signals: Unix FIFO read tests and generic restore tests exercise these helpers indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file_unix_test.go -->
# sources/sync-backup/restic/internal/fs/file_unix_test.go

Purpose: Unix-only regression test for safe directory reads on FIFOs.

Important APIs: `TestReaddirnamesFifo`.

Control flow and state: Creates a FIFO with `mkfifo`, calls `Readdirnames(NewLocal(), fifo, 0)`, and asserts the error is `ENOTDIR`.

Dependencies and integration: Covers `Readdirnames`, `O_DIRECTORY`, local `OpenFile`, and Unix `mkfifo`.

Risks: Focused on blocking avoidance; it does not test normal directory reads, which are covered elsewhere.

Test signals: Confirms opening a FIFO as a directory fails promptly rather than blocking on FIFO read behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file_windows.go -->
# sources/sync-backup/restic/internal/fs/file_windows.go

Purpose: Windows path normalization, temp file creation, chmod passthrough, attribute clearing, and EA handle opening.

Important APIs: `fixpath`, `TempFile`, `chmod`, `clearSystem`, `clearAttribute`, and `openHandleForEA`.

Control flow and state: `fixpath` converts absolute paths to extended-length `\\?\` or `\\?\UNC\` paths, preserving VSS `GLOBALROOT` paths and appending a slash for bare snapshot volumes. `TempFile` uses `CreateFile` with temporary and delete-on-close flags and retries random suffix collisions. EA handles are opened with `FILE_READ_EA` and optional `FILE_WRITE_EA`.

Dependencies and integration: Used by almost all Windows filesystem operations, including security descriptor restore, EA restore, VSS path access, and long-path support.

Risks: Path-prefix handling must be exact; malformed `GLOBALROOT`, UNC, or volume GUID paths can break backup/restore. `TempFile` uses pseudo-random suffixes and a fixed retry count.

Test signals: `file_windows_test.go`, `node_windows_test.go`, and Windows EA/security tests validate temp deletion, long path/volume handling, and EA handle usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file_windows_test.go -->
# sources/sync-backup/restic/internal/fs/file_windows_test.go

Purpose: Windows-only test for delete-on-close temporary files.

Important APIs: `TestTempFile`.

Control flow and state: Creates two temp files with the same prefix, verifies distinct names and existence while open, closes both, then verifies the paths no longer exist.

Dependencies and integration: Tests `fs.TempFile` from external package perspective (`fs_test`), covering Windows-specific `CreateFile` flags.

Risks: Does not inspect temporary-file attributes directly; behavior is inferred from existence and deletion.

Test signals: Confirms collision avoidance and delete-on-close semantics for simultaneous temp files.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/file_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local.go -->
# sources/sync-backup/restic/internal/fs/fs_local.go

Purpose: Implements the `FS` and `File` interfaces for the host filesystem.

Important APIs: `NewLocal`, methods on `local`, `newLocalFile`, `localFile.MakeReadable`, `Stat`, `ToNode`, `Read`, `Readdirnames`, and `Close`.

Control flow and state: Package init attempts to enable platform privileges. `newLocalFile` either opens the file immediately or returns a metadata-only object. `cacheFI` lazily caches metadata using the open file handle, `Lstat`, or `Stat` depending on follow flags. `MakeReadable` reopens a metadata-only file and resets cached metadata.

Dependencies and integration: Bridges OS files to backup logic via `ExtendedFileInfo` and `nodeFromFileInfo`. Used directly for normal backup/restore and wrapped by `LocalVss` and `Track`.

Risks: Metadata-only mode may be path-based on local filesystems, so race behavior after rename/type changes is implementation-dependent and explicitly tolerated by tests. `Read`/`Readdirnames` assume `MakeReadable` or non-metadata open has supplied `f.f`.

Test signals: `fs_local_test.go` covers metadata, symlink following, file reads, directory reads, race after rename, and type changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local_test.go -->
# sources/sync-backup/restic/internal/fs/fs_local_test.go

Purpose: Cross-platform tests for local `FS` metadata and readable transitions.

Important APIs: `TestFSLocalMetadata`, `TestFSLocalRead`, `TestFSLocalReaddir`, `TestFSLocalReadableRace`, and `TestFSLocalTypeChange`.

Control flow and state: Table-driven setup creates files, directories, symlinks, and symlink targets. Tests open metadata-only and normal files, call `MakeReadable`, compare `ExtendedFileInfo` to `os.Stat`/`os.Lstat`, and convert to `data.Node`.

Dependencies and integration: Validates `NewLocal`, `localFile.cacheFI`, `ToNode`, `O_NOFOLLOW`, and directory reads.

Risks: Race/type-change tests intentionally accept both handle-based and path-based implementations, so they document rather than forbid TOCTOU behavior.

Test signals: Strong coverage for the main local filesystem abstraction used by backup traversal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local_unix_test.go -->
# sources/sync-backup/restic/internal/fs/fs_local_unix_test.go

Purpose: Unix-only extension of local metadata tests for sockets and FIFOs.

Important APIs: `TestFSLocalMetadataUnix`.

Control flow and state: Creates a Unix domain socket by binding a syscall socket and creates a FIFO via `mkfifo`, then reuses `runFSLocalTestcase`.

Dependencies and integration: Exercises `nodeTypeFromFileInfo`, Unix stat extraction, and local metadata-only open for special node types.

Risks: Device nodes are intentionally not tested because they require root.

Test signals: Confirms backup metadata recognizes socket and FIFO node types on Unix.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local_vss.go -->
# sources/sync-backup/restic/internal/fs/fs_local_vss.go

Purpose: Wraps the local filesystem with transparent Windows Volume Shadow Copy Service snapshot access.

Important APIs: `VSSConfig`, `ParseVSSConfig`, `ErrorHandler`, `MessageHandler`, `volumeFilter`, `LocalVss`, `NewLocalVss`, `DeleteSnapshots`, `OpenFile`, `Lstat`, `isMountPointIncluded`, and `snapshotPath`.

Control flow and state: `LocalVss` keeps maps of successful and failed snapshots keyed by lowercased volume, protected by an RW mutex. `snapshotPath` normalizes a path, skips UNC shares, lazily creates one VSS snapshot per volume, tracks excluded volumes/mount points, maps mount-point paths to their own snapshots when available, and falls back to the original path on unsupported or failed snapshot creation.

Dependencies and integration: Delegates real filesystem operations to `NewLocal`; calls VSS functions from `vss_windows.go` or stubs from `vss.go`; uses `options` registration on Windows.

Risks: Snapshot creation is side-effectful and privilege-dependent. Fallback to original paths preserves backup progress but weakens consistency. Mount-point mapping is case-insensitive and relies on correct volume normalization.

Test signals: `fs_local_vss_test.go` covers config parsing, excluded volumes, provider parsing, and admin-only snapshot behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local_vss.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local_vss_test.go -->
# sources/sync-backup/restic/internal/fs/fs_local_vss_test.go

Purpose: Windows-only tests for VSS configuration, provider selection, excluded mount points, and snapshot-backed filesystem access.

Important APIs: `TestVSSConfig`, `TestParseMountPoints`, `TestParseProvider`, and `TestVSSFS`.

Control flow and state: Tests parse `options.Options`, build `LocalVss`, collect error/message callbacks, compare normalized volume GUID maps, resolve providers by alias/GUID/name, and run a live snapshot test when admin privileges are available.

Dependencies and integration: Exercises `ParseVSSConfig`, `parseMountPoints`, `isMountPointIncluded`, `getProviderID`, `HasSufficientPrivilegesForVSS`, `Lstat`, `OpenFile`, and `DeleteSnapshots`.

Risks: Many assertions depend on a Windows machine with `C:` and the Microsoft VSS provider. The live snapshot test is skipped without sufficient privileges.

Test signals: Strong coverage for VSS option semantics and a high-value integration test proving deleted original files can still be read from a snapshot.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_local_vss_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_reader.go -->
# sources/sync-backup/restic/internal/fs/fs_reader.go

Purpose: Implements an in-memory/synthetic `FS` exposing a single reader as a file plus generated parent directories.

Important APIs: `ReaderOptions`, `NewReader`, `reader.OpenFile`, `Lstat`, path helpers, `readerFile`, `ErrFileEmpty`, `fakeFile`, and `fakeDir`.

Control flow and state: `NewReader` normalizes the target path, creates a file item and all ancestor directory items, and records child names. The file reader can be opened once using `sync.Once`; later opens return `EIO`. `readerFile.Read` turns EOF before any bytes into `ErrFileEmpty` unless empty files are allowed.

Dependencies and integration: Used for backup from stdin or command output as a virtual filesystem. Converts synthetic metadata to `data.Node` with current UID/GID.

Risks: Single-open semantics are strict and can surprise callers that retry reads. `fakeDir.Readdirnames(n>0)` is unimplemented. Path handling uses slash-based `path`, not OS-specific separators.

Test signals: `fs_reader_test.go` covers file content, nested directories, stat/lstat, missing paths, single synthetic directory traversal, and empty-reader errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_reader_command.go -->
# sources/sync-backup/restic/internal/fs/fs_reader_command.go

Purpose: Exposes subprocess stdout as an `io.ReadCloser` suitable for `NewReader`.

Important APIs: `commandReader`, `NewCommandReader`, `Read`, `wait`, and `Close`.

Control flow and state: `NewCommandReader` validates args, sets up stdout/stderr pipes, starts a goroutine that forwards stderr lines to a callback, then starts the command. `Read` reads stdout and, on EOF, waits once for command exit so failures are reported even if output was empty. `Close` cancels unfinished commands and waits.

Dependencies and integration: Uses `exec.CommandContext`, restic errors, and caller-provided error-output logging. Intended for backup from command output.

Risks: The stderr scanner goroutine starts before `Start`; pipe behavior depends on `exec`. `alreadyClosedReadErr` caches terminal errors, so callers see consistent post-close behavior. Fatal command errors abort snapshot flows.

Test signals: `fs_reader_command_test.go` covers success, failure exit status, invalid command, empty args, captured stdout, and quick close of a long-running process.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_reader_command.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_reader_command_test.go -->
# sources/sync-backup/restic/internal/fs/fs_reader_command_test.go

Purpose: External-package tests for subprocess-backed readers.

Important APIs: `TestCommandReaderSuccess`, `TestCommandReaderFail`, `TestCommandReaderInvalid`, `TestCommandReaderEmptyArgs`, `TestCommandReaderOutput`, and `TestCommandReaderQuickClose`.

Control flow and state: Tests use simple shell commands (`true`, `false`, `echo`, `sleep`) to verify read, error, and close behavior. Quick close uses a timeout context and expects cancellation.

Dependencies and integration: Tests public `fs.NewCommandReader` behavior from package `fs_test`.

Risks: Assumes Unix-like commands exist in the test environment; less portable to minimal Windows shells.

Test signals: Confirms command exit failures propagate through reads and that closing kills a long-running command without waiting for the full sleep duration.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_reader_command_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_reader_test.go -->
# sources/sync-backup/restic/internal/fs/fs_reader_test.go

Purpose: Unit tests for the synthetic reader filesystem.

Important APIs: Helpers `verifyFileContentOpenFile`, `verifyDirectoryContents`, `checkFileInfo`, `createReadDirTest`, `createFileTest`, `createDirTest`, and tests `TestFSReader`, `TestFSReaderNested`, `TestFSReaderDir`, `TestFSReaderMinFileSize`.

Control flow and state: Each subtest builds a fresh `NewReader` because file content is single-use. Tests compare directory entries, content bytes, missing-path errors, metadata, absolute/relative cleaning, and empty-reader behavior.

Dependencies and integration: Covers `FS` contract compliance for `reader`, `readerFile`, `fakeFile`, and `fakeDir`.

Risks: Does not directly test second-open `EIO`; focuses on normal backup-like access.

Test signals: Good behavioral coverage for stdin/command backup filesystem semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_track.go -->
# sources/sync-backup/restic/internal/fs/fs_track.go

Purpose: Debug wrapper that detects leaked open `File` handles.

Important APIs: `Track.OpenFile`, `trackFile`, `newTrackFile`, and `trackFile.Close`.

Control flow and state: `OpenFile` delegates to an underlying `FS`, captures a stack trace, and wraps the result in a `trackFile` with a finalizer. If garbage collection releases the wrapper before `Close`, the finalizer prints the opening stack and panics. `Close` clears the finalizer and closes the underlying file.

Dependencies and integration: Uses `runtime.SetFinalizer` and `runtime/debug.Stack`. Can wrap any `FS` implementation during tests or debugging.

Risks: Finalizer-based checks are nondeterministic and should not be part of normal runtime behavior. Panic on leaked file is intentional but disruptive.

Test signals: No direct tests in this subset; leaks are observable when wrapper is enabled.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/fs_track.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/interface.go -->
# sources/sync-backup/restic/internal/fs/interface.go

Purpose: Defines the filesystem abstraction used by backup and restore code.

Important APIs: `FS` and `File` interfaces.

Control flow and state: Interfaces specify path operations, `Lstat`, and `OpenFile` behavior. `OpenFile(metadataOnly=true)` must return a `File` for arbitrary file types and may defer real filesystem access. `File.MakeReadable` transitions metadata-only objects to readable mode; `ToNode` must be consistent with `Stat`.

Dependencies and integration: Implemented by `local`, `reader`, `LocalVss`, and wrappers like `Track`. Integrates with `data.Node` as the persisted metadata model.

Risks: The consistency requirement between `Stat` and `ToNode` is central; implementations must avoid returning metadata for different filesystem states. Only `O_NOFOLLOW` and `O_DIRECTORY` are guaranteed flags.

Test signals: Local and reader tests exercise the interface contract across real and synthetic filesystems.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/mknod_unix.go -->
# sources/sync-backup/restic/internal/fs/mknod_unix.go

Purpose: Generic Unix `mknod` implementation for non-FreeBSD, non-Windows platforms.

Important APIs: `mknod`.

Control flow and state: Calls `unix.Mknod(path, mode, int(dev))` and wraps failures as `*os.PathError` with operation `"mknod"`.

Dependencies and integration: Used by `NodeCreateAt` to create block devices, character devices, and FIFOs via `mkfifo`.

Risks: Device creation usually requires elevated privileges. Device number conversion to `int` relies on platform size compatibility.

Test signals: `node_unix_test.go` verifies error wrapping through `mkfifo`; restore tests cover FIFO creation when supported.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/mknod_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node.go -->
# sources/sync-backup/restic/internal/fs/node.go

Purpose: Converts filesystem metadata into `data.Node` values and restores nodes/metadata to disk.

Important APIs: `nodeFromFileInfo`, `buildBasicNode`, `nodeTypeFromFileInfo`, `nodeFillExtendedStat`, username/group lookup caches, `NodeCreateAt`, and `NodeRestoreMetadata`.

Control flow and state: Backup conversion builds a basic node, fills extended stat, generic attributes, and xattrs. Restore creation dispatches by node type to mkdir, file creation, symlink, device, FIFO, or socket no-op. Metadata restore applies ownership, xattrs, generic attributes, timestamps, and finally chmod for non-symlinks.

Dependencies and integration: Central bridge between `ExtendedFileInfo`/OS metadata and restic repository `data.Node`. Platform-specific files supply `lchown`, `utimesNano`, `mknod`, generic attributes, and xattrs.

Risks: Restore order matters, especially on Windows read-only files where chmod/file attributes can block later metadata updates. User/group name lookup caches map missing names to zero/empty values. Non-root Unix permission errors may be ignored by public `NodeRestoreMetadata`.

Test signals: `node_test.go`, `node_unix_test.go`, `node_windows_test.go`, and xattr tests validate conversion, restore, ownership, timestamps, xattrs, and error behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_freebsd.go -->
# sources/sync-backup/restic/internal/fs/node_freebsd.go

Purpose: FreeBSD-specific node helpers.

Important APIs: `nodeRestoreSymlinkTimestamps` and `mknod`.

Control flow and state: Symlink timestamp restore helper is a no-op. `mknod` calls `syscall.Mknod` and wraps errors with `*os.PathError`.

Dependencies and integration: Provides platform hooks used by generic node restore/create code on FreeBSD.

Risks: Symlink timestamp preservation is intentionally unsupported here. Device creation keeps normal privilege constraints.

Test signals: Unix node tests cover mknod-style error wrapping where applicable; generic restore tests account for BSD symlink timestamp limitations.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_linux.go -->
# sources/sync-backup/restic/internal/fs/node_linux.go

Purpose: Linux timestamp restore that does not follow symlinks.

Important APIs: `utimesNano`.

Control flow and state: Converts nanosecond access/modification timestamps into `unix.Timespec` values and calls `unix.UtimesNanoAt` with `AT_SYMLINK_NOFOLLOW`.

Dependencies and integration: Used by `nodeRestoreTimestamps` for all node types on Linux.

Risks: Errors include missing paths and permission failures. Unlike some Unix targets, symlinks are handled rather than skipped.

Test signals: `node_linux_test.go` checks missing symlink timestamp restore returns a not-exist error including the path.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_linux_test.go -->
# sources/sync-backup/restic/internal/fs/node_linux_test.go

Purpose: Linux-specific regression test for symlink timestamp restore errors.

Important APIs: `TestRestoreSymlinkTimestampsError`.

Control flow and state: Creates a symlink-type node, calls `nodeRestoreTimestamps` on a nonexistent path, and asserts `fs.ErrNotExist` plus path context.

Dependencies and integration: Validates `node_linux.go` and the error wrapping from `nodeRestoreTimestamps`.

Risks: Narrow test; successful timestamp preservation is covered indirectly by broader node restore tests.

Test signals: Ensures Linux no-follow timestamp calls surface useful missing-path errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_noxattr.go -->
# sources/sync-backup/restic/internal/fs/node_noxattr.go

Purpose: No-op xattr implementation for platforms without supported xattr handling in this package.

Important APIs: `nodeRestoreExtendedAttributes` and `nodeFillExtendedAttributes`.

Control flow and state: Both functions ignore inputs and return nil.

Dependencies and integration: Selected for AIX, DragonFly, and OpenBSD so generic node conversion/restoration can compile without xattr support.

Risks: Extended attributes are silently omitted on these platforms. This is intentional compatibility behavior but affects metadata fidelity.

Test signals: No direct tests; broader restore tests will see no xattrs on no-xattr platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_noxattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_test.go -->
# sources/sync-backup/restic/internal/fs/node_test.go

Purpose: Cross-platform tests and benchmark for node conversion and metadata restore.

Important APIs: `BenchmarkNodeFromFileInfo`, `nodeTests`, `TestNodeRestoreAt`, `AssertFsTimeEqual`, and `TestNodeRestoreMetadataError`.

Control flow and state: Test nodes cover files, dirs, symlinks, setuid/setgid/sticky modes, repeated existing names, and xattrs. Each node is created, metadata is restored, then read back through `NewLocal().OpenFile(...).ToNode`.

Dependencies and integration: Exercises `NodeCreateAt`, `NodeRestoreMetadata`, xattr filters, timestamp restore, chmod, lchown, and node equality.

Risks: Platform differences are explicitly handled: Windows UID/GID skipped, some sticky-bit and symlink timestamp limitations skipped, macOS resource fork only on Darwin.

Test signals: High-value integration coverage for the backup metadata round-trip.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_unix.go -->
# sources/sync-backup/restic/internal/fs/node_unix.go

Purpose: Unix ownership and generic-attribute hooks.

Important APIs: `lchown`, `nodeRestoreGenericAttributes`, and `nodeFillGenericAttributes`.

Control flow and state: `lchown` chooses numeric UID/GID or resolves names via caches, then calls `os.Lchown`. Generic attribute restore delegates unknown-attribute warnings to `data.HandleAllUnknownGenericAttributesFound`; fill is no-op.

Dependencies and integration: Used by `NodeRestoreMetadata` on non-Windows targets.

Risks: Name-based ownership fallback returns zero for unknown users/groups, which can map to root if called with unresolved names. Unix generic attributes are currently not persisted except unknown-warning handling.

Test signals: `node_unix_test.go` covers ownership by numeric IDs and by names.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_unix_notlinux.go -->
# sources/sync-backup/restic/internal/fs/node_unix_notlinux.go

Purpose: Non-Linux Unix timestamp restore helper.

Important APIs: `utimesNano`.

Control flow and state: Skips symlinks, then calls `syscall.UtimesNano` for other node types using access and modification timestamps.

Dependencies and integration: Used by generic metadata restore on Unix platforms other than Linux.

Risks: Symlink timestamps are not restored on these targets due to Go/platform limitations. It follows normal syscall behavior for permission and filesystem support errors.

Test signals: `node_test.go` has platform-aware timestamp assertions that skip symlink timestamp checks on Darwin/BSD/OpenBSD/NetBSD/Solaris.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_unix_notlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_unix_test.go -->
# sources/sync-backup/restic/internal/fs/node_unix_test.go

Purpose: Unix-only tests for node metadata extraction, mknod error wrapping, and ownership restore.

Important APIs: `TestNodeFromFileInfo`, `TestMknodError`, and `TestLchown`.

Control flow and state: Reads metadata for source files, symlinks, `/dev/null`, and optionally `/dev/sda`; compares stat fields, device IDs, sizes, ownership, and timestamps. Ownership is tested by UID/GID and by user/group name.

Dependencies and integration: Validates `ExtendedStat`, `ToNode`, `mknod`/`mkfifo`, `lchown`, and user/group lookup integration.

Risks: Device-file tests are skipped if paths are unavailable; macOS/Solaris skip `/dev/null` xattr quirks.

Test signals: Strong Unix stat-to-node fidelity coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_windows.go -->
# sources/sync-backup/restic/internal/fs/node_windows.go

Purpose: Windows-specific node metadata, extended attributes, generic attributes, encryption flags, security descriptors, and volume handling.

Important APIs: `mknod`, `lchown`, `utimesNano`, `nodeRestoreExtendedAttributes`, `nodeFillExtendedAttributes`, `restoreExtendedAttributes`, `nodeRestoreGenericAttributes`, `genericAttributesToWindowsAttrs`, `restoreCreationTime`, `restoreFileAttributes`, `fixEncryptionAttribute`, `nodeFillGenericAttributes`, `checkAndStoreEASupport`, `getVolumePathName`, `isVolumePath`, and `prepareVolumeName`.

Control flow and state: Timestamp restore opens paths with backup semantics and open-reparse-point. EA backup skips alternate data streams and non-file/dir nodes, checks per-volume EA support with a `sync.Map`, opens EA handles, and reads/writes all EAs at once. Generic attributes serialize creation time, file attributes, and security descriptors; restore parses them and applies creation time, attributes, and SDs. Encryption toggles call `EncryptFileW`/`DecryptFileW`, temporarily resetting permissions/system flags on access errors.

Dependencies and integration: Uses `data.WindowsAttributes`, `sd_windows.go`, `ea_windows.go`, `file_windows.go`, Windows syscalls, and restic error/debug helpers. This is the main Windows metadata fidelity layer for backup/restore.

Risks: High-risk code due to unsafe syscalls, path normalization, alternate data stream exclusions, case-insensitive EAs, privilege-dependent SD handling, and mutable global EA support cache. Fallbacks can silently skip unsupported volumes.

Test signals: `node_windows_test.go`, `ea_windows_test.go`, `sd_windows_test.go`, and xattr tests cover SD restore, inheritance flags, creation time, file attributes including encryption, EAs, volume-name parsing, and EA support checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_windows_test.go -->
# sources/sync-backup/restic/internal/fs/node_windows_test.go

Purpose: Windows-only integration tests for generic attributes, security descriptors, EAs, and volume path handling.

Important APIs: `TestRestoreSecurityDescriptors`, `TestRestoreSecurityDescriptorInheritance`, `TestRestoreSecurityDescriptorInheritanceLowPrivilege`, `TestRestoreCreationTime`, `TestRestoreFileAttributes`, `TestNewGenericAttributeType`, `TestRestoreExtendedAttributes`, `TestPrepareVolumeName`, and `TestGetVolumePathName`.

Control flow and state: Tests construct `data.Node` values with Windows generic attributes, restore metadata to temporary files/directories, reopen them through `NewLocal`, and compare serialized attributes. Volume tests cover drive paths, UNC/extended UNC, `GLOBALROOT`, volume GUID paths, relative/empty paths, and invalid paths.

Dependencies and integration: Exercises `node_windows.go`, `sd_windows.go`, `ea_windows.go`, and data generic-attribute conversions.

Risks: Some cases require admin privileges, system drive assumptions, encryption support, or real Windows path semantics. The tests are necessarily platform-integration heavy.

Test signals: Broadest Windows metadata coverage in this subset, including low-privilege inheritance behavior and unknown generic attribute warnings.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_xattr.go -->
# sources/sync-backup/restic/internal/fs/node_xattr.go

Purpose: POSIX-like xattr backup and restore implementation for Darwin, FreeBSD, NetBSD, Linux, and Solaris.

Important APIs: `getxattr`, `listxattr`, `isListxattrPermissionError`, `setxattr`, `removexattr`, `handleXattrErr`, `nodeRestoreExtendedAttributes`, and `nodeFillExtendedAttributes`.

Control flow and state: Backup lists xattr names, optionally ignores permission errors, reads each value, warns and skips individual unreadable attributes, and appends them to the node. Restore sets expected xattrs that match the selection filter, lists current xattrs, and removes unexpected selected ones.

Dependencies and integration: Uses `github.com/pkg/xattr` and `data.ExtendedAttribute`. Called by generic node conversion/restore.

Risks: `handleXattrErr` treats unsupported/ENOATTR as nil, which can hide unsupported metadata. Restore removal is filter-sensitive, so excluded xattrs are left untouched. `warnf` must be non-nil when individual reads fail.

Test signals: `node_xattr_test.go` verifies permission-error detection; `node_xattr_all_test.go` verifies overwrite/removal and selection filters.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_xattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_xattr_all_test.go -->
# sources/sync-backup/restic/internal/fs/node_xattr_all_test.go

Purpose: Cross-platform xattr restore/fill tests for platforms with xattr support, including Windows.

Important APIs: `setAndVerifyXattr`, `setAndVerifyXattrWithSelectFilter`, `TestOverwriteXattr`, and `TestOverwriteXattrWithSelectFilter`.

Control flow and state: Tests restore xattrs onto a temp file, read them back into a node, and compare expected names/values. Filter tests simulate `--include-xattr` patterns and confirm only selected attributes are restored while old selected-but-unexpected attrs are removed.

Dependencies and integration: Uses `filter.IncludeByPattern` for selection and adapts names to uppercase on Windows.

Risks: Platform xattr naming and filesystem support differ; Windows case-insensitivity is explicitly handled.

Test signals: Confirms xattr overwrite semantics and filter-driven restore behavior across supported platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_xattr_all_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_xattr_test.go -->
# sources/sync-backup/restic/internal/fs/node_xattr_test.go

Purpose: Tests xattr permission-error classification on POSIX-like xattr platforms.

Important APIs: `TestIsListxattrPermissionError`.

Control flow and state: Creates synthetic `xattr.Error` values, passes them through `handleXattrErr`, and checks whether `isListxattrPermissionError` recognizes only list-permission failures.

Dependencies and integration: Supports `nodeFillExtendedAttributes(ignoreListError=true)` behavior.

Risks: Only synthetic errors are tested; real filesystem permission behavior is covered indirectly elsewhere.

Test signals: Confirms the backup option to ignore xattr list permission errors targets the intended error shape.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/node_xattr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/path_prefix.go -->
# sources/sync-backup/restic/internal/fs/path_prefix.go

Purpose: Determines whether one path is equal to or inside another path.

Important APIs: `HasPathPrefix`.

Control flow and state: Compares volume names and absolute/relative status, cleans paths, returns true for equality, then walks parent directories of `p` until root looking for `base`.

Dependencies and integration: Used by VSS mount-point snapshot mapping to detect whether a requested path lies under a mount point.

Risks: Matching is case-sensitive by design, while Windows callers lower-case paths before use where needed. Relative path semantics can make `"."` a prefix of cleaned relative paths.

Test signals: `path_prefix_test.go` covers equality, root behavior, sibling false positives, case sensitivity, absolute/relative mismatch, and Windows drive normalization.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/path_prefix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/path_prefix_test.go -->
# sources/sync-backup/restic/internal/fs/path_prefix_test.go

Purpose: Unit tests for `HasPathPrefix`.

Important APIs: `fromSlashAbs` and `TestHasPathPrefix`.

Control flow and state: Converts slash paths to OS paths, adding `c:` to absolute paths on Windows, then checks a table of base/path/result cases.

Dependencies and integration: Validates path-prefix logic used by VSS mount-point routing.

Risks: Tests intentionally preserve case sensitivity even on Windows by using the function contract rather than filesystem behavior.

Test signals: Good coverage for boundary cases that could otherwise cause VSS to route sibling paths into the wrong snapshot.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/path_prefix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/preallocate_darwin.go -->
# sources/sync-backup/restic/internal/fs/preallocate_darwin.go

Purpose: Darwin file preallocation using `F_PREALLOCATE`.

Important APIs: `PreallocateFile`.

Control flow and state: Tries contiguous allocation with `F_ALLOCATECONTIG|F_ALLOCATEALL`; if that fails, retries non-contiguous `F_ALLOCATEALL`.

Dependencies and integration: Used where restic wants to reserve output file space before writing.

Risks: Preallocation can fail depending on filesystem free-space layout or unsupported filesystems. The function returns the second allocation error if both attempts fail.

Test signals: `preallocate_test.go` validates behavior for zero, small, page, and MiB sizes, skipping unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/preallocate_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/preallocate_linux.go -->
# sources/sync-backup/restic/internal/fs/preallocate_linux.go

Purpose: Linux file preallocation using `fallocate`.

Important APIs: `PreallocateFile` and `ignoringEINTR`.

Control flow and state: Returns nil for non-positive sizes. For positive sizes, calls `unix.Fallocate(fd, 0, 0, size)` and retries on `EINTR`.

Dependencies and integration: Used by restore/output writers that can benefit from reserved disk space and known file length.

Risks: Filesystems can return `ENOTSUP`, and allocation mode changes file size. EINTR handling is copied from Go internals and should remain simple.

Test signals: `preallocate_test.go` checks resulting size or allocated blocks and skips unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/preallocate_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/preallocate_other.go -->
# sources/sync-backup/restic/internal/fs/preallocate_other.go

Purpose: Fallback preallocation for non-Linux, non-Darwin platforms.

Important APIs: `PreallocateFile`.

Control flow and state: Calls `wr.Truncate(size)`. On Windows this maps to `SetEndOfFile`, which may allocate disk space.

Dependencies and integration: Keeps callers platform-neutral even where true preallocation is unavailable.

Risks: Truncate changes file length and may create sparse files rather than reserving real blocks depending on filesystem.

Test signals: `preallocate_test.go` validates size/block outcomes generically.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/preallocate_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/preallocate_test.go -->
# sources/sync-backup/restic/internal/fs/preallocate_test.go

Purpose: Cross-platform test for `PreallocateFile`.

Important APIs: `TestPreallocate`.

Control flow and state: Iterates sizes `0`, `1`, `4096`, and `1 MiB`, opens a temp file, calls `PreallocateFile`, skips `ENOTSUP`, then asserts size equals requested size or allocated block count is positive.

Dependencies and integration: Exercises platform implementations through a single contract.

Risks: Assertion allows either exact size or allocated blocks, which accommodates platform differences but is not strict about sparse allocation.

Test signals: Confirms preallocation functions do not fail unexpectedly on supported filesystems.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/preallocate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/priv.go -->
# sources/sync-backup/restic/internal/fs/priv.go

Purpose: Non-Windows privilege hook.

Important APIs: `enableProcessPrivileges`.

Control flow and state: Returns nil; no process privileges are adjusted.

Dependencies and integration: Called from `fs_local.go` package init. Provides a common hook for the Windows implementation.

Risks: None beyond being a no-op on non-Windows.

Test signals: No direct tests; local filesystem init depends on this compiling and returning nil.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/priv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/priv_windows.go -->
# sources/sync-backup/restic/internal/fs/priv_windows.go

Purpose: Enables Windows backup/restore/security/take-ownership privileges for the process.

Important APIs: `processPrivileges` and `enableProcessPrivileges`.

Control flow and state: Iterates privileges one at a time using `winio.EnableProcessPrivileges`, joins errors, and returns aggregate failure information. Enabling one at a time avoids misleading all-or-nothing errors.

Dependencies and integration: Called at package init before local filesystem operations. Supports ACL bypass, security descriptor access, and restore of protected metadata.

Risks: Privilege availability depends on admin/token rights. Errors are logged by init rather than fatal, so later operations may fall back or fail with lower privilege.

Test signals: `priv_windows_test.go` checks backup/restore privilege behavior on restricted ACLs when running as admin.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/priv_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/priv_windows_test.go -->
# sources/sync-backup/restic/internal/fs/priv_windows_test.go

Purpose: Windows-only tests that privileges can bypass restrictive ACLs.

Important APIs: `TestBackupPrivilegeBypassACL`, `TestRestorePrivilegeBypassACL`, and `testGetRestrictedFilePath`.

Control flow and state: Tests skip without administrator membership. They create a file, deny read/write/execute to Everyone while allowing delete, then verify read open and write handle open with backup semantics.

Dependencies and integration: Exercises privilege enablement from package init and Windows security descriptor manipulation.

Risks: Requires admin rights and specific Windows ACL semantics. It does not directly assert which privilege was enabled, only resulting access behavior.

Test signals: Good integration signal that restic can access protected files for backup/restore on privileged Windows runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/priv_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/sd_windows.go -->
# sources/sync-backup/restic/internal/fs/sd_windows.go

Purpose: Windows security descriptor backup/restore helpers with high- and low-privilege modes.

Important APIs: `lowerPrivileges`, security flag sets, `getSecurityDescriptor`, `setSecurityDescriptor`, `getNamedSecurityInfoHigh/Low`, `setNamedSecurityInfoHigh/Low`, `isHandlePrivilegeNotHeldError`, `isAccessDeniedError`, `securityDescriptorBytesToStruct`, and `securityDescriptorStructToBytes`.

Control flow and state: A global atomic flag switches to lower privilege after `ERROR_PRIVILEGE_NOT_HELD`. Backup first tries full owner/group/DACL/SACL/security info, falls back to low privileges on access denied, and ignores unsupported filesystems. Restore parses SD bytes, extracts owner/group/DACL/SACL/control flags, applies high or low security info, and preserves DACL/SACL protection flags.

Dependencies and integration: Called by Windows generic attribute fill/restore in `node_windows.go`. Uses `x/sys/windows`, unsafe byte views, and restic errors.

Risks: Global `lowerPrivileges` affects subsequent operations process-wide. Low-privilege restore cannot restore owner/group/SACL fully. Unsafe byte-to-struct conversion requires valid self-relative SD bytes.

Test signals: `sd_windows_test.go`, `sd_windows_test_helpers.go`, and `node_windows_test.go` cover file/folder SD round-trips, admin vs non-admin expectations, and inheritance protection flags.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/sd_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/sd_windows_test.go -->
# sources/sync-backup/restic/internal/fs/sd_windows_test.go

Purpose: Windows-only direct tests for security descriptor set/get.

Important APIs: `TestSetGetFileSecurityDescriptors`, `TestSetGetFolderSecurityDescriptors`, and `testSecurityDescriptors`.

Control flow and state: Creates temp file/folder targets, decodes base64 SD fixtures, sets each descriptor, gets it back, and delegates semantic comparison.

Dependencies and integration: Validates `setSecurityDescriptor`, `getSecurityDescriptor`, and helper comparison logic under current privilege level.

Risks: Base64 fixture semantics are opaque without helper decoding. Expected results differ for admin and non-admin users.

Test signals: Confirms SD byte restore/read behavior for both files and directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/sd_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/sd_windows_test_helpers.go -->
# sources/sync-backup/restic/internal/fs/sd_windows_test_helpers.go

Purpose: Shared Windows security descriptor fixtures and comparison helpers.

Important APIs: `testFileSDs`, `testDirSDs`, `isAdmin`, and `compareSecurityDescriptors`.

Control flow and state: `isAdmin` checks membership in the built-in Administrators SID. `compareSecurityDescriptors` parses input/output SDs and compares owner, group, DACL, and SACL expectations, adjusting owner/group/SACL expectations for non-admin restores.

Dependencies and integration: Used by SD and Windows node tests to avoid byte-for-byte comparisons that would be wrong under low privilege.

Risks: Assumes current user SID/group SID are available through `os/user`. Comparison depends on Windows APIs for SID equality and ACL equality.

Test signals: Provides the semantic oracle for security descriptor round-trip tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/sd_windows_test_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/setflags_linux.go -->
# sources/sync-backup/restic/internal/fs/setflags_linux.go

Purpose: Linux read optimization that attempts to prevent atime updates.

Important APIs: `setFlags`.

Control flow and state: Reads current file status flags with `F_GETFL`, then sets `O_NOATIME` in addition to existing flags with `F_SETFL`.

Dependencies and integration: Called after local files are opened for reading in `newLocalFile`; errors are intentionally ignored by production code but returned for tests.

Risks: `O_NOATIME` can fail unless the process owns the file or is privileged, and support depends on filesystem. Ignoring errors is expected.

Test signals: `setflags_linux_test.go` verifies atime is unchanged on filesystems known to support no-atime.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/setflags_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/setflags_linux_test.go -->
# sources/sync-backup/restic/internal/fs/setflags_linux_test.go

Purpose: Linux test for `O_NOATIME` behavior.

Important APIs: `TestNoatime` and `supportsNoatime`.

Control flow and state: Creates an owned temp file, writes data, records access time, calls `setFlags`, reads one byte, then asserts atime did not change. The support helper only runs on known compatible filesystem magic values.

Dependencies and integration: Validates `setflags_linux.go` and `ExtendedStat` access-time extraction.

Risks: Skips on many filesystems; timestamp granularity and mount options could affect behavior.

Test signals: Confirms the optimization works where expected and avoids false failures elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/setflags_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/setflags_other.go -->
# sources/sync-backup/restic/internal/fs/setflags_other.go

Purpose: Non-Linux no-op for open-file flag tuning.

Important APIs: `setFlags`.

Control flow and state: Returns nil without modifying the file.

Dependencies and integration: Lets `newLocalFile` call `setFlags` unconditionally across platforms.

Risks: No atime suppression or I/O tuning occurs on these platforms through this hook.

Test signals: No direct tests; behavior is intentionally inert.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/setflags_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat.go -->
# sources/sync-backup/restic/internal/fs/stat.go

Purpose: Defines restic's normalized file metadata struct and public conversion wrapper.

Important APIs: `ExtendedFileInfo` and `ExtendedStat`.

Control flow and state: `ExtendedStat` panics on nil `os.FileInfo`, then delegates to platform-specific `extendedStat`. `ExtendedFileInfo` stores common stat fields, timestamps, block info, and a private `sys` value for platform-specific checks.

Dependencies and integration: Used by all `FS` implementations, node conversion, preallocation tests, no-atime tests, and cloud-placeholder detection.

Risks: Platform implementations must populate fields consistently. The panic on nil is deliberate but requires callers to check errors before conversion.

Test signals: `stat_test.go`, platform stat tests, and node tests validate conversion and recall-on-access behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_bsd.go -->
# sources/sync-backup/restic/internal/fs/stat_bsd.go

Purpose: FreeBSD/NetBSD `extendedStat` implementation.

Important APIs: `extendedStat` and `ExtendedFileInfo.RecallOnDataAccess`.

Control flow and state: Extracts stat fields from `syscall.Stat_t`, using BSD `Atimespec`, `Mtimespec`, and `Ctimespec`. `RecallOnDataAccess` always returns false.

Dependencies and integration: Feeds node metadata conversion on BSD targets.

Risks: No cloud-placeholder detection on BSD. Field type conversions must match platform syscall layout.

Test signals: Generic stat/node tests cover this on BSD builders.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_darwin.go -->
# sources/sync-backup/restic/internal/fs/stat_darwin.go

Purpose: macOS stat conversion plus dataless-file detection.

Important APIs: `extendedStat` and `ExtendedFileInfo.RecallOnDataAccess`.

Control flow and state: Extracts POSIX stat fields and stores the raw `*syscall.Stat_t` in `sys`. `RecallOnDataAccess` checks `unix.SF_DATALESS` to detect cloud-only placeholder files.

Dependencies and integration: Used by backup code to avoid unintended cloud downloads when checking recall-on-data-access status.

Risks: `RecallOnDataAccess` errors if `sys` is missing or not a Darwin stat struct. HFS+ timestamp precision differences are handled in tests.

Test signals: `stat_darwin_test.go` covers real regular files, mocked dataless files, regular mocks, and missing sys errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_darwin_test.go -->
# sources/sync-backup/restic/internal/fs/stat_darwin_test.go

Purpose: macOS tests for recall-on-data-access detection.

Important APIs: `TestRecallOnDataAccessRealFile`, `mockFileInfo`, `TestRecallOnDataAccessMockCloudFile`, `TestRecallOnDataAccessMockRegularFile`, and `TestRecallOnDataAccessMockError`.

Control flow and state: Tests real temp-file stat conversion and mock `os.FileInfo` values with `SF_DATALESS` set/unset. Error test constructs an `ExtendedFileInfo` without a Darwin sys payload.

Dependencies and integration: Validates `stat_darwin.go` and public `fs.ExtendedStat` from external package perspective.

Risks: Real file test only checks a normal local file; cloud state is simulated through mocks.

Test signals: Confirms correct detection and error reporting for macOS cloud placeholders.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_darwin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_test.go -->
# sources/sync-backup/restic/internal/fs/stat_test.go

Purpose: Cross-platform tests for public `ExtendedStat`.

Important APIs: `TestExtendedStat` and `TestNilExtendPanic`.

Control flow and state: Writes a temp file, calls package `Lstat`, converts it, and compares modification time. The nil test recovers and asserts the panic message.

Dependencies and integration: Covers `stat.go` and platform `extendedStat` indirectly.

Risks: Minimal metadata assertion; detailed stat field checks live in node tests.

Test signals: Confirms basic wrapper behavior and deliberate nil panic.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_unix.go -->
# sources/sync-backup/restic/internal/fs/stat_unix.go

Purpose: Generic Unix stat conversion for non-Windows, non-Darwin, non-FreeBSD, non-NetBSD targets.

Important APIs: `extendedStat` and `ExtendedFileInfo.RecallOnDataAccess`.

Control flow and state: Extracts common stat fields from `syscall.Stat_t`, including nanosecond timestamps from `Atim`, `Mtim`, and `Ctim`. `RecallOnDataAccess` returns false.

Dependencies and integration: Provides metadata for Linux and other Unix-like backup/restore paths.

Risks: No cloud-placeholder detection here. Platform build tags must exclude syscall layouts that do not have these fields.

Test signals: Linux node/stat/no-atime tests exercise this implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_windows.go -->
# sources/sync-backup/restic/internal/fs/stat_windows.go

Purpose: Windows stat conversion and cloud-placeholder detection.

Important APIs: `extendedStat` and `ExtendedFileInfo.RecallOnDataAccess`.

Control flow and state: Converts `Win32FileAttributeData` into size and timestamps, using LastWriteTime as ChangeTime because Windows lacks Unix ctime semantics. `RecallOnDataAccess` checks `FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS`.

Dependencies and integration: Feeds Windows node conversion and backup skip/download decisions.

Risks: Panics if `os.FileInfo.Sys()` is not `*syscall.Win32FileAttributeData`. ChangeTime semantics differ from Unix.

Test signals: `stat_windows_test.go` covers real regular files and mocked recall-on-access attributes.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_windows_test.go -->
# sources/sync-backup/restic/internal/fs/stat_windows_test.go

Purpose: Windows tests for recall-on-data-access detection.

Important APIs: `TestRecallOnDataAccessRealFile`, `mockFileInfo`, `TestRecallOnDataAccessMockCloudFile`, and `TestRecallOnDataAccessMockRegularFile`.

Control flow and state: Tests a real local temp file and mocked `Win32FileAttributeData` values with recall and archive attributes.

Dependencies and integration: Validates `stat_windows.go` and external-package public API behavior.

Risks: Real cloud placeholder behavior is mocked rather than requiring OneDrive or similar services.

Test signals: Confirms Windows placeholder detection is based on the expected file attribute bit.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/stat_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/vss.go -->
# sources/sync-backup/restic/internal/fs/vss.go

Purpose: Non-Windows stubs for VSS types and functions.

Important APIs: `mountPoint`, `vssSnapshot`, `HasSufficientPrivilegesForVSS`, `getVolumeNameForVolumeMountPoint`, `newVssSnapshot`, `Delete`, and `GetSnapshotDeviceObject`.

Control flow and state: All snapshot-related operations either return false/empty values, return the input mount point, or return an error explaining VSS is Windows-only.

Dependencies and integration: Lets `fs_local_vss.go` compile on all platforms while only functioning on Windows.

Risks: Callers must not expect VSS functionality outside Windows; error strings are the operational signal.

Test signals: Windows-specific tests cover real VSS; non-Windows behavior is compile-time compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/vss.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/vss_windows.go -->
# sources/sync-backup/restic/internal/fs/vss_windows.go

Purpose: Low-level Windows VSS COM bindings and snapshot lifecycle implementation.

Important APIs: `HRESULT`, VSS constants, `vssError`, `IVssBackupComponents` methods, `IVSSAsync`, `IVSSAdmin`, `IVssEnumObject`, `mountPoint`, `vssSnapshot`, `initializeVssCOMInterface`, `HasSufficientPrivilegesForVSS`, `getVolumeNameForVolumeMountPoint`, `newVssSnapshot`, `Delete`, `getProviderID`, `callAsyncFunctionAndWait`, `loadIVssBackupComponentsConstructor`, `queryInterface`, `isRunningOn64BitWindows`, and `enumerateMountedFolders`.

Control flow and state: Initializes COM and security, creates `IVssBackupComponents`, resolves provider, initializes backup state, gathers metadata, checks volume support, retries snapshot-set creation while another set is in progress, adds the main volume and selected mount points, prepares and creates snapshots asynchronously before returning snapshot device objects. Deletion frees snapshot properties, calls `BackupComplete`, deletes snapshots, and releases COM interfaces.

Dependencies and integration: Used by `LocalVss.snapshotPath`. Depends on `go-ole`, `VssApi.dll`, Windows COM/syscalls, and architecture-specific syscall argument layouts.

Risks: Very high-risk integration surface: unsafe vtable calls, COM initialization rules, admin/backup privileges, timeout/deadline handling, architecture mismatch checks, mount-point partial snapshot behavior, and cleanup after failed `PrepareForBackup`/`DoSnapshotSet`.

Test signals: `fs_local_vss_test.go` validates provider lookup, privilege availability, and live snapshot access when admin privileges are available.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fs/vss_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/dir.go -->
# sources/sync-backup/restic/internal/fuse/dir.go

Purpose: Implements FUSE directory nodes backed by restic repository trees.

Important APIs: `dir`, `cleanupNodeName`, `newDir`, `unwrapCtxCanceled`, `replaceSpecialNodes`, `newDirFromSnapshot`, `open`, `Attr`, `calcNumberOfLinks`, `ReadDirAll`, `Lookup`, `Listxattr`, `Getxattr`, and `Forget`.

Control flow and state: Directories lazily load their tree once under a mutex into `items`. Special directory nodes named `.` or `/` with subtrees are replaced by their subtree contents. `ReadDirAll` emits `.`/`..` plus entries with inode/type. `Lookup` uses a tree cache to create child FUSE nodes by restic node type. `Forget` calls the inode cache cleanup callback.

Dependencies and integration: Uses `anacrolix/fuse`, restic `data.LoadTree`, repository blob loading, node-to-inode helpers, xattr helpers, and child node constructors (`newFile`, `newLink`, `newOther`).

Risks: Lazy tree loading must handle concurrent FUSE calls and context cancellation correctly. `calcNumberOfLinks` depends on `items` being loaded; callers typically call it after open for listings, but `Attr` can run before open. Duplicate cleaned names overwrite earlier entries.

Test signals: No direct tests in this subset; behavior is exercised by FUSE integration tests elsewhere. Interface assertions verify required FUSE contracts at compile time.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/file.go -->
# sources/sync-backup/restic/internal/fuse/file.go

Purpose: Implements FUSE regular file nodes backed by restic content blobs.

Important APIs: `file`, `openFile`, `newFile`, `file.Attr`, `file.Open`, `openFile.getBlobAt`, `openFile.Read`, xattr methods, and `Forget`.

Control flow and state: `Open` looks up every content blob size, builds cumulative offsets, and adjusts reported size if stored node size differs from blob total. `Read` handles empty files, binary-searches the starting blob for the requested offset, fetches blobs through a shared blob cache, slices the first blob by offset, and copies until the response buffer is full or content ends.

Dependencies and integration: Uses `anacrolix/fuse`, restic repository `LookupBlobSize`/`LoadBlob`, blob cache, `restic.BlobHandle`, `data.Node`, and xattr helpers.

Risks: Missing blob sizes fail open. Read correctness depends on cumulative-size indexing and response buffer sizing. Concurrent reads rely on the blob cache for synchronization. Link count is clamped to at least one because Windows backups may store zero.

Test signals: No direct tests in this subset; compile-time interface assertions and FUSE integration coverage elsewhere protect behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/fuse/file.go -->
