# sources/compression/zlib/contrib/iostream3/test/add_subdirectory_test.cmake.in

Purpose: template for a normal consumer project that builds iostream3 through `add_subdirectory`.

Important APIs/types/functions: project `iostream_add_subdirectory`, options for shared/static/testing, `add_subdirectory(@iostreamV3_SOURCE_DIR@ ...)`, and example executable targets linked to iostream3 aliases.

Control flow: after substitution, CMake configures the iostream3 source as a child project, disables its tests, then builds example executables from `test.cc` for each enabled library variant.

State and persistence: generated only in the CTest work area; creates consumer build outputs.

Dependencies/integration: depends on direct source-tree consumption and target aliases `IOSTREAMV3::IOSTREAMV3` and `IOSTREAMV3::IOSTREAMV3STATIC`.

Risks: because it uses source paths directly, it can mask install/export problems that find-package tests catch separately. It does not run the executable, only ensures target graph and compilation work.

Test signals: configured and built by the `iostream3_add_subdirectory_configure` and build CTest entries.
