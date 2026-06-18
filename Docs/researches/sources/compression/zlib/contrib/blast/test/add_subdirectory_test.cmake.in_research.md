# sources/compression/zlib/contrib/blast/test/add_subdirectory_test.cmake.in

Purpose: generated consumer project that verifies normal `add_subdirectory` consumption of blast.

Important APIs/settings: mirrors shared/static/testing options and links `blast-test.c` executables against `BLAST::BLAST` and/or `BLAST::BLASTSTATIC`.

Control flow: adds the blast source directory, defines one executable per enabled library kind, and links through the public alias targets.

State and persistence: generated source project and build artifacts under the blast test work directory.

Dependencies and integration: exercises source-tree embedding rather than installed package discovery.

Risks: assumes the blast source path is valid and reusable as a subproject from another binary directory.

Test signals: configure/build success proves subdirectory integration and alias target visibility.
