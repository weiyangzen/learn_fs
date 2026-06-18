<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/CMakeLists.txt

Purpose: Builds the full-file cache implementation.

APIs and control flow: Globs `*.cpp` into static library `full_file_cache_lib` and exposes Photon include dirs.

State and persistence: No direct runtime state.

Dependencies and integration: Linked into `cache_lib`; `new_full_file_cached_fs` instantiates `FileCachePool` and `FileCacheStore`.

Risks and test signals: Build graph depends on reconfigure after adding source files. Cache unit tests and file cache mode daemon reads validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/full_file_cache/CMakeLists.txt -->
