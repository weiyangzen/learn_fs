<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMakeLists.txt -->
# sources/cloud-native/overlaybd/CMakeLists.txt

Purpose: Top-level build definition for OverlayBD.

APIs and control flow: Requires CMake 3.14, enables C/C++, restricts CPU architectures to x86_64/aarch64/arm64, sets output paths, module path, warning and version flags, optional static libstdc++, locates zstd, and declares options for bundled curl, stream convertor, and ext2fs source. It fetches Photon and TCMU, optionally yaml-cpp, enables CTest, adds `src` and `baselayers`, and includes packaging.

State and persistence: Uses `build/output` for runtime binaries and base layer extraction.

Dependencies and integration: Centralizes external dependency configuration for all runtime and tools.

Risks and test signals: Architecture and static library detection are host-sensitive. CI configure and package builds are the main tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMakeLists.txt -->
