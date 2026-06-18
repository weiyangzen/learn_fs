<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/cimfs_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/windows/cimfs_test.go

## Purpose
Tests parsing of CimFS-related mount options used by Windows CimFS snapshotters and mount handlers.

## Important APIs, Types, And Functions
`TestGetOptionByPrefix` constructs a `mount.Mount` with `LayerCimPathFlag` and `ParentLayerCimPathsFlag`, then calls `mount.GetCimPath` and `mount.GetParentCimPaths`.

## Control Flow
The test marshals two parent CIM paths to JSON, appends both options to a CimFS mount, parses them back, and asserts exact values and order.

## State And Persistence
No filesystem state; all data is in-memory strings.

## Dependencies And Integration Points
Depends on containerd `core/mount` CimFS flag helpers and Windows build tags.

## Risks And Edge Cases
This only validates option parsing, not actual CimFS mounting, layer creation, or parent path existence.

## Test Signals
Protects the string contract between snapshotters that emit CimFS mount options and consumers that parse them.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/windows/cimfs_test.go -->
