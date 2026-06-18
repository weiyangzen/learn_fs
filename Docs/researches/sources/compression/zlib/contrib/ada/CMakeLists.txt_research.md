# sources/compression/zlib/contrib/ada/CMakeLists.txt

Purpose: CMake build for zlib Ada bindings and stream wrappers.

Important APIs/options: project `zlibAda` with languages C and ADA; options `ZLIB_ADA_BUILD_SHARED`, `ZLIB_ADA_BUILD_STATIC`, and `ZLIB_ADA_BUILD_TESTING`. Uses custom `ada_add_library`, `ada_find_ali`, and `find_package(ZLIB COMPONENTS shared/static CONFIG)` when standalone.

Control flow: when built from the root, inherits zlib shared/static/testing/install options. Standalone builds require installed ZLIB components matching requested library kinds. Shared and static paths build `zlib_ada_Ada`/`zlib_ada_AdaStatic` from `zlib-thin.adb` and `zlib.adb`, then stream libraries from `zlib-streams.adb`, linking to the corresponding zlib target. Tests are added when enabled.

State and persistence: creates Ada object and ALI files plus CMake targets; additional clean files are configured by the custom Ada language support.

Dependencies and integration: relies on custom Ada CMake modules in `cmake/Modules`, GNAT, and zlib CMake package targets. Integrated by root contrib options and standalone contrib CI.

Risks: custom Ada support is GNAT-oriented and may not support other Ada compilers. Link interfaces use `INTERFACE` for base Ada-to-zlib linkage, which affects consumers rather than necessarily the library link line in all contexts.

Test signals: `contrib/ada/test/CMakeLists.txt` builds demos/tests for shared and static variants; `contribs.yml` installs GNAT and runs them on Ubuntu.
