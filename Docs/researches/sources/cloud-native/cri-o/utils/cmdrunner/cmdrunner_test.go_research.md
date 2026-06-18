<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test.go -->
# sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test.go

Purpose: Ginkgo/Gomega specs for the command runner singleton and prepend behavior.

Important coverage: verifies prepend state can be reset, default `CombinedOutput` matches `exec.Command`, configured `PrependCommandsWith("which")` changes command output and reports the prepended command, and configuring only prepend args with an empty command does not wrap execution.

State and integration: mutates the package singleton and explicitly resets it in test bodies. It depends on host `ls` and `which` commands. Risks include PATH/environment-specific output and no coverage for `CommandContext`, concurrent access, or prepend argument slice mutation. Test signal is direct unit coverage of the main public behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test.go -->
