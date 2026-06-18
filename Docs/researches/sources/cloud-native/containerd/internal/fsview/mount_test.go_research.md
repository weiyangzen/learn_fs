# sources/cloud-native/containerd/internal/fsview/mount_test.go

## Purpose
Tests fsview mount resolution over bind, EROFS, overlay, and formatted overlay mounts.

## Important APIs, Types, And Functions
Includes helpers for `mkfs.erofs` availability and creating EROFS layers from tar fixtures. Tests call `FSMounts`, `NewOverlayFS`, and read files through returned views.

## Control Flow
The tests create temporary directories/layers, build mount slices, resolve views, read expected paths, and check absence of hidden/whiteouted paths.

## State And Persistence
Creates temporary directories and EROFS layer files. Views are closed with defer.

## Dependencies And Integration Points
Depends on `mkfs.erofs` for some cases, the EROFS fsview plugin import, `tartest`, and containerd mount structs.

## Risks
External command/version dependency causes skips. The test file is integration-heavy and platform-sensitive.

## Test Signals
Good coverage for last-mount selection, EROFS reading, overlay composition, and whiteout/opaque semantics.
