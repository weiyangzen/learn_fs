## sources/cloud-native/overlaybd/src/overlaybd/zstd/CMakeLists.txt

Purpose: builds the zstd adaptor library from all `*.cpp` files in the directory.

Important build actions: `file(GLOB SOURCE_ZSTD "*.cpp")`, `add_library(zstd_lib STATIC ${SOURCE_ZSTD})`, includes `${PHOTON_INCLUDE_DIR}`, and links `photon_static` plus `${LIBZSTD}`.

Control flow/state: build-only file; no runtime state. It depends on the parent build defining Photon and libzstd variables and on glob results at configure time.

Integration points: `zstd_lib` supplies `open_zstdfile_adaptor` and `is_zstdfile` to consumers needing sequential ZSTD decompression. Risks: CMake globbing requires reconfigure to pick up added source files in older CMake workflows; `${LIBZSTD}` must be a valid library path/name. Test coverage for this specific target is not visible in the listed files.
