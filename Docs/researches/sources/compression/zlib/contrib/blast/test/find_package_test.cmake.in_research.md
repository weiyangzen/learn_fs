# sources/compression/zlib/contrib/blast/test/find_package_test.cmake.in

Purpose: generated consumer project that verifies explicit blast package component discovery.

Important APIs/settings: conditionally calls `find_package(blast REQUIRED COMPONENTS shared CONFIG)` and/or `find_package(blast REQUIRED COMPONENTS static CONFIG)`, then links `blast-test.c` against the matching alias targets.

Control flow: only requests components for enabled library kinds, then builds consumer executables.

State and persistence: generated source and consumer build outputs in the test work directory.

Dependencies and integration: validates installed component export files `blast-shared.cmake` and `blast-static.cmake`.

Risks: repeated `find_package` calls for separate components depend on CMake package state remaining consistent.

Test signals: configure/build success proves explicit component usage works for shared and static installs.
