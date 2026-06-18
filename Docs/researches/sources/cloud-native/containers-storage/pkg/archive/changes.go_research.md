# sources/cloud-native/containers-storage/pkg/archive/changes.go

## Purpose
`changes.go` computes filesystem differences between layers or directories and exports those differences as AUFS-style tar changes. It is used for layer diff generation and size estimation.

## Important Types and APIs
`ChangeType` enumerates modify, add, and delete operations and renders as `C`, `A`, or `D`. `Change` stores path and kind. `Changes(layers, rw)` walks a read-write layer against read-only layers using AUFS whiteout rules. `ChangesDirs(newDir, newMappings, oldDir, oldMappings)` builds `FileInfo` trees and compares them. `ChangesSize` estimates changed payload size without double-counting hardlinks. `ExportChanges` streams a tar archive for a list of changes, writing whiteout entries for deletes.

## Control Flow
`changes` walks the rw directory, rebases paths to absolute-style OS paths, skips metadata, maps `.wh.*` files to deletes, scans lower layers to distinguish adds from modifies, accounts for lower-layer whiteouts, and injects parent directory modify records for adds/deletes. The `FileInfo` comparison path recursively compares stat metadata, capabilities, symlink targets, and xattrs, records adds/modifies/deletes, and inserts directory modify records when children changed.

## State and Persistence
`FileInfo` is an in-memory tree containing parent links, ID mappings, stat data, children, capabilities, xattrs, targets, and an `added` marker. `ExportChanges` persists results only through the returned pipe stream. Delete changes become tar headers named with `WhiteoutPrefix`.

## Dependencies and Integration Points
The file depends on `archive/tar`, filesystem APIs, `fileutils`, `idtools`, `pools`, `system`, and platform helpers from `changes_linux.go`, `changes_unix.go`, `changes_other.go`, or `changes_windows.go`. `layers.go` calls driver-level changes, and drivers/archive flows use these helpers for diff exports and validation.

## Risks and Edge Cases
Filesystem races are expected during live diffing; `ExportChanges` logs and skips some file-add errors to keep streaming. Time comparison allows one side to have zero nanoseconds to account for tar precision. Whiteout and parent-directory logic is subtle and platform-specific. The old-dir empty case creates and removes a temp directory with `os.Remove`, not `RemoveAll`, which is fine for the empty temp dir but worth preserving intentionally.

## Test Signals
Generic archive tests use `ChangesDirs` for round-trip equality. BSD-specific tests validate file flags in changes on supported platforms. Full platform helper coverage is split across other files outside this subset.
