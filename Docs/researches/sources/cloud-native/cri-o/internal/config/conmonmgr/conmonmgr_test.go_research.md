# sources/cloud-native/cri-o/internal/config/conmonmgr/conmonmgr_test.go

Purpose: validates `ConmonManager` construction and feature-detection rules without invoking a real conmon binary.

Important APIs/types/functions: uses `runnerMock.MockCommandRunner`, `cmdrunner.SetMocked`, and Ginkgo/Gomega test cases around `New`, `parseConmonVersion`, `initializeSupportsSync`, and `initializeSupportsLogGlobalSizeMax`.

Control flow: setup installs a mocked command runner. Tests assert failure for non-absolute paths, failed version command, malformed version output, and invalid semver. Threshold tables are expressed as individual examples for major/minor/patch/equal comparisons. Log-global-size tests additionally mock `--help` output for versions below the threshold.

State and persistence behavior: modifies global cmdrunner mock state for the test process. No disk state is used.

Dependencies/integration points: depends on Ginkgo/Gomega, gomock, CRI-O test mocks, and `cmdrunner`. It verifies the integration contract between the manager and the shell-command abstraction.

Risks: command expectations use broad `gomock.Any()` arguments, so they primarily verify behavior outcome rather than exact `--version`/`--help` invocation shape. Tests do not cover unusual version strings with prefixes or build metadata.

Test signals: strong unit coverage for conmon feature gates and error paths, including the backported `--log-global-size-max` fallback.
