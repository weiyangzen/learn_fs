# sources/compression/zlib/contrib/iostream3/test/find_package_wrong_components_test.cmake.in

Purpose: template for ensuring unsupported iostream3 package components fail at configure time.

Important APIs/types/functions: `find_package(iostreamv3 REQUIRED COMPONENTS wrongCONFIG)` plus optional example targets that would link to shared/static aliases if configuration continued.

Control flow: the generated project immediately requests an unsupported component. The installed config checks requested components against `_iostreamv3_supported_components`, sets the package not found message, and the parent CTest expects this configure step to fail.

State and persistence: generated in a CTest work directory; normally no build targets are produced because configure should fail.

Dependencies/integration: depends on the package config component validation path.

Risks: the static block references `${PUFF_SRCS}` instead of `${IOSTREAM_SRCS}`, but this should be unreachable when the test behaves correctly. If package validation regresses and configure continues, the typo provides an additional failure signal but with a misleading cause.

Test signals: parent CTest marks the configure test `WILL_FAIL`.
