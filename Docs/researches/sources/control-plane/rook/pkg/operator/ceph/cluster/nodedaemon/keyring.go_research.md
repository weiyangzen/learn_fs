# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/keyring.go

## Purpose
This file creates and rotates CephX keyrings and Kubernetes Secrets for node daemons: crash collector and ceph-exporter.

## Important APIs, Types, And Functions
Constants define clients and keyring templates for `client.crash` and `client.ceph-exporter`. Public functions are `CreateCrashCollectorSecret()` and `CreateExporterSecret()`. Internal helpers include `cephCrashCollectorKeyringCaps()`, `createCrashCollectorKeyring()`, `updateCrashCollectorCephxStatus()`, `createOrUpdateCrashCollectorSecret()`, `createExporterKeyringCaps()`, `createExporterKeyring()`, `updateCephExporterCephxStatus()`, and `createOrUpdateExporterSecret()`.

## Control Flow And State
Secret creation obtains a `keyring.SecretStore`, generates or gets a Ceph key with daemon-specific caps, checks the owning `CephCluster` for key rotation requirements, optionally rotates the CephX key, updates `cluster.Status.Cephx.CrashCollector` or `CephExporter` via retry-on-conflict and `reporting.UpdateStatus`, formats a keyring file, sets owner refs on a Kubernetes Secret, and creates/updates it through the secret store. Crash collector caps allow monitor crash profile and manager read/write. Exporter caps allow monitor exporter profile plus read access to mgr/osd/mds.

## Dependencies And Integration Points
The file depends on Ceph command execution behind `keyring.SecretStore`, CephCluster status, Rook key rotation policy helpers, owner refs, Kubernetes Secrets, status reporting, and retry-on-conflict. It feeds the volumes mounted by `crash.go`, `exporter.go`, and `pruner.go`.

## Risks And Test Signals
Risks include overbroad caps, stale Kubernetes Secret data after rotation, status update conflicts, and version/policy mismatches. The TODO notes rotation during Ceph version updates should distinguish running and desired versions. `keyring_test.go` covers caps and key rotation/status update for both crash collector and exporter using mocked Ceph command output.
