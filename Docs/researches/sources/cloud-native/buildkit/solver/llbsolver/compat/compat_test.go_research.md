<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/compat/compat_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/compat/compat_test.go

Purpose: verifies the compatibility version constants and validation messages.

Important APIs and types: `TestSupportedCompatibilityVersions` and `TestValidateCompatibilityVersion` exercise `SupportedCompatibilityVersions`, `CompatibilityVersionCurrent`, and `ValidateCompatibilityVersion`.

Control flow: tests assert the exact supported slice `[10, 20, 30]`, current `30`, no error for version 13/current constants, an unsupported message for `11`, and an upgrade hint for `40`.

State and dependencies: test-only; depends on testify `require`.

Integration points: protects client/server compatibility negotiation and exporter metadata that depends on job compatibility.

Risks and test signals: exact slice assertion intentionally forces test updates when compatibility versions change.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/compat/compat_test.go -->
