# sources/cloud-native/containerd/integration/images/volume-ownership/Makefile

## Purpose

This Makefile builds and publishes multi-architecture `ghcr.io/containerd/volume-ownership:2.1` fixture images for Linux and optionally Windows. The fixture supports ownership, image pull timeout, and volume behavior tests.

## Important APIs, Types, And Functions

- Build variables mirror the volume-copy-up Makefile: `PROJ`, `VERSION`, `IMAGE`, `OS`, `ARCH`, `OSVERSION`, and `OUTPUT_TYPE`.
- `build-tools` compiles `tools/get_owner_windows.go` for Windows image builds.
- `clean-tools` removes the generated helper executable.
- `build`, `push`, `build-local`, `build-registry`, `container`, and `push-manifest` orchestrate image creation.

## Control Flow

Linux local builds use buildx for all Linux architectures. Registry builds compile the Windows owner helper first, build all enabled Linux and Windows images, clean the helper, then create/push a manifest list. Windows builds are enabled when `REMOTE_DOCKER_URL` is set.

## State And Persistence Behavior

It creates Docker/buildx images, optional helper binaries, and registry manifests. The generated Windows helper is cleaned after registry builds.

## Dependencies And Integration Points

It depends on Docker/buildx, Go for the Windows helper, optional gcloud auth, optional remote Windows Docker, and Dockerfiles in the fixture directory. Integration tests reference the published image by default.

## Risks And Edge Cases

The Windows helper build uses `-mod=vendor`, so vendor state matters. Manifest OS version annotation uses shell parsing. Failed builds can leave `tools/get_owner_windows.exe` until `clean-tools` runs.

## Test Signals

Downstream tests validate this image by pulling it, using it for image pull timeout traffic, and running containers with image-defined volumes.
