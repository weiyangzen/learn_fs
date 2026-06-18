<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/CMakeLists.txt

Purpose: Builds the on-demand download cache library.

APIs and control flow: Globs `*.cpp` into static library `download_cache_lib` and exposes Photon include directories.

State and persistence: No direct runtime state.

Dependencies and integration: Linked into `cache_lib`; factory `new_download_cached_fs` is selected by `ImageService` for `cacheType=download`.

Risks and test signals: Single-file glob is simple but reconfigure-dependent. Startup with download cache and layer reads validate it.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/download_cache/CMakeLists.txt -->
