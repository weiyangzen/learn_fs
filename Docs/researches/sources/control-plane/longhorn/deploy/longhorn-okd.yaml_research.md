# sources/control-plane/longhorn/deploy/longhorn-okd.yaml

## Purpose

`longhorn-okd.yaml` is a Helm-rendered, single-file Longhorn installation manifest specialized for OKD/OpenShift. It creates the `longhorn-system` namespace, high-priority scheduling class, service accounts, bootstrap config maps, Longhorn CRDs, broad RBAC, services, the Longhorn manager DaemonSet, the CSI driver deployer, the web UI deployment, and an OpenShift `Route` for UI access.

The file is not application code with callable functions, but it defines the Kubernetes and OpenShift API surface Longhorn depends on. Applying it installs both the control plane definitions and the initial controllers that later reconcile Longhorn volumes, replicas, engines, backing images, backups, settings, and node storage inventory.

## Document Layout

The manifest contains 48 YAML documents:

- Namespace and scheduling bootstrap: `Namespace/longhorn-system` and `PriorityClass/longhorn-critical`.
- Service accounts: `longhorn-service-account`, `longhorn-ui-service-account`, and `longhorn-support-bundle`.
- ConfigMaps: empty `longhorn-default-resource`, `longhorn-default-setting`, and `longhorn-storageclass`.
- CRDs in API group `longhorn.io`, all namespaced and served/stored as `v1beta2`.
- RBAC: cluster-wide Longhorn permissions, OpenShift SCC-use permissions, support bundle cluster-admin binding, and namespace-scoped Role/RoleBinding.
- Services: `longhorn-backend`, `longhorn-ui`, `longhorn-frontend`, `longhorn-admission-webhook`, and `longhorn-recovery-backend`.
- Workloads: `DaemonSet/longhorn-manager`, `Deployment/longhorn-driver-deployer`, and `Deployment/longhorn-ui`.
- OpenShift route: `Route/longhorn-ui` with reencrypt TLS termination.

## Important APIs and Resource Types

The install defines 23 Longhorn CRDs:

- Backing image APIs: `BackingImageDataSource`, `BackingImageManager`, `BackingImage`, and `BackupBackingImage` track image import/upload/clone/restore sources, per-disk image placement, manager pods, checksums, sizes, and backup URLs.
- Backup APIs: `Backup`, `BackupTarget`, and `BackupVolume` represent backup jobs, remote backup target configuration, synced backup metadata, availability, progress, and error messages.
- Engine APIs: `EngineFrontend`, `EngineImage`, and `Engine` describe data-engine runtime state, frontend devices (`blockdev`, `iscsi`, `nvmf`, `ublk`, or empty), engine images, replica address maps, backup/restore/rebuild status, snapshots, expansion state, and v2 switchover fields.
- Runtime placement APIs: `InstanceManager`, `Node`, `Replica`, `ShareManager`, and `Orphan` track per-node instance managers, schedulable disks, replica lifecycle, RWX share endpoints, storage health data, and orphaned replica data.
- User and maintenance APIs: `RecurringJob`, `Setting`, `Snapshot`, `SupportBundle`, `SystemBackup`, `SystemRestore`, `VolumeAttachment`, and `Volume` expose recurring snapshot/backup/system-backup jobs, mutable settings, snapshot metadata, diagnostics collection, whole-system backup/restore, attachment tickets, and the main volume state machine.

Most CRDs define `status` subresources, so controllers update observed state separately from user-written spec. Several schemas encode important constraints: required fields such as `EngineImage.spec.image`, `SupportBundle.spec.description`, `SystemRestore.spec.systemBackup`, `Snapshot.spec.volume`, and `VolumeAttachment.spec.volume`; enum fields for data engines (`v1`, `v2`), volume access modes (`rwo`, `rwop`, `rwx`), frontend types, backup modes, compression methods, recurring job tasks, disk drivers, and disk types; and validation rules making fields like `Volume.spec.backingImage` and `Volume.spec.encrypted` immutable.

## Control Flow

