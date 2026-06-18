<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release/build.sh -->
# sources/cloud-native/overlaybd/.github/workflows/release/build.sh

Purpose: Distro-aware package build script used inside release containers.

APIs and control flow: Positional args are `OS`, `PACKAGE_VERSION`, `RELEASE_NO`, and `COMMIT_ID`. The script installs dependencies with `apt`, `yum`, or `tdnf`, handles CentOS vault repos and toolset compilers, downloads a fixed CMake binary by architecture, configures CMake with package version/release and `OBD_VER`, builds, then runs `cpack --verbose`.

State and persistence: Creates `/usr/local/cmake-*`, a repository-local `build` directory, and generated RPM/DEB packages.

Dependencies and integration: Needs package managers, compilers, libaio, curl, OpenSSL, libnl3, e2fsprogs, zstd, rpm-build/dpkg tooling, and network access to cmake.org.

Risks and test signals: `--no-check-certificate` and external downloads reduce supply-chain assurance. Test signal is successful CMake configure, `make -j8`, and CPack output.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release/build.sh -->
