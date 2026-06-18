<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindOpenSSL.cmake -->
# sources/cloud-native/overlaybd/CMake/FindOpenSSL.cmake

Purpose: Custom OpenSSL resolver that can build OpenSSL 1.0.2 static libraries for bundled curl builds.

APIs and control flow: If `BUILD_CURL_FROM_SOURCE` is true, FetchContent clones `OpenSSL_1_0_2-stable`, runs `sh config -fPIC no-unit-test no-shared`, builds and installs into the binary tree, then defines imported targets `OpenSSL::SSL` and `OpenSSL::Crypto`. Otherwise it includes CMake's standard FindOpenSSL.

State and persistence: Produces static libssl/libcrypto and include directories under the FetchContent build output.

Dependencies and integration: `FindCURL.cmake` depends on `openssl102_static_build`.

Risks and test signals: OpenSSL 1.0.2 is obsolete and only acceptable for controlled compatibility. Link success and TLS registry access are the key functional signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/FindOpenSSL.cmake -->
