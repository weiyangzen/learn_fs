<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/suite_test.go -->
# sources/cloud-native/cri-o/utils/suite_test.go

Purpose: Ginkgo suite bootstrap for the `utils` package tests.

Important flow: `TestUtils` registers fail handling and runs framework specs. Suite setup constructs a CRI-O `TestFramework` with no-op callbacks, calls `Setup`, and tears it down after all specs.

State and integration: suite-level test framework lifecycle; no production behavior. Risks are shared package-global state across specs and hidden framework setup assumptions. Test signal is enabling all `utils` Ginkgo specs under the CRI-O test framework.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/suite_test.go -->
