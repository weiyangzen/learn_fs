<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner.go -->
# sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner.go

Purpose: package-level command execution abstraction for CRI-O code that needs globally configurable command wrapping, commonly for tests or running commands under another tool.

Important APIs and flow: `CommandRunner` defines `Command`, `CommandContext`, and `CombinedOutput`. The package-level `commandRunner` singleton defaults to `os/exec`. `PrependCommandsWith` installs a `prependableCommandRunner`; its `Command` and `CommandContext` replace the executable with `prependCmd` and prepend configured args plus the original command and args. `GetPrependedCmd` and `ResetPrependedCmd` expose state for tests.

State and persistence: singleton process state, no disk persistence. Risks include global mutable state with no synchronization, `prependArgs` slice aliasing and append mutation, and cross-test contamination without reset. Integration points are all code paths importing this package instead of `exec` directly. Test signal is `cmdrunner_test.go`, plus `cmdrunner_test_inject.go` for build-tagged mock injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner.go -->
