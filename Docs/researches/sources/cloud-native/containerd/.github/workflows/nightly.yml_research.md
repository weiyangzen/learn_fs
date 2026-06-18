# sources/cloud-native/containerd/.github/workflows/nightly.yml

## Purpose
This workflow performs scheduled and self-test nightly binary builds across Linux architectures and Windows amd64.

## Important APIs, Types, And Functions
Linux builds target amd64, arm64, s390x, ppc64le, and riscv64 using crossbuild packages and `make binaries`. Windows builds amd64 on `windows-latest`. Artifacts are uploaded per platform.

## Control Flow
On daily schedule or PR changes to the workflow, Linux checkout/install steps set GOPATH/PATH, install cross compilers, build each arch into separate `bin_*` directories, and upload each. Windows checks out, installs Go, sets env, builds, and uploads `bin/`.

## State And Persistence
Persistent outputs are Actions build artifacts. Runner state includes cross compiler packages and build directories.

## Dependencies And Integration Points
It uses the local Go action, Makefile `binaries`, crossbuild-essential packages, and Actions artifacts.

## Risks
Nightly does not run full tests; it detects build regressions. Cross compiler package availability and runner image changes can affect results.

## Test Signals
Successful artifact upload for each architecture is the main signal.
