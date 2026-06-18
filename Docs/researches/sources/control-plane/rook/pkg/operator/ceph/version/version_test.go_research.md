# sources/control-plane/rook/pkg/operator/ceph/version/version_test.go

Purpose: verifies Ceph version formatting, parsing, support decisions, ordering, and external-cluster compatibility rules.

Important APIs/types/functions: `TestToString`, `TestCephVersionFormatted`, `TestReleaseName`, `extractVersionHelper`, `TestExtractVersion`, `TestSupported`, `TestIsRelease`, `TestVersionAtLeast`, `TestVersionAtLeastX`, `TestIsIdentical`, `TestIsSuperior`, `TestIsInferior`, `TestValidateCephVersionsBetweenLocalAndExternalClusters`, and `TestCephVersion_Unsupported`.

Control flow: parse tests feed release output, multiline shell output, development build output, no-version development output, and round-trip serialized output. Comparison tests check major/minor/extra/build relationships. External validation tests allow identical, allow external major/minor ahead, and reject local ahead. Unsupported tests assert current versions are not in the unsupported list.

State and persistence behavior: no persistence; all tests are pure in-memory assertions.

Dependencies/integration: uses testify and package-level version constants/regex behavior.

Risks: current tests do not cover commit-ID superiority/inferiority asymmetry deeply, Umbrella `IsAtLeast` helpers, or future unsupported-version entries. Duplicate test case names in `TestCephVersion_Unsupported` are harmless but reduce clarity.

Test signals: strong guard for parser compatibility with real `ceph --version` outputs and release policy changes.
