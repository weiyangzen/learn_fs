## sources/cloud-native/containers-storage/pkg/directory/directory_windows.go

Purpose: Windows implementation of directory usage accounting.

Important APIs/types/functions: `Size` and `Usage`.

Control flow: `Usage` walks the tree, increments inode count for every entry, skips directory sizes, sums file sizes, ignores disappeared children, and errors on missing root. `Size` calls `Usage` but returns `0, nil` on error.

State and persistence: read-only traversal.

Dependencies and integration points: fulfills package API for Windows builds.

Risks: `Size` suppresses errors from `Usage`, unlike Unix; this may hide missing or inaccessible paths. Inode count is really entry count, not unique inode count.

Test signals: shared directory tests exercise behavior when run on Windows, but no Windows-specific error suppression test is selected.
