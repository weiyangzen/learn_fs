# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMake/FindCyrusSASL.cmake

## Purpose
This CMake find-module locates a host Cyrus SASL installation for libhdfs++ authentication support.

## Important APIs, Control Flow, and State
It searches for `sasl/sasl.h` and the `sasl2` library, then uses `find_package_handle_standard_args` to set `CYRUS_SASL_FOUND`. It publishes `CYRUS_SASL_INCLUDE_DIR` and `CYRUS_SASL_SHARED_LIB`, and marks both advanced. The comments explain why the project prefers the host installation rather than vendoring SASL: plugin/library version mismatches can produce `SASL_NOMECH`.

## Dependencies and Integration Points
`libhdfspp/CMakeLists.txt` includes this module via `CMAKE_MODULE_PATH`, then prefers Cyrus over GSASL when selecting SASL libraries and compile definitions.

## Risks and Test Signals
The module does not search custom names beyond CMake's normal prefix mechanisms, so `CYRUS_SASL_DIR`/`CMAKE_PREFIX_PATH` setup matters. Tests should configure with present, absent, required, and disabled Cyrus SASL, and verify include/library variables link a real client.
