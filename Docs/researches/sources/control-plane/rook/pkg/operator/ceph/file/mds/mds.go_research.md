# sources/control-plane/rook/pkg/operator/ceph/file/mds/mds.go

## Purpose
This file manages the lifecycle of Ceph MDS daemon Deployments for a CephFS filesystem, including keyring generation, deployment creation/update, upgrade sequencing, scale-down/deletion of unwanted daemons, and cleanup of daemon Ceph config/auth objects.

## Important APIs, Types, and Functions
`Cluster` stores cluster info, contexts, cluster spec, filesystem spec, owner info, host data path, and key-rotation flag. `NewCluster` constructs it. `Start` validates memory, detects upgrades with `isCephUpgrade`, runs `upgradeMDS` when needed, starts desired MDS deployments, and scales down extras. `startDeployment` builds per-daemon `mdsConfig`, generates keyrings, sets config flags, creates/updates Deployments, annotates key versions and last-applied hash, and sets owner references. `scaleDownDeployments`, `DeleteMdsCephObjects`, and `finishedWithDaemonUpgrade` handle cleanup and post-upgrade restoration.

## Control Flow, State, and Persistence
`Start` calculates desired replicas from `ActiveCount`, doubled when `ActiveStandby` is true. It honors skip-reconcile labels by returning without touching that daemon. For each desired daemon, it starts a Deployment named `rook-ceph-mds-<fs>-<letter>`. If a Ceph upgrade is detected from daemon versions lower than target `clusterInfo.CephVersion`, it disables standby replay, fails standby-replay daemons, reduces `max_mds` to 1, waits for one active rank, keeps only the active deployment, updates it, waits for standbys to disappear, then defers restoration of active count and standby replay.

Deployment state is persisted in Kubernetes. Ceph auth and config state are persisted in Ceph and keyring Secrets. Extra deployments are deleted or scaled to zero only after Ceph reports the desired number of active ranks, reducing filesystem downtime risk.

## Dependencies and Integration Points
The file integrates with Ceph daemon version discovery, CephFS rank and standby commands, Kubernetes Deployments, Rook deployment update gates, keyring Secret stores, monitor config stores, skip-reconcile labels, and deployment spec creation in `spec.go`. It relies on `mon.UpdateCephDeploymentAndWait` for safe rolling updates.

## Risks
Upgrade sequencing is complex and intentionally conservative; failures can leave `max_mds` or standby replay temporarily changed, with only logged remediation if deferred restoration fails. Daemon letter extraction splits the Ceph daemon name on `-`, so unusual filesystem names increase parsing ambiguity even though the last token should remain the letter. Returning immediately on a skip-reconcile daemon can skip reconciliation of later desired daemons. Extra deployment cleanup is gated by Ceph health/rank waits and may leave stale deployments when waits fail.

## Test Signals
Signals include memory validation, correct desired replica counts, generated deployment names, skip-reconcile handling, update path for existing deployments, upgrade detection from daemon versions, standby-replay disable/restore, active-rank waits, scale-down/delete behavior for extras, Ceph auth/config deletion, and deployment annotation changes on key rotation.
