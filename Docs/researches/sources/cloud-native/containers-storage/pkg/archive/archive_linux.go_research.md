# sources/cloud-native/containers-storage/pkg/archive/archive_linux.go

## Purpose
This Linux-specific file implements overlay whiteout conversion and Linux ownership/chmod helpers for archive creation and extraction.

## Important APIs and Types
`GetWhiteoutConverter(format, data)` returns an `overlayWhiteoutConverter` for overlay format, optionally with lower-layer paths. `overlayWhiteoutConverter.ConvertWrite` converts overlay character-device whiteouts and opaque directory xattrs into AUFS-style tar entries. `ConvertReadWithHandler` converts AUFS `.wh.*` and `.wh..wh..opq` entries back into overlay character devices and opaque xattrs. `directHandler` applies xattrs, mknod, and chown directly. `GetFileOwner` returns UID, GID, and mode from `syscall.Stat_t`. Linux `handleLChmod` chmods non-symlink entries and carefully handles hardlinks.

## Control Flow
On write, character devices with major/minor zero become `.wh.<name>` regular tar entries. Opaque directories with overlay opaque xattr may produce an additional AUFS opaque whiteout entry only if lower layers indicate the directory existed and was not already hidden by a parent whiteout. On read, `.wh..wh..opq` sets the overlay opaque xattr on the directory and suppresses writing the marker file; `.wh.<name>` creates a zero-device character node and chowns it, suppressing the marker file.

## State and Persistence
The file reads and writes overlay xattrs, creates character-device whiteouts, applies ownership, and changes permissions. `GetOverlayXattrName` from `archive.go` selects trusted or user overlay xattr namespace based on rootless state.

## Dependencies and Integration Points
Dependencies include `archive/tar`, `os`, `filepath`, `strings`, `syscall`, `idtools`, `system`, and `x/sys/unix`. The code is invoked by `tarWriter.prepareAddFile` and `Unpack` when `TarOptions.WhiteoutFormat` is `OverlayWhiteoutFormat`.

## Risks and Edge Cases
Whiteout conversion is subtle around lower layers, parent-directory whiteouts, and nested whiteout entries. Device creation may fail in restricted environments. `isWhiteOut` assumes `stat.Sys()` is `*syscall.Stat_t`. Incorrect opaque handling can change layer deletion semantics.

## Test Signals
`archive_linux_test.go` validates overlay-to-overlay round trips, overlay-to-AUFS extraction, nested whiteouts, modes, opaque xattrs, and whiteout device preservation.
