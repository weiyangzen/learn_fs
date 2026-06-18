# sources/compression/zlib/contrib/iostream3/test/find_package_test.cmake.in

Purpose: template for validating installed iostream3 package consumption with explicit `shared` and/or `static` components.

Important APIs/types/functions: project `iostream_find_package`, options `ZLIB_IOSTREAM_BUILD_SHARED` and `ZLIB_IOSTREAM_BUILD_STATIC`, `find_package(iostreamv3 REQUIRED COMPONENTS shared CONFIG)`, `find_package(... static CONFIG)`, and example targets linked to imported aliases.

Control flow: for each enabled variant, the generated consumer project requests the matching package component, builds `test.cc`, and links to the expected imported target.

State and persistence: generated in CTest work directories; produces consumer build targets.

Dependencies/integration: depends on installed package config, component export files, and target names.

Risks: option names omit the `3` used elsewhere, so substitution must provide matching values or both blocks can be disabled. The template tests configure/build linkage, not runtime behavior.

Test signals: parent CTest configure/build entries validate component-based installed package use.
