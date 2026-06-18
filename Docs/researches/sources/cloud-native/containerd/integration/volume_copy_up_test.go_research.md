# sources/cloud-native/containerd/integration/volume_copy_up_test.go

## Purpose

`volume_copy_up_test.go` verifies image-defined volume copy-up behavior and ownership preservation on Linux and Windows.

## Important APIs, Types, and Functions

- Constants describe the expected Windows `ContainerUser` SID.
- `volumeFile` and `containerVolume` describe expected volume contents.
- `TestVolumeCopyUp` checks host bind volume mappings, copied files, in-container reads, and host-visible writes.
- `TestVolumeOwnership` checks in-container and host ownership of image-defined volumes.
- `getContainerBindVolumes` reads verbose CRI container status, unmarshals runtime spec mounts, and returns destination-to-source mappings.

## Control Flow

The copy-up test creates a sandbox and container from the volume-copy-up image, starts it, defines OS-specific expected volume paths/files, reads CRI verbose status to find host bind paths, checks copied contents both through host filesystem and `ExecSync`, writes new content from inside the container, and confirms the host path changes. The ownership test starts a second image, checks ownership inside the container, maps the host path, and calls OS-specific `getOwnership`.

## State and Persistence Behavior

The tests validate generated bind mount directories and runtime spec mount metadata. They also validate that writes through the container persist to the host volume path.

## Dependencies and Integration Points

They depend on CRI runtime service, raw verbose status, OCI runtime spec mount JSON, image fixtures, OS-specific ownership helpers, and exec sync.

## Risks and Edge Cases

Path formats differ sharply by OS, including odd Linux paths with colons and Windows drive roots. The test depends on fixture image contents and helper binaries such as Windows `get_owner.exe`.

## Test Signals

Failures point to regressions in image volume detection, copy-up, bind mount injection, runtime spec reporting, host/container write propagation, or ownership handling.
