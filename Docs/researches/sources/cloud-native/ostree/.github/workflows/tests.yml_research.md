<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/tests.yml -->
## sources/cloud-native/ostree/.github/workflows/tests.yml

### Purpose
This is the main C/autotools CI workflow for OSTree, covering style, minimal feature builds, Fedora builds, and a Linux distribution matrix.

### APIs, Types, and Control Flow
Jobs include `codestyle` for submodule commit-message policy, `clang-format` through `just clang-format-check`, `minimal` for a broad set of disabled optional dependencies, `build-c` for a Fedora-style build/install artifact, and a matrix `tests` job. The matrix spans Debian stable/testing, i386 Debian, Ubuntu rolling, feature variants for curl/libsoup/FUSE/static prepare-root/libsystemd/openssl/ed25519, and passes image-specific package/configure options into `ci/gh-install.sh` and `ci/gh-build.sh`.

### State, Dependencies, and Integration
It uses containerized runners, submodules, distro package managers, non-root builder users, a named volume mounted at `/test-tmp`, and uploaded install tarballs. It integrates the repository shell CI scripts with GitHub Actions matrix metadata.

### Risks and Test Signals
The matrix is sensitive to package names, seccomp behavior, Docker image freshness, and architecture runner quirks. Several checkout action versions are older. The key test signal is cross-distro `make check` success under non-overlayfs temp storage and with `MAKEFLAGS=-j2`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/tests.yml -->
