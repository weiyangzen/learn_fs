<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/build.sh -->
## sources/cloud-native/ostree/ci/build.sh

### Purpose
This shared CI build script installs dependencies, chooses default configure options, hardens compiler flags, and performs a normal build.

### APIs, Types, and Control Flow
It rejects a `0000` umask, runs `ci/installdeps.sh`, adds Fedora default `--with-curl` unless soup/no-curl is requested, adds composefs and openssl for RHEL/Fedora-like systems, enables exclusive installed tests when curl/soup and a desktop testing runner are present, exports warning-as-error CFLAGS, and calls `build --enable-gtk-doc ${CONFIGOPTS:-}` from `libbuild.sh`.

### State, Dependencies, and Integration
It depends on `/etc/os-release` variables sourced by `libbuild.sh`, package installation helpers, autotools, and compiler toolchains. It mutates the build tree under the helper's target directory.

### Risks and Test Signals
The shell pattern `*--with-curl*|--with-soup*` appears asymmetric and may not match all soup-containing option strings as intended. Warning-as-error can expose distro compiler drift. Test signal is successful configured build with docs enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/build.sh -->
