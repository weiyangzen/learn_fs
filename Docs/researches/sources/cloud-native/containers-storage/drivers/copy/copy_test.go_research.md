# sources/cloud-native/containers-storage/drivers/copy/copy_test.go

## Purpose
`copy_test.go` validates Linux copy helper behavior for regular-file content, recursive directory metadata, and hardlink preservation.

## Important APIs, Types, And Functions
Tests include `TestCopy`, `TestCopyWithoutRange`, `TestCopyDir`, and `TestCopyHardlink`. Helpers include `randomMode`, `populateSrcDir`, and `doCopyTest`.

## Control Flow
Regular-file tests create deterministic random data and compare destination bytes. Directory tests generate a nested tree with random modes, mtimes, files, directories, and a socket, then walk source and destination to compare mode, ownership, and mtime metadata. Hardlink tests create two source names for the same inode and assert the copied destination names also share an inode.

## State And Persistence
All state is test temporary filesystem content. Tests intentionally create Unix sockets and hardlinks to validate special handling.

## Dependencies And Integration Points
The suite depends on `system.Chtimes`, `x/sys/unix`, `gotest.tools` assertions, and Linux build tags.

## Risks
Tests are filesystem-sensitive: inode equality, ctime comments, ownership, and special files can vary by platform or permissions. They do not directly verify xattr copying.

## Test Signals
Strong signal for content correctness, metadata preservation, and hardlink topology, but limited signal for reflink/copy_file_range paths because fallback behavior depends on kernel/filesystem support.
