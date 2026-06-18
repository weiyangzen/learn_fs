## sources/cloud-native/overlaybd/src/overlaybd/zfile/thirdparty/CMakeLists.txt

Purpose: optional custom build target for zfile third-party acceleration libraries: Intel DML when `ENABLE_DSA` is set and ISA-L when `ENABLE_ISAL` is set.

Important build actions: defines `thirdparty_lib`, sets `THIRDPARTY_PATH`, checks out pinned DML commit `5a2956...`, configures/builds/installs DML into a local build directory, copies `libdml*.a` and headers to `${LIBRARY_OUTPUT_PATH}`. For ISA-L it checks out commit `ad8dce...`, runs `autogen.sh`, `./configure`, `make`, copies `libisal.a`, and exports `crc.h`.

Control flow: build commands run as `add_custom_command(TARGET thirdparty_lib ...)` side effects attached to the custom target. They mutate submodule working trees by `git checkout` and place static artifacts in the library output path.

State/persistence: persistent build outputs land under third-party build directories and `${LIBRARY_OUTPUT_PATH}`. Dependencies include git, cmake, make/autotools, DML source tree, ISA-L source tree, and writable output directories.

Integration points: provides accelerated CRC/DSA support used by zfile CRC paths and tested by `ZFileTest.dsa`. Risks: build is not hermetic, mutates source checkout state, lacks explicit byproducts, and can be fragile under parallel or read-only builds. Network is not used here, but missing submodules or toolchains break the target.
