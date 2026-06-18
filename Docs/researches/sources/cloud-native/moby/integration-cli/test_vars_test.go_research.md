## sources/cloud-native/moby/integration-cli/test_vars_test.go

Purpose: platform-neutral helper that chooses a long-running container command for the daemon OS. `sleepCommandForDaemonPlatform` returns `["sleep", "240"]` for Windows because Windows busybox lacks `top`, and `["top"]` otherwise.

Control flow is a simple branch on `testEnv.DaemonInfo.OSType`. State is read-only daemon platform metadata. Dependencies are package-level `testEnv` and companion platform constants.

Risks are tests assuming `top` behavior on Windows or the fixed 240-second sleep being insufficient for slow tests. Integration points are service scale tests, container lifecycle helpers, and any test needing an idle container. Test signals are indirect: containers remain running long enough for subsequent CLI/API assertions on supported platforms.
