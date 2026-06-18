# sources/cloud-native/cri-o/internal/criocli/suite_test.go

Purpose: Ginkgo suite bootstrap for CLI tests.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers fail handler, runs framework specs named `CLIConfig`, initializes the CRI-O test framework, and tears it down.

State and persistence behavior: suite-local test framework state.

Dependencies/integration points: Ginkgo/Gomega and CRI-O test framework.

Risks: suite setup failures prevent CLI tests from running.

Test signals: harness only.
