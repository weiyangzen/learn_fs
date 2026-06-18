<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/CMakeLists.txt

Purpose: Builds gzip target-file cache support.

APIs and control flow: Globs local cpp files into `gzip_cache_lib`, links `gzindex_lib`, and exposes Photon include dirs.

State and persistence: No direct runtime state.

Dependencies and integration: Used when global `gzipCacheConfig.enable` is true and a layer has `targetDigest` plus `gzipIndex`.

Risks and test signals: Requires gzindex linkage. Tests should open gzip-indexed target layers with gzip cache enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/gzip_cache/CMakeLists.txt -->
