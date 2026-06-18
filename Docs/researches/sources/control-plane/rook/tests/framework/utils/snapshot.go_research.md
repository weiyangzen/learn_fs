# sources/control-plane/rook/tests/framework/utils/snapshot.go

Purpose: this file installs/removes Kubernetes CSI snapshot CRDs/controllers and checks VolumeSnapshot readiness for integration tests.

Important APIs/types/functions: snapshotter constants for version `v8.5.0`, GitHub raw paths, `CheckSnapshotISReadyToUse`, `CreateSnapshotController`, `DeleteSnapshotController`, `CreateSnapshotCRD`, `DeleteSnapshotCRD`, and internal `snapshotController`/`snapshotCRD`.

Control flow: snapshot readiness polls `kubectl get volumesnapshot ... jsonpath={.status.readyToUse}` with increasing sleeps and parses a bool. Controller setup fetches the remote controller manifest, replaces `canary` with the pinned version, applies/deletes it via stdin, then applies/deletes RBAC by URL. CRD setup applies/deletes volume snapshot and volume group snapshot CRDs from remote URLs, adding `--validate=false` for create/apply.

State and persistence behavior: mutates cluster-scoped CRDs, snapshot-controller deployment/RBAC in `kube-system`, and VolumeSnapshot status observations.

Dependencies and integration points: used by Helm CSI driver installation and storage snapshot tests. Depends on GitHub raw content, kubectl, Kubernetes apps client for controller readiness, and shared retry interval.

Risks: external URL availability is required. `WaitForSnapshotController` may dereference deployment status even when not found because the zero-value object is not set when `ss` is nil in some client-go cases; this should be checked carefully. Readiness parsing treats non-bool output as retryable. Applying CRDs by URL depends on network and Kubernetes API compatibility.

Test signals: CRD existence, snapshot-controller ready replicas, VolumeSnapshot `readyToUse=true`, and cleanup deletion are key signals.
