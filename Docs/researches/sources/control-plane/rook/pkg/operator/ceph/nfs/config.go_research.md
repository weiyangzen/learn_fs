<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/config.go

## Purpose
This file generates NFS-Ganesha CephX identities and config text, and manages Kerberos-related Ganesha config stored in RADOS objects. It also provides atomic helper functions for prepending/removing config blocks in RADOS with object locks.

## Important APIs and control flow
Identity helpers derive node IDs, client IDs, config object names, and RADOS URLs. `generateKeyring` creates or rotates a per-daemon `client.nfs-ganesha.<nfs>.<id>` key with monitor read caps and OSD read/write caps scoped to the `.nfs` pool and optional namespace, then writes a Kubernetes Secret. `getGaneshaConfig` returns the base Ganesha config using RADOS recovery, RADOS URLs, RGW identity, and NFSv4 settings. `setRadosConfig` adds or removes Kerberos config according to `nfs.Spec.Security.KerberosEnabled()`.

`setKerberosRadosConfig` writes the Kerberos block into a `kerberos` RADOS object and atomically prepends an include block into the main `conf-nfs.<name>` object. `removeKerberosRadosConfig` atomically removes that include block and deletes the Kerberos object. `atomicPrependToConfigObject` and `atomicRemoveFromConfigObject` create temp files, lock the RADOS object, fetch current content, skip idempotent work, rewrite content, put it back, and unlock with timeout-tolerant logging.

## State and persistence
Persistent state includes Ceph auth users, Kubernetes keyring Secrets, `.nfs` RADOS namespace objects (`conf-nfs.<name>` and `kerberos`), and the contents of Ganesha config in RADOS. Temporary files are local process state and are closed but not explicitly removed.

## Dependencies and integration points
The code depends on Rook Ceph client command wrappers, RADOS lock/unlock helpers, keyring secret store helpers, cluster context, Ceph version data, and NFS security CRD fields. It integrates with CSI/user changes to Ganesha exports by taking RADOS object locks before config mutation.

## Risks and test signals
Atomic config changes depend on exact string containment/replacement; formatting changes can create duplicate include blocks or fail removal. RADOS lock failures block reconciliation, and unlock failures are logged but tolerated because locks have timeouts. Tests in `controller_test.go` and `nfs_test.go` mock RADOS commands indirectly; this file's atomic read/write behavior is not deeply unit-tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/config.go -->
