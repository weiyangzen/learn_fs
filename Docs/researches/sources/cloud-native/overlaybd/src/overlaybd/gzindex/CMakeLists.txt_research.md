<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/CMakeLists.txt

## Purpose
Builds the gzip random-access index library and optionally its tests.

## Important APIs, Types, And Functions
Globs all `*.cpp` into static library `gzindex_lib`, includes Photon headers, links `photon_static`, and adds `test` when `BUILD_TESTING` is enabled.

## Control Flow
CMake configures library before descending to test directory.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Exports library used by gzip stream/index tests and other OverlayBD components needing `new_gzfile` or `create_gz_index`.

## Risks And Test Signals
`file(GLOB)` can miss new files until CMake reconfigure depending on generator behavior. Source size reviewed: 9 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/CMakeLists.txt -->
