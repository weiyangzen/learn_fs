# sources/cloud-native/moby/integration/daemon/nri/plugin.go

Purpose: in-process NRI plugin test harness used by the NRI integration tests to inject deterministic container-create adjustments.

Important APIs and types: `builtinPluginConfig`, `builtinPlugin`, `startBuiltinPlugin`, and NRI lifecycle methods `Configure`, `Synchronize`, `Shutdown`, `RunPodSandbox`, `StopPodSandbox`, `RemovePodSandbox`, `CreateContainer`, `PostCreateContainer`, `StartContainer`, `PostStartContainer`, `UpdateContainer`, `PostUpdateContainer`, `StopContainer`, `RemoveContainer`, and `onClose`.

Control flow: `startBuiltinPlugin` constructs a `stub.Stub` with plugin name/index/socket path and an on-close callback, starts it, waits for `Synchronize` to close a channel, and returns `stub.Stop`. Most lifecycle callbacks log and return nil. `CreateContainer` returns the configured `ctrCreateAdj` and no updates, making the tests control exactly what adjustment the daemon receives.

State and persistence: state is process-local: the configured adjustment, stub handle, logger, and a `sync.Once`-guarded synchronization channel. No persistent files are written by this helper.

Dependencies and integration: depends on containerd NRI `api` and `stub`, containerd logging, testing assertions, and daemon NRI socket support. It integrates the Go test process as an NRI plugin.

Risks: `Configure` rejects non-empty YAML config, so tests using this helper cannot cover plugin config parsing. If synchronization never arrives, `startBuiltinPlugin` fails via context cancellation.

Test signals: helper-only file; it enables high-signal NRI daemon tests by removing external plugin process complexity for most adjustment cases.
