# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/keyring_test.go

## Purpose
This file tests node-daemon CephX caps, key generation, rotation, and CephCluster status updates for crash collector and ceph-exporter.

## Important APIs, Types, And Functions
`TestCephCrashCollectorKeyringCaps` and `TestExporterKeyringCaps` validate exact cap slices. `TestCreateCrashCollectorKeyring` exercises `createCrashCollectorKeyring()`. `TestCreateCephExporterKeyring` exercises `createExporterKeyring()`.

## Control Flow And State
Both keyring tests construct a fake CephCluster with key-generation policy, uninitialized cephx status, fake controller-runtime client, and mock executor. The mock returns a static key for `auth get-or-create-key` and a rotated key for `auth rotate`. The tests first verify initial key generation, then update cluster spec key generation, raise Ceph version to a rotation-supporting version, call the keyring function again, and verify the rotated key plus status generation update.

## Dependencies And Integration Points
The tests depend on Rook keyring helpers, fake controller-runtime clients, Ceph version constants, mock executors, CephCluster API types, and cluster info owner refs. They validate the integration between Ceph auth commands and Kubernetes CR status.

## Risks And Test Signals
The tests prove both daemon identities rotate independently and update the correct `Status.Cephx` field. They do not validate final Kubernetes Secret creation, owner refs, or retry conflict behavior in the status update path.
