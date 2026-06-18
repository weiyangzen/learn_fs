<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/CMakeLists.txt

## Purpose
Builds and registers the OCF cache performance/manual test executable.

## Important APIs, Types, And Functions
Creates `ocf_perf_test` from `ocf_perf_test.cpp`, adds include paths for CURL/Photon, links gflags, pthread, CURL, `photon_static`, and `overlaybd_lib`, and registers a CTest entry.

## Control Flow
CTest runs the executable with `--ut_pass=true`, making CI validate build/link/startup path without executing the heavy manual benchmark.

## State And Persistence
No runtime state in the CMake file. The executable itself writes temporary cache/media files depending on flags.

## Dependencies And Integration Points
Requires `GFLAGS` environment paths and `find_package(CURL)`. Integrates test target with the OCF cache library through `overlaybd_lib`.

## Risks And Test Signals
The registered test is intentionally shallow; it passes directly with `ut_pass`. Real OCF behavior requires manual invocation with `flags.conf`. Source size reviewed: 21 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/CMakeLists.txt -->
