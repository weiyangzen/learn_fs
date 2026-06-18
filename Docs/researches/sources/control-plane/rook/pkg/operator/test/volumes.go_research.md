# sources/control-plane/rook/pkg/operator/test/volumes.go

## Purpose
`volumes.go` provides reusable volume and volume-mount assertions for Rook pod spec tests.

## Important APIs, Types, and Functions
Simple helpers include `VolumeExists()`, `VolumeIsEmptyDir()`, `VolumeIsHostPath()`, and `VolumeMountExists()`. Human-readable helpers format volumes/mounts for assertion messages. `VolumesSpec`, `MountsSpec`, and `VolumesAndMountsTestDefinition` model full checks, and `TestMountsMatchVolumes()` verifies every mount has a volume and every volume is used. Internal `getVolume()` and `getMount()` perform lookup.

## Control Flow, State, and Persistence
The helpers scan slices and report errors or `testing.T` assertions. Lookups return pointers to range variable copies, so they are read-only for practical purposes.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 volume types and testify. It integrates with `PodSpecTester.AssertVolumesAndMountsMatch()`.

## Risks
The full match test treats any unused volume as an error, which is good for strict specs but can be too strict for conditional templates. It recognizes EmptyDir and HostPath specifically; other volume sources are shown generically.

## Test Signals
`volumes_test.go` covers existence, EmptyDir/HostPath type checks, wrong HostPath paths, dual-source errors, and missing mounts.
