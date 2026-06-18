# sources/compression/zlib/contrib/ada/cmake/Modules/CMakeADACompiler.cmake.in

Purpose: generated CMake platform-info template for the custom ADA language.

Important variables: sets `CMAKE_ADA_COMPILER`, compiler args/id/version/platform, `CMAKE_AR`, compiler loaded/work flags, source and ignored extensions, environment variable name `ADA`, and paths to binder/compiler/link helper scripts.

Control flow: no logic beyond variable assignment. `CMakeDetermineADACompiler.cmake` configures this template into `CMakeADACompiler.cmake` under CMake's platform information directory.

State and persistence: generated output persists in the CMake build tree and tells subsequent configure/generate steps how to invoke Ada tools.

Dependencies and integration: included by CMake's language enablement flow for the custom `ADA` language.

Risks: commented-out ranlib/linker/ABI variables mean this language definition is intentionally minimal. If helper script paths move, configured builds fail until regenerated.

Test signals: successful `project(... LANGUAGES C ADA)` and `try_compile` in `CMakeTestADACompiler.cmake` validate that the generated file is usable.
