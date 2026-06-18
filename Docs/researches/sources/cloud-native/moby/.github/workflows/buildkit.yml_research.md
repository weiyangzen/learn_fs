<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/buildkit.yml -->
# sources/cloud-native/moby/.github/workflows/buildkit.yml

## Purpose
Builds Moby daemon binaries and runs the upstream BuildKit integration test suite against those binaries on Linux and Windows, validating compatibility between Moby's dockerd and the BuildKit version selected by `hack/buildkit-ref`.

## Important APIs, Types, And Functions
- Jobs: `validate-dco`, `build-linux`, `test-linux`, `build-windows`, and `test-windows`.
- Linux build uses Bake target `binary` and uploads `./build`.
- Linux tests checkout Moby and BuildKit, expose GitHub runtime cache env, build BuildKit integration test image, and run `./hack/test integration`.
- Windows build produces `docker.exe`, `dockerd.exe`, registry, BuildKit `buildctl`, and containerd artifacts.
- Windows test matrix slices BuildKit packages, especially `frontend/dockerfile#1-12` through `#12-12`.

## Control Flow
DCO gates builds. Linux builds upload Moby binaries, then BuildKit tests download them into `buildkit/build/moby`, reset Docker daemon config, build the BuildKit test image, and run package/worker-specific tests. Windows builds create artifacts through `Dockerfile.windows`, check out BuildKit master for `buildctl`, then Windows tests download artifacts, compute package/test flags, and run `gotestsum` against BuildKit with `TEST_DOCKERD_BINARY` pointing to Moby `dockerd`.

## State And Persistence
Artifacts persist for one day. BuildKit cache runtime variables expose GitHub Actions cache service to tests. Windows test reports are placed under `buildkit/bin/testreports`.

## Dependencies And Integration Points
Integrates Moby, BuildKit, Docker Buildx/Bake, GitHub runtime cache, QEMU, Go setup, registry binary, and Moby's `hack/buildkit-ref` mapping.

## Risks And Edge Cases
It mixes Moby's selected BuildKit ref with BuildKit master for Windows `buildctl`, which can drift. Disabled features remove azblob/s3 and merge_diff in some workers. Windows package slicing requires correct `TESTFLAGS` construction. Tests are skipped for validate-only PRs.

## Test Signals
Build artifact checks and BuildKit integration package results are the core signals. Failures show incompatibility in BuildKit client/frontend/solver behavior against Moby dockerd.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/buildkit.yml -->
