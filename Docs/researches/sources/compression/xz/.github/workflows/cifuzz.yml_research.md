# sources/compression/xz/.github/workflows/cifuzz.yml

## Purpose
This workflow runs OSS-Fuzz CIFuzz for XZ on pushes to master and manual dispatch. It builds and runs fuzzers under address, undefined, and memory sanitizers.

## Important Control Flow
The single `CIFuzz` job uses a matrix over sanitizer values. It invokes `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master`, then `run_fuzzers@master` for 600 seconds with timeout and OOM reporting. If fuzzing fails after a successful build, artifacts from `./out/artifacts` are uploaded.

## State, Dependencies, and Integration
State is produced by OSS-Fuzz action containers under the runner workspace. The workflow depends on the external OSS-Fuzz GitHub actions and the `xz` project definition in OSS-Fuzz, using `language: c++` to match that definition even though XZ is C.

## Risks and Test Signals
It gives high-value sanitizer-backed fuzz regression signals but depends on external action behavior and a relatively short fuzzing window. Pinning to `@master` increases exposure to upstream action changes.
