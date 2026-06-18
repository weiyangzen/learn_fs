# sources/cloud-native/moby/daemon/internal/directory/directory_windows.go

## Purpose
Implements Windows directory size calculation.

## APIs, Control Flow, and Integration
`calcSize` uses `filepath.Walk`, ignores disappeared non-root entries, honors context cancellation, skips nil infos, directories, and zero-byte files, and sums sizes of all visited files.

## State, Dependencies, and Risks
No de-duplication state is maintained, so hard links/reparse semantics may count differently than Unix. The implementation depends on Go walk behavior and Windows filesystem errors. Shared tests validate basic totals and nonexistent root errors but not cancellation, symlinks, or locked files.
