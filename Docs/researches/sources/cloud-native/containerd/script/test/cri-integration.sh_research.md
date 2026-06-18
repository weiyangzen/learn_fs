<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/test/cri-integration.sh -->
# sources/cloud-native/containerd/script/test/cri-integration.sh

- Purpose: Runs the built `cri-integration.test` binary against a freshly started test containerd daemon.
- Important variables: `FOCUS`, `REPORT_DIR`, `RUNTIME`, `RUNC_FLAVOR`, `TEST_IMAGE_LIST`, and paths initialized by sourced `utils.sh`.
- Control flow: Source test utilities, register teardown trap, choose report directory by OS, call `test_setup`, build a command with sudo/env, run the Go test binary with CRI endpoint/runtime/containerd/build-dir/image-list flags, and print logs on failure.
- State and persistence: Creates report directory, starts containerd with test root/state paths, and may move `containerd.log` into `$GITHUB_WORKSPACE/report`.
- Dependencies and integration: Requires built `bin/cri-integration.test`, `bin/containerd`, `crictl`, CNI/runc setup, and `utils.sh`.
- Risks: Command assembly via string variables can mishandle unusual paths; failure handling moves logs only in GitHub workspace mode.
- Test signals: Go test exit code and emitted containerd logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/test/cri-integration.sh -->
