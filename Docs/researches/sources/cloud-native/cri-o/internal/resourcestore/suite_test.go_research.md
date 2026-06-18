# sources/cloud-native/cri-o/internal/resourcestore/suite_test.go

Purpose: Ginkgo suite bootstrap for resource store tests.

Important APIs/types/functions: `TestResourceStore`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers fail handler, runs framework specs named `ResourceStore`, sets up test framework state, and tears it down afterward.

State and persistence behavior: shared test framework state only.

Dependencies and integration points: depends on Ginkgo v2, Gomega, Go testing, and CRI-O test framework helpers.

Risks: global framework use means test files depend on suite initialization.

Test signals: enables `t.Describe` in resource cleaner/store tests.
