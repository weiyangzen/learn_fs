# sources/cloud-native/overlaybd/src/overlaybd/zfile/CMakeLists.txt

Purpose: build configuration for zfile compression, CRC32C, optional acceleration libraries, and zfile tests.

Important APIs/types/functions: globs zfile C++ sources, LZ4 C sources, and `crc32/crc32c.cpp`; creates static `crc32_lib` and `zfile_lib`; configures C++ standard levels; adds CPU-specific CRC flags; conditionally adds thirdparty dependencies and definitions for `ENABLE_DSA`, `ENABLE_ISAL`, and `ENABLE_QAT`; adds `test` subdirectory when `BUILD_TESTING`.

Control flow: at configure/build time it compiles CRC with SSE4.2/CRC32 flags on x86_64 or native/generic CRC flags on other architectures, links DSA/ISAL support when enabled, then builds zfile with Photon, CRC32, zstd, and LZ4/QAT sources.

State and persistence: no runtime state. Build outputs are static libraries and optional thirdparty artifacts under configured output paths.

Dependencies/integration: depends on Photon include/library variables, `${LIBZSTD}`, optional libpci, dml, dl, ISAL, and pthread. `zfile_lib` is the compression backend for zfile format code outside this subset.

Risks: `file(GLOB ...)` can miss source changes until CMake reconfigure. Setting `CMAKE_CXX_STANDARD` to 17 for CRC and later 14 globally may surprise downstream targets. Optional acceleration flags affect ABI/behavior and require matching thirdparty libraries and CPU features.

Test signals: build enables zfile tests through `add_subdirectory(test)` when testing is on; CRC/compressor behavior is also indirectly covered by zfile format tests.
