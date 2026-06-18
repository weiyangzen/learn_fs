# sources/compression/zlib/contrib/ada/cmake/Modules/CMakeTestADACompiler.cmake

Purpose: CMake language test module that verifies the configured Ada compiler can build a simple program.

Important APIs/functions: uses `include(CMakeTestCompilerCommon)`, `PrintTestCompilerStatus`, `file(WRITE)`, `try_compile`, `CMakeError.log`, and `CMakeOutput.log`.

Control flow: clears cached `CMAKE_ADA_COMPILER_WORKS`, writes `main.adb` that prints “Hello, World!”, runs `try_compile`, then either logs failure and raises `FATAL_ERROR` or logs success.

State and persistence: writes temporary source under `CMakeFiles/CMakeTmp` and appends compiler output to CMake logs.

Dependencies and integration: called during Ada language enablement after compiler detection. Relies on custom Ada compile/link rules from the language modules.

Risks: a compiler that can compile but not run is sufficient because `try_compile` only builds; runtime Ada library discovery issues may still appear later. Error text says CMake cannot generate the project on failure, which is accurate for Ada targets.

Test signals: first-line configure gate for Ada contrib; failing it blocks all Ada builds.
