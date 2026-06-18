# sources/cloud-native/containerd/integration/images/volume-ownership/Dockerfile

## Purpose

This fixture image defines a volume directory owned by `nobody:nogroup`, used to test image-defined volume ownership and overlay volatile behavior.

## Important APIs, Types, And Functions

- `FROM ubuntu` provides the base.
- A `RUN` command creates `/test_dir` and changes ownership to `nobody:nogroup`.
- `VOLUME /test_dir` declares the image volume.

## Control Flow

At build time, the image creates and changes ownership of `/test_dir`. At runtime, CRI image-defined volume handling should create/mount a volume using this metadata.

## State And Persistence Behavior

The image layer persists directory ownership and the config persists the volume declaration. No runtime state is managed in the Dockerfile.

## Dependencies And Integration Points

It is built by the sibling Makefile and used by `container_volume_linux_test.go`, image pull timeout tests, and image fixture references in `image_list.go`.

## Risks And Edge Cases

The image assumes Ubuntu contains `nobody:nogroup`. Changing the volume path breaks tests that refer to `/test_dir` or the published fixture semantics.

## Test Signals

Tests using `images.VolumeOwnership` validate that containerd can pull/run the image and handle its volume declaration under specific snapshotter settings.
