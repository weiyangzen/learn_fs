# sources/control-plane/rook/pkg/operator/ceph/file/mds/spec.go

## Purpose
This file constructs Kubernetes Deployment and container specs for MDS daemons. It applies Ceph daemon labels, volumes, init containers, probes, network settings, placement, annotations, resources, security contexts, log collection, and image/version labels.

## Important APIs, Types, and Functions
`makeDeployment` builds the full Deployment. `makeChownInitContainer` creates the init container for Ceph data directories. `makeMdsDaemonContainer` creates the `ceph-mds` container with daemon flags and generated liveness probe. `podLabels` builds stable labels including `rook_file_system`. `getMdsDeployments`, `deleteMdsDeployment`, and `scaleMdsDeployment` list, delete, or scale filesystem-specific MDS Deployments.

## Control Flow, State, and Persistence
The pod template starts with a chown init container and one MDS container. It mounts daemon volumes, applies unreachable-node toleration, placement, labels, annotations, host networking or Multus configuration, log collector sidecar when enabled, default service account, and priority class. The Deployment uses Recreate strategy, one replica, a selector based on pod labels, revision history limit, Rook version label, and Ceph version label. Non-host and non-Multus networking adds `--public-addr=$(ROOK_POD_IP)` to MDS args.

## Dependencies and Integration Points
The spec integrates with Rook controller helpers for daemon flags, volumes, env vars, log collection, security context, probes, Multus, version labels, and chown init containers. It consumes fields from `CephFilesystem.Spec.MetadataServer` and `ClusterSpec.Network`, `ClusterSpec.LogCollector`, and Ceph image settings.

## Risks
`scaleMdsDeployment` dereferences `d.Spec.Replicas` after a Get that may fail with not-found when scaling to zero, which can panic if callers pass a missing deployment and replicas is zero. The Deployment selector is immutable; changes to selector labels can force higher-level delete/recreate behavior elsewhere. Applying both Rook labels and user labels means user label conflicts could affect selectors or identity if not guarded upstream.

## Test Signals
Signals include full pod template conformance, resource requests/limits, priority class propagation, liveness probe override behavior, `--public-addr` presence only for pod networking, host-network DNS policy, log collector sidecar behavior, Multus annotation application, and `rook_file_system` selector listing.
