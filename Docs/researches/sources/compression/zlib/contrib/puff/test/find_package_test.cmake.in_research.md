# sources/compression/zlib/contrib/puff/test/find_package_test.cmake.in

Purpose: Template for testing explicit component discovery of installed puff packages.

Important APIs, types, and functions: Uses `find_package(puff REQUIRED COMPONENTS shared CONFIG)` for shared builds and `find_package(puff REQUIRED COMPONENTS static CONFIG)` for static builds, then links `PUFF::PUFF` and `PUFF::PUFFSTATIC` respectively.

Control flow: Shared and static branches run independently based on configured options. Each branch discovers the matching component before creating the executable that links it.

State and persistence: Produces only generated test build targets and CMake cache entries.

Dependencies and integration points: Validates installed `puff-shared.cmake`, `puff-static.cmake`, and `puffConfig.cmake` component handling.

Risks: It does not run the produced executable, so it only catches configure/link problems. Component names are hard-coded to the package config contract.

Test signals: Parent CTest registers configure and build tests after the install fixture, making this the positive package-import path.
