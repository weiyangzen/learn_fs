# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/crash.go

## Purpose
This file builds per-node Ceph crash collector Deployments. Crash collectors run `ceph-crash` on nodes hosting Ceph pods so crashes are posted to the Ceph cluster.

## Important APIs, Types, And Functions
Constants define crash collector cephx identity and secret names. `(r *ReconcileNode) createOrUpdateCephCrash(node, tolerations, cephCluster, cephVersion)` creates or updates a node-specific Deployment. `getCrashDirInitContainer()`, `getCrashChownInitContainer()`, `getCrashDaemonContainer()`, and `generateCrashEnvVar()` build the pod pieces.

## Control Flow And State
`createOrUpdateCephCrash` requires the Kubernetes hostname label on the node, constructs a truncated deployment name, sets controller ownership, builds base volumes and crash keyring volume, and calls `controllerutil.CreateOrUpdate`. The mutate function sets stable selector labels only on create, applies deployment labels, Ceph version and Rook version labels, and builds a pod bound to the target hostname through `NodeSelector`. The pod has crash directory and chown init containers, one `ceph-crash` container, inherited tolerations, optional host networking, priority class, empty pod security context, default service account, and crash collector annotations.

## Dependencies And Integration Points
The file depends on CephCluster API fields, Rook controller volume/env/security helpers, keyring volume helpers, Kubernetes Deployments, node labels, owner refs, and Ceph version labels. It integrates with `ReconcileNode.createOrUpdateNodeDaemons()` and the crash collector secret created in `keyring.go`.

## Risks And Test Signals
The hostname label is mandatory; missing it prevents deployment. Selector immutability is handled by setting selectors only for new objects. The crash container runs as the Ceph user because the script has no user flag. `crash_test.go` covers env var generation, create/update behavior, labels, tolerations, host network, priority class, Rook version label placement, and security context user/group.
