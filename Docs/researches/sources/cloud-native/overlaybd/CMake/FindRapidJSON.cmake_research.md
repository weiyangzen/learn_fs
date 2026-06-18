<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindRapidJSON.cmake -->
# sources/cloud-native/overlaybd/CMake/FindRapidJSON.cmake

Purpose: Locates RapidJSON via pkg-config or fetches a pinned Tencent RapidJSON revision.

APIs and control flow: `pkg_check_modules(RAPIDJSON RapidJSON)` is tried first. If not found, FetchContent populates `rapidjson` at commit `80b6d1...` without submodules and sets `RAPIDJSON_INCLUDE_DIRS`.

State and persistence: Only provides header include paths; RapidJSON is header-only.

Dependencies and integration: Config structs in `src/config.h` depend on RapidJSON through `ConfigUtils`.

Risks and test signals: FetchContent requires network unless dependency is cached. JSON config parsing in service and image configs exercises this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindRapidJSON.cmake -->
