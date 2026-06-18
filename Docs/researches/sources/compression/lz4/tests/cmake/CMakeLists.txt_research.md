# sources/compression/lz4/tests/cmake/CMakeLists.txt

Purpose: downstream CMake package-consumption smoke test for an installed/exported LZ4 package.

Important commands: `find_package(lz4 CONFIG REQUIRED)`, target existence check for `LZ4::lz4`, property checks on `LZ4::lz4_shared`, and two `decompress-partial` executable builds linked against `LZ4::lz4_shared` and `lz4::lz4`.

Control flow/state: configure-time `message(FATAL_ERROR)` catches missing exported targets/properties; build-time linking validates usability. No runtime test is registered here.

Dependencies/integration: requires CMake 3.5 through 4.0.2 compatibility and adjacent `tests/decompress-partial.c`.

Risks: assumes both uppercase and lowercase namespace targets are exported; checks `LOCATION`, which is intentionally strict for this package contract.

Test signals: successful configure/build means downstream C projects can discover includes and link to the installed LZ4 targets.
