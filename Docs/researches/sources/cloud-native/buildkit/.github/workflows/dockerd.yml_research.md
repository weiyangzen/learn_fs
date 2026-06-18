# sources/cloud-native/buildkit/.github/workflows/dockerd.yml

## Purpose
Manual workflow for testing BuildKit against a specified Docker daemon version or source URL.

## APIs, Flow, And State
Input `version` is interpreted as a URL if parseable; URLs are built with `docker/build-push-action`, while version strings download static Docker binaries. The `prepare` job uploads a `dockerd` artifact. The `test` job downloads it, fixes permissions, then runs `./hack/test` across dockerd worker modes and selected packages with Docker daemon network flags.

## Dependencies And Integration
Depends on Buildx, Docker binary archives or source build contexts, QEMU, GitHub runtime cache, and BuildKit integration tests. Matrix workers are `dockerd` and `dockerd-containerd`.

## Risks And Test Signals
Running user-supplied URLs as build contexts is powerful and should remain manual. Network settings are fixed to avoid address conflicts but may still collide in runner environments. Signals are integration test results plus the uploaded daemon artifact.
