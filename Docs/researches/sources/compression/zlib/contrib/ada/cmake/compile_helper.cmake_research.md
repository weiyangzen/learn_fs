# sources/compression/zlib/contrib/ada/cmake/compile_helper.cmake

Purpose: CMake script wrapper around GNAT Ada compilation.

Important inputs: expects compiler in `CMAKE_ARGV3`, object directory in `CMAKE_ARGV4`, source file in `CMAKE_ARGV5`, and remaining arguments as flags.

Control flow: validates required arguments, collects flags, executes `${compiler} compile <flags> <source>` in the object directory, and fails the CMake step on nonzero result.

State and persistence: writes Ada object and ALI files into the object directory via GNAT.

Dependencies and integration: used by `CMAKE_ADA_COMPILE_OBJECT` in `CMakeADAInformation.cmake`.

Risks: assumes GNAT command syntax (`gnat compile`). Output is discarded except error text, which can reduce diagnostics.

Test signals: every Ada source compilation uses this wrapper; CMake build failure indicates compiler or flags problems.
