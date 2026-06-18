# sources/cloud-native/nydus-snapshotter/Makefile

Purpose: build, package, install, test, and integration entry point.

Targets and flow: `build` compiles `containerd-nydus-grpc` and `nydus-overlayfs`; `static`/`static-release` build static binaries; `build-optimizer` builds the NRI plugin and Rust optimizer server; package targets tar binaries and checksums; install targets place binaries/config/systemd units; test targets run vet, golangci-lint, race unit tests, coverage, smoke, and privileged integration Docker runs.

State/dependencies: writes `bin`, `package`, `_out`, system paths under sudo, and uses Go/Rust/Docker/Nydus/containerd.

Integration points: consumed by CI, release, integration, and local installs.

Risks/tests: several targets mutate host `/etc`, `/usr/local/bin`, systemd, and Docker. Version metadata comes from git state and can include `.m` dirty suffix.
