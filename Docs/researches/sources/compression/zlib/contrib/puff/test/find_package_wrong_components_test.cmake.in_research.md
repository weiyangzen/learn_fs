# sources/compression/zlib/contrib/puff/test/find_package_wrong_components_test.cmake.in

Purpose: Negative package-discovery template ensuring unsupported puff components fail.

Important APIs, types, and functions: Calls `find_package(puff REQUIRED COMPONENTS wrong CONFIG)` and contains normal shared/static consumer target definitions that should not be reached successfully.

Control flow: Configure should fail during `find_package` because `wrong` is not in `_puff_supported_components`. Parent CTest marks the configure test `WILL_FAIL`.

State and persistence: Only generated CMake configure state is created; no successful build targets are expected.

Dependencies and integration points: Directly validates error handling in `puffConfig.cmake.in`.

Risks: If package config stops rejecting unknown components, this negative test would unexpectedly pass and expose a package contract regression. Later target definitions are mostly incidental.

Test signals: Parent CTest's `WILL_FAIL TRUE` setting makes successful configuration a failure signal.
