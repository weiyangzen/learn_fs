## sources/cloud-native/containers-storage/pkg/chunked/filesystem_linux.go

Purpose: Linux-only fd-oriented filesystem helpers for the chunked differ. The file keeps extraction under a target root using `openat2(RESOLVE_IN_ROOT)` when available, a securejoin fallback otherwise, and helpers for hard links, symlinks, directories, sparse holes, metadata/xattr ownership application, whiteouts, and an in-memory seekable wrapper over an `io.ReaderAt`.

Important APIs/types/functions: `fileMetadata` embeds `minimal.FileMetadata` and adds chunk slices plus `skipSetAttrs`; `splitPath`, `openFileUnderRoot`, `openOrCreateDirUnderRoot`, `doHardLink`, `copyFileContent`, `setFileAttrs`, `safeMkdir`, `safeLink`, `safeSymlink`, `whiteoutHandler`, `seekableFile.GetBlobAt`, and `newSeekableFile`. `skipOpenat2` caches kernel lack of `openat2`.

Control flow: paths are normalized with `internal/path.CleanAbsPath`; file opens first try `openat2`, fall back only on `ENOSYS`, and create missing parents for `O_CREAT`. `setFileAttrs` chooses descriptor versus path mode, forces symlink operations through path-based syscalls, applies chown, base64-decoded xattrs except ignored SELinux labels, timestamps, then chmod. Copying prefers a hard link when allowed, otherwise creates a new file and delegates copy acceleration to `drivers/copy.CopyRegularToFile`.

State and persistence: creates directories/files/symlinks/hardlinks under the checkout root, mutates xattrs, ownership, times, modes, device whiteouts, and sparse file size. `skipSetAttrs` prevents hard-link dedupe from changing shared inode metadata. `skipOpenat2` is process-global. `seekableFile` owns and closes the wrapped reader.

Dependencies and integration points: used by `storage_linux.go` extraction, whiteout conversion, composefs flat paths, and tar metadata staging. Depends on `unix`, `/proc/self/fd`, `archive.TarOptions`, `securejoin`, `tar-split`, and storage path helpers.

Risks: fallback root containment relies on procfs target prefix checking and securejoin semantics; hard-link dedupe deliberately skips metadata changes; xattr values must be valid base64; `setFileAttrs` ignores `ENOSYS`/`ENOTSUP` for xattr/time/chmod operations; symlink tests intentionally show link targets may point outside root but opening remains root-confined.

Test signals: `filesystem_linux_test.go` covers section reads, hard-link replacement, sparse holes, root-confined mkdir/link/symlink/open, copy versus hard-link inode behavior, and path normalization. No full end-to-end `ApplyDiff` test is in this file. Local test execution was blocked because `go` is not installed.
