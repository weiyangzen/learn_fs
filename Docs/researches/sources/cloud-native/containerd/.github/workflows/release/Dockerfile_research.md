# sources/cloud-native/containerd/.github/workflows/release/Dockerfile

## Purpose
This Dockerfile builds cross-platform containerd release artifacts inside Docker Buildx.

## Important APIs, Types, And Functions
It defines `UBUNTU_VERSION`, `BASE_IMAGE`, `GO_VERSION=1.26.4`, and `GO_IMAGE`, imports `tonistiigi/xx:1.6.1`, installs build tools and target gcc through `xx-apt-get`, binds the Go toolchain from the Go image, wraps Go with `xx-go`, runs `make release static-release`, verifies binaries with `xx-verify`, checks the git tree, and exports `/releases` from a scratch stage.

## Control Flow
The release workflow passes target platform and release args. The Dockerfile builds a base with cross tooling, branches into `linux` or `windows` stages, copies the source, builds release artifacts for the target, verifies executable compatibility, fails if the build dirties the repository, and emits release files.

## State And Persistence
Persistent output is the release stage contents. Build cache mounts store Go build and module cache data during Buildx runs.

## Dependencies And Integration Points
It integrates with `.github/workflows/release.yml`, Makefile release targets, `tonistiigi/xx`, the Go container image, and Ubuntu package repositories.

## Risks
Base image and cross-toolchain availability affect reproducibility. The git dirty check can fail if generation during release changes tracked files. Windows CNI args are supplied externally and must match release workflow expectations.

## Test Signals
Buildx matrix success, `xx-verify` success for executables, and clean git status after `make release static-release` are key signals.
