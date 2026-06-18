# sources/cloud-native/containers-storage/drivers/overlay/check_116.go

## Purpose
`check_116.go` scans an overlay storage home for artifacts that indicate prior use of a mount program such as fuse-overlayfs.

## Important APIs, Types, And Functions
`scanForMountProgramIndicators(home string) (detected bool, err error)` walks the tree looking for whiteout-prefixed names or directory xattrs with `user.fuseoverlayfs.` or `user.containers.` prefixes.

## Control Flow
The walk stops early with `fs.SkipDir` once an indicator is detected. Directory xattrs are listed with `system.Llistxattr`; unsupported xattrs are ignored.

## State And Persistence
The function is read-only. It inspects existing file names and xattrs.

## Dependencies And Integration Points
It depends on `archive.WhiteoutPrefix`, `system.Llistxattr`, `filepath.WalkDir`, and build-time Linux support. Overlay initialization can use it for compatibility decisions.

## Risks
Large storage trees can make scans expensive if no indicator is found. Read errors abort the scan. Detection is heuristic and may miss future mount-program markers.

## Test Signals
No direct tests in this subset; behavior is inferred through overlay initialization paths.
