# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/config.go

## Purpose

This file contains monitor configuration helpers shared by mon orchestration and other daemons. It builds the shared mon keyring, derives monitor host data paths, writes client connection config, and exposes the secret volume/mount used by sidecars that need the Ceph admin secret.

## Important APIs and Behavior

`genMonSharedKeyring()` renders `keyringTemplate` with the cluster monitor secret and the admin credential keyring. The template grants the mon identity full mon caps and appends admin keyring material.

`dataDirRelativeHostPath(monName)` returns the mon data directory below `dataDirHostPath`. Legacy names containing `mon` are used directly; letter IDs such as `a` become `mon-a/data`. This preserves Rook's historic storage layout.

`WriteConnectionConfig()` delegates to `cephclient.GenerateConnectionConfig()` and wraps failures. `CephSecretVolume()` creates a Secret volume named `ceph-admin-secret` from the `rook-ceph-mon` secret and maps `controller.CephUserSecretKey` to `secret.keyring`. `CephSecretVolumeMount()` mounts that secret read-only at `/var/lib/rook-ceph-mon`.

## State, Persistence, and Dependencies

Generated keyring content is stored by callers in Kubernetes Secrets. Connection config is written to the operator config directory. The volume helpers are consumed by mgr sidecars and other pods that need mon/admin credentials. Dependencies include Ceph client config generation, Rook key naming conventions, path utilities, and Kubernetes core volume types.

## Risks and Test Signals

The keyring template and secret key names are security-sensitive. Path compatibility is also important because changing `dataDirRelativeHostPath()` could orphan existing mon data. Coverage is mostly indirect through mon and mgr spec/startup tests that use these helpers to build deployments and sidecar volume mounts.
