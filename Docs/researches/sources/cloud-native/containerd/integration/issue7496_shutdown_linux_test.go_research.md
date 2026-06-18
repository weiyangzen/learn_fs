# sources/cloud-native/containerd/integration/issue7496_shutdown_linux_test.go

## Purpose

This Linux regression test documents a desired retry behavior for shim `Shutdown` after issue 7496-style timing races. It is currently skipped until retry support is available.

## Important APIs, Types, And Functions

- `TestIssue7496_ShouldRetryShutdown` is the skipped test.
- `injectShimFailpoint` is called to inject a `Shutdown` failpoint into the sandbox config.
- `connectToShim` and `shimPid` inspect the failpoint-enabled shim.

## Control Flow

If enabled, the test would create a sandbox using the failpoint runtime handler with a `Shutdown` failpoint that returns one error, connect to its shim, stop and remove the sandbox, and then assert that connecting to the shim fails, proving it was eventually shut down despite the injected error.

## State And Persistence Behavior

The intended state under test is shim lifecycle after a transient shutdown API failure. Failpoint configuration is carried through sandbox annotations into the failpoint shim.

## Dependencies And Integration Points

It depends on the failpoint shim runtime, ttrpc task APIs, CRI sandbox lifecycle, and the `injectShimFailpoint` helper defined elsewhere in the integration suite.

## Risks And Edge Cases

The test is explicitly skipped with a message to re-enable when shutdown retry is implemented. If enabled prematurely, it would fail by design.

## Test Signals

Currently the only signal is skipped coverage. When re-enabled, passing would confirm transient shim shutdown errors are retried rather than leaking the shim.
