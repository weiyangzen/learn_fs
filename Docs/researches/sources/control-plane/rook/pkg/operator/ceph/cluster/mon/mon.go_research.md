# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/mon.go

## Purpose

This file is the core monitor orchestrator for Rook-managed Ceph clusters. It creates and updates monitor Deployments, Services, PVCs, EndpointSlices, and endpoint ConfigMaps; initializes cluster info and keyrings; schedules monitors safely; waits for quorum; configures stretch clusters; persists mon identity state; and rotates monitor cephx keys.

## Important Types and APIs

`Cluster` holds cluster info, Kubernetes/Ceph context, spec, namespace, image, orchestration lock, port, `maxMonID`, startup wait flag, timeout map, node mapping, owner info, upgrade flag, arbiter mon, deferred failover map, and mon key Secret resource version. `monConfig` is the per-monitor runtime plan: resource name, daemon ID, public IP, port, zone, node, data path map, and whether the mon uses host networking. `SchedulingResult` returns the canary-scheduled node and optional canary artifacts.

`New()` initializes an empty mon cluster with a context-backed `ClusterInfo`, empty scheduling map, `maxMonID = -1`, and empty timeout/failover maps. `Start()` serializes orchestration, validates host-network/allow-multiple constraints and mon memory, initializes cluster info, and calls `startMons()`.

## Control Flow and Persistence

`initClusterInfo()` loads or creates cluster info and max mon ID, applies metadata to the mon secret, saves mon config, stores the shared mon keyring, and stores the admin keyring. `initMonConfig()` converts existing cluster info to `monConfig`s and appends new IDs/zones up to the desired count. `startMons()` schedules mons, sets default Ceph configs before or after starting depending on whether a cluster already exists, creates mons one at a time when growing, force-updates existing mons when needed, applies network settings, configures stretch behavior, reconciles PDBs, and removes orphan PVCs.

`scheduleMonitor()` creates a canary deployment to let Kubernetes choose a node while avoiding mutation of real mon storage. `assignMons()` runs canary scheduling concurrently, records explicit node info for host-network or hostPath mons, records zone assignments when required, and cleans canaries when appropriate. `initMonIPs()` creates services or uses host-network node addresses, exports services for multi-cluster service when enabled, and updates `ClusterInfo.InternalMonitors`.

`startDeployments()` creates or updates each mon deployment, waits for quorum according to startup/upgrade safety rules, and removes extra deployment resources. `startMon()` builds default or floating mon deployment specs, annotates them with the cephx key resource version and last-applied hash, configures storage/scheduling, updates existing deployments, creates new deployments, commits maxMonID after deployment creation, and persists expected mon daemons. `configureDefaultMonStorage()` preserves existing hostPath/PVC choices, expands PVCs on update, flags host-network/path transitions for failover, and applies placement and anti-affinity.

`saveMonConfig()` persists expected mons to the endpoint ConfigMap and EndpointSlices, updates the global config store, writes local connection config, and creates CSI `CephConnection`/default client profile when monitors exist. EndpointSlice persistence splits IPv4 and IPv6 addresses and exposes msgr2 plus optional msgr1 ports. ConfigMap persistence stores flattened endpoints, external mon IDs, maxMonID, scheduling mapping JSON, out-of-quorum mons, and CSI cluster config.

Stretch helpers enable stretch election strategy, create default stretch CRUSH rule, wait for CRUSH failure domains and `.mgr` pool, then configure or update the arbiter/tiebreaker. `RotateMonCephxKeys()` and `UpdateMonCephxStatus()` rotate monitor daemon keys when policy and Ceph version allow it, update the cluster access secret/shared keyring, and persist status with conflict retries.

## Dependencies and Integration Points

The file integrates with Ceph command APIs, Rook controller config and keyring stores, CSI custom resources, Kubernetes apps/core/discovery clients, service export helpers, object matcher annotations, Rook owner references, and health/failover logic in `health.go`. It is the persistence source for monitor endpoint data consumed by daemons, CSI, and sidecars.

## Risks and Test Signals

High-risk areas include maxMonID persistence during interrupted failovers, preserving mon identity across host-network and storage-mode changes, canary cleanup, EndpointSlice address parsing, stretch-cluster readiness gates, and quorum waits during upgrades. Tests in adjacent mon files cover deployment specs, scheduling, health, node assignment, endpoint persistence, and key rotation behavior; this file's functions are also indirectly exercised by `health_test.go`.
