# sources/cloud-native/cri-o/internal/storage/references/suite_test.go

Purpose: test-suite bootstrap for `internal/storage/references`.

Important APIs/types/functions: `TestReferences` registers Gomega's fail handler and runs framework specs named `Storage/references`; `BeforeSuite` creates and sets up a `TestFramework`; `AfterSuite` tears it down.

Control flow: Go test invokes `TestReferences`, Ginkgo runs specs, and suite hooks manage the shared framework lifecycle around all tests in the package.

State and persistence: holds package-level `t *TestFramework`. Any temporary resources are delegated to the framework setup/teardown.

Dependencies/integration: imports `github.com/cri-o/cri-o/test/framework` and Ginkgo/Gomega. This is standard CRI-O test wiring and not production code.

Risks: the package-level variable name `t` shadows common test naming but is a local suite convention. If framework setup grows heavier, even simple reference tests inherit that cost.

Test signals: confirms tests are framework-integrated, so build tags and suite setup must be available for the reference package tests to run.
