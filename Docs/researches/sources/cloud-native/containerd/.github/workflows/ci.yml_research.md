# sources/cloud-native/containerd/.github/workflows/ci.yml

## Purpose
This is the primary containerd CI workflow for pull requests and merge queue entries. It runs linting, project checks, protobuf checks, manpage generation, crossbuilds, binaries, Linux/Windows/macOS tests, Vagrant distro integration tests, CRI-in-userns tests, and Kubernetes node e2e.

## Important APIs, Types, And Functions
Major jobs are `linters`, `project`, `protos`, `man`, `crossbuild`, `binaries`, `integration-windows`, `integration-linux`, `integration-vagrant`, `tests-cri-in-userns`, `tests-mac-os`, reusable `node-e2e`, and final `results`. The workflow uses the local Go action, pinned checkout/upload/cache actions, `golangci-lint-action`, `containerd/project-checks`, Makefile targets, setup scripts, Vagrant/libvirt, Podman, cri-tools, CRIU, erofs-utils, and artifact uploads.

## Control Flow
Static gates run first (`project`, `linters`, `protos`, `man`). Build/test jobs depend on those gates. Linux integration installs runtime dependencies, builds newer erofs-utils, loads EROFS and dm-verity modules, installs containerd, runs unit/root/integration/CRI/critest/checkpoint tests, and uploads logs. Windows integration builds with `mingw32-make`, installs CNI, runs root/integration/CRI/critest, and uploads results. Vagrant tests exercise Fedora and AlmaLinux boxes with cgroupfs/systemd and runc/crun combinations. The `results` job collapses required statuses.

## State And Persistence
The workflow persists artifacts for test reports and logs. Runner state includes installed packages, kernel modules, containerd services, Vagrant boxes, test images, and temporary reports. It does not modify repository state.

## Dependencies And Integration Points
It is the central integration point for `.golangci.yml`, `Makefile`, scripts under `script/setup` and `script/test`, generated protobufs, Kubernetes cri-tools, EROFS tools, and the reusable node e2e workflow.

## Risks
The workflow is broad and sensitive to external package repositories, GitHub runner images, Azure/Windows quirks, kernel module availability, Vagrant box availability, and flaky CRI tests. Some jobs are skipped for merge queue or private ARM runners. The Linux job builds erofs-utils from a versioned tarball due to package age. Required-check masking is handled by the `results` job, so `needs` must stay aligned with intended required jobs.

## Test Signals
Passing CI itself is the signal. Important granular signals are `make verify-vendor`, `make check-protos`, lint results, crossbuilds, unit/root tests, serial and parallel integration tests, CRI integration, critest reports, checkpoint/restore, Vagrant distro coverage, macOS unit tests, and node e2e logs.
