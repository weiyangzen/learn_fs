# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/command/command_builder_test.go

This test file verifies the command builder's observable argument ordering for a representative fscache singleton daemon command. `TestBuildCommand` constructs option slices using `WithMode`, `WithFscacheDriver`, `WithFscacheThreads`, `WithAPISock`, and optionally `WithUpgrade`, then joins the returned args to compare exact output strings.

The benchmark repeatedly calls `BuildCommand` with the same option set and asserts no error. Its comments record historical timings for the reflection implementation versus a baseline, making performance awareness explicit even though the benchmark is not a correctness gate.

The tests are useful because command-line ordering is field-order dependent in `DaemonCommand`; a refactor that reorders fields can change process launch behavior and fail this test. Coverage is narrow: it does not exercise fuse mode, config/bootstrap/mountpoint arguments, log options, supervisor/id coupling, backend source, prefetch files, failover policy, zero-value omission for numeric fields, or invalid tag handling. There is no filesystem or process state, only in-memory option application.
