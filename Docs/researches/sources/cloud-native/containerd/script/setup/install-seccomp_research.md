<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-seccomp -->
# sources/cloud-native/containerd/script/setup/install-seccomp

- Purpose: Builds and installs libseccomp `2.5.5` into `/usr/local`.
- Important behavior: Downloads release tarball, configures, makes, installs with sudo, runs `ldconfig`, and removes the temp directory.
- Control flow and state: Temporary source extraction followed by system library install.
- Dependencies and integration: Requires curl, tar, compiler toolchain, make, sudo, and dynamic linker cache updates. Supports runc/containerd seccomp build tags and tests.
- Risks: No checksum verification; global library install can override distro packages; build prerequisites are implicit.
- Test signals: Successful seccomp-enabled runtime build and seccomp integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-seccomp -->
