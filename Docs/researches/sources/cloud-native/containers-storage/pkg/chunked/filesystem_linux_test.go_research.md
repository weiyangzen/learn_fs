## sources/cloud-native/containers-storage/pkg/chunked/filesystem_linux_test.go

Purpose: Linux unit tests for the fd-safe filesystem primitives used by chunked layer extraction.

Important APIs/types/functions: defines `nopCloser`, `createTempFile`, and tests `newSeekableFile.GetBlobAt`, `doHardLink`, `appendHole`, `safeMkdir`, `safeLink`, `safeSymlink`, `openOrCreateDirUnderRoot`, `copyFileContent`, and `splitPath`.

Control flow: each test builds temporary roots and file descriptors, exercises helper behavior, then verifies by reading through `openFileUnderRoot`, `Fstat`, inode comparison, file size seeking, or expected normalized path pairs. Privilege-sensitive chown calls are bypassed with `archive.TarOptions{IgnoreChownErrors:true}`.

State and persistence: tests create real temporary files, directories, hard links, symlinks, and sparse holes. The suite checks whether hard-link dedupe returns nil destination file and preserves inode identity, while copy mode creates a distinct inode.

Dependencies and integration points: test coverage targets `filesystem_linux.go`; uses `testify`, `syscall`, `archive.TarOptions`, and `minimal.FileMetadata`. It validates assumptions consumed later by `storage_linux.go`.

Risks: tests use Linux filesystem semantics and may require symlink/hardlink support. They exercise helper primitives but do not validate whiteout handler, xattr application, `openat2` ENOSYS fallback, or fs-verity flows.

Test signals: the case table for `splitPath` is broad and important because many *at syscalls receive its base name. Local execution was not possible because `go` is unavailable.
