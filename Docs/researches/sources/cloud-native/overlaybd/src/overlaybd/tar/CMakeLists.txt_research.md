# sources/cloud-native/overlaybd/src/overlaybd/tar/CMakeLists.txt

## Purpose
Builds the base static `tar_lib` and wires in tar tests and the EROFS sublibrary.

## Important APIs and Types
Globs local tar `.cpp` sources, creates `tar_lib`, includes Photon headers, conditionally adds `test`, adds `erofs`, and links `tar_lib` privately against `erofs_lib`.

## Control Flow
CMake creates the tar library first, then descends into EROFS so EROFS support is available to tar consumers.

## State and Persistence
No runtime state is defined here. Build artifacts are static libraries.

## Dependencies and Integration Points
Connects tar handling to Photon and EROFS conversion code. Consumers of `tar_lib` can use EROFS-backed functionality via the private link.

## Risks
Glob-based inclusion and private EROFS linkage can hide dependency changes from consumers. Formatting lacks a newline before `include(FetchContent)` in the displayed concatenated output of adjacent CMake files, but each file remains separate.

## Test Signals
Build `tar_lib` and run tar/EROFS tests when `BUILD_TESTING` is enabled.