Installation starts with namespace and service account creation, then installs default configuration. The `longhorn-default-setting` ConfigMap sets `priority-class: "longhorn-critical"` and disables the revision counter for v1 data engine by default. The `longhorn-storageclass` ConfigMap contains a `StorageClass` definition named `longhorn`, marked as default, using provisioner `driver.longhorn.io`, expansion enabled, `Delete` reclaim policy, `Immediate` binding, three replicas, `ext4`, v1 data engine, and backup target `default`.

The CRDs must be accepted by the API server before Longhorn controllers can create or reconcile custom resources. The main controller process is `DaemonSet/longhorn-manager`, which runs `longhorn-manager -d daemon` on every node under `longhorn-service-account`. It exposes the manager API on port 9500, the admission webhook on 9502, and recovery backend on 9503. Readiness probes hit `/v1/healthz` on port 9502 over HTTPS.

After manager availability, `Deployment/longhorn-driver-deployer` waits until `http://longhorn-backend:9500/v1` returns HTTP 200, then runs `longhorn-manager -d deploy-driver --manager-url http://longhorn-backend:9500/v1`. This deploys the CSI stack using image environment variables for attacher, provisioner, node-driver-registrar, resizer, snapshotter, and liveness probe.

The UI runs as `Deployment/longhorn-ui` with two replicas. An `oauth-proxy` sidecar listens on 8443, authenticates via OpenShift using `longhorn-ui-service-account`, and proxies to the Longhorn UI container on localhost port 8000. The service `longhorn-ui` exposes 443 to the sidecar, and `Route/longhorn-ui` provides external OpenShift access with reencrypt TLS. The older `longhorn-frontend` service still exposes port 80 to the UI container internally.

## State and Persistence Behavior

Kubernetes stores all CR specs and statuses in etcd through the declared CRDs. Longhorn control-plane state is therefore represented by namespaced custom resources in `longhorn-system`, including volume desired state, engine and replica runtime state, backup metadata, settings, recurring jobs, and system backup/restore records.

Persistent Longhorn data lives on each node under host path `/var/lib/longhorn/`, mounted into the manager pod with bidirectional mount propagation. The manager also mounts host `/boot`, `/dev`, `/proc`, and `/etc`, allowing it to inspect host devices and kernel/node configuration. The optional secret `longhorn-grpc-tls` mounts at `/tls-files/`; the OpenShift serving certificate secret `longhorn-ui-tls` is generated via service annotation and mounted into the UI proxy.

The `Node` CRD models Longhorn's storage view of cluster nodes, including disk paths, scheduling flags, reserved storage, disk type/driver, SMART or SPDK health data, and scheduled replica/backing image bytes. `Volume`, `Engine`, `Replica`, and `InstanceManager` resources persist the desired and observed state needed to rebuild, salvage, attach, detach, expand, migrate, and expose volumes.

## Dependencies

The manifest depends on Kubernetes APIs for namespaces, services, config maps, secrets, pods, endpoints, events, PV/PVC, nodes, deployments, daemonsets, statefulsets, jobs, cronjobs, leases, storage classes, CSI objects, priority classes, PDBs, endpoint slices, admission webhooks, API services, and CRDs.

It also depends on OpenShift APIs and behavior:

- `security.openshift.io/securitycontextconstraints` with `use` rights for `anyuid` and `privileged`.
- `route.openshift.io/v1` `Route` for external UI exposure.
- OpenShift service account OAuth redirect annotations.
- Service serving certificate injection through `service.alpha.openshift.io/serving-cert-secret-name`.
- OpenShift OAuth proxy behavior and subject access review arguments.

Container image dependencies are significant. The manifest references `docker.io/longhornio/longhorn-manager:master-head`, `longhorn-engine:master-head`, `longhorn-instance-manager:master-head`, `longhorn-share-manager:master-head`, `backing-image-manager:master-head`, `support-bundle-kit:v0.0.84`, `longhorn-ui:master-head`, and CSI sidecar images tagged with `20260428` builds.

## Integration Points

The StorageClass provisioner `driver.longhorn.io` is the key integration with PVC provisioning. The driver deployer installs CSI components that integrate with Kubernetes storage classes, volume attachments, CSINodes, CSIDrivers, snapshot resources, and volume expansion.

