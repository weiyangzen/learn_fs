# sources/cloud-native/stargz-snapshotter/.github/workflows/tests.yml

## Purpose
The main test workflow runs build, unit tests, linting, integration matrices, runtime validation, IPFS/k3s/podman scenarios, benchmark-adjacent workflow tests, and CNCF/containerd project checks on pushes to main and pull requests.

## Important APIs, Types, and Functions
Jobs include `build`, `test`, `linter`, `integration`, `test-optimize`, `test-kind`, `test-criauth`, `test-cri-containerd`, `test-cri-cri-o`, `test-podman`, `test-k3s`, `test-ipfs`, `test-k3s-argo-workflow`, and `project`. Matrix axes cover containerd release vs main, builtin snapshotter, metadata store, fuse passthrough, fuse manager, transfer service, and CRI-O metadata store. Project checks run `containerd/project-checks`, generated-code validation, patent check, and vendor validation.

## Control Flow, State, and Persistence
Most jobs checkout and invoke Makefile targets. Some jobs install external tools, remove runner disk-heavy directories, collect Azure metadata, or upload artifacts. Matrix exclusions bound incompatible combinations.

## Dependencies and Integration Points
The workflow depends on GitHub Actions, Go setup, golangci-lint action, Docker/apt/network installers, containerd project checks, Makefile targets, and scripts under `script/`.

## Risks and Test Signals
This is a high-signal but expensive workflow. Several steps fetch network scripts or binaries. Disk cleanup in the Argo job is a runner-specific workaround. Matrix exclusions encode important compatibility constraints and should be maintained alongside feature flags.
