<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findaio.cmake -->
# sources/cloud-native/overlaybd/CMake/Findaio.cmake

Purpose: Minimal finder for Linux libaio.

APIs and control flow: Uses `find_path` for `libaio.h`, `find_library` for `aio`, and `find_package_handle_standard_args` to populate `AIO_INCLUDE_DIR` and `AIO_LIBRARIES`.

State and persistence: No generated files or runtime state.

Dependencies and integration: `src/CMakeLists.txt` links `${AIO_LIBRARIES}` into image library and `overlaybd-tcmu`; direct IO paths in `ImageFile` select `ioengine_libaio`.

Risks and test signals: Header/library mismatch would appear at compile or link time. CI installs `libaio-dev`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/Findaio.cmake -->
