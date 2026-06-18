# sources/cloud-native/fuse-overlayfs/tests/suid-test.c

## Purpose
`tests/suid-test.c` is a small helper used by Fedora integration tests to distinguish preserved setuid bits from setuid bits cleared by writes after chmod.

## Important APIs, Types, And Functions
`main` unlinks `suid` and `nosuid`, creates each with `open(O_WRONLY | O_CREAT | O_EXCL)`, writes data, calls `fchown(fd, 0, 0)`, applies `fchmod(fd, S_ISUID | 0755)`, and for `nosuid` performs an extra write after chmod before closing.

## Control Flow
The first file is chmodded setuid and closed without further writes. The second is chmodded setuid and then written again, which should trigger kernel privilege-bit clearing semantics.

## State And Persistence
It creates two files in the current working directory of the mounted overlay. Their resulting modes are checked by `fedora-installs.sh` in the upper layer.

## Dependencies And Integration Points
Depends on libc/POSIX file APIs and sufficient privilege or mount behavior to allow chown/chmod. It integrates with overlay write handling, especially code that preserves setuid/setgid for writeback-cache writepage but not normal user writes.

## Risks
Return values are not checked, so failures can lead to misleading downstream mode checks. It assumes running as root or with permissions that make `fchown(0,0)` and setuid chmod meaningful.

## Test Signals
`fedora-installs.sh` expects `upper/suid` to retain setuid and `upper/nosuid` not to retain it, validating correct privilege-bit behavior around writes.
