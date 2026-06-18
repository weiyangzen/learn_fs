## sources/cloud-native/moby/integration-cli/docker_hub_pull_suite_test.go

Purpose: defines `DockerHubPullSuite`, an isolated daemon suite for pull/push tests that need a clean image store rather than the globally preloaded integration daemon.

Control flow: `SetUpSuite` requires Linux and a local daemon, constructs a `daemon.Daemon` with the current environment, and starts it. `SetUpTest` requires network access. `TearDownTest` removes all images from the suite daemon and delegates generic cleanup to `DockerSuite`. `Cmd`, `CmdWithError`, and `MakeCmd` wrap `docker --host <suite-sock>` invocations.

State is the dedicated daemon, its image store, and the suite socket path. Dependencies include `integration-cli/daemon`, `internal/testutil/daemon`, network requirement checks, and `exec.Command`. Risks include reliance on Docker Hub/network availability, destructive image cleanup within the isolated daemon, and command wrappers that use combined output. Test signals are indirect: consuming tests get a fresh daemon and fail through `assert.Assert` on nonzero command errors.
