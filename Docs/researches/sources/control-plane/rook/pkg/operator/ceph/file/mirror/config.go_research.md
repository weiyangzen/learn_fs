# sources/control-plane/rook/pkg/operator/ceph/file/mirror/config.go

## Purpose
This file generates and stores the CephX keyring for the `cephfs-mirror` daemon managed by `CephFilesystemMirror`. It defines the daemon user, capabilities, and key-rotation path.

## Important APIs, Types, and Functions
Constants define the keyring template, user `client.fs-mirror`, and user ID `fs-mirror`. `daemonConfig` carries the Kubernetes resource name, data path map, and owner info. `(*ReconcileFilesystemMirror).generateKeyring` requests caps for monitor, manager, MDS, and OSD access, optionally rotates the key, renders the keyring, and stores it with `CreateOrUpdate`.

## Control Flow, State, and Persistence
The reconciler calls `generateKeyring` before creating/updating the mirror Deployment. The key is generated or retrieved from Ceph auth state through the keyring store. If `shouldRotateCephxKeys` is true, `RotateKey` replaces it. The rendered keyring is persisted in the Kubernetes Secret named by `daemonConfig.ResourceName`, and its resource version is used to annotate the Deployment template.

## Dependencies and Integration Points
The file integrates with the keyring secret store, Ceph auth command helpers, filesystem mirror Deployment startup, owner references, and CephX rotation status in `CephFilesystemMirror.Status.Cephx`.

## Risks
The OSD cap string is nested in quotes inside the keyring template and must stay aligned with Ceph's parser. The `client.fs-mirror` user is shared for the daemon, so rotation affects all mirror daemon usage in the namespace. Failed rotation prevents deployment reconciliation.

## Test Signals
Signals include generated Secret data for `rook-ceph-fs-mirror-keyring`, resource version annotation changes, successful key generation, rotation when configured, and status updates reflecting the new key generation and Ceph version.
