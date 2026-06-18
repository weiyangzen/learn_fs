# sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/CMakeLists.txt

## Purpose
Builds the `overlaybd-streamConv` executable from the stream convertor sources.

## Important APIs and Types
Globs local `.cpp` files, adds Photon and RapidJSON include directories, and links `photon_static`, `gzip_lib`, `gzindex_lib`, `tar_lib`, and `yaml-cpp`.

## Control Flow
CMake creates the executable and leaves a test subdirectory hook commented out.

## State and Persistence
No runtime state is defined. The built executable later persists gzip and tar metadata under its configured work directory.

## Dependencies and Integration Points
Integrates the service with OverlayBD gzip, tar, Photon networking, and YAML configuration libraries.

## Risks
Glob-based source inclusion can accidentally pull in local experiments. The executable assumes the linked gzip/tar libraries provide stream parsing and metadata generation.

## Test Signals
Build/link success and manual service startup with a YAML config are the primary signals; there are no active CTest entries here.
