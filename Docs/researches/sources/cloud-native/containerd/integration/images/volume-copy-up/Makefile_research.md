# sources/cloud-native/containerd/integration/images/volume-copy-up/Makefile

## Purpose

This Makefile builds and publishes multi-architecture `ghcr.io/containerd/volume-copy-up:2.2` fixture images for Linux and optionally Windows. The fixture supports CRI volume copy-up integration tests.

## Important APIs, Types, And Functions

- Variables `PROJ`, `VERSION`, `IMAGE`, `OS`, `ARCH`, `OSVERSION`, and `OUTPUT_TYPE` parameterize builds.
- `build`, `build-local`, `build-registry`, `container`, and `push-manifest` are primary targets.
- Pattern target `sub-container-%` decomposes output/OS/arch/version tokens.
- `.container-linux-*` uses `docker buildx build`.
- `.container-windows-*` uses remote Docker arguments and `Dockerfile_windows`.

## Control Flow

`make build` selects buildx and builds all Linux architectures into the local Docker output. `make push` configures registry auth, builds registry outputs for all enabled OS/arch combinations, and pushes a manifest list. Windows builds are enabled only when `REMOTE_DOCKER_URL` is set and include OS version annotations in the final manifest.

## State And Persistence Behavior

The Makefile creates local Docker/buildx images or registry images and manifests. It does not manage source-tree state.

## Dependencies And Integration Points

It depends on Docker/buildx, optional gcloud auth, optional remote Windows Docker, and the Dockerfiles in the fixture directory. Integration tests reference the published image through `images.VolumeCopyUp`.

## Risks And Edge Cases

Manifest annotation relies on parsing `docker manifest inspect` output with grep/awk. Remote Windows builds require certificates and Hyper-V isolation. Local builds only cover Linux targets.

## Test Signals

The downstream test signal is that the published image contains the expected volume declarations and copied contents for volume-copy-up tests.
