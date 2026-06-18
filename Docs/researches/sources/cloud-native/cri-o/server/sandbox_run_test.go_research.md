# sources/cloud-native/cri-o/server/sandbox_run_test.go

Purpose: Ginkgo tests for `RunPodSandbox` validation and selected failure cleanup behavior.

Important APIs and functions: calls `sut.RunPodSandbox` with mocked storage runtime expectations and CRI sandbox configs.

Control flow: tests container creation failure after storage setup, nil/missing metadata validation, missing namespace validation, and relative log path rejection.

State and persistence: uses mocks for storage runtime calls, temporary paths, server name/index state, and test fixture setup. Some tests skip rootless where root is required.

Dependencies and integration: gomock storage runtime server, CRI-O test framework, storage container info, image-spec config, CRI sandbox types.

Risks: the file explicitly notes the internal function has high cyclomatic complexity and should be refactored for more isolated testing. It covers early errors more than successful sandbox creation.

Test signals: protects critical validation gates and confirms cleanup calls such as storage deletion are expected in early failure scenarios.
