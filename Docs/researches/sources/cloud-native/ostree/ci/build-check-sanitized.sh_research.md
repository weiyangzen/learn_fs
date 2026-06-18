<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-check-sanitized.sh -->
## sources/cloud-native/ostree/ci/build-check-sanitized.sh

### Purpose
This CI script builds OSTree with ASAN/UBSAN and runs unit tests.

### APIs, Types, and Control Flow
It enables strict shell options, sources `ci/libbuild.sh`, disables ASAN leak detection because of known global leaks, calls `build --disable-gtk-doc --with-curl --with-openssl --enable-sanitizers`, then runs `make check`.

### State, Dependencies, and Integration
It mutates the build tree through the shared `build` helper and writes normal test/build logs. It integrates with sanitizer-capable compilers and CI environments.

### Risks and Test Signals
Leak detection is disabled, so this catches memory errors/UB but not leaks. Test signal is sanitizer-clean `make check`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-check-sanitized.sh -->
