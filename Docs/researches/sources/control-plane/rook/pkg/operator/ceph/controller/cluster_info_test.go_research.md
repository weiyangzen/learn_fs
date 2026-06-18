# sources/control-plane/rook/pkg/operator/ceph/controller/cluster_info_test.go

## Purpose
`cluster_info_test.go` validates cluster credential creation/loading and CSI setting defaulting for `CreateOrLoadClusterInfo()`.

## Important APIs, Types, and Functions
`TestCreateClusterSecrets` uses a mock executor that intercepts `ceph-authtool --create-keyring` and writes a fake keyring. It then calls `CreateOrLoadClusterInfo()` through several Secret formats and ClusterSpec variants. Assertions cover admin username/secret, FSID presence, `rook-ceph-mon` Secret contents, owner-reference reconstruction, old `admin-secret` migration, legacy external creds, and CephFS kernel mount option defaulting.

## Control Flow, State, and Persistence
The test creates a local temporary config dir and persists Kubernetes Secrets in a fake clientset. It mutates the stored `rook-ceph-mon` Secret to simulate older clusters and external-cluster placeholders, then creates `rook-ceph-operator-creds` for legacy external credentials. It also toggles operator env `CSI_CEPHFS_KERNEL_MOUNT_OPTIONS` and spec CSI values.

## Dependencies and Integration Points
It depends on fake Kubernetes clients, `exectest.MockExecutor`, Ceph CR specs, `cephclient.NewMinimumOwnerInfoWithOwnerRef()`, and Kubernetes Secret APIs. It exercises file-system writes for generated keyrings.

## Risks
The test is broad and stateful, which makes ordering important. It does not validate monitor endpoint ConfigMap parsing even though `CreateOrLoadClusterInfo()` always calls `loadMonConfig()`. It uses fake client behavior for status and Secret updates. The mock executor writes identical key text for mon and admin keys, so it does not catch command argument mix-ups beyond the first args.

## Test Signals
Strong signals are credential persistence, backward compatibility, owner ref reuse, and CSI mount option precedence: explicit spec over env, env over empty default, encryption default when applicable. Missing signals include invalid keyring parsing, Secret update conflicts, mon mapping JSON errors, and context-canceled external cluster waits.
