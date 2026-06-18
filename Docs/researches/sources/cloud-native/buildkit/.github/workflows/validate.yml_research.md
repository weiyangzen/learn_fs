# sources/cloud-native/buildkit/.github/workflows/validate.yml

## Purpose
Runs BuildKit validation bake targets across platforms selected from the bake definition.

## APIs, Flow, And State
`prepare` checks out the repo, asks `docker/bake-action/subaction/matrix` for the `validate` target platforms, then enriches entries with either arm or x86 runners based on platform and repository privacy. `validate` sets up Buildx and executes the target/platform pair.

## Dependencies And Integration
Depends on bake target `validate`, Buildx, the BuildKit setup image, and optional public `ubuntu-24.04-arm` runners. Environment toggles enable multi-platform lint/archutil validation only for `moby/buildkit`.

## Risks And Test Signals
Dynamic bake matrices can hide validation gaps if bake target metadata drifts. Runner selection must avoid unavailable arm runners for private repositories. Test signal is each bake validation target status.
