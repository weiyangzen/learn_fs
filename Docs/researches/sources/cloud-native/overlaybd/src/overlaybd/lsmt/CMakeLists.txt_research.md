<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/lsmt/CMakeLists.txt

## Purpose
Builds the LSMT layer/image file library and optional tests.

## Important APIs, Types, And Functions
Globs `*.cpp` into static library `lsmt_lib`, includes Photon headers, and adds the `test` subdirectory when `BUILD_TESTING` is enabled.

## Control Flow
CMake creates the library before configuring tests.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Exports `lsmt_lib` for OverlayBD image/layer logic.

## Risks And Test Signals
`file(GLOB)` has reconfigure caveats. Test coverage is in `lsmt/test`, outside this work item. Source size reviewed: 10 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/lsmt/CMakeLists.txt -->
