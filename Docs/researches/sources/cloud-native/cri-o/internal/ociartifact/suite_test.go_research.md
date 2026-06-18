# sources/cloud-native/cri-o/internal/ociartifact/suite_test.go

Purpose: Ginkgo suite bootstrap for the `ociartifact_test` package.

Important APIs/types/functions: `TestRun`, package-global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers the Gomega fail handler, runs framework specs named `OCIArtifact`, creates a CRI-O `TestFramework` before the suite, and tears it down afterward.

State and persistence behavior: initializes shared test framework state and temporary test resources. No production state is persisted.

Dependencies and integration points: depends on Ginkgo v2, Gomega, Go `testing`, and `github.com/cri-o/cri-o/test/framework`.

Risks: global `t` means individual tests assume suite setup succeeded. Failures in setup can cascade across the package.

Test signals: required for all OCI artifact tests using `t.Describe`, `t.MustTempDir`, and framework helpers.
