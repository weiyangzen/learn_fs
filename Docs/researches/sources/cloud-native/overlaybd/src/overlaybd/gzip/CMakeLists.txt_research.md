<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/gzip/CMakeLists.txt

## Purpose
Builds the gzip stream/adaptor library.

## Important APIs, Types, And Functions
Globs `*.cpp` into static library `gzip_lib`, includes Photon headers, and links `photon_static` plus `checksum_lib`.

## Control Flow
The test subdirectory is present but disabled in comments.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Library is consumed by gzindex tests and stream conversion paths needing `open_gzfile_adaptor` or `open_gzstream_file`.

## Risks And Test Signals
Test build is disabled here; coverage comes through `gzindex/test`. Source size reviewed: 11 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzip/CMakeLists.txt -->
