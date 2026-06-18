# sources/compression/zlib/contrib/iostream3/test/find_package_no_components_test.cmake.in

Purpose: template for validating `find_package(iostreamv3 CONFIG)` without explicit components.

Important APIs/types/functions: project `iostream_find_package_no_components`, options for shared/static expectations, `find_package(iostreamv3 REQUIRED CONFIG)`, and example executables linked to available shared/static aliases.

Control flow: after installation to a test prefix, CTest configures this project. The package config attempts to load both shared and static exports when no components are requested. The template then declares executable targets for the variants expected by the substituted options.

State and persistence: generated and configured in a CTest work directory.

Dependencies/integration: depends on installed iostreamv3 package config and imported targets.

Risks: the package config intentionally fails no-components mode when either shared or static is missing; the parent test marks that case `WILL_FAIL`. This is strict behavior that may surprise consumers.

Test signals: the corresponding configure test should pass only when both variants were built and installed.
