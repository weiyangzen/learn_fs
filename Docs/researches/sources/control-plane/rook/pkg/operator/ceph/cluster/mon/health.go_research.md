# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/health.go

## Purpose

This file implements the monitor health loop and failover/removal logic. It is responsible for periodically checking Ceph monitor quorum, reconciling external monitors, adding or removing monitors to match the CRD, failing over unhealthy monitors, persisting out-of-quorum state, and cleaning up Kubernetes resources after mon changes.

## Important APIs and Control Flow

`NewHealthChecker()` creates a checker with the default `HealthCheckInterval`. `HealthChecker.Check()` loops until the cluster health context or cluster-info context is canceled. On each interval it refreshes `MonOutTimeout` and check interval from legacy env vars or CRD health settings, then calls `Cluster.checkHealth()`.

`checkHealth()` is serialized by the mon orchestration mutex. It validates cluster info, skips empty non-external clusters, honors skip-reconcile labels, handles external clusters through `handleExternalMonStatus()`, reconciles the mon PDB, reads quorum status, reconciles configured external mon IDs, and then compares Ceph quorum state with `ClusterInfo.InternalMonitors`. It marks mons in/out of quorum via `trackMonInOrOutOfQuorum()`, waits for `MonOutTimeout` before failover unless disabled or the assigned node was deleted, retries once for unscheduled pods after node drains, and handles one unhealthy mon per pass. It also starts new mons when below desired count, removes one extra mon when above desired count, cleans canaries on healthy convergence, evicts duplicate-node mons once per operator restart, checks multi-cluster service export state, and processes deferred `monsToFailover`.

`reconcileExternalMons()` tracks `spec.Mon.ExternalMonIDs` for local clusters by adding in-quorum external mons to `ClusterInfo.ExternalMons`, removing absent ones, saving config on change, and stripping external mons from quorum status before normal internal-mon logic. `removeMonsFromQuorumStatusResponse()` performs that rank-aware filtering.

`failMon()` chooses between removing an extra mon and `failoverMon()`. `failoverMon()` picks a replacement zone, optionally scales down the failed mon, schedules and starts a replacement, configures stretch arbiter if needed, increments max mon ID only after success, and removes the old mon. A defer path reverts replicas, removes the replacement, and rolls back maxMonID if replacement startup fails. `removeMonWithOptionalQuorum()` updates Ceph quorum, `ClusterInfo`, mapping, mon config, bootstrap peer secret, and Kubernetes resources.

## State, Persistence, and Dependencies

State spans `ClusterInfo.InternalMonitors`, `ExternalMons`, `OutOfQuorum`, `monTimeoutList`, `mapping.Schedule`, `monsToFailover`, mon endpoint ConfigMap, connection config on disk, PDBs, Deployments, Services, PVCs, and bootstrap peer Secret. Dependencies include Ceph quorum/mon commands, Rook controller config helpers, Kubernetes pod/node/deployment/PVC APIs, CSI config generation, and operator logging.

## Risks and Test Signals

This is high-risk quorum-preservation code. Risks include failing over too aggressively, losing quorum during drains, stale endpoint persistence, host-network replacement conflicts, external mons skewing desired-count logic, and global timeout variables shared across tests/process state. `health_test.go` provides broad signals for missing mons, extra mons, immediate node-deletion failover, duplicate-node eviction, host-network stop decisions, replica scaling, out-of-quorum persistence, timeout/interval overrides, and external mon behavior. `drain_test.go` complements it for PDB safety.
