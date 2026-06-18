<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/spec.go

## Purpose
This file generates Kubernetes Services, Deployments, containers, probes, labels, and volumes for each CephNFS Ganesha daemon instance.

## Important APIs and control flow
`generateCephNFSService` creates a Service exposing NFS TCP 2049 and metrics 9587, using headless service mode for host networking. `createCephNFSService` creates it with an owner reference and treats already-existing services as success. `makeDeployment` builds the one-replica Deployment with generated Ceph config init container, `nfs-ganesha` daemon container, `dbus-daemon` sidecar, ceph/keyring/ganesha/dbus volumes, host network or Multus settings, placement, priority, stable hostname for Kerberos, config hash annotation, labels, annotations, and security additions. `connectionConfigInitContainer` uses the Ceph cluster image to generate minimal Ceph config and mount keyrings. `daemonContainer` runs `ganesha.nfsd` in foreground with log level, env vars, resources, liveness probe, and config/keyring/dbus mounts. `defaultGaneshaLivenessProbe` uses `rpcinfo` for Ceph >= 18.2.1 and TCP otherwise. `dbusContainer`, image helpers, label helpers, and volume helpers define supporting sidecar and volumes.

## State and persistence
State is Kubernetes resource specification. Config content is mounted from ConfigMaps; Ceph config and dbus sockets use emptyDir; keyrings use Secrets. Deployment annotations carry config hash to trigger rollouts.

## Dependencies and integration points
The file depends on Rook controller helpers for labels, probes, Ceph config init containers, image pull policy, version labels, placement, Multus, and security context. It calls `security.go` to add SSSD/Kerberos pod additions.

## Risks and test signals
In `makeDeployment`, host-network DNS policy is set on `podSpec` after `podTemplateSpec` is created in one branch, so later mutations must be carefully reflected in the template. Service creation does not update existing Services, so port/label changes may not reconcile until deletion. Tests cover base deployment, SSSD, Kerberos, combined security, resource expectations, service account, priority, labels, and liveness probe defaults.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/spec.go -->
