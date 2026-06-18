# sources/compression/zlib/contrib/blast/test/add_subdirectory_exclude_test.cmake.in

Purpose: generated consumer project that verifies blast can be added by `add_subdirectory(... EXCLUDE_FROM_ALL)`.

Important APIs/settings: options mirror `ZLIB_BLAST_BUILD_SHARED`, `ZLIB_BLAST_BUILD_STATIC`, and `ZLIB_BLAST_BUILD_TESTING`; links test executables to `BLAST::BLAST` and/or `BLAST::BLASTSTATIC`.

Control flow: adds the blast source directory into a local binary dir excluded from the default all target, then creates explicit executables from `blast-test.c` for enabled library kinds.

State and persistence: generated into the test work directory and produces consumer build artifacts.

Dependencies and integration: configured by blast test CMakeLists using `@blast_SOURCE_DIR@` and option substitutions.

Risks: because blast is excluded from all, target dependencies must correctly bring in the library when test executables are built; this template is designed to catch that.

Test signals: configure/build success proves exported aliases work even with `EXCLUDE_FROM_ALL`.
