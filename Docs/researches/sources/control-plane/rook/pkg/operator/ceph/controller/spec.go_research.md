# sources/control-plane/rook/pkg/operator/ceph/controller/spec.go

## Purpose
`spec.go` is the shared pod/container spec construction library for Rook Ceph daemons and sidecars. It defines common volumes, mounts, flags, env vars, labels, probes, security contexts, log collection, external metrics endpoints, and skip-reconcile discovery.

## Important APIs, Types, and Functions
Volume helpers include `PodVolumes`, `CephVolumeMounts`, `RookVolumeMounts`, `DaemonVolumesBase`, `DaemonVolumesDataPVC`, `DaemonVolumesDataHostPath`, `DaemonVolumes`, `DaemonVolumeMounts`, and `AddVolumeMountSubPath`. Flag/env helpers include `DaemonFlags`, `AdminFlags`, `NetworkBindingFlags`, `DaemonEnvVars`, `ApplyNetworkEnv`, and `ContainerEnvVarReference`. Labels are built with `AppLabels` and `CephDaemonAppLabels`. Validation and init helpers include `CheckPodMemory`, `ChownCephDataDirsInitContainer`, and `GenerateMinimalCephConfInitContainer`. Probe helpers generate admin-socket, TCP, and rpcinfo probes. Security helpers include `DefaultContainerSecurityContext`, `CephSecurityContext`, and `PrivilegedContext`. Log/ops sidecars are built by `LogCollectorContainer` and `RgwOpsLogSidecarContainer`. External metrics are handled by `createExternalMetricsEndpoints`, `ConfigureExternalMetricsEndpoint`, and `extractMgrIP`. `GetDaemonsToSkipReconcile()` lists deployments labeled for skip-reconcile.

## Control Flow, State, and Persistence
Most functions build Kubernetes API structs in memory. Persistence happens when callers create/update pods, controllers, endpoint slices, or deployments. `ConfigureExternalMetricsEndpoint()` queries Ceph mgr map, adjusts the first external endpoint to the active mgr IP, builds an EndpointSlice, compares it with the current one, and creates or updates it. Log collector containers run an embedded bash loop to rewrite logrotate config and rotate logs every 15 minutes.

## Dependencies and Integration Points
This file integrates with `opconfig` data path and default flag helpers, keyring volume helpers, stored monitor env vars, Ceph CR specs/resources/placement/labels, Kubernetes core/discovery APIs, Ceph mgr map client calls, `k8sutil` endpoint helpers, and the broader daemon deployment code for mons, mgrs, OSDs, MDS, RGW, NFS, and mirror daemons.

## Risks
Because this file is shared by many daemons, small changes can have broad rollout impact. Volume/mount name mismatches can break pod creation. Several helpers depend on env vars for privileged/root behavior. Embedded shell scripts must remain compatible with image tools and logrotate config format. `ConfigureExternalMetricsEndpoint()` mutates a local copy of monitoring spec and can set an empty endpoint if mgr-map lookup fails but the spec differs. `CheckPodMemory()` warns on below-recommended memory but only errors when limit is below request. External metric EndpointSlice deep equality may be sensitive to server-populated fields.

## Test Signals
`spec_test.go` covers representative volume/mount matching, memory validation, admin socket commands, liveness probes, daemon/network flags, mgr IP extraction, external metrics endpoint create/update, log collector script generation, image pull policy defaulting, network env vars, and skip-reconcile deployment discovery. Many branches remain untested, including PVC/subpath helpers, security env toggles, minimal ceph.conf init, TCP/rpcinfo probes, labels, and RGW ops log sidecar.
