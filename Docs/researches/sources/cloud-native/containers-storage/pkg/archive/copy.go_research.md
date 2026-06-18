<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy.go -->
# sources/cloud-native/containers-storage/pkg/archive/copy.go

Purpose: implements Docker-style copy semantics by turning source resources into tar streams, optionally rebasing entries, and extracting into destination paths.

Important APIs/types/functions: errors `ErrNotDirectory`, `ErrDirNotExists`, `ErrCannotCopyDir`, `ErrInvalidCopySource`; path helpers `PreserveTrailingDotOrSeparator`, `SplitPathDirEntry`; `CopyInfo`; `CopyInfoSourcePath`; `CopyInfoDestinationPath`; `PrepareArchiveCopy`; `RebaseArchiveEntries`; `CopyResource`; `CopyTo`; `ResolveHostSourcePath`; `GetRebaseName`.

Control flow: source paths are normalized, cleaned, and optionally resolved through symlinks. `TarResourceRebase` archives the containing directory with `IncludeFiles` and `RebaseNames`. `CopyInfoDestinationPath` follows destination symlinks, validates parent existence, and records whether the target exists and is a directory. `PrepareArchiveCopy` applies the copy matrix: merge into existing directories, reject directory-to-file copies, reject file-to-nonexistent-asserted-directory copies, or rebase the first archive path element to the desired destination basename. `CopyTo` extracts with `NoLchown` and `NoOverwriteDirNonDir`.

State/persistence: writes happen only through final `Untar` extraction. The rebasing path uses an `io.Pipe` goroutine and tar reader/writer; no intermediate archive file is persisted.

Dependencies/integration: integrates with `TarWithOptions`, `Untar`, `fileutils.Lexists`, tar headers, path normalization in OS-specific files, and archiver copy helpers.

Risks: path intent is encoded in trailing slash and `/.`, so normalization bugs can copy the wrong level. Destination symlink resolution follows up to 10 hops. `RebaseArchiveEntries` uses first string replacement, so callers must pass normalized base names. Pipe goroutine errors propagate only when the returned reader is consumed.

Test signals: `copy_unix_test.go` covers source/destination matrix cases A-J, symlink following, trailing slash/current-dir preservation, and expected error classes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy.go -->
