<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/diff.go -->
# sources/cloud-native/containers-storage/pkg/archive/diff.go

Purpose: applies OCI/Docker layer tar streams to a destination directory, including whiteout handling, AUFS metadata compatibility, ID remapping, immutable flag reset, and directory mtime restoration.

Important APIs/types/functions: `UnpackLayer`, `ApplyLayer`, `ApplyUncompressedLayer`, and `applyLayerHandler`.

Control flow: `applyLayerHandler` cleans destination, sets umask to zero, optionally decompresses, and calls `UnpackLayer`. `UnpackLayer` iterates tar headers, normalizes names, creates missing parent dirs, skips AUFS metadata except hardlink plnk targets, rejects path breakout via `filepath.Rel`, processes `.wh.*` whiteouts and opaque directory whiteouts, removes/replaces existing non-merge entries after resetting immutable flags, remaps IDs, extracts via `extractTarFileEntry`, tracks unpacked paths, and restores directory times/file flags after all entries.

State/persistence: mutates the destination tree by creating, replacing, deleting, chmod/chowning, timestamping, xattrs/flags, and temporary AUFS hardlink files. Size returned is cumulative tar payload size.

Dependencies/integration: relies on tar readers, `fileutils.Lexists`, `idtools`, `system.Umask/Chtimes`, `DecompressStream`, `WriteFileFlagsFromTarHeader`, `resetImmutable`, whiteout constants, and lower-level extraction helpers from archive package.

Risks: this is security-sensitive. Breakout prevention, hardlink/symlink extraction, whiteout deletion, and immutable flag reset must stay correct. Windows colon filtering is permissive for Linux images on Windows. AUFS plnk temporary extraction requires correct cleanup. Directory mtime restoration can fail after later mutations.

Test signals: `diff_test.go` covers invalid filenames, hardlink/symlink breakout attempts, and whiteout layering. `changes_test.go` applies exported layers round-trip. Chroot archive tests exercise this through a sandboxed reexec path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/diff.go -->
