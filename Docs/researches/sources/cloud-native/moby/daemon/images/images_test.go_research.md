<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/images_test.go -->
# sources/cloud-native/moby/daemon/images/images_test.go

Purpose: unit tests for platform matching fallback behavior.

Important APIs and control flow: `TestOnlyPlatformWithFallback` constructs an ARM v8 platform and asserts that the matcher accepts the same OS/architecture with no variant, accepts the exact variant, and rejects a different architecture.

State and persistence: no state.

Dependencies and integration: uses OCI platform structs and `gotest.tools` assertions. It validates the matcher used by `GetImage`, pull, and BuildKit local image resolution.

Risks: the test covers only one architecture family and does not assert OS mismatch or different non-empty variants. It still captures the main config-without-variant compatibility rule.

Test signals: direct coverage for `OnlyPlatformWithFallback`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/images_test.go -->
