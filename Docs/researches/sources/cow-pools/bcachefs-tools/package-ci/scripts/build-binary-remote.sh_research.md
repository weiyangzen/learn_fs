# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/build-binary-remote.sh

## Purpose
Remote wrapper for binary `.deb` builds, intended for arm64 builds on `farm1`.

## Workflow
- Accepts host, distro, arch, commit, source dir, result dir, and Rust version.
- Creates remote work directories under `/tmp/bcachefs-ci/$commit/$distro-$arch`.
- Copies source artifacts and `build-binary.sh` to the remote host.
- Runs the normal binary build script remotely.
- Copies result artifacts back.
- Removes the remote work directory.

## Dependencies
Requires ssh/scp access and matching build scripts on the local side.
