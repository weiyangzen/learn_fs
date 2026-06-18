# sources/compression/zlib/contrib/blast/test/find_package_wrong_components_test.cmake.in

Purpose: generated negative test for unsupported blast package components.

Important APIs/settings: calls `find_package(blast REQUIRED COMPONENTS wrong CONFIG)` and contains normal executable linkage blocks that should not be reached on successful failure.

Control flow: package config should reject `wrong`, set not-found state, and cause configure failure because `REQUIRED` is used. Parent CTest marks this configure with `WILL_FAIL TRUE`.

State and persistence: generated under test work directory; expected to fail during configure before build artifacts matter.

Dependencies and integration: validates component validation in `blastConfig.cmake.in`.

Risks: if package config stops rejecting unknown components, this test will fail by unexpectedly succeeding.

Test signals: expected configure failure is the signal.