The manager service `longhorn-backend` is the central internal API endpoint. The driver deployer polls it before installing the CSI driver, and the UI points `LONGHORN_MANAGER_IP` at `http://longhorn-backend:9500`. The admission and recovery services expose manager subcomponents through selectors `longhorn.io/admission-webhook: longhorn-admission-webhook` and `longhorn.io/recovery-backend: longhorn-recovery-backend`.

OpenShift UI integration is split across three resources: the `longhorn-ui-service-account` OAuth redirect annotation points to `Route/longhorn-ui`; the `longhorn-ui` service requests a serving cert secret named `longhorn-ui-tls`; and the `oauth-proxy` sidecar uses the service account, TLS secret, and `--openshift-sar={"namespace":"longhorn-system","group":"longhorn.io","resource":"setting","verb":"delete"}` to gate UI access on a Longhorn API authorization check.

## Risks and Edge Cases

The manifest grants broad permissions. `longhorn-role` can mutate CRDs, storage APIs, snapshot APIs, Longhorn CRDs, admission webhooks, PV/PVC/nodes/events, and cluster RBAC objects. `longhorn-support-bundle` is bound to `cluster-admin`. These may be intentional for Longhorn but are high-value escalation surfaces and should be reviewed for the target cluster.

The manager runs privileged and mounts sensitive host paths, including writable `/dev` and `/var/lib/longhorn` with bidirectional mount propagation. OpenShift SCC use for `privileged` and `anyuid` is required. If SCC admission is not granted, core pods will fail; if granted too broadly, compromised Longhorn pods have substantial host access.

Several images use mutable `master-head` tags. This makes installs non-reproducible and can silently change behavior between deploys. The chart label says `v1.12.0-dev`, reinforcing that this is a development-flavored manifest rather than a pinned release install.

The UI `oauth-proxy` container has `image: ""`, which is not deployable unless a downstream process patches it before apply. Its `--cookie-secret=SECRET` is a literal placeholder and should be replaced with a strong secret. Without these fixes, UI pods may fail admission or runtime startup, and cookie security is weak even if an image is supplied.

The default StorageClass marks Longhorn as the cluster default and uses `volumeBindingMode: Immediate`. This can affect unrelated PVCs immediately after installation and may provision Longhorn volumes before a workload is scheduled to a specific topology.

The DaemonSet update strategy permits `maxUnavailable: 100%`, which can roll all manager pods down during update. That may be acceptable for a generated deployment but is risky for availability-sensitive environments.

The manifest includes a `validate-psp-install.yaml` source marker with no actual resource, which is expected on modern clusters without PSP but means PSP validation is not active here.

## Test Signals

Static validation should include `kubectl apply --dry-run=server` or `oc apply --dry-run=server` against an OKD/OpenShift API server, because this file depends on OpenShift Route and SCC APIs and on CRD schema acceptance. `kubectl`-only clusters without `route.openshift.io` will reject the Route.

Post-apply health checks should verify:

- `oc -n longhorn-system get pods` shows `longhorn-manager` DaemonSet pods ready on every eligible node, `longhorn-driver-deployer` complete/running as expected, and two `longhorn-ui` replicas ready.
- `oc -n longhorn-system get crd | grep longhorn.io` lists all 23 Longhorn CRDs, and each CRD has `v1beta2` served and storage.
- `oc -n longhorn-system get svc longhorn-backend longhorn-ui longhorn-admission-webhook longhorn-recovery-backend` exposes ports 9500, 443, 9502, and 9503 respectively.
- `oc -n longhorn-system get route longhorn-ui` reports a host and reencrypt TLS.
- `oc auth can-i use scc/privileged --as system:serviceaccount:longhorn-system:longhorn-service-account` succeeds, and the equivalent `anyuid` check succeeds where required.
- `oc -n longhorn-system logs deploy/longhorn-driver-deployer` shows successful driver deployment after the `longhorn-backend:9500/v1` readiness loop.
- Creating a PVC with `storageClassName: longhorn` provisions a Longhorn `Volume` CR and a Kubernetes PV, and deleting it honors the `Delete` reclaim policy.
- UI-specific validation should confirm the OAuth proxy image has been patched to a real image and the cookie secret is not the literal `SECRET`.
