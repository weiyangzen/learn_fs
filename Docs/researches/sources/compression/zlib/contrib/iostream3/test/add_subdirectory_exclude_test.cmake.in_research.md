# sources/compression/zlib/contrib/iostream3/test/add_subdirectory_exclude_test.cmake.in

Purpose: template for a consumer project that adds iostream3 with `EXCLUDE_FROM_ALL` and links explicit example executables.

Important APIs/types/functions: project `iostream_add_subdirectory_exclude`, options mirroring shared/static build settings, `add_subdirectory(... EXCLUDE_FROM_ALL)`, and targets linked to `IOSTREAMV3::IOSTREAMV3` or `IOSTREAMV3::IOSTREAMV3STATIC`.

Control flow: CTest configures this template with source/build paths and option values. The consumer project adds iostream3 out of the default all target, then explicitly declares example executables from `test.cc` for enabled variants so required library targets are still built as dependencies.

State and persistence: generated into a test work directory; produces consumer build targets only.

Dependencies/integration: depends on the source tree path substitution and iostream3 CMake aliases.

Risks: verifies a subtle integration mode where excluded subdirectories must still satisfy target dependencies. If alias target names change, this test catches it. It does not run the resulting executables, only configures/builds in the parent test flow.

Test signals: configured and built by `iostream3_add_subdirectory_exclude_*` CTest entries.
