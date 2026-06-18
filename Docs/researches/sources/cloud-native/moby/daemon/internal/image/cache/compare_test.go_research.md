## sources/cloud-native/moby/daemon/internal/image/cache/compare_test.go

Purpose: Tests cache comparison helpers.

Important tests: `TestCompare` builds same/different `container.Config` pairs covering ignored fields, user, stdin flags, env, command, labels, exposed ports, entrypoints, volumes, and count mismatches. `TestPlatformCompare` checks architecture, OS, ARM variants, and Windows OS version compatibility.

Control flow and state: The config test iterates maps of pointer pairs and fails fast on unexpected compare results. Platform OSVersion cases are skipped when not running on Windows because containerd's platform matcher only compares OSVersion on Windows.

Dependencies and integration: Uses API `container.Config`, network port parsing, OCI platform structs, runtime GOOS, and `gotest.tools` assertions.

Risks covered: Regressions in ignored fields, ordered slice matching, map membership/value matching, ARM variant compatibility, and Windows major/minor semantics. Gaps include stop timeout, healthcheck, shell, onbuild, and labels with nil vs empty map distinctions beyond length checks.

Persistence: None.
