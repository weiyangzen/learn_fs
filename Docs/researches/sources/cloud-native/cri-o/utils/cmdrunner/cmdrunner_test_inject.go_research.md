<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test_inject.go -->
# sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test_inject.go

Purpose: test-build-only injection hook for replacing the command runner singleton with a generated mock.

Important API: under build tag `test`, `SetMocked` accepts `*MockCommandRunner` from `test/mocks/cmdrunner` and assigns it to the package-level `commandRunner`.

State and integration: mutates process-global command runner state during tests. No persistence. Risks include tests forgetting to reset the mock and the hook being unavailable unless the `test` build tag is used. Test signal is indirect: packages that need mocked command execution can use this hook.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test_inject.go -->
