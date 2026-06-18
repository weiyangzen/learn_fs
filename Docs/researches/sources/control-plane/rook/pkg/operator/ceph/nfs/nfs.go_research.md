<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/nfs.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/nfs.go

## Purpose
This file manages concrete NFS-Ganesha daemon lifecycle beneath the `CephNFS` reconciler: creating/updating per-instance ConfigMaps, Deployments, Services, RADOS config objects, keyrings, grace database entries, and scale-down cleanup.

## Important APIs and control flow
`upCephNFS` discovers daemons labeled to skip reconcile, loops over desired active instances (`a`, `b`, `c`, ...), creates/updates the config map, ensures the RADOS config object exists, applies Kerberos RADOS config, generates keyrings, builds and creates/updates the Deployment, creates the Service, and adds the server to the Ganesha grace database. `addRADOSConfigFile` stats and creates `conf-nfs.<name>`. `addServerToDatabase` and `removeServerFromDatabase` wrap `ganesha-rados-grace`. `generateConfigMap` and `createConfigMap` persist generated Ganesha config and return a stable hash. `downCephNFS` deletes Service, ConfigMap, grace DB entry, then Deployment for removed instances. `validateGanesha` checks required name/namespace/RADOS/active fields. `configureNFSPool` creates `.nfs` and enables the `nfs` application.

## State and persistence
State includes Kubernetes ConfigMaps, Deployments, Services, keyring Secrets, `.nfs` pool/application metadata, Ganesha config RADOS objects, Kerberos RADOS config, and grace database records. The config hash is persisted in Deployment pod template annotations.

## Dependencies and integration points
The file integrates Rook controller helpers, Ceph command wrappers, `ganesha-rados-grace`, deployment update machinery, Kubernetes owner references, skip-reconcile labels, and config/security/spec helpers from the same package.

## Risks and test signals
Scale-down deletes service/config before deployment and ignores grace DB remove errors by logging; partial failures can leave stale Ceph-side grace records. `configureNFSPool` unconditionally issues pool create and app enable commands, relying on Ceph idempotency or command behavior. Tests cover config hash stability, multi-instance creation, services, skip-reconcile behavior, and list-failure errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/nfs.go -->
