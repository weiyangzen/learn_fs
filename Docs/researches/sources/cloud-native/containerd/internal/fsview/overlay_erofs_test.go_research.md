# sources/cloud-native/containerd/internal/fsview/overlay_erofs_test.go

## Purpose
Tests overlay semantics over EROFS-backed filesystem layers.

## Important APIs, Types, And Functions
Tests build or open EROFS layers, call `fsview.FSMounts` and `NewOverlayFS`, and inspect files, directory entries, and EROFS whiteout metadata.

## Control Flow
Cases verify base-layer reads, upper-over-lower precedence, whiteout hiding, opaque directory behavior, multiple EROFS layers, and mixed EROFS plus directory upper layers.

## State And Persistence
Creates temporary EROFS images and directories during tests.

## Dependencies And Integration Points
Depends on `mkfs.erofs`, `github.com/erofs/go-erofs`, the fsview EROFS plugin, and tartest fixtures.

## Risks
Tests skip or fail depending on external tool support. Whiteout assertions depend on EROFS stat representation.

## Test Signals
High-value integration coverage for the EROFS plugin plus userspace overlay semantics.
