# sources/compression/zlib/contrib/puff/test/find_package_no_components_test.cmake.in

Purpose: Template for testing `find_package(puff REQUIRED CONFIG)` without explicit components.

Important APIs, types, and functions: Defines shared/static options, calls `find_package(puff REQUIRED CONFIG)`, builds `test_example` and/or `test_example_static`, and links imported `PUFF::PUFF` / `PUFF::PUFFSTATIC`.

Control flow: Package discovery occurs before target creation. The template then creates consumers for each enabled build variant.

State and persistence: Uses only generated build-tree state. It reads installed package config files from the prefix provided by the parent test.

Dependencies and integration points: Exercises `puffConfig.cmake` no-component behavior and installed target files.

Risks: The config requires both shared and static targets when no components are requested; the parent test marks configure as `WILL_FAIL` when either variant is disabled. This is intentional but can surprise downstream users expecting no-component discovery to accept any available variant.

Test signals: Parent CTest expects success only when both puff library variants are available.
