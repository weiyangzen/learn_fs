# sources/cloud-native/cri-o/internal/factory/container/namespaces_test.go

## Purpose
Tests Linux namespace configuration for the factory container, documenting how pod sandbox namespaces and CRI namespace options alter the OCI spec.

## Important APIs, Types, And Functions
- Exercises `sut.SpecAddNamespaces` and `sut.PidNamespace`.
- Uses `sandbox.Sandbox`, `nsmgrtest.AllSpoofedNamespaces`, `nsmgrtest.ContainerWithPid`, and `config.Config.NamespaceManager`.
- Uses CRI `types.NamespaceOption` modes and OCI `rspec` namespace constants.

## Control Flow
Tests create container configs with namespace options, attach spoofed namespace paths to a sandbox, clear default generator namespaces, call `SpecAddNamespaces`, and inspect resulting `spec.Config.Linux.Namespaces`. Target PID mode initializes a real namespace manager, resolves the current process as the target container, and verifies the stored managed PID namespace path.

## State And Persistence
Most tests mutate only the OCI generator. The target PID test creates namespace-manager state under a temp directory and defers removal of the managed namespace returned by `sut.PidNamespace()`.

## Dependencies And Integration Points
Integrates CRI namespace modes with CRI-O sandbox and namespace manager test helpers. The target PID path depends on Linux `/proc` and is skipped when running rootless because namespace operations require privileges.

## Risks And Edge Cases
Test coverage highlights host namespace removal, empty managed namespace path skipping, sandbox PID misconfiguration risk, and target PID cleanup requirements. The host-PID expectation is sensitive to default namespace entries and spoofed namespace fixture contents.

## Test Signals
Strong signal for Linux namespace behavior. It covers success and important mode-dependent transformations, including the privileged target PID path.
