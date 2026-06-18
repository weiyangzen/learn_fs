<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/suite_test.go -->
# sources/cloud-native/cri-o/utils/cmdrunner/suite_test.go

Purpose: Ginkgo suite bootstrap for `utils/cmdrunner`.

Important flow: `TestCommandRunner` registers Gomega's fail handler and calls CRI-O's `RunFrameworkSpecs`. `BeforeSuite` creates a `TestFramework` with no-op setup/teardown callbacks and calls `Setup`; `AfterSuite` tears it down.

State and integration: initializes shared CRI-O test framework state for this package. Risks are hidden framework side effects and suite-level state shared across specs. Test signal is that cmdrunner specs run under the same framework conventions as broader CRI-O tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/suite_test.go -->
