# sources/cloud-native/moby/daemon/internal/directory/directory_unix.go

## Purpose
Implements Unix directory size calculation for Linux, FreeBSD, and Darwin.

## APIs, Control Flow, and Integration
`calcSize` walks the path with `filepath.Walk`, ignores vanished non-root entries, checks context cancellation on each visited file, ignores directories and zero-byte files, and sums file sizes. It tracks inode numbers from `syscall.Stat_t` to avoid counting hard-linked content multiple times.

## State, Dependencies, and Risks
State is a map of visited inode numbers. Risks include assuming `Sys()` is `*syscall.Stat_t`, inode-only de-duplication without device ID, and `filepath.Walk` behavior on permission errors. Tests cover basic size cases through `Size`; hard links and cancellation are untested.
