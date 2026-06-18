# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/suite_test.go

Purpose: Ginkgo suite bootstrap for seccomp OCI artifact tests.

Important APIs/types/functions: `TestRun`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers fail handler, runs specs named `SeccompOCIArtifact`, initializes the CRI-O test framework before tests, and tears it down after.

State and persistence behavior: suite-level test framework state and temporary resources.

Dependencies/integration points: Ginkgo/Gomega and CRI-O test framework.

Risks: setup failure prevents artifact tests from running.

Test signals: harness only.
