# sources/cloud-native/overlaybd/src/overlaybd/tar/test/CMakeLists.txt

Purpose: CMake definition for the tar integration test executable.

Important APIs/types/functions: configures GFlags/GTest include and library directories from environment variables, creates `untar_test` from `test.cpp`, includes Photon headers, links gtest, pthread, `photon_static`, `tar_lib`, `lsmt_lib`, `gzip_lib`, `gzindex_lib`, and `checksum_lib`, and registers the test with CTest.

Control flow: build-time only. `add_test` runs `${EXECUTABLE_OUTPUT_PATH}/untar_test`.

State and persistence: no runtime state in the build file; the executable itself creates `/tmp/tar_test` artifacts during tests.

Dependencies/integration: assumes `$GFLAGS`, `$GTEST`, `${PHOTON_INCLUDE_DIR}`, and linked Overlaybd static libraries are configured by the parent build. It integrates tar tests into `BUILD_TESTING` parent flows.

Risks: environment-variable include/link paths can break reproducibility if not set. Direct linking with several static libraries means transitive dependencies must already be ordered correctly by the parent build.

Test signals: the existence of this file means tar tests are discoverable by CTest as `untar_test`.
