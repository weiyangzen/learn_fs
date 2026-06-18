<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal.go

Purpose: provides process-wide shutdown signal handling shared by long-running components.

Important API/state: `SetupSignalHandler() <-chan struct{}` and package globals `once`, `stop`, and `shutdownSignals` (`os.Interrupt`, `SIGTERM`). The first call installs `signal.Notify` and launches a goroutine.

Control flow and state: on the first shutdown signal, the goroutine closes `stop`, broadcasting graceful shutdown. On a second signal, it calls `os.Exit(1)`. `sync.Once` ensures all callers receive the same channel and only one signal goroutine is installed.

Dependencies/integration: used by the system controller server to close its Unix listener. It is intentionally process-global.

Risks and test signals: because it is singleton global state, tests or components cannot reset it in-process. A second signal forces immediate exit, which can bypass deferred cleanup. `signal_test.go` verifies the broadcast behavior for two listeners.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal.go -->
