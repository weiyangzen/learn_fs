<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/format_test.go -->
# sources/cloud-native/containerd/core/mount/manager/format_test.go

Purpose: unit-tests the `mountFormatter` transformer against synthetic active mounts.

Important APIs/types/functions: `TestFormatMount` constructs five `mount.ActiveMount` entries with predictable `Source`, `Target`, and `MountPoint` values, then table-tests `mountFormatter{}.Transform`.

Control flow: each case runs the transformer and compares the whole returned `mount.Mount` with the expected struct using `assert.Equal`.

State and persistence: no external state; all test data is in-memory.

Dependencies and integration points: validates the transformer contract expected by `manager.go`, especially that later overlay mounts can reference earlier manager-activated mount points.

Risks covered: verifies no formatting leaves mounts unchanged, overlay ranges preserve intended ordering, reverse overlay ranges work, and source/target references use the correct active mount fields.

Test signals: positive-only coverage. It does not cover malformed templates, out-of-range indexes, or invalid overlay ranges, so error-path confidence comes from implementation inspection rather than tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/format_test.go -->
