# sources/cloud-native/containers-storage/drivers/chown_unix.go

## Purpose
`chown_unix.go` provides the non-Windows, non-Darwin `LChown` implementation for ID-map rewriting, with special hardlink preservation for filesystems that break inodes during copy-up.

## Important APIs, Types, And Functions
It defines `inode`, `platformChowner`, `newLChowner`, and `(*platformChowner).LChown`. The chowner maps a device/inode pair to the first path seen, not just a boolean.

## Control Flow
For each entry, the code records the first path for an inode. If a later hardlink to the same inode is found, it removes the new path and links it to the first path instead of chowning again. For first occurrences, it maps UID/GID through `toContainer` and `toHost`, preserves `security.capability`, applies `Lchown`, restores setuid/setgid bits, and restores capabilities.

## State And Persistence
In-memory state tracks inode-to-path mappings during a walk. Persistent effects include ownership changes, hardlink topology preservation, mode restoration, and capability xattr restoration.

## Dependencies And Integration Points
It depends on `idtools`, `system`, `os`, `syscall`, and `sync`. It is selected for Linux, FreeBSD, Solaris-like non-Darwin Unix builds and is used by the reexec chown walker.

## Risks
The locking around hardlinks avoids races while relinking/chowning, but path removal and relink can fail if files change concurrently. Capability xattr errors other than unsupported/overflow are fatal. Zero-ID fallback behavior can mask parent layers that were not mapped as expected.

## Test Signals
No direct test in this subset. The hardlink preservation logic is a critical indirect dependency for overlay and other copy-up filesystems during ID-map updates.
