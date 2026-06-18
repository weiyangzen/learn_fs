# sources/cloud-native/containers-storage/pkg/archive/archive_unix.go

## Purpose
This Unix platform file provides tar header stat population, canonical path behavior, special-device extraction, hardlink behavior, and UID/GID extraction for archive operations.

## Important Functions
`init` installs `statUnix` into `sysStatOverride`, so `FileInfoHeader` can populate UID, GID, and device major/minor without extra OS lookups. `fixVolumePathPrefix` is a no-op. `getWalkRoot` preserves trailing include semantics by concatenating paths instead of `filepath.Join`. `CanonicalTarNameForPath` returns Unix-style paths unchanged. `chmodTarEntry` is a no-op. `setHeaderForSpecialDevice`, `getInodeFromStat`, `getFileUIDGID`, `major`, `minor`, `handleTarTypeBlockCharFifo`, and `handleLLink` implement Unix metadata and filesystem operations.

## Control Flow and State
The file mutates tar headers based on `syscall.Stat_t`, creates block/char/fifo filesystem entries through `system.Mknod`, and creates hardlinks via `unix.Linkat` without following symlinks. Its persistent effects occur during extraction when special files and hardlinks are created.

## Dependencies and Integration Points
Dependencies include `archive/tar`, `os`, `filepath`, `syscall`, `idtools`, `system`, and `x/sys/unix`. The functions are called by `archive.go` during tar creation, extraction, and hardlink tracking.

## Risks and Edge Cases
Device creation requires appropriate privileges. Hardlink behavior intentionally avoids symlink following; changing that would weaken breakout protections. `getWalkRoot` has path-cleaning implications for include roots and should remain aligned with tests.

## Test Signals
`archive_unix_test.go` validates canonical names, chmod behavior, hardlink preservation and rebasing, special device/fifo round trips, and xattr preservation.
