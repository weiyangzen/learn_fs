# sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr_test.go

Purpose: exercises the CNI manager readiness state machine, watcher notification behavior, shutdown semantics, garbage-collection deferral, and optional continuous health monitoring grace period. The file is test-only but documents the intended contract for `CNIManager` more completely than many callers do.

Important APIs/types/functions: `fakeCNIPlugin` implements the `ocicni.CNIPlugin` surface used by the manager, including `Status`, `StatusWithContext`, `GC`, pod setup/teardown, and network status methods. `newTestManager`, `newTestManagerWithGrace`, and `waitFor` build deterministic polling tests around short intervals and timeout guards. Main tests are `TestStatusPolling` and `TestGracePeriod`.

Control flow: tests start a manager with a fake plugin, mutate `statusErr`, and wait for `ReadyOrError` transitions. They verify initial readiness, startup recovery, runtime failure detection, recovery after failure, repeated flaps, shutdown cancellation, watcher delivery for ready/recovery/shutdown/already-ready states, abandoned watcher nonblocking behavior, GC on startup readiness, immediate GC when already ready, deferred GC when not ready, and GC error propagation.

State and persistence behavior: all state is in-memory test state: fake plugin status protected by a mutex, `gcCalls` as an atomic counter, manager readiness/error fields behind manager locks, watcher channels, and context cancellation. No disk persistence is used.

Dependencies/integration points: depends on `github.com/cri-o/ocicni/pkg/ocicni`, Go `testing`, `context`, `sync`, `atomic`, and `time`. It directly constructs a `CNIManager`, bypassing `New`, so it verifies manager internals and polling behavior without real CNI files or plugins.

Risks: timing-based tests can be sensitive to slow hosts because they rely on sleeps and polling deadlines. Since fake plugin methods mostly return nil for non-status operations, the tests do not validate real CNI setup/teardown behavior. The direct struct construction may miss initialization differences in `New`.

Test signals: this is the primary test signal for CNI manager health reporting. It gives strong coverage for readiness state transitions, watcher behavior, shutdown error reporting, and GC scheduling around readiness.
