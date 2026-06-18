<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-rpm.sh -->
## sources/cloud-native/ostree/ci/build-rpm.sh

### Purpose
This script creates an OSTree source RPM and rebuilds binary RPMs in the current directory.

### APIs, Types, and Control Flow
It sources `libbuild.sh`, installs buildroot/rpmbuild/git dependencies when running as root, initializes submodules if needed, defaults Fedora builds to curl unless soup or no-curl is configured, enables exclusive installed tests when curl/soup and a desktop testing runner are available, runs `make -f ci/Makefile.dist-packaging srpm PACKAGE=libostree DISTGIT_NAME=ostree`, installs build dependencies if root, and rebuilds the SRPM with `ci/rpmbuild-cwd`, printing any `config.log` on failure.

### State, Dependencies, and Integration
It writes SRPM/RPM artifacts and build directories in the current tree. It integrates with Fedora packaging, `libbuild.sh`, package managers, and RPM build tooling.

### Risks and Test Signals
Non-root runs assume dependencies are already installed. Fedora default feature injection can surprise callers relying on implicit no-curl builds. Test signal is successful `rpmbuild --rebuild` and generated binary RPMs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-rpm.sh -->
