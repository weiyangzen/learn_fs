# sources/cloud-native/containerd/internal/fsview/overlay.go

## Purpose
Implements a userspace overlay `fs.FS` over ordered layers, including directory merging, whiteouts, opaque directories, and symlink resolution.

## Important APIs, Types, And Functions
`NewOverlayFS` returns an `overlayFS`. `Open`, `Lstat`, and `ReadLink` implement view operations. Internal helpers include `resolve`, `openDirect`, `lstatDirect`, `readlinkDirect`, `hasOpaqueParent`, and `overlayDir.ReadDir`.

## Control Flow
Paths are validated, symlinks are resolved component-by-component across the overlay, then direct open/stat/readlink scans layers from upper to lower, stopping at whiteouts or opaque parents. Directories collect mergeable layers and sorted unique entries.

## State And Persistence
State is only the ordered layer list and per-directory read offsets/cache. No writes are performed.

## Dependencies And Integration Points
Uses `io/fs`, path manipulation, registered xattr/whiteout helpers, and platform-specific overlay helpers. It underpins fsview overlay and formatted EROFS overlay behavior.

## Risks
Symlink resolution is complex and capped at 255 to avoid loops. Layers without `fs.ReadLinkFS` degrade final symlink behavior. Whiteout/opaque detection depends on platform xattrs or registered handlers.

## Test Signals
Overlay tests cover whiteouts, opaque directories, symlink chains, absolute symlinks across layers, directory/file replacement, and EROFS whiteouts.
