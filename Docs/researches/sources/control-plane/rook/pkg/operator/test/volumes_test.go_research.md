# sources/control-plane/rook/pkg/operator/test/volumes_test.go

## Purpose
This file tests basic volume and volume-mount assertion helpers.

## Important APIs, Types, and Functions
`TestVolumeExists()`, `TestVolumeIsEmptyDir()`, `TestVolumeIsHostPath()`, and `TestVolumeMountExists()` cover success and failure cases. `vols()` is a small slice builder.

## Control Flow, State, and Persistence
Tests are table-driven and pure. They assert only the presence or absence of errors.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 volume types and Go testing. These tests protect the helper library used by many operator pod-spec tests.

## Risks
Human-readable formatting and full `VolumesAndMountsTestDefinition.TestMountsMatchVolumes()` are not directly tested. Pointer-to-copy behavior of `getVolume()` and `getMount()` is not covered.

## Test Signals
Signals include correct detection of missing volumes/mounts, wrong source type, wrong HostPath path, and invalid dual EmptyDir/HostPath sources.
