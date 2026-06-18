# sources/cloud-native/containerd/plugins/mount/fsview/erofs/erofs.go

## Purpose
Registers an fsview handler that can inspect EROFS images without mounting them through the kernel.

## Important APIs, Types, And Functions
`handleMount` opens the EROFS source and extra `device=` readers, calls `erofs.Open`, and returns an `erofsView`. `erofsView.Close` closes all files. `getxattr` reads EROFS xattrs from `erofs.Stat`. `isWhiteout` identifies char-device whiteouts with rdev zero.

## Control Flow
The init function registers `handleMount`, `getxattr`, and `isWhiteout`. `handleMount` rejects non-EROFS mounts, opens source and extra devices, cleans up on error, requires `fs.ReadLinkFS`, and returns a closable read-link filesystem view.

## State And Persistence
No persistence. It opens file descriptors for EROFS images and closes them through the view.

## Dependencies And Integration Points
Integrates with `internal/fsview`, core mount types, `github.com/erofs/go-erofs`, xattr handling, and whiteout detection used by archive/diff logic.

## Risks
All opened readers must be closed on every error path. Only `device=` options are interpreted. If go-erofs does not expose expected `erofs.Stat`, xattr and whiteout detection return false.

## Test Signals
No direct tests in this subset. Covered indirectly by EROFS diff/view integration.
