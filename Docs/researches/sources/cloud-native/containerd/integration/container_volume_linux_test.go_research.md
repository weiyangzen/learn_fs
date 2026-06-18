# sources/cloud-native/containerd/integration/container_volume_linux_test.go

## Purpose

This Linux test validates that containers can run when the overlayfs snapshotter is configured with the `volatile` mount option and image-defined volumes are honored. It specifically exercises kernel support for volatile overlay mounts.

## Important APIs, Types, And Functions

- `TestRunContainerWithVolatileOption` is the sole test entry point.
- `kernelversion.GreaterEqualThan` gates the test to kernel 5.10 or newer.
- `newCtrdProc`, `pullImagesByCRI`, and `newPodTCtx` start an isolated containerd process and run a container against it.

## Control Flow

The test skips old kernels, writes a temporary containerd config enabling CRI image-defined volumes and setting overlayfs `mount_options = ["volatile"]`, starts a separate containerd process from that work directory, registers cleanup for pods and process shutdown, pulls the `VolumeOwnership` image, creates a pod test context, and runs a container executing `sleep 1d`.

## State And Persistence Behavior

It creates an isolated temporary containerd root/state directory and config file. All container and snapshot state is cleaned up with the test containerd process.

## Dependencies And Integration Points

It integrates with containerd process management helpers outside this file, CRI image pull/runtime services, overlayfs snapshotter configuration, kernel version detection, and the `ghcr.io/containerd/volume-ownership` fixture image.

## Risks And Edge Cases

The test assumes overlayfs is the active snapshotter and that the host kernel supports volatile semantics. It only proves container creation/start succeeds; detailed mount-option verification for image volumes is covered in `image_volume_linux_test.go`.

## Test Signals

Passing indicates the CRI/runtime path can create image-defined volumes and containers under overlayfs volatile mount configuration.
