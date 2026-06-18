# sources/compression/zlib/contrib/blast/test/find_package_no_components_test.cmake.in

Purpose: generated consumer project that verifies default `find_package(blast REQUIRED CONFIG)` behavior without component selection.

Important APIs/settings: calls `find_package(blast REQUIRED CONFIG)`, then links test executables to shared/static targets according to substituted build options.

Control flow: package config decides whether both targets are available. The parent test marks this configure as expected failure when either shared or static blast was not built.

State and persistence: generated and configured under the blast test work directory.

Dependencies and integration: validates installed `blastConfig.cmake` no-components semantics.

Risks: no-components requiring both shared and static can be stricter than consumer expectations, but the test documents current behavior.

Test signals: configure success only when installed package exposes both component targets.
