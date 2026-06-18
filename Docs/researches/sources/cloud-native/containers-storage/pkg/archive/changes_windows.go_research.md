<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_windows.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_windows.go

Purpose: Windows implementation of archive change comparison primitives.

Important APIs/types/functions: `statDifferent`, `(*FileInfo).isDir`, `getIno`, and `hasHardlinks`.

Control flow: `statDifferent` compares mtime, mode, and size for non-directories. Windows inode and hardlink helpers return zero/false because this path does not use Unix inode/hardlink metadata.

State/persistence: no writes; reads `system.StatT` values supplied by the common change scanner.

Dependencies/integration: used by common archive change logic on Windows. It keeps the API shape compatible with Unix files while reflecting reduced metadata support.

Risks: no UID/GID, rdev, xattr, file flag, inode, or hardlink comparison means Windows diffs are necessarily less precise. Size comparison expression relies on operator precedence to ignore directory size.

Test signals: Windows-specific reset helper is no-op, and many generic symlink/hardlink tests skip Windows; coverage is mainly compile-time and generic path behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_windows.go -->
