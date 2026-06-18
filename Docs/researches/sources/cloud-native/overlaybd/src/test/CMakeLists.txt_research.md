## sources/cloud-native/overlaybd/src/test/CMakeLists.txt

Purpose: CMake wiring for OverlayBD image service, simple credential server, and trace/prefetch tests.

Important targets: `image_service_test` links GTest/GFlags/Photon/overlaybd libraries and includes Photon/RapidJSON. `simple_credsrv_test` links `overlaybd_image_lib`, Photon, rt/resolv/aio/pthread, and GTest. `trace_test` compiles `trace_test.cpp` plus `../tools/comm_func.cpp` and links GTest/GFlags/Photon/overlaybd libs. Each target is registered with CTest.

Control flow/state: build-only file, relying on `$GFLAGS`, `$GTEST`, `${PHOTON_INCLUDE_DIR}`, `${RAPIDJSON_INCLUDE_DIRS}`, `${EXECUTABLE_OUTPUT_PATH}`, and project libraries. Runtime tests create files under `/tmp`, bind localhost ports, and may download remote assets.

Integration points: validates image service behavior, credential HTTP loading, and dynamic prefetch. Risks: hardcoded ports can conflict; environment-variable library paths can be brittle; trace test depends on network downloads and external URLs. Test signal is broad integration coverage rather than isolated unit coverage.
