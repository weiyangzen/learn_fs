# sources/cloud-native/buildkit/.github/workflows/compatibility-releases.yml

## Purpose
Runs compatibility tests against BuildKit release combinations. It triggers on manual dispatch, PRs, and pushes to master/release branches.

## APIs, Flow, And State
Single `compatibility` job checks out code, exposes GitHub runtime for cache, sets up arm64 QEMU and Buildx, builds `integration-tests-base` and `integration-tests`, then runs `./hack/test-compatibility-releases` with a fixed test image name and disabled test image build.

## Dependencies And Integration
Depends on Buildx, bake targets, QEMU arm64, GitHub Actions cache, and the `hack/test-compatibility-releases` script. It shares cache scope with integration tests.

## Risks And Test Signals
Compatibility signal is only as good as the release list in the hack script and the current test image. Cache or emulation issues can mask compatibility failures. The workflow produces pass/fail logs rather than persistent artifacts.
