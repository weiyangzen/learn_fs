# sources/cloud-native/containers-storage/pkg/archive/archive_unix_test.go

## Purpose
This Unix-only test file validates path canonicalization, chmod behavior, hardlinks, special device/fifo handling, and xattr round trips.

## Important Tests
`TestCanonicalTarNameForPath` and `TestCanonicalTarName` assert Unix names are preserved and directories get trailing slashes. `TestChmodTarEntry` verifies chmod is a no-op on Unix. `TestTarWithHardLink` checks hardlink preservation and ensures tar hardlink entries target a real file entry rather than another hardlink entry. `TestTarWithHardLinkAndRebase` validates hardlinks after archive rebasing. `TestTarWithBlockCharFifo` checks special device/fifo preservation. `TestTarUntarWithXattr` verifies security capability and user xattrs survive tar/untar where supported.

## Control Flow and State
The tests create real Unix filesystem features: hardlinks, block devices, char devices, fifos, and xattrs. They tar to memory, untar to temp directories, and compare inodes or `ChangesDirs` output.

## Dependencies and Integration Points
The file depends on `system`, `unix`, `idtools`, `archive.go`, `archive_unix.go`, and `changes.go`. Some tests skip on platforms such as Solaris or FreeBSD for xattr limitations.

## Risks and Edge Cases
Privilege and filesystem support affect special device and xattr tests. The tests cover preservation, but not all failure branches in extraction. Hardlink tests are especially important for security because link targets must not become symlink-following escapes.

## Test Signals
Strong Unix platform coverage for metadata fidelity and hardlink/device semantics. These tests complement the generic breakout tests in `archive_test.go`.
