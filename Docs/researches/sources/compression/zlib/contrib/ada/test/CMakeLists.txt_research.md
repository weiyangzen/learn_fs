# sources/compression/zlib/contrib/ada/test/CMakeLists.txt

Purpose: CTest definitions for zlib Ada binding examples and tests.

Important APIs/functions: defines `ZLIB_ADA_findTestEnv` to add the zlib DLL directory to `PATH` on Windows-like environments. Uses `ada_add_executable`, `target_link_libraries`, `ada_find_ali`, `add_test`, fixtures, and resource locks.

Control flow: for shared builds, creates and tests `zlib_ada_test`, `zlib_ada_buffer_demo`, and `zlib_ada_read`; builds but does not test `mtest` because it is an endless loop. Static builds create analogous `*Static` targets/tests. A cleanup test removes `testzlib.in`, `.out`, and `.zlb` as fixture cleanup.

State and persistence: test programs create temporary test files in the binary directory; cleanup removes them. CTest resource locks serialize tests using shared Ada test files.

Dependencies and integration: links against Ada binding targets and zlib targets. Windows-like shared tests need PATH updates for DLL discovery.

Risks: function name is defined with uppercase segments but called as lowercase in some places; CMake commands are case-insensitive, so this works. One shared test calls `zlib_ada_findtestenv(zlib_ada_ada-test)`, which does not match the registered `zlib_ada_test` test name and may fail to set the intended environment.

Test signals: validates shared/static Ada APIs, stream wrappers, demos, and cleanup behavior.
