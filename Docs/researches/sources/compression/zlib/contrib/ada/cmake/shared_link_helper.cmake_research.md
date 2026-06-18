# sources/compression/zlib/contrib/ada/cmake/shared_link_helper.cmake

Purpose: CMake script wrapper that creates an Ada shared library using GNAT.

Important inputs: linker/compiler in `CMAKE_ARGV3`, output library in `CMAKE_ARGV4`, object files before the `LIBS` sentinel, and libraries after it.

Control flow: parses object and library arguments, writes a dummy Ada procedure `dummylib.adb`, compiles and binds it with no main, then links a shared library from `dummylib.ali`, collected object files, and libraries.

State and persistence: creates `dummylib.adb`, `dummylib.ali`, `dummylib.o`, and the shared library; cleanup files are registered by `ada_add_library`.

Dependencies and integration: used by `CMAKE_ADA_CREATE_SHARED_LIBRARY`.

Risks: the parser sets `REACHED_FILES` but checks `REACHED_LIBS`, so library collection appears broken unless CMake argument behavior masks it. Intermediate dummy files are written in the current build directory and can conflict if parallel targets share it.

Test signals: shared Ada library builds and downstream tests reveal link failures.
