# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/CMake/FindGSasl.cmake

## Purpose
This CMake find-module locates GNU SASL (`gsasl`) as the fallback SASL provider for libhdfs++.

## Important APIs, Control Flow, and State
If `GSASL_INCLUDE_DIR` and `GSASL_LIBRARIES` are already cached, it sets quiet mode. It searches for `gsasl.h` and `gsasl`, invokes `FIND_PACKAGE_HANDLE_STANDARD_ARGS`, and marks the variables advanced. It sets `GSASL_FOUND`, `GSASL_INCLUDE_DIR`, and `GSASL_LIBRARIES`.

## Dependencies and Integration Points
The top-level libhdfs++ CMake file uses this module after Cyrus SASL. If Cyrus is unavailable and GSASL is found, it sets `USE_SASL` and `USE_GSASL` and links `GSASL_LIBRARIES`.

## Risks and Test Signals
The comments mention `GSASL_DEFINITIONS` but the file does not set it. Tests should cover discovery through `GSASL_DIR`/`CMAKE_PREFIX_PATH`, required/disabled package flags, and successful link of SASL-authentication code with only GSASL installed.
