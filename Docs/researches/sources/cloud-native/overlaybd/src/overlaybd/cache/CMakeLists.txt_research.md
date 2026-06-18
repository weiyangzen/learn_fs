<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/CMakeLists.txt

Purpose: Build definition for the cache subsystem.

APIs and control flow: Adds full-file, OCF, download, and gzip cache subdirectories, globs local cache cpp files into `cache_lib`, links cache implementations plus Photon, and includes cache tests when testing is enabled.

State and persistence: No runtime state; controls which cache factories link into `overlaybd_lib`.

Dependencies and integration: `cache_lib` exports `new_full_file_cached_fs`, `new_ocf_cached_fs`, `new_download_cached_fs`, and gzip cache support through linked sublibraries.

Risks and test signals: `file(GLOB)` can miss new source files until CMake reconfigure. Cache tests and daemon cache-mode startup cover it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/CMakeLists.txt -->
