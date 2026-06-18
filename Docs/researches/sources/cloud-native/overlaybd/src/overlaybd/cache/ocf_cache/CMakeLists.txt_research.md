<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/CMakeLists.txt

Purpose: Builds Open CAS Framework based cache integration.

APIs and control flow: Optionally adds tests, builds `ocf_env_lib` from ease binding environment cpp files, builds `ocf_lib` from OCF C sources with OCF and env includes plus zlib, then builds `ocf_cache_lib` from cache wrapper and ease bindings linked to OCF and Photon.

State and persistence: Build only; runtime state is OCF metadata/media managed by implementation files outside this subset plus ease bindings.

Dependencies and integration: Requires vendored OCF source, zlib, Photon, and env bindings.

Risks and test signals: C and C++ ABI boundaries and include ordering are fragile. OCF cache startup and reload tests are key.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/CMakeLists.txt -->
