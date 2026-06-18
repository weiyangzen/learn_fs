# sources/cloud-native/cri-o/test/nri/nri_suite_test.go

## Purpose
Suite harness and helper methods for CRI-O NRI integration tests.

## Important APIs, Types, And Functions
Defines global `crio *runtime`, `setup`, `cleanup`, `TestMain`, `setupLogging`, `testLogger`, `nriTest`, `(*nriTest).Setup`, `StartPlugins`, `Cleanup`, lifecycle helpers, `execShellScript`, and ID verification helpers.

## Control Flow
`TestMain` parses flags, skips runtime setup for `go test -list`, redirects logrus to test output, connects to CRI-O when sockets are provided, pulls images, runs tests, then disconnects. Each `nriTest` allocates a namespace, purges leftover pods/containers, creates configured test plugins, starts them, waits for synchronization when requested, and registers cleanup.

## State And Persistence
Uses live CRI-O runtime state through sockets, creates/removes pods and containers in unique namespaces, and manages in-process plugin instances.

## Dependencies And Integration Points
Integrates with the local NRI plugin implementation, containerd NRI API, runtime helpers from other NRI test files, logrus, and testify/require.

## Risks And Test Signals
Requires a running CRI-O test instance with NRI enabled. Cleanup is defensive but depends on CRI-O responsiveness. Strong integration signal for NRI event flow and runtime lifecycle.
