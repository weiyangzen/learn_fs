# sources/cloud-native/containers-storage/drivers/chown_darwin.go

## Purpose
`chown_darwin.go` provides the Darwin implementation of platform-specific `LChown` for ID-map rewriting.

## Important APIs, Types, And Functions
It defines `inode`, `platformChowner`, `newLChowner`, and `(*platformChowner).LChown`. The chowner tracks visited device/inode pairs to avoid processing hardlinked files repeatedly.

## Control Flow
`LChown` extracts `syscall.Stat_t`, skips already-seen inodes, maps UID/GID from host to container and back to host, reads `security.capability` when present, calls `system.Lchown`, restores setuid/setgid mode bits, and restores the capability xattr.

## State And Persistence
The in-memory `inodes` map deduplicates processing during one walk. Persistent changes are file ownership, mode restoration, and xattr restoration.

## Dependencies And Integration Points
It integrates with `chown.go` through `newLChowner`. Dependencies include `idtools`, `system`, `os`, `syscall`, and `sync`.

## Risks
Darwin has no Linux-style hardlink copy-up issue here, so repeated hardlinks are skipped rather than relinked. Capability xattr handling is best-effort for unsupported platforms. Mapping failures for nonzero IDs abort the walk.

## Test Signals
No direct Darwin test in this subset; behavior is exercised only when ID-map updates run on Darwin builds.
