# sources/cloud-native/buildkit/.github/workflows/test-os.yml

## Purpose
Builds and tests BuildKit on non-default operating systems, mainly Windows and FreeBSD, and performs sandbox Linux builds.

## APIs, Flow, And State
The `build` job cross-builds `windows/amd64` and `freebsd/amd64` binaries via bake and uploads artifacts. `test-windows-amd64` downloads binaries, shards package tests, runs `gotestsum`, uploads Codecov and test reports. `test-freebsd-amd64` downloads FreeBSD binaries, installs Vagrant/libvirt, boots a FreeBSD VM, retries smoke provisioning, and prints BuildKit/containerd logs. `sandbox-build` verifies integration test base builds on linux/amd64 and arm64 for the canonical repo.

## Dependencies And Integration
Depends on Buildx, QEMU indirectly through bake images, GitHub cache/artifacts, Codecov, gotest annotations, Vagrant, libvirt, and `hack/Vagrantfile.freebsd`.

## Risks And Test Signals
High flake risk from Windows runners, Vagrant/libvirt installation, FreeBSD VM boot, and cache state. Persistent state includes artifacts, test reports, Codecov data, and runner cache. Strong test signals cover cross-compiled binaries, Windows integration/unit behavior, FreeBSD smoke behavior, and Linux sandbox buildability.
