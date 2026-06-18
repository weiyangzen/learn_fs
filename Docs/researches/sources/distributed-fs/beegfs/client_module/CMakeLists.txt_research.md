## sources/distributed-fs/beegfs/client_module/CMakeLists.txt

### Purpose
Integrates the BeeGFS client kernel module into the CMake packaging/build flow, including DKMS source installation, default config installation, and Debian/RPM package metadata.

### Important APIs, Types, and Functions
- If `BEEGFS_SKIP_CLIENT` is not set, `ExternalProject_Add(client-module)` builds in source using `make -C build -j $(nproc)` with `KDIR` and `OFED_INCLUDE_PATH`.
- `configure_file` produces DKMS and package maintainer scripts from build templates.
- Installs the client module source tree to `usr/src/beegfs-${BEEGFS_VERSION}` and compat source tree to `usr/src/beegfs-compat-${BEEGFS_VERSION}`.
- Installs generated `dkms.conf` and default `etc/beegfs/beegfs-client.conf`.
- Sets package dependencies/requires on `dkms` and package script hooks for Debian/RPM.

### Control Flow and State
CMake configure time generates files; build time invokes the kernel-module make flow; install/package time copies source trees and scripts. No runtime application state.

### Dependencies and Integration Points
Depends on CMake `ExternalProject`, Makefile targets under `client_module/build`, kernel directory variable `BEEGFS_KERNELDIR`, optional OFED include directory `BEEGFS_OFEDDIR`, and CPACK variables.

### Risks and Edge Cases
`BUILD_COMMAND` uses `$(nproc)`, which is shell/make-specific inside CMake and may be nonportable. Installing `DIRECTORY ""` copies a broad source tree and relies on exclusion patterns to avoid unwanted files. Compat DKMS packaging appears commented as currently unsupported. Missing kernel headers or OFED path failures surface during external build.

### Test Signals
Build/package tests should exercise normal client build, `BEEGFS_SKIP_CLIENT`, Debian/RPM package metadata, and DKMS install paths.
