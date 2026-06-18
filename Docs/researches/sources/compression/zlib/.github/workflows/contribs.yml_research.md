# sources/compression/zlib/.github/workflows/contribs.yml

Purpose: CI workflow for zlib contributed modules, both all-at-once from the root project and standalone contrib subprojects.

Important jobs/settings: matrix builds all contribs on Ubuntu and Windows, plus standalone Ada, blast, iostream3, minizip, puff, testzlib, and zlib1-dll jobs. Root all-contrib jobs toggle options such as `ZLIB_BUILD_ADA`, `ZLIB_BUILD_BLAST`, `ZLIB_WITH_CRC32VX`, and `ZLIB_WITH_GVMAT64`.

Control flow: checks out source, installs Linux packages (`gnat`, `libbz2-dev`), optionally builds and installs root zlib before standalone contrib builds, configures the chosen source directory, builds, and runs CTest.

State and persistence: CI-local `../build-zlib` and `../build` directories; optional install into the runner system using `sudo` on Linux.

Dependencies and integration: exercises `contrib/CMakeLists.txt`, subproject `find_package(ZLIB CONFIG)` paths, GNAT Ada support, CMake install exports, and Windows-specific contrib projects.

Risks: standalone tests depend on installing zlib into a discoverable prefix, which can differ by runner permissions and CMake package cache behavior. Windows matrix values use both `windows-latest` and `Windows-latest`; GitHub is case-insensitive today but consistency would reduce risk.

Test signals: verifies contributed CMake packages can build both as root subdirectories and as standalone consumers of installed zlib.
