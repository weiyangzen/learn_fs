# sources/control-plane/juicefs-csi-driver/pkg/driver/driver_test.go

Purpose: tests `NewDriver` construction under normal, subservice-error, and `config.ByProcess` modes.

Important APIs and functions: `TestNewDriver` uses GoConvey cases. It patches `k8s.NewClient`, `newNodeService`, `newProvisionerService`, `exec.Command`, and `(*exec.Cmd).CombinedOutput` to avoid real Kubernetes or command execution, then asserts the endpoint is preserved or an error propagates from node service construction.

Control flow: each case replaces package functions with fakes, builds a Prometheus registerer using `util.NewPrometheus`, and calls `NewDriver`. The `by process` case sets `config.ByProcess = true` to skip Kubernetes client creation.

State and persistence behavior: manipulates global `config.ByProcess`, patches global functions, and constructs transient fake clientsets. It does not run the gRPC server or create persistent resources.

Dependencies and integration points: depends on gomonkey, GoMock, GoConvey, fake Kubernetes clientsets, Prometheus utility helpers, and driver subservice constructors. It is intended to verify constructor orchestration rather than CSI behavior.

Risks and test signals: the patch functions shown in this file use older signatures for `newNodeService` and `newProvisionerService` than the current implementations, which now accept Prometheus/leader-election arguments. That suggests the test may be stale or fail to compile until updated. The test also mutates `config.ByProcess` without restoring it, creating possible cross-test contamination.
