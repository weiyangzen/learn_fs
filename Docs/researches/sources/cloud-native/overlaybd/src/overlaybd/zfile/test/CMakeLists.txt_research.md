## sources/cloud-native/overlaybd/src/overlaybd/zfile/test/CMakeLists.txt

Purpose: CMake wiring for the zfile GoogleTest executable. It configures include/link search paths for GFlags and GTest from environment variables, builds `zfile_test` from `test.cpp`, links Photon and OverlayBD libraries, and registers a CTest test.

Important build targets: `add_executable(zfile_test ./test.cpp)`, `target_link_libraries(zfile_test gtest gtest_main gflags pthread photon_static overlaybd_lib)`, `target_include_directories(zfile_test PUBLIC ${PHOTON_INCLUDE_DIR})`, and `add_test(NAME zfile_test COMMAND ${EXECUTABLE_OUTPUT_PATH}/zfile_test)`.

Control flow: build-time only. It assumes parent CMake has set `PHOTON_INCLUDE_DIR`, `EXECUTABLE_OUTPUT_PATH`, and imported/visible `overlaybd_lib` and `photon_static`.

State/persistence: no runtime persistence, but the linked test writes temporary files under `/tmp` at execution time. Dependencies are environment variable paths `$GFLAGS` and `$GTEST`, which can make the test non-portable outside the project build environment.

Integration points: this file is the test gateway for `zfile.cpp`, `compressor.cpp`, CRC code, and Photon file abstractions. Risks: direct environment-variable include/link directories can silently resolve wrong library versions; the CTest command does not pass flags such as `--nwrites`, so default test size is used.
