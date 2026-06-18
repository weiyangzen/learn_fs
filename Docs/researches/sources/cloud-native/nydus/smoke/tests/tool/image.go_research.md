# sources/cloud-native/nydus/smoke/tests/tool/image.go

## Purpose
This helper manages local registry image preparation and simple image conversion for smoke tests.

## Important APIs, Types, And Functions
`Registry` stores the Docker registry container ID. `NewRegistry` runs `docker run -d -it --rm -p <REGISTRY_PORT>:5000 registry:2`. `Destroy` removes that container. `PrepareImage` maps a source to `localhost:<port>/<source>`, reuses it if already pullable, otherwise tags/pulls/pushes it. `ConvertImage` prepares a workdir and runs `nydusify convert` with context-selected fs version and optional OCI ref.

## Control Flow
Package setup starts the registry. Tests call `PrepareImage` to ensure a source image exists in the local registry, then call `ConvertImage` for Nydus targets when needed.

## State And Persistence
State includes a Docker registry container and pushed image tags in that registry. `ConvertImage` creates and destroys a workdir but leaves target image state in the registry/runtime.

## Dependencies And Integration Points
It integrates Docker, registry:2, `nydusify`, `nydus-image`, and the shared `Context`. It is used by image, commit, compatibility, performance, and takeover tests.

## Risks
Image references are embedded in shell commands without escaping. `PrepareImage` assumes target pull failure means it should tag/pull/push. Registry cleanup removes the container, losing pushed images after the package test run.

## Test Signals
Signals are successful Docker pull/tag/push and successful `nydusify convert` command exit.
