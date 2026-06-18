# sources/cloud-native/moby/integration/container/pidmode_linux_test.go

Purpose: Linux PID namespace tests for host mode and `container:<name>` mode.

Important APIs and flow: `TestPIDModeHost` reads host `/proc/1/ns/pid`, runs a host-PID container and a default container, then compares namespace links via `container.GetContainerNS`. `TestPIDModeContainer` validates three cases: non-existing target errors at create, non-running target creates but fails at start with an internal namespace-join error, and running target starts successfully.

State and dependencies: Uses namespace symlinks, running/stopped containers, and API create/start boundaries. Skips non-Linux and remote daemon for host namespace comparisons.

Risks and signals: It protects PID namespace mode validation timing and error reporting. Failures can mean containers join wrong namespaces, reject valid deferred cases, or misclassify missing/non-running target errors.
