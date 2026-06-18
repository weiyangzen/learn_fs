<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal_test.go

Purpose: validates that `SetupSignalHandler` returns a stop channel that broadcasts to multiple goroutines on SIGINT.

Important test: `TestSetupSignalHandler` starts two goroutines waiting on the returned channel, sends SIGINT to the current process with `syscall.Kill`, sleeps one second, and asserts both waiters incremented an atomic counter.

Control flow and state: the test mutates process-global signal handler state and sends a real process signal. Because production uses `sync.Once`, this test can affect later tests in the same process.

Dependencies/integration: uses syscall, atomic, time, and testify require.

Risks and test signals: strong signal for the first-signal close behavior, but it does not test second-signal forced exit or SIGTERM. It can be order-sensitive with other tests that also install signal handlers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal_test.go -->
