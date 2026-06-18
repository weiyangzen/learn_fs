<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindCURL.cmake -->
# sources/cloud-native/overlaybd/CMake/FindCURL.cmake

Purpose: Custom libcurl resolver with optional static-from-source build.

APIs and control flow: When `BUILD_CURL_FROM_SOURCE` is true, FetchContent clones curl tag `curl-7_42_1`, runs autotools configure with HTTP-only static options and OpenSSL root, creates `libcurl_static_build`, and defines/imports `CURL::libcurl`. Otherwise it delegates to CMake's built-in FindCURL.

State and persistence: Builds curl into the FetchContent binary tree and exposes include/lib variables.

Dependencies and integration: Depends on `FindOpenSSL.cmake`, zlib, autotools, make, and CMake target dependencies. `src/CMakeLists.txt` consumes `CURL_LIBRARIES` and `CURL_INCLUDE_DIRS`.

Risks and test signals: Old curl plus disabled protocols are intentional but security-sensitive. Static target correctness is verified by successful link of registryfs and image service.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindCURL.cmake -->
