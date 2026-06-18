# sources/compression/zlib/contrib/ada/cmake/Modules/CMakeDetermineADACompiler.cmake

Purpose: custom CMake compiler-detection module for the Ada language.

Important APIs/variables: includes `CMakeDetermineCompiler.cmake`, optional platform Ada modules, `CMAKE_ADA_COMPILER_NAMES`, `_cmake_find_compiler`, `_cmake_find_compiler_path`, `CMAKE_ADA_COMPILER_ID`, and helper script path variables.

Control flow: seeds compiler names with `gnat` and `gnat-11` through `gnat-99` if none are provided, finds the compiler or compiler path, marks it advanced, assumes GNU identity, sets helper script commands using `${CMAKE_COMMAND} -P`, and configures `CMakeADACompiler.cmake.in`.

State and persistence: writes CMake platform info for Ada into the build tree and stores compiler cache entries.

Dependencies and integration: invoked by CMake when enabling `LANGUAGES ADA` in the Ada project. Assumes GNAT-style command interface.

Risks: compiler ID is hard-coded to `GNU`; non-GNAT Ada compilers are effectively unsupported. Helper script paths use `CMAKE_CURRENT_SOURCE_DIR`, so standalone/root inclusion must preserve expected layout.

Test signals: followed by `CMakeTestADACompiler.cmake`, which performs a simple compile test.
