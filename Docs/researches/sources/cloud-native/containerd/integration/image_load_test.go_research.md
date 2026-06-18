# sources/cloud-native/containerd/integration/image_load_test.go

## Purpose

This test verifies that an image saved as a tarball and imported directly into containerd's `k8s.io` namespace becomes visible to CRI and can be used to create a container.

## Important APIs, Types, And Functions

- `TestImageLoad` is the only test.
- External tools `docker` and `ctr` pull/save/import the image.
- `imageService.ImageStatus`, `imageService.RemoveImage`, and CRI runtime calls validate import visibility and usability.

## Control Flow

The test skips a known Windows Server 2025 host issue. It checks `docker` availability, pulls and saves BusyBox to a temporary tar, removes any existing CRI image, locates `ctr`, imports the tar into the configured containerd endpoint and `k8s.io` namespace using `--local=true` and a platform selector, then waits for CRI `ImageStatus` to see the image. Finally it creates and starts a container from that image and checks it is running.

## State And Persistence Behavior

The test mutates containerd image store state by importing a tarball. Temporary tarball state lives under `t.TempDir`. Container and sandbox state are cleaned up by shared helpers.

## Dependencies And Integration Points

It depends on Docker, `ctr`, containerd endpoint flags, platform-specific image manifests, CRI image reconciliation, and the test BusyBox image.

## Risks And Edge Cases

External CLI availability is a major host dependency. Docker image store behavior can save multi-platform artifacts, so the platform flag avoids missing manifest references. CRI visibility is asynchronous and requires polling.

## Test Signals

Passing confirms directly imported images are indexed by CRI and runnable.
