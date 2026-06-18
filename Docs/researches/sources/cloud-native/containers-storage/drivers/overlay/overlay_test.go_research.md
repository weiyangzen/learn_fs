<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_test.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay_test.go

## Purpose
`overlay_test.go` defines Linux graphdriver conformance tests and performance benchmarks for the overlay driver.

## Important APIs, Types, And Functions
`init` swaps archive helpers to non-chroot implementations for easier debugging and initializes reexec. `skipIfNaive` skips native-diff-only tests when the host cannot support native diff. Tests include `TestContainersOverlayXattr`, `TestSupportsShifting`, the standard `graphtest` lifecycle tests, and benchmarks for exists/get/diff/apply/deep-layer scenarios.

## Control Flow
The suite initializes a shared driver between `TestOverlaySetup` and `TestOverlayTeardown`, then runs create, base/snapshot, template, deep read, diff/apply, changes, echo, and layer list checks. `TestContainersOverlayXattr` intentionally runs before setup because it uses a distinct `force_mask=700` configuration. `TestSupportsShifting` compares contiguous and non-contiguous mappings with and without `mount_program`.

## State And Persistence
Tests create temporary graphdriver storage through `graphtest` and rely on real overlay support where available. They may mount filesystems and write layer directories, xattrs, and diff contents under test roots.

## Dependencies And Integration Points
The tests depend on `drivers/graphtest`, archive package hooks, reexec, idtools, and testify. They are integration-like and require Linux overlay capabilities; native diff tests skip when unsupported.

## Risks And Test Signals
The file provides good broad behavioral coverage but limited direct coverage for composefs, additional layer stores, feature cache files, stale symlink repair, quota enforcement, and mount-data page-size fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay_test.go -->
