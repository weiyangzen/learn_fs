# sources/cloud-native/cri-o/internal/process/defunct_processes_suite_test.go

Purpose: Ginkgo suite bootstrap for process package tests.

Important APIs/types/functions: `TestProcess`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers Gomega failures, runs `Process` framework specs, creates the test framework before tests, and tears it down after tests.

State and persistence behavior: initializes shared test fixtures and framework state; production state is untouched.

Dependencies and integration points: depends on Ginkgo v2, Gomega, Go `testing`, and CRI-O test framework helpers.

Risks: tests depend on relative fixture paths under the process package working directory.

Test signals: enables `t.Describe` use in `defunct_processes_test.go`.
