<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/context.go -->
# sources/control-plane/rook/pkg/clusterd/context.go

Purpose: defines `clusterd.Context`, the shared dependency container used by Rook cluster orchestration and daemons when applying Kubernetes and Ceph configuration.

Important APIs/types/functions: the `Context` struct carries `KubeConfig`, core `Clientset`, controller-runtime `Client`, Rook typed clientset, API extensions client, local and remote command executors, config paths, CNI network client, and discovered `Devices`.

Control flow: this file has no functions; callers construct and pass `Context` through operator and daemon code so lower layers can access Kubernetes, execution, configuration, networking, and device inventory dependencies consistently.

State and persistence behavior: the struct is process-local state. Its clients talk to Kubernetes persistence, executors run host or pod commands, and `Devices` snapshots local disk discovery results.

Dependencies and integration points: integrates Kubernetes client-go, controller-runtime, Rook generated clients, CNI network attachment clients, Rook exec abstractions, and `sys.LocalDisk` inventory. Cleanup and discovery code in this subset consumes it directly.

Risks: because the struct is broad and mutable, nil fields can panic in consumers that assume a fully initialized context. Tests often populate only the executor, so new consumers should keep dependency requirements explicit.

Test signals: construction paths for operator contexts, unit tests with partial contexts, and integration tests that exercise Kubernetes clients, remote execution, and device inventory together.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/context.go -->
