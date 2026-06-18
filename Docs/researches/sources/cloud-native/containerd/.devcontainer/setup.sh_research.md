# sources/cloud-native/containerd/.devcontainer/setup.sh

## Purpose
This setup script installs runtime/test helper tools and builds/installs containerd inside the devcontainer.

## Important APIs, Types, And Functions
It calls repository scripts: `script/setup/install-seccomp`, `install-runc`, `install-cni`, `install-critools`, `install-failpoint-binaries`, `install-gotestsum`, and `install-teststat`. It then runs `make binaries GO_BUILD_FLAGS="-mod=vendor"` and `sudo -E PATH=$PATH make install`.

## Control Flow
With `set -eux`, any command failure stops provisioning. The CNI plugin version is extracted from `go.mod` by grepping `containernetworking/plugins`.

## State And Persistence
The script installs host/container-level binaries and builds repository artifacts under `bin/`. It also installs containerd into the configured prefix.

## Dependencies And Integration Points
It depends on the devcontainer image packages, repository setup scripts, vendored Go modules, and Makefile install semantics.

## Risks
The `grep ... go.mod | awk '{print $2}'` version extraction assumes module file format. Running with sudo and inherited PATH can install tools globally inside the container.

## Test Signals
Successful devcontainer creation, `containerd --version`, `runc --version`, CNI binaries presence, and `make test`/`make root-test` are relevant checks.
