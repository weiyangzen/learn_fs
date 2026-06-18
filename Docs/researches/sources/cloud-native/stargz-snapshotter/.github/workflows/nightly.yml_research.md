# sources/cloud-native/stargz-snapshotter/.github/workflows/nightly.yml

## Purpose
The nightly workflow runs compatibility and integration tests against containerd main and selected runtime environments on a daily schedule and on changes to the workflow.

## Important APIs, Types, and Functions
Global env sets BuildKit and `DOCKER_BUILD_ARGS=--build-arg=CONTAINERD_VERSION=main`. Jobs include integration, optimize, kind, CRI auth, CRI validation with containerd and CRI-O, and k3s. Several jobs install `apache2-utils`; CRI-O installs Docker and disables swap; k3s installs Go, k3d, yq, and htpasswd.

## Control Flow, State, and Persistence
Each job checks out the repo and invokes a Makefile target such as `make integration`, `make test-optimize`, `make test-kind`, `make test-criauth`, `make test-cri-containerd`, `make test-cri-o`, or `make test-k3s`.

## Dependencies and Integration Points
The workflow integrates GitHub Actions with Docker-based integration scripts, containerd main builds, private registry setup, CRI-O, k3s, and related test scripts.

## Risks and Test Signals
Because it tracks containerd main, failures may indicate upstream breakage rather than local changes. Several installation steps fetch scripts/binaries from the network. Job names include a typo in "Varidate" but behavior is unaffected. The nightly signal is broad runtime compatibility.
