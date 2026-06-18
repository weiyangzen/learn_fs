# sources/control-plane/rook/pkg/operator/ceph/controller/cleanup.go

## Purpose
`cleanup.go` builds and launches Kubernetes Jobs that perform destructive or forced cleanup for Rook Ceph custom resources. It also provides the annotation check used to detect user-requested force deletion.

## Important APIs, Types, and Functions
`ResourceCleanup` holds the target Kubernetes object, owning `CephCluster`, Rook image, and cleanup env configuration. `NewResourceCleanup()` constructs it. `StartJob()` creates a `batch.Job` and delegates execution to `k8sutil.RunReplaceableJob()`. `jobContainer()` builds the privileged cleanup container with args `ceph clean <Kind>`, resource-specific env vars, optional `ROOK_DATA_DIR_HOST_PATH`, pod namespace, and cleanup resources. `jobTemplateSpec()` wraps the container with volumes, restart policy, priority class, service account, and pod security context. `ForceDeleteRequested()` checks `rook.io/force-deletion: true` case-insensitively.

## Control Flow, State, and Persistence
Cleanup state is represented by an owned or replaceable Kubernetes Job. If `DataDirHostPath` is set, the path is mounted into the cleanup container and passed by env var. Resource-specific state is passed as environment variables from `config`. The job container runs the Rook image and relies on command dispatch inside that image to perform actual deletion work.

## Dependencies and Integration Points
The file integrates with Ceph CR types, cleanup resource/priority helpers from `cephv1`, Kubernetes batch/core APIs, `PrivilegedContext()` from `spec.go`, and `k8sutil.RunReplaceableJob()`. Constants define env names used by CephFS subvolume group and block pool RADOS namespace cleanup commands.

## Risks
`jobTemplateSpec()` always appends a hostPath volume using `cluster.Spec.DataDirHostPath`, even when the path is empty; the container only mounts it when non-empty. Cleanup jobs run privileged and as root, so incorrect config can have broad host impact. Map iteration over `config` makes env var order nondeterministic, which tests should avoid depending on. Force deletion is controlled by a simple annotation and should only be honored by callers after other safety checks.

## Test Signals
`cleanup_test.go` verifies job args/env count for a CephFS subvolume group and annotation detection. It does not run the job, verify hostPath behavior when empty, check owner references, or cover error paths from `RunReplaceableJob()`.
