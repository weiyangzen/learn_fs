# sources/control-plane/rook/pkg/operator/k8sutil/pod.go

## Purpose
`pod.go` provides common pod-spec, environment, lookup, toleration, anti-affinity, deletion, and scheduling helpers for Rook operator code.

## Important APIs, Types, and Functions
Environment helpers create downward-API env vars: `ConfigOverrideEnvVar()`, `PodIPEnvVar()`, `NamespaceEnvVar()`, `NameEnvVar()`, `NodeEnvVar()`, and `ConfigDirEnvVar()`. Container helpers include `GetContainerImage()`, `GetSpecContainerImage()`, and `GetContainerByName()`. Pod status helpers include `GetRunningPod()`, `PodsRunningWithLabel()`, `PodsWithLabelAreAllRunning()`, `GetPodPhaseMap()`, and `IsPodScheduled()`. Spec mutators include `AddUnreachableNodeToleration()`, `ClusterDaemonEnvVars()`, `SetNodeAntiAffinityForPod()`, `ForceDeletePodIfStuck()`, and `RemoveDuplicateEnvVars()`.

## Control Flow, State, and Persistence
Some functions are pure spec builders; others read environment variables or Kubernetes pods/nodes. `ForceDeletePodIfStuck()` only force-deletes terminating pods on not-ready nodes and suppresses delete errors after logging. `RemoveDuplicateEnvVars()` keeps the first occurrence by name.

## Dependencies and Integration Points
It integrates with Kubernetes `PodSpec`, Rook `clusterd.Context`, Ceph placement application, and node readiness helpers. Downward-API env names are shared with operator manifests.

## Risks
`SetNodeAntiAffinityForPod()` assumes `pod.Affinity` is non-nil; callers must initialize it or use placement helpers first. `IsPodScheduled()` inspects only the first matching pod. `ForceDeletePodIfStuck()` treats delete failures as non-fatal, which preserves reconciliation but can hide stuck pods.

## Test Signals
`pod_test.go` covers container lookup mutation, phase maps, unreachable toleration replacement/defaulting, anti-affinity counts after placement, and pod scheduling detection.
