## sources/cloud-native/containers-storage/pkg/directory/directory_unix.go

Purpose: non-Windows implementation of directory size and inode usage accounting.

Important APIs/types/functions: `Size` and `Usage`.

Control flow: `Usage` walks with `filepath.WalkDir`, ignores disappeared children, errors on missing root, deduplicates visited inode numbers from `syscall.Stat_t`, skips directory sizes, and sums regular/non-directory file sizes. `Size` returns `Usage.Size`.

State and persistence: read-only traversal; no persistent mutation.

Dependencies and integration points: used by storage accounting code and tests. Depends on Unix `Stat_t` being present in `FileInfo.Sys()`.

Risks: inode dedupe uses inode number alone without device ID, which can undercount if a walk crosses devices with overlapping inode numbers. Directory sizes are ignored intentionally. Concurrent deletion is tolerated for children but not root.

Test signals: directory tests cover basic size/count cases but not hard links or cross-device walks. Local execution unavailable because `go` is missing.
