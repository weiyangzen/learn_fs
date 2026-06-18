# sources/cloud-native/containers-storage/pkg/archive/archive_bsd.go

## Purpose
This BSD/Darwin platform file implements symlink-aware chmod behavior during tar extraction where `fchmodat` with `AT_SYMLINK_NOFOLLOW` is available.

## Important Function
`handleLChmod(hdr, path, hdrInfo, forceMask)` computes the permissions from the header file info or a forced mask, then calls `unix.Fchmodat(AT_FDCWD, path, mode, AT_SYMLINK_NOFOLLOW)`.

## Control Flow and State
The function directly applies mode bits to an extracted filesystem path. It does not branch on tar type beyond using the supplied mode. The persistent effect is the file mode on disk.

## Dependencies and Integration Points
The file is built on NetBSD, FreeBSD, or Darwin. It depends on `archive/tar`, `os`, and `golang.org/x/sys/unix`. `extractTarFileEntry` in `archive.go` calls `handleLChmod` after chown and before timestamp/xattr restoration.

## Risks and Edge Cases
Because this platform implementation applies `Fchmodat` with no-follow semantics, behavior can differ from Linux's selective chmod of non-symlink entries and hardlinks. Force-mask handling must stay aligned with extraction code and chunked package comments.

## Test Signals
There is no direct BSD test in this subset for `handleLChmod`. BSD-specific file flag tests in `changes_bsd_test.go` exercise adjacent platform metadata handling.
