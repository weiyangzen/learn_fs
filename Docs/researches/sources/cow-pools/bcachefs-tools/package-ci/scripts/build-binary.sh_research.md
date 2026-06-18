# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-binary.sh

## Purpose
Build binary Debian packages for one distro/architecture pair inside podman.

## Supported Inputs
- Distros: `unstable`, `forky`, `trixie`, `plucky`, `questing`
- Architectures: `amd64`, `ppc64el`, `arm64`
- Source directory containing a `.dsc`
- Result directory
- Rust version

## Workflow
- Selects a Debian/Ubuntu base image.
- Enables ppc64el cross-build setup when needed.
- Finds the source `.dsc`.
- Builds or reuses a cached podman image keyed by distro, arch, Rust version, and cache version.
- Installs build-essential, devscripts, dpkg tools, build dependencies, and cross tools.
- Installs rustup Rust if the distro Rust is older than required.
- Adds cargo cross-linker config for ppc64el.
- Runs `dpkg-buildpackage -b`.
- Copies `.deb`, `.ddeb`, `.changes`, and `.buildinfo` to result dir.

## Implementation Notes
- Cache rebuild can be forced by `REBUILD_CACHE=1` or marker files.
- Uses `seccomp=unconfined`, `apparmor=unconfined`, `/dev/fuse`, and `SYS_ADMIN` for the build container.
- Caps parallelism through `DEB_BUILD_OPTIONS=parallel=$MAX_PARALLEL`, default 16.
- Works around Debian's cargo wrapper discarding `RUSTFLAGS` by writing `.cargo/config.toml`.

## Dependencies
Requires podman, apt, dpkg-dev/devscripts, rustup as needed, and cross-compilation packages for ppc64el.
