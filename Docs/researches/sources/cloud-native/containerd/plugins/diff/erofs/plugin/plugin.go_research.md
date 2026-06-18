# sources/cloud-native/containerd/plugins/diff/erofs/plugin/plugin.go

## Purpose
Registers the EROFS diff plugin and validates host/tooling support before exposing an EROFS comparer/applier.

## Important APIs, Types, And Functions
`Config` exposes `MkfsOptions`, `EnableTarIndex`, and `EnableDmverity`. `init` registers the `erofs` diff plugin and builds `erofs.NewErofsDiffer` with configured options.

## Control Flow
Startup verifies `mkfs.erofs` tar support, loads metadata DB, advertises Linux platform support plus an `erofs` OS feature variant, gets the content store, maps config fields to differ options, checks dm-verity support when requested, and returns the configured differ or skips the plugin when prerequisites are unavailable.

## State And Persistence
No direct persistence. It reads metadata DB only to obtain the content store. Plugin metadata advertises supported platforms/features.

## Dependencies And Integration Points
Depends on metadata, `internal/erofsutils`, `internal/dmverity`, platforms, plugin registry, and the EROFS differ package. The diff service uses this plugin according to platform-specific differ order.

## Risks
Host tool availability directly controls plugin loading. Enabling dm-verity can skip the plugin entirely if kernel support is missing. Platform metadata is manually adjusted to prefer EROFS-native images.

## Test Signals
No direct tests in this file. Dm-verity helper tests and integration tests with mkfs.erofs provide coverage.
