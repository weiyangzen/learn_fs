# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-source.sh

## Purpose
Build source-only Debian package artifacts for a target commit.

## Workflow
- Clones the bcachefs-tools git repo into a temporary workdir.
- Checks out the requested commit.
- Computes package version from exact tag, latest tag, `.version`, commit hash, and UTC snapshot timestamp.
- Preserves a Debian epoch from `debian/changelog` if present.
- Starts a `debian:trixie-slim` podman container with cached rustup/cargo/apt directories.
- Installs source-build dependencies.
- Installs or updates rustup to the configured Rust version.
- Installs `cargo-vendor-filterer` if missing.
- Updates changelog with `dch`.
- Runs `dpkg-buildpackage -d -S -us -uc -nc`.
- Copies source artifacts to the result directory.

## Dependencies
Requires podman, git, Debian packaging tools, rustup, cargo-vendor-filterer, and network access for apt/cargo.
