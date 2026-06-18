# sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr_test_inject.go

Purpose: provides a `test` build-tag injection hook for replacing the CNI plugin inside an existing `CNIManager` during tests.

Important APIs/types/functions: `(*CNIManager).SetCNIPlugin(plugin ocicni.CNIPlugin) error` shuts down any currently installed plugin, assigns the supplied plugin, and calls `statusPollFunc` once to initialize readiness state without launching a racing background poller.

Control flow: when called, it first invokes `Shutdown` on the old plugin if present, returns that error if shutdown fails, replaces `c.plugin`, and performs a synchronous status poll with `isStartup=false`, ignoring the returned status/error intentionally for test setup.

State and persistence behavior: mutates only the in-memory `CNIManager.plugin` and readiness fields updated by `statusPollFunc`. It has no persistent storage behavior.

Dependencies/integration points: imports `context` and `ocicni`. The build tag `//go:build test` keeps this helper out of normal CRI-O binaries while allowing test code to control the otherwise internal plugin dependency.

Risks: because it ignores the poll result, callers must inspect manager state separately. The helper mutates manager internals and can race if used against a manager with active polling; the comment explicitly frames it as a way to avoid races in mocked setup.

Test signals: no independent tests in this file; it supports tests that need CNI plugin injection.
