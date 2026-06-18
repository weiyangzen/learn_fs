# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_stop_test.go

This test file targets the helper `criService.waitSandboxStop`. It constructs a test CRI service and sandbox store objects with different internal states, then verifies waiting behavior under context deadlines, cancellation, and already-stopped sandboxes.

The table cases show that a ready sandbox with a short context timeout returns an error when no stop signal arrives, an already-cancelled context returns an error immediately, and a not-ready sandbox created through `sandboxstore.NewSandbox` has its stop channel already closed and returns nil before the long timeout. The important integration point is the `store.StopCh` embedded in `sandboxstore.Sandbox`; `NewSandbox` marks not-ready sandboxes as stopped by calling `Stop`.

The test provides a narrow signal for stop waiting semantics and context propagation. It does not exercise the larger `StopPodSandbox` control flow: container force stop, sandbox controller stop, NRI callbacks, CNI teardown, netns removal, metric updates, or image mount cleanup. Risks outside this test remain in idempotency and partial cleanup interactions, while this test specifically guards against deadlocks and incorrect handling of context cancellation.
