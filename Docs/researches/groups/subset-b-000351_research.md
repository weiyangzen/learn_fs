# subset-b-000351 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/deploy.sh -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/deploy.sh

## Purpose
This script is the authoritative hostpath CSI deployment workflow for the Kubernetes 1.30 family and the shared util path. It applies sidecar RBAC, optionally applies snapshot-metadata service resources, renders every `hostpath/*.yaml` manifest with image/tag and kubelet path substitutions, waits for the deployed StatefulSet set to become ready, and can emit a Prow `test-driver.yaml` file.

## Important APIs, Types, And Functions
The shell entry points are environment-variable driven. `rbac_version()` extracts image tags from YAML and maps canary tags to RBAC branches. `version_gt()` compares release-style versions. `volume_mode_conversion()` and `snapshot_metadata()` gate optional manifest patches. `update_image()` excludes images such as `socat` from image override substitution. `run()` logs and executes commands. Readiness is handled by `check_statefulset()` and `check_statefulsets()`.

The most important variables are `BASE_DIR`, `TEMP_DIR`, `KUBELET_DATA_DIR`, `UPDATE_RBAC_RULES`, `IMAGE_REGISTRY`, `IMAGE_TAG`, per-image `*_REGISTRY` and `*_TAG`, `VOLUME_MODE_CONVERSION_TESTS`, `SNAPSHOT_METADATA_TESTS`, `CSI_*_RBAC`, `CSI_PROW_TEST_DRIVER`, and `INSTALL_CRD`. RBAC URLs are derived from sidecar versions for provisioner, attacher, snapshotter, resizer, health monitor, and optional snapshot metadata.

## Control Flow
The script creates a temporary directory and removes it on exit. It derives RBAC URLs from manifest image tags, fetches or copies each RBAC file, creates a small kustomization that applies standard `app.kubernetes.io` labels, and runs `kubectl apply --kustomize`. When snapshot metadata is enabled, it also fetches TLS secret, service CR, and service manifests from external-snapshot-metadata and labels/applies them.

For every sorted YAML file under `hostpath/`, the script copies it into the temp directory, applies optional `sed` patches for volume mode conversion and snapshot metadata, replaces `/var/lib/kubelet/` with `KUBELET_DATA_DIR`, rewrites configurable image registry/tag components, prints the resolved image lines, and pipes the rendered manifest to `kubectl apply -f -`. After applying, it discovers all labeled StatefulSets and polls readiness for up to roughly five minutes. On failure it describes labeled resources and prints pod logs. If `CSI_PROW_TEST_DRIVER` is set, it copies the local test driver config and appends `ClientNodeName` from `csi-hostpathplugin-0` for same-node late-binding tests.

## State, Persistence, And Dependencies
The script persists Kubernetes resources through `kubectl apply` and hostpath PV data through the manifest's hostPath directories. Temporary RBAC/kustomization files live only under `TEMP_DIR`. It depends on `bash`, `sed`, `grep`, `sort -V`, `curl`, `wget`, `diff`, `kubectl`, the Kubernetes kustomize integration, and network access to GitHub raw content unless RBAC URLs are overridden to local files.

## Integration Points
It integrates with the deployment-specific `hostpath` manifest directory, external CSI sidecar RBAC repositories, external-snapshot-metadata test resources, Prow storage e2e via `CSI_PROW_TEST_DRIVER`, and the hostpath driver socket under the kubelet plugin directory. The labels it injects are also the contract used by the destroy script and readiness diagnostics.

## Risks
The script applies live cluster-wide RBAC and privileged hostPath workloads. Version extraction is based on simple `sed`/`grep` parsing of image lines, so unusual manifest formatting can produce wrong RBAC branches. Image overrides can decouple sidecar images from checked-in RBAC unless `UPDATE_RBAC_RULES` remains true. The `sed` patches depend on marker comments in the plugin manifest. `KUBELET_DATA_DIR` replacement assumes all nodes use one kubelet data directory. Readiness waits for any labeled StatefulSet names; missing or mislabeled manifests can make diagnostics misleading.

## Test Signals
Useful checks include running with default manifests, overridden image tags, overridden RBAC URLs, `IMAGE_TAG=canary` with blacklist behavior, `VOLUME_MODE_CONVERSION_TESTS=true`, `SNAPSHOT_METADATA_TESTS=true`, and non-default `KUBELET_DATA_DIR`. Cluster-level validation should confirm labeled RBAC exists, sidecars use the expected images, all StatefulSets become ready, Prow driver output includes `ClientNodeName`, and destroy removes every labeled resource.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/deploy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/destroy.sh -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/destroy.sh

## Purpose
This script removes a hostpath CSI deployment by deleting all Kubernetes resources that carry the deployment's standard labels. It is intended to stay synchronized with the deploy scripts and provides a simple cleanup path for test clusters.

## Important APIs, Types, And Functions
There are no shell functions. The script uses two `kubectl delete` commands under `set -e` and `set -o pipefail`. Both select resources with `app.kubernetes.io/instance=hostpath.csi.k8s.io` and `app.kubernetes.io/part-of=csi-driver-host-path`.

## Control Flow
The first delete targets the Kubernetes `all` category across all namespaces and waits for deletion. The second delete explicitly removes `role`, `clusterrole`, `rolebinding`, `clusterrolebinding`, `serviceaccount`, `storageclass`, and `csidriver` resources across all namespaces with the same labels.

## State, Persistence, And Dependencies
The script mutates only Kubernetes API state. It does not remove host data directories like `/var/lib/csi-hostpath-data` or kubelet plugin directories from nodes. It depends on `bash` and a configured `kubectl` with permissions to delete namespaced and cluster-scoped resources.

## Integration Points
Its deletion contract relies on labels applied by `deploy-hostpath.sh` and the deployment manifests. It complements the hostpath deploy scripts for CI and local test cleanup.

## Risks
Resources missing the standard labels will survive. Persistent hostPath data on nodes is not cleaned. The command is broad across all namespaces for matching labels, so unrelated resources with the same labels would be deleted. If CRDs or snapshot metadata custom resources are introduced without labels or without explicit resource kinds here, cleanup can be incomplete.

## Test Signals
A good validation deploys the driver, runs this script, then checks that labeled `all`, RBAC, service account, storage class, and CSIDriver resources are gone. It should also verify repeated runs against an already-clean cluster fail or pass as expected for the chosen `kubectl delete` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/destroy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-attacher.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-attacher.yaml

## Purpose
This manifest deploys the external CSI attacher as a single-replica StatefulSet for the split Kubernetes 1.30 test deployment. It connects the attacher sidecar to the hostpath driver's Unix socket so Kubernetes `VolumeAttachment` operations can call controller publish/unpublish.

## Important APIs, Types, And Functions
The resource is an `apps/v1` `StatefulSet` named `csi-hostpath-attacher`. It uses service account `csi-attacher`, container `registry.k8s.io/sig-storage/csi-attacher:v4.8.0`, arguments `--v=5` and `--csi-address=/csi/csi.sock`, and a privileged security context. The only volume is hostPath `/var/lib/kubelet/plugins/csi-hostpath` mounted at `/csi`.

## Control Flow
Kubernetes schedules one pod with required pod affinity to the `hostpath.csi.k8s.io` deployment instance on the same hostname. The sidecar starts, opens `/csi/csi.sock`, and watches/handles attach workflows through the RBAC applied by the deploy script.

## State, Persistence, And Dependencies
No application state is stored by this manifest. It depends on the driver StatefulSet creating the socket directory and on compatible external-attacher RBAC. The hostPath volume may be created automatically with `DirectoryOrCreate`.

## Integration Points
It is consumed by `deploy.sh`, which can rewrite image registry/tag and kubelet base path before applying. The labels tie it to readiness checks and destroy cleanup.

## Risks
The manifest is privileged solely to allow socket access under SELinux; that is acceptable for test deployments but too broad for production. If pod affinity cannot place it with the driver, the sidecar cannot reach the socket. Version/RBAC skew can break leader election or attachment operations.

## Test Signals
Verify the StatefulSet becomes ready, the container logs show successful CSI connection, `VolumeAttachment` operations complete when attach is enabled, and the hostPath socket path is shared with the plugin pod.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-attacher.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-driverinfo.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-driverinfo.yaml

## Purpose
This `CSIDriver` object declares the hostpath CSI driver's cluster-facing capabilities for the single-node Kubernetes 1.30 deployments. It tells Kubernetes that the driver supports persistent volumes and inline ephemeral volumes and that pod information is required on mount.

## Important APIs, Types, And Functions
The resource is `storage.k8s.io/v1`, kind `CSIDriver`, named `hostpath.csi.k8s.io`. The key spec fields are `volumeLifecycleModes: [Persistent, Ephemeral]`, `podInfoOnMount: true`, and `fsGroupPolicy: File`.

## Control Flow
The deploy script applies this resource with common labels. Kubernetes consults it during volume admission and kubelet CSI calls. `podInfoOnMount` enables kubelet to pass the `csi.storage.k8s.io/ephemeral` context entry that the node server uses to identify inline ephemeral volumes.

## State, Persistence, And Dependencies
The resource persists in the Kubernetes API. It has no local storage state and depends on the cluster supporting `storage.k8s.io/v1` CSIDriver objects.

## Integration Points
It integrates with the node server's ephemeral handling, fsGroup behavior in kubelet, and the destroy script's label-based cleanup. The driver name must match the plugin `--drivername`, StorageClass provisioner, and snapshot classes.

## Risks
A mismatch in driver name breaks all Kubernetes-to-CSI routing. Enabling ephemeral lifecycle requires the node server to handle ephemeral create/delete correctly. `fsGroupPolicy: File` allows kubelet ownership changes and can alter test volume contents or permissions.

## Test Signals
Check that `kubectl get csidriver hostpath.csi.k8s.io` shows both lifecycle modes, inline volume examples reach `NodePublishVolume` with ephemeral context, and fsGroup-related storage e2e tests behave as expected.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-plugin.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-plugin.yaml

## Purpose
This manifest deploys the core hostpath CSI plugin for the split Kubernetes 1.30 test setup. It runs the driver, liveness probe, external health monitor controller, and node-driver-registrar in a single one-replica StatefulSet pinned to one node.

## Important APIs, Types, And Functions
The resource is a `StatefulSet` named `csi-hostpathplugin`. The `hostpath` container runs `hostpathplugin:v1.15.0` with `--drivername=hostpath.csi.k8s.io`, `--endpoint=$(CSI_ENDPOINT)`, and `--nodeid=$(KUBE_NODE_NAME)`. Sidecars include `livenessprobe:v2.15.0`, `csi-external-health-monitor-controller:v0.14.0`, and `csi-node-driver-registrar:v2.13.0`. It exposes health port `9898` and registrar socket registration path `/var/lib/kubelet/plugins/csi-hostpath/csi.sock`.

## Control Flow
Kubernetes starts one privileged driver pod. The driver creates `/csi/csi.sock`; the registrar registers that socket with kubelet; liveness probes call CSI health through the socket; health-monitor-controller talks to the controller service. Other split sidecars use pod affinity and the shared hostPath socket directory.

## State, Persistence, And Dependencies
Driver data persists under hostPath `/var/lib/csi-hostpath-data/` mounted at `/csi-data-dir`. The driver also mounts kubelet pods and plugin directories with bidirectional propagation plus `/dev` for block volume loop devices. It depends on privileged pod admission, kubelet plugin registry presence, and the node name downward API.

## Integration Points
The manifest is rendered by the deploy script for image/path overrides and optional snapshot metadata insertion. It is the socket endpoint for attacher, provisioner, resizer, snapshotter, health monitor, socat testing, and kubelet registration.

## Risks
This is a privileged test driver with broad hostPath access. Single-replica topology means volumes only work on one node; the deploy script appends a Prow client node to avoid late-binding placement errors. Version skew with split sidecars can surface as CSI RPC or RBAC failures. Host data under `/var/lib/csi-hostpath-data` survives pod recreation and destroy.

## Test Signals
Readiness should show the StatefulSet ready and HTTP liveness passing. Kubelet should list the driver from the registrar, dynamic provisioning should create data directories, node publish should bind mount under kubelet pod paths, and block tests should create loop devices via `/dev` access.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-plugin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-provisioner.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-provisioner.yaml

## Purpose
This manifest runs the external CSI provisioner as a separate one-replica StatefulSet in the Kubernetes 1.30 test deployment. It handles PVC-driven `CreateVolume` and `DeleteVolume` workflows against the hostpath driver socket.

## Important APIs, Types, And Functions
The resource is `apps/v1` `StatefulSet` `csi-hostpath-provisioner`, service account `csi-provisioner`, image `registry.k8s.io/sig-storage/csi-provisioner:v5.2.0`, arguments `-v=5`, `--csi-address=/csi/csi.sock`, and `--feature-gates=Topology=true`. It mounts `/var/lib/kubelet/plugins/csi-hostpath` at `/csi` and runs privileged for SELinux socket access.

## Control Flow
Pod affinity colocates the provisioner with the hostpath plugin. Once running, it watches PVC/PV objects and calls the driver's controller service over `/csi/csi.sock`, using topology support so created volumes advertise the hostpath node topology when enabled.

## State, Persistence, And Dependencies
The provisioner stores state in Kubernetes PV/PVC objects and uses the driver state store indirectly through CSI calls. It depends on provisioner RBAC fetched by the deploy script and on the driver socket hostPath.

## Integration Points
It integrates with StorageClasses using provisioner `hostpath.csi.k8s.io`, test-driver topology capabilities, and optional deploy-script insertion of `--prevent-volume-mode-conversion=true` for volume mode conversion tests.

## Risks
If the provisioner lands on a different node than the plugin, the socket path will not be usable. Topology feature-gate mismatches can affect binding. RBAC/image version skew is a common failure mode when tags are overridden.

## Test Signals
PVC creation should produce PVs, `CreateVolume` calls should appear in driver logs, topology-aware tests should bind to the driver node, and volume mode conversion tests should show the optional flag when enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-provisioner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-resizer.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-resizer.yaml

## Purpose
This manifest runs the external CSI resizer as a separate StatefulSet for controller expansion testing. It watches PVC resize requests and calls the driver's `ControllerExpandVolume` RPC through the shared CSI socket.

## Important APIs, Types, And Functions
The resource is `StatefulSet` `csi-hostpath-resizer`, service account `csi-resizer`, image `registry.k8s.io/sig-storage/csi-resizer:v1.13.1`, arguments `-v=5` and `-csi-address=/csi/csi.sock`, and a privileged container with `/csi` mounted from `/var/lib/kubelet/plugins/csi-hostpath`.

## Control Flow
The pod is colocated with the hostpath plugin via required pod affinity. The resizer observes PVC capacity changes, sends CSI expansion calls, and lets kubelet perform node-side expansion when required by the driver response.

## State, Persistence, And Dependencies
Resize state is reflected in Kubernetes PVC/PV status and in the driver state JSON where volume size is updated. The manifest depends on external-resizer RBAC and socket availability.

## Integration Points
It is used with StorageClasses that set `allowVolumeExpansion: true` and with the driver's controller/node expansion capability flags. Deploy image substitution can alter the sidecar version.

## Risks
The container is privileged for socket access. If controller or node expansion flags are disabled in the driver, the sidecar observes unsupported RPCs. Driver expansion updates metadata but does not grow a real filesystem, because this is an e2e test driver.

## Test Signals
Expansion e2e should show the PVC size increasing, `ControllerExpandVolume` and `NodeExpandVolume` calls in driver logs, and failure for requests above configured maximum sizes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-resizer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-snapshotclass.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-snapshotclass.yaml

## Purpose
This manifest defines the default hostpath `VolumeSnapshotClass` used by snapshot examples and storage e2e tests. It binds snapshot requests to the hostpath CSI driver and deletes underlying snapshots when snapshot objects are deleted.

## Important APIs, Types, And Functions
The resource is `snapshot.storage.k8s.io/v1`, kind `VolumeSnapshotClass`, named `csi-hostpath-snapclass`. It sets `driver: hostpath.csi.k8s.io` and `deletionPolicy: Delete` with the standard deployment labels.

## Control Flow
When a `VolumeSnapshot` references this class, external-snapshotter routes the request to the hostpath driver's `CreateSnapshot`/`DeleteSnapshot` controller RPCs. DeletionPolicy `Delete` asks the snapshot controller to remove the backend snapshot via CSI.

## State, Persistence, And Dependencies
The class persists in Kubernetes. Actual snapshot archive files persist under the driver state directory until deleted. It depends on snapshot CRDs and compatible external-snapshotter deployment.

## Integration Points
It is referenced by `examples/csi-snapshot-v1.yaml`, block snapshot examples, and `test-driver.yaml` snapshot capability configuration. The driver name must match plugin and CSIDriver resources.

## Risks
The comment notes v1 snapshot API dependency on external-snapshotter v4.x or newer. A class/driver mismatch leaves snapshot requests unhandled. Delete policy can remove snapshot data during cleanup.

## Test Signals
Creating a VolumeSnapshot with this class should produce a ready snapshot, driver logs should show snapshot archive creation, and deletion should remove the corresponding `.snap` file and state entry.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-snapshotter.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-snapshotter.yaml

## Purpose
This manifest deploys the external CSI snapshotter sidecar as a separate StatefulSet for the split Kubernetes 1.30 test deployment. It turns Kubernetes VolumeSnapshot controller events into CSI snapshot RPCs.

## Important APIs, Types, And Functions
The resource is `StatefulSet` `csi-hostpath-snapshotter`, service account `csi-snapshotter`, image `registry.k8s.io/sig-storage/csi-snapshotter:v8.2.0`, arguments `-v=5` and `--csi-address=/csi/csi.sock`, and a privileged mount of the hostpath driver socket directory.

## Control Flow
Pod affinity colocates it with the plugin. After startup it connects to `/csi/csi.sock` and calls snapshot RPCs for VolumeSnapshotContent lifecycle events.

## State, Persistence, And Dependencies
Snapshot state is coordinated through Kubernetes snapshot CRDs and the driver's JSON state plus `.snap` files. The manifest depends on external-snapshotter RBAC, installed CRDs, and socket availability.

## Integration Points
It works with `csi-hostpath-snapshotclass.yaml`, snapshot examples, restore examples, and controller server snapshot methods. Deploy script version parsing uses this file to derive snapshotter RBAC path.

## Risks
Snapshot CRD/RBAC version skew is a frequent failure mode. The sidecar is privileged for socket access. Because hostpath snapshots are `tar` or file copies, large volumes can make snapshot RPCs slow and block the driver's serialized state mutex.

## Test Signals
Snapshot creation and deletion should progress to ready/deleted states, restore PVCs should be populated, and logs should show calls to `CreateSnapshot`, `ListSnapshots`, and `DeleteSnapshot`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-snapshotter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-testing.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-testing.yaml

## Purpose
This manifest exposes the hostpath driver's Unix CSI socket as a TCP `NodePort` service for manual and automated testing with tools such as `csi-sanity` or `csc`. It is explicitly marked as test-only, not production deployment material.

## Important APIs, Types, And Functions
It defines a `Service` named `hostpath-service` with port `10000` and a `StatefulSet` named `csi-hostpath-socat`. The pod runs the `socat` command from image `registry.k8s.io/sig-storage/hostpathplugin:v1.15.0` with arguments `tcp-listen:10000,fork,reuseaddr` and `unix-connect:/csi/csi.sock`.

## Control Flow
The socat pod is colocated with the hostpath plugin through required pod affinity, mounts the driver socket hostPath at `/csi`, and forwards each TCP connection to the Unix socket. The distributed variant also mounts `/var/lib/kubelet/pods` because daemonset driver pod names are non-deterministic for sanity testing.

## State, Persistence, And Dependencies
No durable application state is created. The service allocates a NodePort and the pod relies on the driver socket directory. The socat image is intentionally excluded from deploy-script image overrides.

## Integration Points
External CSI test clients can connect to the NodePort and exercise the same CSI endpoint used by sidecars. Labels connect it to deploy readiness and destroy cleanup.

## Risks
Exposing the CSI socket over a NodePort can allow remote callers to create, delete, mount, or snapshot volumes, so this must remain test-only. Pod affinity or daemonset scheduling issues can point socat at a missing socket.

## Test Signals
Verify the service has a NodePort, TCP connections reach CSI RPCs, `csi-sanity` can run through the port, and deleting the manifest removes both service and forwarding pod.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-testing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/test-driver.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/test-driver.yaml

## Purpose
This file describes the hostpath deployment to Kubernetes external storage e2e tests. It advertises which storage features the deployed driver supports so the test suite can select relevant test patterns.

## Important APIs, Types, And Functions
The YAML declares `StorageClass.FromName`, `SnapshotClass.FromName`, `DriverInfo.Name: hostpath.csi.k8s.io`, minimum size `1Mi`, and capabilities for block, controller expansion, exec, multipods, node expansion, persistence, single-node volumes, snapshot data sources, topology, and `FSResizeFromSourceNotSupported`. It also enables shared inline volumes.

## Control Flow
The deploy script may copy this file to `CSI_PROW_TEST_DRIVER` and append `ClientNodeName` based on the running plugin pod. The e2e framework reads it to create storage classes/snapshot classes by name and skip unsupported cases.

## State, Persistence, And Dependencies
The file itself is static test configuration. Its correctness depends on the deployed manifests actually enabling the advertised sidecars and driver flags.

## Integration Points
It integrates with Kubernetes Prow storage e2e, the deploy script, hostpath StorageClass/SnapshotClass resources, and the driver's controller and node capability responses.

## Risks
Over-advertising capabilities causes false test failures. Under-advertising skips coverage. The file still references Kubernetes 1.17 external storage test docs although it is used for newer deployment variants. Same-node constraints require deploy-time `ClientNodeName` injection.

## Test Signals
Run the external storage e2e suite with the copied file and verify selected tests match the manifest set, especially block, expansion, snapshot, topology, and inline volume cases.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/test-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/deploy.sh -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/deploy.sh

## Purpose
This script is the authoritative hostpath CSI deployment workflow for the Kubernetes 1.30 family and the shared util path. It applies sidecar RBAC, optionally applies snapshot-metadata service resources, renders every `hostpath/*.yaml` manifest with image/tag and kubelet path substitutions, waits for the deployed StatefulSet set to become ready, and can emit a Prow `test-driver.yaml` file.

## Important APIs, Types, And Functions
The shell entry points are environment-variable driven. `rbac_version()` extracts image tags from YAML and maps canary tags to RBAC branches. `version_gt()` compares release-style versions. `volume_mode_conversion()` and `snapshot_metadata()` gate optional manifest patches. `update_image()` excludes images such as `socat` from image override substitution. `run()` logs and executes commands. Readiness is handled by `check_statefulset()` and `check_statefulsets()`.

The most important variables are `BASE_DIR`, `TEMP_DIR`, `KUBELET_DATA_DIR`, `UPDATE_RBAC_RULES`, `IMAGE_REGISTRY`, `IMAGE_TAG`, per-image `*_REGISTRY` and `*_TAG`, `VOLUME_MODE_CONVERSION_TESTS`, `SNAPSHOT_METADATA_TESTS`, `CSI_*_RBAC`, `CSI_PROW_TEST_DRIVER`, and `INSTALL_CRD`. RBAC URLs are derived from sidecar versions for provisioner, attacher, snapshotter, resizer, health monitor, and optional snapshot metadata.

## Control Flow
The script creates a temporary directory and removes it on exit. It derives RBAC URLs from manifest image tags, fetches or copies each RBAC file, creates a small kustomization that applies standard `app.kubernetes.io` labels, and runs `kubectl apply --kustomize`. When snapshot metadata is enabled, it also fetches TLS secret, service CR, and service manifests from external-snapshot-metadata and labels/applies them.

For every sorted YAML file under `hostpath/`, the script copies it into the temp directory, applies optional `sed` patches for volume mode conversion and snapshot metadata, replaces `/var/lib/kubelet/` with `KUBELET_DATA_DIR`, rewrites configurable image registry/tag components, prints the resolved image lines, and pipes the rendered manifest to `kubectl apply -f -`. After applying, it discovers all labeled StatefulSets and polls readiness for up to roughly five minutes. On failure it describes labeled resources and prints pod logs. If `CSI_PROW_TEST_DRIVER` is set, it copies the local test driver config and appends `ClientNodeName` from `csi-hostpathplugin-0` for same-node late-binding tests.

## State, Persistence, And Dependencies
The script persists Kubernetes resources through `kubectl apply` and hostpath PV data through the manifest's hostPath directories. Temporary RBAC/kustomization files live only under `TEMP_DIR`. It depends on `bash`, `sed`, `grep`, `sort -V`, `curl`, `wget`, `diff`, `kubectl`, the Kubernetes kustomize integration, and network access to GitHub raw content unless RBAC URLs are overridden to local files.

## Integration Points
It integrates with the deployment-specific `hostpath` manifest directory, external CSI sidecar RBAC repositories, external-snapshot-metadata test resources, Prow storage e2e via `CSI_PROW_TEST_DRIVER`, and the hostpath driver socket under the kubelet plugin directory. The labels it injects are also the contract used by the destroy script and readiness diagnostics.

## Risks
The script applies live cluster-wide RBAC and privileged hostPath workloads. Version extraction is based on simple `sed`/`grep` parsing of image lines, so unusual manifest formatting can produce wrong RBAC branches. Image overrides can decouple sidecar images from checked-in RBAC unless `UPDATE_RBAC_RULES` remains true. The `sed` patches depend on marker comments in the plugin manifest. `KUBELET_DATA_DIR` replacement assumes all nodes use one kubelet data directory. Readiness waits for any labeled StatefulSet names; missing or mislabeled manifests can make diagnostics misleading.

## Test Signals
Useful checks include running with default manifests, overridden image tags, overridden RBAC URLs, `IMAGE_TAG=canary` with blacklist behavior, `VOLUME_MODE_CONVERSION_TESTS=true`, `SNAPSHOT_METADATA_TESTS=true`, and non-default `KUBELET_DATA_DIR`. Cluster-level validation should confirm labeled RBAC exists, sidecars use the expected images, all StatefulSets become ready, Prow driver output includes `ClientNodeName`, and destroy removes every labeled resource.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/deploy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/destroy.sh -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/destroy.sh

## Purpose
This script removes a hostpath CSI deployment by deleting all Kubernetes resources that carry the deployment's standard labels. It is intended to stay synchronized with the deploy scripts and provides a simple cleanup path for test clusters.

## Important APIs, Types, And Functions
There are no shell functions. The script uses two `kubectl delete` commands under `set -e` and `set -o pipefail`. Both select resources with `app.kubernetes.io/instance=hostpath.csi.k8s.io` and `app.kubernetes.io/part-of=csi-driver-host-path`.

## Control Flow
The first delete targets the Kubernetes `all` category across all namespaces and waits for deletion. The second delete explicitly removes `role`, `clusterrole`, `rolebinding`, `clusterrolebinding`, `serviceaccount`, `storageclass`, and `csidriver` resources across all namespaces with the same labels.

## State, Persistence, And Dependencies
The script mutates only Kubernetes API state. It does not remove host data directories like `/var/lib/csi-hostpath-data` or kubelet plugin directories from nodes. It depends on `bash` and a configured `kubectl` with permissions to delete namespaced and cluster-scoped resources.

## Integration Points
Its deletion contract relies on labels applied by `deploy-hostpath.sh` and the deployment manifests. It complements the hostpath deploy scripts for CI and local test cleanup.

## Risks
Resources missing the standard labels will survive. Persistent hostPath data on nodes is not cleaned. The command is broad across all namespaces for matching labels, so unrelated resources with the same labels would be deleted. If CRDs or snapshot metadata custom resources are introduced without labels or without explicit resource kinds here, cleanup can be incomplete.

## Test Signals
A good validation deploys the driver, runs this script, then checks that labeled `all`, RBAC, service account, storage class, and CSIDriver resources are gone. It should also verify repeated runs against an already-clean cluster fail or pass as expected for the chosen `kubectl delete` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/destroy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-driverinfo.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-driverinfo.yaml

## Purpose
This `CSIDriver` object declares the hostpath CSI driver's cluster-facing capabilities for the single-node Kubernetes 1.30 deployments. It tells Kubernetes that the driver supports persistent volumes and inline ephemeral volumes and that pod information is required on mount.

## Important APIs, Types, And Functions
The resource is `storage.k8s.io/v1`, kind `CSIDriver`, named `hostpath.csi.k8s.io`. The key spec fields are `volumeLifecycleModes: [Persistent, Ephemeral]`, `podInfoOnMount: true`, and `fsGroupPolicy: File`.

## Control Flow
The deploy script applies this resource with common labels. Kubernetes consults it during volume admission and kubelet CSI calls. `podInfoOnMount` enables kubelet to pass the `csi.storage.k8s.io/ephemeral` context entry that the node server uses to identify inline ephemeral volumes.

## State, Persistence, And Dependencies
The resource persists in the Kubernetes API. It has no local storage state and depends on the cluster supporting `storage.k8s.io/v1` CSIDriver objects.

## Integration Points
It integrates with the node server's ephemeral handling, fsGroup behavior in kubelet, and the destroy script's label-based cleanup. The driver name must match the plugin `--drivername`, StorageClass provisioner, and snapshot classes.

## Risks
A mismatch in driver name breaks all Kubernetes-to-CSI routing. Enabling ephemeral lifecycle requires the node server to handle ephemeral create/delete correctly. `fsGroupPolicy: File` allows kubelet ownership changes and can alter test volume contents or permissions.

## Test Signals
Check that `kubectl get csidriver hostpath.csi.k8s.io` shows both lifecycle modes, inline volume examples reach `NodePublishVolume` with ephemeral context, and fsGroup-related storage e2e tests behave as expected.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-plugin.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-plugin.yaml

## Purpose
This manifest deploys the all-in-one Kubernetes 1.30 hostpath CSI plugin. Unlike the split test deployment, it bundles controller sidecars, registrar, liveness probe, RBAC bindings, and the driver into one StatefulSet and service account.

## Important APIs, Types, And Functions
It creates `ServiceAccount` `csi-hostpathplugin-sa`, ClusterRoleBindings/RoleBindings to external sidecar roles, and a one-replica `StatefulSet` `csi-hostpathplugin`. Containers include `hostpathplugin:v1.17.0`, health monitor controller `v0.16.0`, node-driver-registrar `v2.15.0`, livenessprobe `v2.17.0`, attacher `v4.10.0`, provisioner `v6.0.0`, resizer `v2.0.0`, and snapshotter `v8.4.0`.

## Control Flow
The deploy script first applies upstream RBAC, then this manifest binds those roles to the plugin service account. The StatefulSet starts one pod on a single node; the driver creates `/csi/csi.sock`; every sidecar in the pod connects locally to that socket; the registrar exposes its own HTTP health endpoint; liveness probe monitors the driver health port.

## State, Persistence, And Dependencies
Persistent test data lives in `/var/lib/csi-hostpath-data/`. Kubelet socket, plugin registry, pod mount paths, plugin directories, and `/dev` are mounted from the host. Marker comments allow deploy-time insertion of snapshot metadata sidecar, volumes, and hostpath args. The manifest depends on privileged pods and compatible RBAC resources named by external sidecar deployments.

## Integration Points
This is the primary Kubernetes 1.30 deployment target for storage e2e tests. It integrates with snapshot class, CSIDriver, testing socat, deploy-script image substitution, optional snapshot metadata, optional volume mode conversion, and Prow test driver generation.

## Risks
The pod has broad privileged host access and should remain a test driver. All sidecars share one pod lifecycle, so a single crash can affect the whole stack. Role binding names must match upstream RBAC resource names. The leading indentation before the opening comment is harmless YAML-wise only because comments are ignored, but it is visually odd. Data survives pod and resource deletion unless node directories are cleaned.

## Test Signals
`kubectl describe statefulset csi-hostpathplugin` should show one ready replica. Sidecar logs should show successful leader election/CSI socket connection. Kubelet plugin registration, PVC provisioning, attachment, resizing, snapshots, and health monitor tests should all use this single pod.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-plugin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-snapshotclass.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-snapshotclass.yaml

## Purpose
This manifest defines the default hostpath `VolumeSnapshotClass` used by snapshot examples and storage e2e tests. It binds snapshot requests to the hostpath CSI driver and deletes underlying snapshots when snapshot objects are deleted.

## Important APIs, Types, And Functions
The resource is `snapshot.storage.k8s.io/v1`, kind `VolumeSnapshotClass`, named `csi-hostpath-snapclass`. It sets `driver: hostpath.csi.k8s.io` and `deletionPolicy: Delete` with the standard deployment labels.

## Control Flow
When a `VolumeSnapshot` references this class, external-snapshotter routes the request to the hostpath driver's `CreateSnapshot`/`DeleteSnapshot` controller RPCs. DeletionPolicy `Delete` asks the snapshot controller to remove the backend snapshot via CSI.

## State, Persistence, And Dependencies
The class persists in Kubernetes. Actual snapshot archive files persist under the driver state directory until deleted. It depends on snapshot CRDs and compatible external-snapshotter deployment.

## Integration Points
It is referenced by `examples/csi-snapshot-v1.yaml`, block snapshot examples, and `test-driver.yaml` snapshot capability configuration. The driver name must match plugin and CSIDriver resources.

## Risks
The comment notes v1 snapshot API dependency on external-snapshotter v4.x or newer. A class/driver mismatch leaves snapshot requests unhandled. Delete policy can remove snapshot data during cleanup.

## Test Signals
Creating a VolumeSnapshot with this class should produce a ready snapshot, driver logs should show snapshot archive creation, and deletion should remove the corresponding `.snap` file and state entry.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-testing.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-testing.yaml

## Purpose
This manifest exposes the hostpath driver's Unix CSI socket as a TCP `NodePort` service for manual and automated testing with tools such as `csi-sanity` or `csc`. It is explicitly marked as test-only, not production deployment material.

## Important APIs, Types, And Functions
It defines a `Service` named `hostpath-service` with port `10000` and a `StatefulSet` named `csi-hostpath-socat`. The pod runs the `socat` command from image `registry.k8s.io/sig-storage/hostpathplugin:v1.15.0` with arguments `tcp-listen:10000,fork,reuseaddr` and `unix-connect:/csi/csi.sock`.

## Control Flow
The socat pod is colocated with the hostpath plugin through required pod affinity, mounts the driver socket hostPath at `/csi`, and forwards each TCP connection to the Unix socket. The distributed variant also mounts `/var/lib/kubelet/pods` because daemonset driver pod names are non-deterministic for sanity testing.

## State, Persistence, And Dependencies
No durable application state is created. The service allocates a NodePort and the pod relies on the driver socket directory. The socat image is intentionally excluded from deploy-script image overrides.

## Integration Points
External CSI test clients can connect to the NodePort and exercise the same CSI endpoint used by sidecars. Labels connect it to deploy readiness and destroy cleanup.

## Risks
Exposing the CSI socket over a NodePort can allow remote callers to create, delete, mount, or snapshot volumes, so this must remain test-only. Pod affinity or daemonset scheduling issues can point socat at a missing socket.

## Test Signals
Verify the service has a NodePort, TCP connections reach CSI RPCs, `csi-sanity` can run through the port, and deleting the manifest removes both service and forwarding pod.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-testing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/test-driver.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/test-driver.yaml

## Purpose
This file describes the hostpath deployment to Kubernetes external storage e2e tests. It advertises which storage features the deployed driver supports so the test suite can select relevant test patterns.

## Important APIs, Types, And Functions
The YAML declares `StorageClass.FromName`, `SnapshotClass.FromName`, `VolumeAttributeClass.FromName`, `DriverInfo.Name: hostpath.csi.k8s.io`, minimum size `1Mi`, and capabilities for block, controller expansion, exec, multipods, node expansion, persistence, single-node volumes, snapshot data sources, topology, and `FSResizeFromSourceNotSupported`. It also enables shared inline volumes.

## Control Flow
The deploy script may copy this file to `CSI_PROW_TEST_DRIVER` and append `ClientNodeName` based on the running plugin pod. The e2e framework reads it to create storage classes/snapshot classes by name and skip unsupported cases.

## State, Persistence, And Dependencies
The file itself is static test configuration. Its correctness depends on the deployed manifests actually enabling the advertised sidecars and driver flags.

## Integration Points
It integrates with Kubernetes Prow storage e2e, the deploy script, hostpath StorageClass/SnapshotClass resources, and the driver's controller and node capability responses.

## Risks
Over-advertising capabilities causes false test failures. Under-advertising skips coverage. The file still references Kubernetes 1.17 external storage test docs although it is used for newer deployment variants. Same-node constraints require deploy-time `ClientNodeName` injection.

## Test Signals
Run the external storage e2e suite with the copied file and verify selected tests match the manifest set, especially block, expansion, snapshot, topology, and inline volume cases.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/test-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/app-generic-ephemeral.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/app-generic-ephemeral.yaml

## Purpose
This example pod demonstrates Kubernetes generic ephemeral volumes with the distributed hostpath deployment. It creates an inline PVC from a template and mounts it into a pause container.

## Important APIs, Types, And Functions
The resource is a `v1` `Pod` named `my-csi-app-inline-volume`. The `my-frontend` container uses `registry.k8s.io/pause` and mounts volume `my-csi-volume` at `/data`. The volume is `ephemeral.volumeClaimTemplate` requesting `4Gi`, `ReadWriteOnce`, and `storageClassName: csi-hostpath-fast`.

## Control Flow
When the pod is created, Kubernetes creates a short-lived PVC from the template. The external provisioner uses `csi-hostpath-fast`, waits for consumer topology, and provisions a hostpath volume on the selected node. Kubelet mounts it into the pod and garbage collection removes the PVC with the pod.

## State, Persistence, And Dependencies
The generated PVC/PV and driver state are tied to pod lifetime. Backing data lives under the hostpath data directory until CSI deletion. It depends on the distributed deployment's fast StorageClass and provisioner.

## Integration Points
It exercises the distributed DaemonSet topology/capacity path rather than the driver-specific inline CSI ephemeral path in `NodePublishVolume`. It validates generic ephemeral support through Kubernetes PVC machinery.

## Risks
The label contains a typo in `ephemral`, which affects only metadata selection if copied. If `csi-hostpath-fast` is absent or capacity is exhausted, the pod remains pending. Generic ephemeral cleanup depends on Kubernetes owner references and sidecar deletion.

## Test Signals
Creating the pod should create an owned PVC, bind to `csi-hostpath-fast`, schedule on a node with capacity, mount `/data`, and remove the PVC/PV when the pod is deleted.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/app-generic-ephemeral.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/deploy.sh -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/deploy.sh

## Purpose
This script deploys the distributed hostpath CSI variant, where a DaemonSet runs the driver and node-local provisioner on every node. It applies provisioner RBAC, detects whether CSIStorageCapacity is available, renders manifests with image/path overrides, waits for the DaemonSet to be ready, and optionally writes Prow test driver configuration.

## Important APIs, Types, And Functions
Key functions are `rbac_version()`, `version_gt()`, `update_image()`, `run()`, and `wait_for_daemonset()`. Important variables are `BASE_DIR`, `TEMP_DIR`, `KUBELET_DATA_DIR`, `UPDATE_RBAC_RULES`, `CSI_PROVISIONER_RBAC`, `CSI_PROVISIONER_TAG`, `IMAGE_REGISTRY`, `IMAGE_TAG`, and `CSI_PROW_TEST_DRIVER`. It derives external-provisioner RBAC from `hostpath/csi-hostpath-plugin.yaml`.

## Control Flow
The script fetches or copies provisioner RBAC, wraps it in a temp kustomization with standard labels, and applies it. It then probes `csistoragecapacities.v1beta1.storage.k8s.io`; if unsupported, it records `have_csistoragecapacity=false`. For each `hostpath/*.yaml`, it substitutes kubelet data paths, rewrites image registry/tag components, and removes `storageCapacity: true` plus `--enable-capacity` lines when the API is unavailable. It applies each rendered manifest, waits until the `csi-hostpathplugin` DaemonSet has all desired pods ready, and writes a test driver with the capacity capability patched to the detected cluster support.

## State, Persistence, And Dependencies
The script mutates Kubernetes API state and creates node-local hostPath state through the DaemonSet manifests. Temporary files are cleaned on exit. It depends on `bash`, `curl`, `wget`, `diff`, `kubectl`, kustomize support, and optional network access to fetch RBAC.

## Integration Points
It integrates with the distributed `hostpath` manifests, the external-provisioner sidecar, Kubernetes CSIStorageCapacity API, Prow storage e2e config, and label-based destroy cleanup.

## Risks
Only provisioner RBAC is applied because this distributed variant avoids separate attach/snapshot sidecars. The CSIStorageCapacity probe is hard-coded to v1beta1 and comments say that is always used, so future API changes can break detection. Removing capacity lines with `grep -v` is formatting-sensitive. It waits only ten 3-second retries, which may be short on slow clusters.

## Test Signals
Validate both clusters with and without CSIStorageCapacity support. Confirm rendered driver info and provisioner args match support, DaemonSet readiness reaches desired node count, fast/slow storage classes provision with topology, and the generated Prow file has the correct `capacity` boolean.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/deploy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/destroy.sh -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/destroy.sh

## Purpose
This script removes a hostpath CSI deployment by deleting all Kubernetes resources that carry the deployment's standard labels. It is intended to stay synchronized with the deploy scripts and provides a simple cleanup path for test clusters.

## Important APIs, Types, And Functions
There are no shell functions. The script uses two `kubectl delete` commands under `set -e` and `set -o pipefail`. Both select resources with `app.kubernetes.io/instance=hostpath.csi.k8s.io` and `app.kubernetes.io/part-of=csi-driver-host-path`.

## Control Flow
The first delete targets the Kubernetes `all` category across all namespaces and waits for deletion. The second delete explicitly removes `role`, `clusterrole`, `rolebinding`, `clusterrolebinding`, `serviceaccount`, `storageclass`, and `csidriver` resources across all namespaces with the same labels.

## State, Persistence, And Dependencies
The script mutates only Kubernetes API state. It does not remove host data directories like `/var/lib/csi-hostpath-data` or kubelet plugin directories from nodes. It depends on `bash` and a configured `kubectl` with permissions to delete namespaced and cluster-scoped resources.

## Integration Points
Its deletion contract relies on labels applied by `deploy-hostpath.sh` and the deployment manifests. It complements the hostpath deploy scripts for CI and local test cleanup.

## Risks
Resources missing the standard labels will survive. Persistent hostPath data on nodes is not cleaned. The command is broad across all namespaces for matching labels, so unrelated resources with the same labels would be deleted. If CRDs or snapshot metadata custom resources are introduced without labels or without explicit resource kinds here, cleanup can be incomplete.

## Test Signals
A good validation deploys the driver, runs this script, then checks that labeled `all`, RBAC, service account, storage class, and CSIDriver resources are gone. It should also verify repeated runs against an already-clean cluster fail or pass as expected for the chosen `kubectl delete` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/destroy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-driverinfo.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-driverinfo.yaml

## Purpose
This `CSIDriver` object declares hostpath capabilities for the distributed DaemonSet deployment. It differs from single-node manifests by disabling attach and enabling storage capacity tracking.

## Important APIs, Types, And Functions
The resource is `storage.k8s.io/v1` `CSIDriver` named `hostpath.csi.k8s.io`. It sets persistent and ephemeral lifecycle modes, `podInfoOnMount: true`, `attachRequired: false`, `storageCapacity: true`, and `fsGroupPolicy: File`.

## Control Flow
The distributed deploy script may remove `storageCapacity: true` if the cluster lacks the CSIStorageCapacity API. Kubernetes uses `attachRequired: false` to skip external-attacher flows and uses storage capacity objects during scheduling when enabled.

## State, Persistence, And Dependencies
The object persists in the Kubernetes API. It depends on `storage.k8s.io/v1` support and optionally the CSIStorageCapacity API.

## Integration Points
It aligns with the distributed plugin DaemonSet's `--node-deployment`, `--strict-topology`, and capacity arguments. It also drives the distributed Prow test-driver capability patching.

## Risks
If `storageCapacity: true` remains on unsupported clusters, scheduling/provisioning behavior can fail. `attachRequired: false` must match the absence of attacher sidecar and driver controller publish usage.

## Test Signals
Check the applied CSIDriver after deploy on capacity and non-capacity clusters, verify no VolumeAttachment objects are required, and run topology/capacity e2e cases against fast and slow classes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-plugin.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-plugin.yaml

## Purpose
This manifest deploys the distributed hostpath CSI plugin as a DaemonSet. Each node runs a local hostpath driver, node-driver-registrar, liveness probe, and external-provisioner configured for node-local provisioning and capacity tracking.

## Important APIs, Types, And Functions
The main resource is `apps/v1` `DaemonSet` `csi-hostpathplugin`. Containers include `csi-provisioner:v6.3.0` with `--enable-capacity`, `--node-deployment=true`, `--strict-topology=true`, `--immediate-topology=false`, and owner reference args; `csi-node-driver-registrar:v2.17.0`; `hostpathplugin:v1.17.1` with `--capacity=slow=10Gi` and `--capacity=fast=100Gi`; and `livenessprobe:v2.19.0`.

## Control Flow
One pod runs per node. The hostpath driver exposes `/csi/csi.sock`; the registrar registers it with kubelet; the node-local provisioner watches PVCs and publishes CSIStorageCapacity for the pod/node; provisioning is topology-strict so volumes land on the same node as consumers. The deploy script strips capacity settings when the cluster cannot support them.

## State, Persistence, And Dependencies
Each node stores volume data under `/var/lib/csi-hostpath-data/` and socket/registration data under kubelet plugin directories. The driver uses the configured capacity kinds to simulate `fast` and `slow` pools. It depends on privileged hostPath mounts, mount propagation, `/dev`, and downward API node/pod/namespace values.

## Integration Points
It works with `csi-hostpath-fast` and `csi-hostpath-slow` StorageClasses, the distributed CSIDriver, generic ephemeral example, and Prow topology/capacity configuration. The hostpath Go code enforces `kind` capacity parameters based on these StorageClass values.

## Risks
Every pod is privileged and mounts sensitive host directories. Capacity accounting is local to the driver's persisted JSON and simulated with configured sizes; it is not real disk quota. If capacity API lines are removed incorrectly, provisioner and CSIDriver may disagree. Node-local state means volumes are not portable across nodes.

## Test Signals
DaemonSet readiness should equal desired node count. PVCs using fast/slow classes should bind after pod scheduling, capacity objects should appear when supported, and driver `GetCapacity` should reflect per-kind usage after volume creation/deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-plugin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-storageclass-fast.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-storageclass-fast.yaml

## Purpose
This StorageClass selects the distributed hostpath driver's `fast` simulated capacity pool. It is used for topology-aware provisioning in the DaemonSet deployment.

## Important APIs, Types, And Functions
The resource is `storage.k8s.io/v1` `StorageClass` named `csi-hostpath-fast`. It uses provisioner `hostpath.csi.k8s.io`, `volumeBindingMode: WaitForFirstConsumer`, and parameter `kind: fast`.

## Control Flow
PVCs referencing this class remain unbound until a consuming pod is scheduled. The node-local provisioner then sends `CreateVolume` with `parameters.kind=fast`, and the driver checks remaining configured capacity for that kind.

## State, Persistence, And Dependencies
The class persists in Kubernetes. Actual volume state is in the driver state JSON and node hostPath data directory. It depends on distributed plugin capacity flags defining `fast`.

## Integration Points
It integrates with the distributed DaemonSet's `--capacity=fast=...` settings, CSIStorageCapacity publication, generic ephemeral example for fast class, and Prow test-driver `FromExistingClassName: csi-hostpath-fast`.

## Risks
If the driver capacity map lacks `fast`, provisioning fails with invalid or exhausted capacity. `WaitForFirstConsumer` requires a consumer pod; PVC-only tests expecting immediate binding need different configuration.

## Test Signals
Create a PVC and pod with this class, verify late binding on a node with capacity, and confirm `GetCapacity` decreases by requested volume size for `fast`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-storageclass-fast.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-storageclass-slow.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-storageclass-slow.yaml

## Purpose
This StorageClass selects the distributed hostpath driver's `slow` simulated capacity pool. It is used for topology-aware provisioning in the DaemonSet deployment.

## Important APIs, Types, And Functions
The resource is `storage.k8s.io/v1` `StorageClass` named `csi-hostpath-slow`. It uses provisioner `hostpath.csi.k8s.io`, `volumeBindingMode: WaitForFirstConsumer`, and parameter `kind: slow`.

## Control Flow
PVCs referencing this class remain unbound until a consuming pod is scheduled. The node-local provisioner then sends `CreateVolume` with `parameters.kind=slow`, and the driver checks remaining configured capacity for that kind.

## State, Persistence, And Dependencies
The class persists in Kubernetes. Actual volume state is in the driver state JSON and node hostPath data directory. It depends on distributed plugin capacity flags defining `slow`.

## Integration Points
It integrates with the distributed DaemonSet's `--capacity=slow=...` settings, CSIStorageCapacity publication, generic ephemeral example for fast class, and Prow test-driver `FromExistingClassName: csi-hostpath-fast`.

## Risks
If the driver capacity map lacks `slow`, provisioning fails with invalid or exhausted capacity. `WaitForFirstConsumer` requires a consumer pod; PVC-only tests expecting immediate binding need different configuration.

## Test Signals
Create a PVC and pod with this class, verify late binding on a node with capacity, and confirm `GetCapacity` decreases by requested volume size for `slow`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-storageclass-slow.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-testing.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-testing.yaml

## Purpose
This manifest exposes the hostpath driver's Unix CSI socket as a TCP `NodePort` service for manual and automated testing with tools such as `csi-sanity` or `csc`. It is explicitly marked as test-only, not production deployment material.

## Important APIs, Types, And Functions
It defines a `Service` named `hostpath-service` with port `10000` and a `StatefulSet` named `csi-hostpath-socat`. The pod runs the `socat` command from image `registry.k8s.io/sig-storage/hostpathplugin:v1.17.1` with arguments `tcp-listen:10000,fork,reuseaddr` and `unix-connect:/csi/csi.sock`.

## Control Flow
The socat pod is colocated with the hostpath plugin through required pod affinity, mounts the driver socket hostPath at `/csi`, and forwards each TCP connection to the Unix socket. The distributed variant also mounts `/var/lib/kubelet/pods` because daemonset driver pod names are non-deterministic for sanity testing.

## State, Persistence, And Dependencies
No durable application state is created. The service allocates a NodePort and the pod relies on the driver socket directory. The socat image is intentionally excluded from deploy-script image overrides.

## Integration Points
External CSI test clients can connect to the NodePort and exercise the same CSI endpoint used by sidecars. Labels connect it to deploy readiness and destroy cleanup.

## Risks
Exposing the CSI socket over a NodePort can allow remote callers to create, delete, mount, or snapshot volumes, so this must remain test-only. Pod affinity or daemonset scheduling issues can point socat at a missing socket.

## Test Signals
Verify the service has a NodePort, TCP connections reach CSI RPCs, `csi-sanity` can run through the port, and deleting the manifest removes both service and forwarding pod.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-testing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/test-driver.yaml -->
# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/test-driver.yaml

## Purpose
This test-driver config describes the distributed hostpath deployment to Kubernetes external storage e2e. It uses an existing fast StorageClass and advertises topology and capacity behavior.

## Important APIs, Types, And Functions
The file sets `StorageClass.FromExistingClassName: csi-hostpath-fast`, `DriverInfo.Name: hostpath.csi.k8s.io`, minimum size `1Mi`, and capabilities for block, exec, multipods, node expansion, persistence, single-node volumes, topology, and capacity. It declares topology key `topology.hostpath.csi/node` and shared inline volumes.

## Control Flow
`deploy.sh` copies this file to `CSI_PROW_TEST_DRIVER` when requested and substitutes `capacity: true` with the actual cluster support detected for CSIStorageCapacity. The e2e framework then targets `csi-hostpath-fast` instead of creating a new class.

## State, Persistence, And Dependencies
The file is static test metadata, but its capacity line is deploy-time mutable. It depends on the fast StorageClass and distributed CSIDriver/DaemonSet being applied.

## Integration Points
It aligns with the driver node topology key, distributed capacity objects, and fast/slow StorageClass model.

## Risks
The `capacity` field must match real API support or tests will fail or skip incorrectly. Snapshot and controller expansion are not advertised here because the distributed deployment does not include those sidecars.

## Test Signals
Run e2e with the generated file and verify late binding, topology, capacity, block, inline, and node expansion cases match distributed deployment behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/test-driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/util/deploy-hostpath.sh -->
# sources/control-plane/csi-driver-host-path/deploy/util/deploy-hostpath.sh

## Purpose
This script is the authoritative hostpath CSI deployment workflow for the Kubernetes 1.30 family and the shared util path. It applies sidecar RBAC, optionally applies snapshot-metadata service resources, renders every `hostpath/*.yaml` manifest with image/tag and kubelet path substitutions, waits for the deployed StatefulSet set to become ready, and can emit a Prow `test-driver.yaml` file.

## Important APIs, Types, And Functions
The shell entry points are environment-variable driven. `rbac_version()` extracts image tags from YAML and maps canary tags to RBAC branches. `version_gt()` compares release-style versions. `volume_mode_conversion()` and `snapshot_metadata()` gate optional manifest patches. `update_image()` excludes images such as `socat` from image override substitution. `run()` logs and executes commands. Readiness is handled by `check_statefulset()` and `check_statefulsets()`.

The most important variables are `BASE_DIR`, `TEMP_DIR`, `KUBELET_DATA_DIR`, `UPDATE_RBAC_RULES`, `IMAGE_REGISTRY`, `IMAGE_TAG`, per-image `*_REGISTRY` and `*_TAG`, `VOLUME_MODE_CONVERSION_TESTS`, `SNAPSHOT_METADATA_TESTS`, `CSI_*_RBAC`, `CSI_PROW_TEST_DRIVER`, and `INSTALL_CRD`. RBAC URLs are derived from sidecar versions for provisioner, attacher, snapshotter, resizer, health monitor, and optional snapshot metadata.

## Control Flow
The script creates a temporary directory and removes it on exit. It derives RBAC URLs from manifest image tags, fetches or copies each RBAC file, creates a small kustomization that applies standard `app.kubernetes.io` labels, and runs `kubectl apply --kustomize`. When snapshot metadata is enabled, it also fetches TLS secret, service CR, and service manifests from external-snapshot-metadata and labels/applies them.

For every sorted YAML file under `hostpath/`, the script copies it into the temp directory, applies optional `sed` patches for volume mode conversion and snapshot metadata, replaces `/var/lib/kubelet/` with `KUBELET_DATA_DIR`, rewrites configurable image registry/tag components, prints the resolved image lines, and pipes the rendered manifest to `kubectl apply -f -`. After applying, it discovers all labeled StatefulSets and polls readiness for up to roughly five minutes. On failure it describes labeled resources and prints pod logs. If `CSI_PROW_TEST_DRIVER` is set, it copies the local test driver config and appends `ClientNodeName` from `csi-hostpathplugin-0` for same-node late-binding tests.

## State, Persistence, And Dependencies
The script persists Kubernetes resources through `kubectl apply` and hostpath PV data through the manifest's hostPath directories. Temporary RBAC/kustomization files live only under `TEMP_DIR`. It depends on `bash`, `sed`, `grep`, `sort -V`, `curl`, `wget`, `diff`, `kubectl`, the Kubernetes kustomize integration, and network access to GitHub raw content unless RBAC URLs are overridden to local files.

## Integration Points
It integrates with the deployment-specific `hostpath` manifest directory, external CSI sidecar RBAC repositories, external-snapshot-metadata test resources, Prow storage e2e via `CSI_PROW_TEST_DRIVER`, and the hostpath driver socket under the kubelet plugin directory. The labels it injects are also the contract used by the destroy script and readiness diagnostics.

## Risks
The script applies live cluster-wide RBAC and privileged hostPath workloads. Version extraction is based on simple `sed`/`grep` parsing of image lines, so unusual manifest formatting can produce wrong RBAC branches. Image overrides can decouple sidecar images from checked-in RBAC unless `UPDATE_RBAC_RULES` remains true. The `sed` patches depend on marker comments in the plugin manifest. `KUBELET_DATA_DIR` replacement assumes all nodes use one kubelet data directory. Readiness waits for any labeled StatefulSet names; missing or mislabeled manifests can make diagnostics misleading.

## Test Signals
Useful checks include running with default manifests, overridden image tags, overridden RBAC URLs, `IMAGE_TAG=canary` with blacklist behavior, `VOLUME_MODE_CONVERSION_TESTS=true`, `SNAPSHOT_METADATA_TESTS=true`, and non-default `KUBELET_DATA_DIR`. Cluster-level validation should confirm labeled RBAC exists, sidecars use the expected images, all StatefulSets become ready, Prow driver output includes `ClientNodeName`, and destroy removes every labeled resource.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/util/deploy-hostpath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/util/destroy-hostpath.sh -->
# sources/control-plane/csi-driver-host-path/deploy/util/destroy-hostpath.sh

## Purpose
This script removes a hostpath CSI deployment by deleting all Kubernetes resources that carry the deployment's standard labels. It is intended to stay synchronized with the deploy scripts and provides a simple cleanup path for test clusters.

## Important APIs, Types, And Functions
There are no shell functions. The script uses two `kubectl delete` commands under `set -e` and `set -o pipefail`. Both select resources with `app.kubernetes.io/instance=hostpath.csi.k8s.io` and `app.kubernetes.io/part-of=csi-driver-host-path`.

## Control Flow
The first delete targets the Kubernetes `all` category across all namespaces and waits for deletion. The second delete explicitly removes `role`, `clusterrole`, `rolebinding`, `clusterrolebinding`, `serviceaccount`, `storageclass`, and `csidriver` resources across all namespaces with the same labels.

## State, Persistence, And Dependencies
The script mutates only Kubernetes API state. It does not remove host data directories like `/var/lib/csi-hostpath-data` or kubelet plugin directories from nodes. It depends on `bash` and a configured `kubectl` with permissions to delete namespaced and cluster-scoped resources.

## Integration Points
Its deletion contract relies on labels applied by `deploy-hostpath.sh` and the deployment manifests. It complements the hostpath deploy scripts for CI and local test cleanup.

## Risks
Resources missing the standard labels will survive. Persistent hostPath data on nodes is not cleaned. The command is broad across all namespaces for matching labels, so unrelated resources with the same labels would be deleted. If CRDs or snapshot metadata custom resources are introduced without labels or without explicit resource kinds here, cleanup can be incomplete.

## Test Signals
A good validation deploys the driver, runs this script, then checks that labeled `all`, RBAC, service account, storage class, and CSIDriver resources are gone. It should also verify repeated runs against an already-clean cluster fail or pass as expected for the chosen `kubectl delete` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/deploy/util/destroy-hostpath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-app-inline.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-app-inline.yaml

## Purpose
This example demonstrates an inline CSI ephemeral-style pod volume for the hostpath CSI driver.

## Important APIs, Types, And Functions
Pod `my-csi-app-inline` mounts a `csi` volume with driver `hostpath.csi.k8s.io` at `/data` in a busybox container and pins scheduling to nodes with topology key `topology.hostpath.csi/node`.

## Control Flow
Kubelet calls `NodePublishVolume` directly with CSI volume context, and the driver can create an ephemeral volume when configured or when Kubernetes passes ephemeral context.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-app-inline.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-app.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-app.yaml

## Purpose
This example demonstrates a pod consuming the standard filesystem PVC for the hostpath CSI driver.

## Important APIs, Types, And Functions
Pod `my-csi-app` mounts PVC `csi-pvc` at `/data` in a busybox container.

## Control Flow
Kubernetes binds the referenced PVC, then kubelet stages and publishes the hostpath volume into the pod.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-app.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-block-clone.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-block-clone.yaml

## Purpose
This example demonstrates a raw block PVC clone for the hostpath CSI driver.

## Important APIs, Types, And Functions
PVC `pvc-raw-clone` uses StorageClass `csi-hostpath-sc`, dataSource PVC `pvc-raw`, and requests `1Gi`.

## Control Flow
External-provisioner sends a clone `CreateVolume` request; the driver copies block data with `dd` when source and target modes are compatible.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-block-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-block-pvc-restore.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-block-pvc-restore.yaml

## Purpose
This example demonstrates a raw block PVC restored from a snapshot for the hostpath CSI driver.

## Important APIs, Types, And Functions
PVC `raw-pvc-restore` is `volumeMode: Block`, dataSource VolumeSnapshot `raw-pvc-snapshot`, and requests `1Gi`.

## Control Flow
The driver creates a block backing file and populates it from snapshot data with `dd`.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-block-pvc-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-block-pvc-snapshot.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-block-pvc-snapshot.yaml

## Purpose
This example demonstrates a VolumeSnapshot of a raw block PVC for the hostpath CSI driver.

## Important APIs, Types, And Functions
VolumeSnapshot `raw-pvc-snapshot` references class `csi-hostpath-snapclass` and source PVC `pvc-raw`.

## Control Flow
External-snapshotter calls `CreateSnapshot`; the driver copies the block backing file into a `.snap` file.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-block-pvc-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-clone.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-clone.yaml

## Purpose
This example demonstrates a filesystem PVC clone for the hostpath CSI driver.

## Important APIs, Types, And Functions
PVC `hp-pvc-clone` uses dataSource PVC `src-hp-pvc` and requests `1Gi` from `csi-hostpath-sc`.

## Control Flow
The driver creates a new mount volume and copies source directory contents with `cp -a`.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-groupsnapshot-v1beta1.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-groupsnapshot-v1beta1.yaml

## Purpose
This example demonstrates a v1beta1 VolumeGroupSnapshot request for the hostpath CSI driver.

## Important APIs, Types, And Functions
VolumeGroupSnapshot `new-groupsnapshot-demo` selects PVCs labelled `app.kubernetes.io/name: postgresql` and uses class `csi-hostpath-groupsnapclass`.

## Control Flow
The group snapshot controller calls the driver's group controller, which snapshots each selected source volume.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-groupsnapshot-v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-groupsnapshotclass-v1beta1.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-groupsnapshotclass-v1beta1.yaml

## Purpose
This example demonstrates a v1beta1 VolumeGroupSnapshotClass for the hostpath CSI driver.

## Important APIs, Types, And Functions
VolumeGroupSnapshotClass `csi-hostpath-groupsnapclass` sets `deletionPolicy: Delete` and driver `hostpath.csi.k8s.io`.

## Control Flow
Group snapshot requests referencing this class are routed to the hostpath group controller service.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-groupsnapshotclass-v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-pod-block.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-pod-block.yaml

## Purpose
This example demonstrates a pod consuming a raw block PVC for the hostpath CSI driver.

## Important APIs, Types, And Functions
Pod `pod-raw` mounts PVC `pvc-raw` as a block device at `/dev/loop3` in a busybox container.

## Control Flow
Kubelet sends block `NodePublishVolume`; the driver bind-mounts the loop device for the backing file onto the requested device path.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-pod-block.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-pvc-block.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-pvc-block.yaml

## Purpose
This example demonstrates a raw block PVC for the hostpath CSI driver.

## Important APIs, Types, And Functions
PVC `pvc-raw` requests `1Gi`, `ReadWriteOnce`, StorageClass `csi-hostpath-sc`, and `volumeMode: Block`.

## Control Flow
The driver allocates a backing file with `fallocate` and attaches it to a loop device.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-pvc-block.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-pvc.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-pvc.yaml

## Purpose
This example demonstrates the standard filesystem PVC for the hostpath CSI driver.

## Important APIs, Types, And Functions
PVC `csi-pvc` requests `1Gi` from StorageClass `csi-hostpath-sc`.

## Control Flow
External-provisioner creates a mount-access hostpath volume and kubelet later bind-mounts it into pods.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-restore.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-restore.yaml

## Purpose
This example demonstrates a filesystem PVC restored from a snapshot for the hostpath CSI driver.

## Important APIs, Types, And Functions
PVC `hpvc-restore` uses dataSource VolumeSnapshot `new-snapshot-demo` and requests `1Gi`.

## Control Flow
The driver extracts the snapshot tar archive into the new volume path.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-snapshot-v1.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-snapshot-v1.yaml

## Purpose
This example demonstrates a v1 VolumeSnapshot for the filesystem PVC for the hostpath CSI driver.

## Important APIs, Types, And Functions
VolumeSnapshot `new-snapshot-demo` references snapshot class `csi-hostpath-snapclass` and source PVC `csi-pvc`.

## Control Flow
The driver archives the source volume directory into a `.snap` file.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-snapshot-v1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-storageclass.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-storageclass.yaml

## Purpose
This example demonstrates the standard hostpath StorageClass for the hostpath CSI driver.

## Important APIs, Types, And Functions
StorageClass `csi-hostpath-sc` uses provisioner `hostpath.csi.k8s.io`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and `allowVolumeExpansion: true`.

## Control Flow
PVCs bind immediately and are eligible for expansion through resizer/controller/node paths.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-volumesnapshotclass.yaml -->
# sources/control-plane/csi-driver-host-path/examples/csi-volumesnapshotclass.yaml

## Purpose
This example demonstrates the example hostpath VolumeSnapshotClass for the hostpath CSI driver.

## Important APIs, Types, And Functions
VolumeSnapshotClass `csi-hostpath-snapclass` uses driver `hostpath.csi.k8s.io` and deletion policy `Delete`.

## Control Flow
VolumeSnapshots route to the hostpath snapshot controller and delete backend snapshots on object deletion.

## State, Persistence, And Dependencies
The object persists in Kubernetes until deleted. Backing volume or snapshot data, when created, is persisted by the hostpath driver under its configured state directory. The examples depend on the matching StorageClass, SnapshotClass, CSIDriver, sidecars, and snapshot/group snapshot CRDs where applicable.

## Integration Points
It integrates with the deployment manifests and the Go driver methods for provisioning, node publishing, cloning, snapshotting, restoring, expansion, or group snapshotting as appropriate. Names in comments identify companion examples that must exist first.

## Risks
These examples are for testing and demonstration. Hard-coded names can collide in a shared namespace. Snapshot and clone examples require source PVCs or snapshots to exist and be ready. Block examples depend on privileged driver loop-device handling and a site-appropriate device path in the pod.

## Test Signals
Apply the prerequisite class/source objects, create this object, and verify the Kubernetes object reaches bound/ready/running state. Driver logs should show the corresponding CSI RPCs and cleanup should remove generated volumes or snapshots when reclaim/delete policy applies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/examples/csi-volumesnapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/hack/bump-image-versions.sh -->
# sources/control-plane/csi-driver-host-path/hack/bump-image-versions.sh

## Purpose
This maintenance script updates sidecar image tags in all deployment files to the latest release tags found in `registry.k8s.io/sig-storage`. It is intended as a helper for release maintenance, not an automatic commit generator.

## Important APIs, Types, And Functions
The script is POSIX `sh` with `set -e` and `set -x`. It defines an `images` list containing CSI sidecars and liveness probe images, checks for `skopeo` and `jq`, then loops over each image. For each image, it runs `skopeo list-tags --retry-times 3`, uses `jq` to list tags, filters tags beginning with `v`, sorts with `sort -V`, selects the last tag, and runs `find deploy -type f -exec sed -i '' ...` to rewrite matching image lines.

## Control Flow
Dependency checks happen first. The loop queries registry tags one image at a time. The substitution replaces any line starting with `image: registry.k8s.io/sig-storage/$image:` with the same prefix and the latest discovered tag. The introductory comment warns maintainers not to commit all changes blindly because older Kubernetes deployments may need older sidecars.

## State, Persistence, And Dependencies
The script edits files under `deploy/` in place. It depends on network access to the registry, `skopeo`, `jq`, `grep`, `sort -V`, `find`, and a BSD/macOS-style `sed -i ''` invocation.

## Integration Points
It updates the image tags that deploy scripts parse for image override defaults and RBAC version derivation. It affects Kubernetes deployment manifests across all versioned deployment directories.

## Risks
`sed -i ''` is not portable to GNU sed without different syntax, so Linux runs may fail. Latest sidecar tags may be incompatible with older deployment manifests or Kubernetes versions. The script does not update RBAC files directly; deploy scripts fetch RBAC based on tags at runtime.

## Test Signals
Run in a disposable branch, inspect `git diff`, verify only intended image lines changed, and deploy each supported manifest variant against its target Kubernetes version before committing any updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/hack/bump-image-versions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/internal/endpoint/endpoint.go -->
# sources/control-plane/csi-driver-host-path/internal/endpoint/endpoint.go

## Purpose
This package normalizes CSI endpoint strings and creates listeners for Unix or TCP endpoints. It is shared by the gRPC server and the bidirectional proxy.

## Important APIs, Types, And Functions
`Parse(ep string)` returns protocol, address, and error. It accepts explicit `unix://` and `tcp://` prefixes case-insensitively, rejects empty post-prefix addresses, and treats all other strings as Unix socket paths. `Listen(endpoint string)` calls `Parse`, removes an existing Unix socket path before listening, returns a `net.Listener`, and returns a cleanup callback that removes Unix socket files on shutdown.

## Control Flow
Callers parse or listen in one step. For Unix endpoints, cleanup starts before `net.Listen` by deleting any stale socket path and ends by deleting the socket file again. TCP endpoints receive a no-op cleanup.

## State, Persistence, And Dependencies
The only persistent state is the Unix socket path on disk. Dependencies are Go `net`, `os`, `strings`, and `fmt`.

## Integration Points
`pkg/hostpath/server.go` uses it to serve CSI gRPC. `internal/proxy/proxy.go` uses it to open both ends of a socket-pair proxy. Endpoint behavior must match command-line `--endpoint` and `--proxy-endpoint` style values.

## Risks
Deleting the Unix socket path before listening is correct for stale sockets but dangerous if the configured path points at an unintended file. Parent directories are not created here. Unsupported schemes without `://` are silently treated as Unix paths, which is permissive but can hide typos.

## Test Signals
Tests should cover explicit Unix and TCP endpoints, bare Unix paths, empty `unix://`, cleanup removing socket files, stale socket replacement, and failure when parent directories are missing.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/internal/endpoint/endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/internal/proxy/proxy.go -->
# sources/control-plane/csi-driver-host-path/internal/proxy/proxy.go

## Purpose
This package implements a socket-pair proxy for cases where neither side can actively dial the other. It listens on two endpoints, pairs one accepted connection from each, and copies bytes in both directions, similar to a two-listener socat setup.

## Important APIs, Types, And Functions
`Run(ctx, endpoint1, endpoint2)` creates a cancellable proxy, listens on both endpoints through `endpoint.Listen`, starts the accept loop, and returns an `io.Closer`. The private `proxy` struct stores context, cancel function, listeners, and cleanup callbacks. `Close()` cancels, closes listeners, and removes socket files. `accept()` retries accept failures unless context is done. `copy()` uses `io.Copy` and closes the destination when one direction ends.

## Control Flow
The goroutine blocks on the first listener, then accepts from the second listener. Once both connections exist, it starts two copy goroutines and loops back to accept another pair. If either listener closes during shutdown, the loop exits and any half-accepted connection is closed.

## State, Persistence, And Dependencies
State is in listener sockets and active TCP/Unix connections. Unix socket files are cleaned by endpoint cleanup callbacks. Dependencies include context cancellation, Go networking, `io.Copy`, klog, and the internal endpoint package.

## Integration Points
The proxy is useful for exposing CSI sockets in tests where both endpoints must be listeners. It mirrors behavior described in comments for a Unix-listen/TCP-listen socat command while keeping both listeners open.

## Risks
Connections are paired strictly in accept order; an unmatched connection on one endpoint waits for the other endpoint. There is no authentication, rate limiting, or backpressure beyond OS sockets. Copy goroutines close only the destination side, so protocol behavior depends on peer EOF semantics.

## Test Signals
Unit tests should connect to both endpoints in both directions, send data each way, and verify closing one side propagates EOF. Additional stress tests could cover multiple sequential pairs, cancellation while one side is waiting, and listener creation failures.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/internal/proxy/proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/internal/proxy/proxy_test.go -->
# sources/control-plane/csi-driver-host-path/internal/proxy/proxy_test.go

## Purpose
This test file verifies the two-listener proxy can move bytes bidirectionally over Unix sockets and propagates connection closure.

## Important APIs, Types, And Functions
`TestProxy` creates a temp directory, starts `Run(ctx, a.sock, b.sock)`, and runs subtests `a-to-b` and `b-to-a`. `sendReceive` dials both endpoints, writes `ping` one way and `pong-pong` the other way, then closes one side and expects EOF on the other.

## Control Flow
Each subtest establishes a paired connection by dialing both endpoints. It performs request/response reads with fixed buffers, validates exact payload strings, closes the first connection, drains the second with `io.Copy`, and asserts no extra bytes arrived.

## State, Persistence, And Dependencies
The test uses temporary Unix socket files that are removed through proxy cleanup and `t.TempDir`. It depends on local Unix socket support and Go testing.

## Integration Points
It validates the behavior relied on by any test deployment or process that uses the proxy instead of socat to bridge CSI endpoints.

## Risks
The test covers only one connection pair at a time and only small payloads. It does not exercise TCP endpoints, cancellation while accepting, listener startup failures, or concurrent clients.

## Test Signals
Passing tests show basic pair establishment, bidirectional data movement, and EOF propagation. Failures usually indicate endpoint cleanup, accept ordering, or copy/close behavior regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/internal/proxy/proxy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/controllerserver.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/controllerserver.go

## Purpose
This file implements the CSI controller service for hostpath volumes: create/delete, validation, attach/detach, capacity reporting, volume listing and health, mutable parameter validation, snapshots, snapshot listing, and controller-side expansion.

## Important APIs, Types, And Functions
Important RPC methods are `CreateVolume`, `DeleteVolume`, `ControllerGetCapabilities`, `ValidateVolumeCapabilities`, `ControllerPublishVolume`, `ControllerUnpublishVolume`, `GetCapacity`, `ListVolumes`, `ControllerGetVolume`, `ControllerModifyVolume`, `CreateSnapshot`, `DeleteSnapshot`, `ListSnapshots`, and `ControllerExpandVolume`. Helpers include `convertSnapshot`, `validateVolumeMutableParameters`, `validateControllerServiceRequest`, and `getControllerServiceCapabilities`. Constant `deviceID` is the publish-context key placeholder.

## Control Flow
Most RPCs validate arguments and feature capabilities, then lock `hp.mutex` before reading or writing shared state. `CreateVolume` rejects missing names/capabilities, mixed block and mount access, invalid capacity ranges, unsupported mutable parameters, and incompatible idempotent requests. New volumes get UUIDs, optional topology, optional kind capacity selection, and optional population from snapshot or source volume. `DeleteVolume` checks lifecycle state, optionally errors when configured, and calls `deleteVolume`. Attach RPCs mark `Attached` and `ReadOnlyAttach` while enforcing node ID and attach limits. Listing sorts volumes/snapshots and supports simple token pagination. Snapshot creation handles idempotency by name/source, creates `.snap` files, and persists `state.Snapshot`. Expansion updates stored `VolSize` and reports whether node expansion is required.

## State, Persistence, And Dependencies
The controller persists all changes through `state.State`. Volume records include size, path, access mode, attachment, staged/published sets, parent source IDs, and kind. Snapshot records include name, ID, source volume, path, creation time, ready flag, and optional group snapshot ID. Dependencies include CSI protobufs, uuid generation, gRPC status codes, protobuf timestamps/wrappers, Kubernetes sets, klog, and helper functions in this package.

## Integration Points
External-provisioner, attacher, resizer, snapshotter, health monitor, and Kubernetes e2e tests call these RPCs through the driver socket. StorageClass `parameters.kind` drives capacity pools. Snapshot classes and examples drive snapshot RPCs. Group snapshots reuse snapshot state written here.

## Risks
All controller operations are serialized, which is simple but makes long tar/cp/dd snapshot or clone operations block unrelated RPCs. `DeleteSnapshot` appears to check `err != nil && snapshot.GroupSnapshotID != ""`, which cannot detect an existing snapshot in a group; this likely allows deleting grouped snapshots directly. `ListVolumes` pagination compares the absolute index against `maxLength`, which can truncate pages incorrectly for non-default starting tokens. Expansion updates metadata but not actual backing file/filesystem size. Lifecycle violations only warn unless `CheckVolumeLifecycle` is enabled.

## Test Signals
Existing tests cover create-volume validation and mutable parameters. Additional tests should cover idempotent create with sources, capacity range edge cases, kind capacity exhaustion, attach limit and readonly idempotency, lifecycle enforcement, list pagination, grouped snapshot deletion protection, snapshot source restore, list snapshots pagination, and expansion limits.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/controllerserver_test.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/controllerserver_test.go

## Purpose
This file tests selected controller service validation paths for volume creation and controller modify volume. It focuses on mutable parameter support, required fields, and feature-gated capabilities.

## Important APIs, Types, And Functions
`TestCreateVolume` builds table-driven `csi.CreateVolumeRequest` cases and compares expected `CreateVolumeResponse` values after clearing generated volume IDs. `TestControllerModifyVolume` preloads volumes through `hp.createVolume` and tests `ControllerModifyVolume` request validation and accepted mutable parameter names.

## Control Flow
Each test case creates a temporary state directory, constructs a `Config` with driver name, endpoint, node ID, maximum size, topology enabled, and per-case modify-volume options, then creates a new driver. Some cases call `CreateVolume`; modify cases preload state volumes and call `ControllerModifyVolume`. The tests assert whether errors occur and compare responses with `testify/assert`.

## State, Persistence, And Dependencies
Tests create real temporary state directories and, for mount volumes, real directories under them. They depend on CSI protobufs, the `state` package, `testify/assert`, and Go temp file cleanup.

## Integration Points
They directly exercise the controller server and core volume creation helpers, providing regression coverage for storage e2e-visible behavior around mutable parameters and topology responses.

## Risks
Coverage is narrow: it does not test snapshots, deletion, attach, capacity, clone/restore, pagination, expansion, or block volumes. Some `CreateVolume` success cases use an empty `VolumeCapabilities` slice, which the implementation currently accepts because it only rejects nil.

## Test Signals
Passing tests show required field checks, mixed access type rejection, feature-gated modify-volume support, accepted mutable parameter filtering, and topology response population.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/controllerserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/flag.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/flag.go

## Purpose
This file defines custom command-line flag value types used by the hostpath driver configuration: simulated storage capacity by kind and comma-separated string arrays.

## Important APIs, Types, And Functions
`Capacity` is `map[string]resource.Quantity` and implements `flag.Value` through `Set`, `String`, and `Enabled`. `Set` requires `<type>=<size>`, parses the size with Kubernetes `resource.ParseQuantity`, initializes the map if needed, and overwrites prior values. `StringArray` is `[]string` and implements `Set` by splitting comma-separated values and trimming whitespace, and `String` by formatting the slice.

## Control Flow
The flag package calls `Set` once per supplied flag occurrence. Multiple `--capacity` flags accumulate or overwrite per kind. Multiple `StringArray.Set` calls append values.

## State, Persistence, And Dependencies
These types hold in-memory process configuration only. Capacity values later affect controller `CreateVolume` and `GetCapacity`; they are not persisted except indirectly through volume `Kind` records. Dependencies are Go `flag`, `strings`, `fmt`, `errors`, and Kubernetes resource quantities.

## Integration Points
Deployment manifests pass `--capacity=slow=10Gi` and `--capacity=fast=100Gi` in the distributed plugin. Mutable parameter configuration uses `StringArray` to filter `ControllerModifyVolume` and `CreateVolume` mutable parameters.

## Risks
`StringArray.Set` does not ignore empty entries, so `--flag=` or trailing commas add empty accepted names. `Capacity.Enabled` dereferences the map receiver, so callers must use an initialized variable or addressable zero value as intended. Capacity is simulated and only enforced by driver code.

## Test Signals
Tests should cover valid/invalid capacity strings, multiple capacities, overwrites, binary/decimal quantities, empty string-array entries, whitespace trimming, and `Enabled` for nil and populated maps.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/flag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/groupcontrollerserver.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/groupcontrollerserver.go

## Purpose
This file implements the CSI group controller service for volume group snapshot create, delete, get, and capability reporting. It creates one ordinary snapshot per source volume and links them through a persisted group snapshot record.

## Important APIs, Types, And Functions
RPCs are `GroupControllerGetCapabilities`, `CreateVolumeGroupSnapshot`, `DeleteVolumeGroupSnapshot`, and `GetVolumeGroupSnapshot`. `validateGroupControllerServiceRequest` accepts only `CREATE_DELETE_GET_VOLUME_GROUP_SNAPSHOT`. It uses `state.GroupSnapshot`, `state.Snapshot`, uuid generation, protobuf timestamps, and `optionsFromParameters`/`createSnapshotFromVolume`.

## Control Flow
Create validates name and source volume IDs, locks state, and handles idempotency by group snapshot name and matching source volume IDs. For a new group, it allocates a group UUID, copies source IDs, loops over each source volume, validates snapshot parameters, creates a snapshot file, stores a snapshot record with `GroupSnapshotID`, and finally stores the group record. Delete finds the group, removes each snapshot file and state record, then deletes the group record. Get validates requested snapshot IDs against the group and returns each snapshot's metadata.

## State, Persistence, And Dependencies
Group state is persisted in `state.json` alongside individual snapshots. Snapshot files are stored in the same `.snap` path scheme as ordinary snapshots. There is no transactional rollback across multiple snapshot files/state writes.

## Integration Points
Group snapshot examples use the v1beta1 Kubernetes group snapshot API. The identity service advertises `GROUP_CONTROLLER_SERVICE`; the gRPC server always registers the group controller. The individual snapshot records also appear through normal snapshot listing with `GroupSnapshotId` set.

## Risks
The TODO notes missing cleanup on partial create failure; a failed later source can leave earlier snapshot files/state without a group record. `hp.state.UpdateSnapshot(snapshot)` errors are ignored inside the loop. Snapshot parameter handling uses the same tar options as ordinary snapshots. This test driver does not coordinate crash-consistent group snapshots; it snapshots volumes sequentially.

## Test Signals
Tests should cover capability response, create idempotency with same/different source sets, partial source missing behavior, delete idempotency for not found, get with mismatched snapshot IDs, parameter validation, and cleanup of all member snapshots.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/groupcontrollerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/healthcheck.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/healthcheck.go

## Purpose
This file implements volume health and stats helpers for controller and node CSI responses. It checks source path existence, filesystem capacity/availability, and whether a volume appears mounted under kubelet pod mount information.

## Important APIs, Types, And Functions
Types `MountPointInfo`, `ContainerFileSystem`, and `FileSystems` model `findmnt --json` output. Helpers include `checkPathExist`, `parseMountInfo`, `checkMountPointExist`, `checkPVCapacityValid`, `getPVStats`, `checkPVUsage`, `doHealthCheckInControllerSide`, and `doHealthCheckInNodeSide`. Constants identify `/var/lib/kubelet/pods` and the CSI pod volume path fragment.

## Control Flow
Controller-side health checks verify the driver source path exists, the filesystem capacity reported by Kubernetes `fs.Info` is at least the requested volume size, and available bytes are positive. Node-side health executes `findmnt --json`, parses the first filesystem tree, finds the `/var/lib/kubelet/pods` subtree, and checks whether any child mount source contains the hostpath volume path and still has a target path on disk.

## State, Persistence, And Dependencies
The functions read live host filesystem and mount state. They depend on `findmnt`, JSON output shape, `os.Stat`, `os/exec`, klog, and Kubernetes `pkg/volume/util/fs.Info`.

## Integration Points
`ListVolumes`, `ControllerGetVolume`, and `NodeGetVolumeStats` include `VolumeCondition` based on these helpers. The deployment manifests mount kubelet pod directories so node-side checks can see pod CSI mounts.

## Risks
Node-side mount detection is heuristic: it looks only under the first top-level filesystem's children and uses substring matching on mount source. Different `findmnt` JSON shapes or kubelet paths can cause false unhealthy results. Controller capacity checks compare the whole filesystem capacity to requested volume size, not real quota. The typo `Filsystem` is only a struct field name but can confuse readers.

## Test Signals
Existing tests parse a representative `findmnt` JSON document and helper extraction functions. Additional tests should cover empty/malformed JSON, missing `/var/lib/kubelet/pods`, mount source substring collisions, `findmnt` absence, and controller-side missing path/capacity/usage failures.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/healthcheck.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/healthcheck_test.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/healthcheck_test.go

## Purpose
This test file provides regression coverage for healthcheck mount-info parsing and two local helper functions that extract PVC names and volume IDs from kubelet-style mount paths.

## Important APIs, Types, And Functions
`originalMountInfo` is a large representative `findmnt --json` payload. `TestParseMountInfo` verifies `parseMountInfo` returns children without error. `TestFilterVolumeName` and `TestFilterVolumeID` verify local test helpers `filterVolumeName` and `filterVolumeID` using CSI pod target/source paths.

## Control Flow
The parser test unmarshals the fixture through production `parseMountInfo`. The extraction tests split or regex-match hard-coded path strings and compare expected identifiers.

## State, Persistence, And Dependencies
The tests are pure in-memory and do not execute `findmnt` or inspect real mounts. Dependencies include Go testing, regexp, strings, and `testify/assert`.

## Integration Points
They support confidence in the JSON structure consumed by `checkMountPointExist`, although the filter helper functions are test-local and not used by production code.

## Risks
Because production mount existence logic is not directly tested, regressions in traversal, substring matching, command execution, or path stat handling can pass. The fixture is large but represents one environment only.

## Test Signals
Passing tests confirm that the expected `findmnt` schema still matches `parseMountInfo`. More complete coverage would mock command output and exercise `checkMountPointExist` for mounted, unmounted, malformed, and missing-path cases.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/healthcheck_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/hostpath.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/hostpath.go

## Purpose
This file defines the core hostpath driver object, configuration, persistent state initialization, volume/snapshot path helpers, and low-level operations for creating, deleting, cloning, restoring, and snapshotting hostpath volumes.

## Important APIs, Types, And Functions
`hostPath` embeds unimplemented CSI identity, controller, node, group controller, and snapshot metadata servers and owns `Config`, a mutex, and `state.State`. `Config` contains driver identity, endpoints, node ID, state directory, maximum sizes, attach limit, capacity map, feature flags, snapshot metadata settings, mutable parameter names, expansion toggles, lifecycle checks, and list-snapshot enablement. `NewHostPathDriver` validates required fields, creates `StateDir`, and opens `state.json`. `Run` starts the nonblocking gRPC server and optionally registers snapshot metadata.

Core helpers include `getVolumePath`, `getSnapshotPath`, `createVolume`, `deleteVolume`, `sumVolumeSizes`, `hostPathIsEmpty`, `loadFromSnapshot`, `loadFromVolume`, `loadFromFilesystemVolume`, `loadFromBlockVolume`, `getAttachCount`, and `createSnapshotFromVolume`.

## Control Flow
Driver construction creates or opens JSON state under `StateDir`. `createVolume` enforces `MaxVolumeSize`, optional per-kind simulated capacity, and access type. Mount volumes become directories; block volumes become files created by `fallocate` and attached through `VolumePathHandler`. It then writes a `state.Volume` record. `deleteVolume` detaches loop devices for block volumes, removes the backing path, and deletes the state record. Restore/clone paths validate source readiness, size, and access mode, then use `tar`, `cp -a`, or `dd`. Snapshot creation uses `tar czf` for filesystem volumes and `cp` for block volumes.

## State, Persistence, And Dependencies
Durable state is split between `state.json`, volume directories/files under `StateDir`, and snapshot files with `.snap` extension. Capacity is not separately persisted; it is recomputed by summing persisted volumes by `Kind`. The code depends on CSI protobufs, gRPC status codes, Kubernetes resource quantities, klog, kubelet `volumepathhandler`, `k8s.io/utils/exec`, and host tools `fallocate`, `tar`, `cp`, and `dd`.

## Integration Points
Controller and node server files call these helpers for CSI RPCs. Deployment manifests mount `/csi-data-dir` as the state directory and `/dev` for loop devices. Capacity parameters connect to distributed StorageClasses with `parameters.kind`.

## Risks
This is a test driver with privileged host operations. Shell commands must exist inside the image and can be slow or fail for large data. Block capacity is rounded down to MiB for `fallocate` by `cap/mib`. `createVolume` writes state after filesystem/device operations, so partial failures can leave files or loop devices. Snapshot/restore operations run under the global mutex in callers, blocking other RPCs. Capacity accounting is simulated and not real disk quota.

## Test Signals
High-value tests cover missing config validation, mount and block volume creation/deletion, capacity exhaustion by kind, clone/restore from filesystem and block sources, snapshot tar/copy creation, loop-device cleanup, idempotent delete of missing volumes, and command failure behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/hostpath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/identityserver.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/identityserver.go

## Purpose
This file implements the CSI identity service for the hostpath driver. It reports plugin name/version, liveness probe readiness, and high-level plugin service capabilities.

## Important APIs, Types, And Functions
`GetPluginInfo` validates `DriverName` and `VendorVersion` and returns them. `Probe` returns an empty successful `ProbeResponse`. `GetPluginCapabilities` always advertises controller service and group controller service, conditionally advertises volume accessibility constraints when topology is enabled, and conditionally advertises snapshot metadata service when enabled.

## Control Flow
Identity RPCs do not lock shared state. They read configuration and build CSI protobuf responses. Missing driver name or vendor version produces `codes.Unavailable`.

## State, Persistence, And Dependencies
No persistent state is touched. Dependencies are CSI protobufs, gRPC status codes, context, and klog.

## Integration Points
Kubelet, sidecars, liveness probe, and CSI test tools call identity RPCs early to discover driver identity and services. Capability advertisement must align with gRPC server registration and feature flags in `Run`.

## Risks
Group controller service is always advertised because the server always registers it; deployments without group snapshot CRDs may still show the CSI capability. Snapshot metadata is advertised only when the optional server is registered. Empty vendor version in tests or builds causes identity failure.

## Test Signals
Tests should check configured and missing driver/version responses, topology capability toggling, snapshot metadata capability toggling, and a successful probe.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/nodeserver.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/nodeserver.go

## Purpose
This file implements the CSI node service: publish/unpublish, stage/unstage, node identity/topology, node capabilities, volume stats and health, and node-side expansion validation.

## Important APIs, Types, And Functions
RPCs are `NodePublishVolume`, `NodeUnpublishVolume`, `NodeStageVolume`, `NodeUnstageVolume`, `NodeGetInfo`, `NodeGetCapabilities`, `NodeGetVolumeStats`, and `NodeExpandVolume`. Constants include `TopologyKeyNode` and the single-writer conflict message. Helpers are `makeFile`, `hasSingleNodeSingleWriterAccessMode`, and `isMountedElsewhere`.

## Control Flow
`NodePublishVolume` validates request fields, detects inline ephemeral context, locks state, optionally creates a 100Mi ephemeral mount volume, looks up the volume, enforces single-node-single-writer target conflicts, and requires persistent volumes to be staged at the requested staging path. Block publishes resolve the loop device for the backing file, create target files, and bind-mount the loop device. Mount publishes create target directories and bind-mount the volume path, adding `ro` for readonly. It records node ID and target path in state. `NodeUnpublishVolume` unmounts and removes target paths, deleting ephemeral volumes or updating published sets. Stage/unstage only update state and enforce attach/stage/publish lifecycle. Info/capabilities report topology, attach-limit-derived max volumes, stats, and expansion support. Node expansion validates requested capacity and target path type but does not resize storage.

## State, Persistence, And Dependencies
Node RPCs mutate `state.Volume` fields `NodeID`, `Published`, `Staged`, and ephemeral records. They read and manipulate host mount state, target paths, loop devices, and filesystem stats. Dependencies include CSI protobufs, gRPC statuses, Kubernetes `mount`, `volumepathhandler`, random attach limit testing, and OS file operations.

## Integration Points
Kubelet calls these RPCs after registrar registration. Controller publish/stage lifecycle depends on `EnableAttach` and state written by controller RPCs. Inline CSI examples and CSIDriver `podInfoOnMount` feed ephemeral behavior. Health and stats tie into `healthcheck.go`.

## Risks
`makeFile` defers `f.Close()` before checking `err`; if `os.OpenFile` fails, `f` can be nil and panic. Stage does not perform an actual mount; publish relies on the backing path directly. Ephemeral volume creation logs `vol.VolPath` even if `createVolume` returned an error with nil `vol` other than `os.IsExist`. Bind mounts and loop devices require privileged host access. Single-writer conflict detection only checks this driver's persisted published target set.

## Test Signals
Tests should cover ephemeral create/delete, missing required fields, mount and block publish idempotency, read-only bind options, single-writer conflict, staging lifecycle errors, attach-required behavior, target path cleanup, stats volume condition, attach limit reporting including random mode, and `makeFile` error behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/nodeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/options.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/options.go

## Purpose
This file parses supported snapshot parameter options into command-line flags used when archiving filesystem volumes. Currently it supports `ignoreFailedRead` for tar-based snapshots.

## Important APIs, Types, And Functions
Constant `ignoreFailedReadParameterName` is `ignoreFailedRead`. `optionsFromParameters(vol, parameters)` returns `[]string{"--ignore-failed-read"}` when the volume is mount-access and the parameter parses as boolean true. It returns nil for absent/false values and for all block volumes. Invalid booleans on mount volumes return an error.

## Control Flow
The function first ignores all parameters for block volumes because block snapshots use file copy, not tar. For mount volumes it reads the parameter string, returns no options when empty, parses with `strconv.ParseBool`, and includes the tar option only for true.

## State, Persistence, And Dependencies
No state is persisted. Dependencies are `strconv`, `fmt`, and the `state.Volume` access type.

## Integration Points
`CreateSnapshot` and `CreateVolumeGroupSnapshot` call this before `createSnapshotFromVolume`, passing the resulting options into the `tar czf` command for filesystem snapshots.

## Risks
Only one snapshot parameter is recognized. Invalid values are deliberately ignored for block volumes, which may surprise users expecting validation to be independent of volume mode. Options are shell command arguments but not shell-expanded, so injection risk is low.

## Test Signals
Existing tests cover absent, false, true, invalid, mounted, and block volume cases. Additional integration tests should verify the tar command actually receives `--ignore-failed-read` for filesystem snapshots.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/options_test.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/options_test.go

## Purpose
This test file verifies snapshot option parsing for the `ignoreFailedRead` parameter across mount and block volume modes.

## Important APIs, Types, And Functions
`TestOptionsFromParameters` uses table-driven cases with `state.Volume{VolAccessType: MountAccess}` and `BlockAccess`. It calls `optionsFromParameters` and compares returned slices with `reflect.DeepEqual`.

## Control Flow
Each case supplies parameters and expected success/result. The test fails if an unexpected error appears, an expected error is absent, or the returned option slice differs.

## State, Persistence, And Dependencies
The test is pure in-memory. Dependencies are Go testing, reflect, and the state package's access type constants.

## Integration Points
It protects snapshot and group snapshot behavior because both call `optionsFromParameters` before archiving filesystem snapshots.

## Risks
It does not verify command execution or that options are forwarded into `createSnapshotFromVolume`. It also codifies that invalid `ignoreFailedRead` is ignored for block volumes.

## Test Signals
Passing tests confirm the boolean parser behavior and block-volume bypass semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/server.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/server.go

## Purpose
This file provides the nonblocking gRPC server wrapper for the hostpath CSI driver and a unary interceptor that logs CSI RPC requests and responses as JSON at high verbosity.

## Important APIs, Types, And Functions
`NewNonBlockingGRPCServer` returns a `nonBlockingGRPCServer`. Methods `Start`, `Stop`, `ForceStop`, and private `serve` manage `grpc.Server` lifecycle. `serve` listens via `endpoint.Listen`, installs `logGRPC`, registers identity, controller, node, group controller, and optional snapshot metadata servers, and serves. `logGRPC` logs requests/responses through `logGRPCJson`, with special handling for `NodePublishVolume` secrets. `logGRPCJson` marshals method, request, response, error string, and full error.

## Control Flow
`Start` launches `serve` in a goroutine and returns immediately. `serve` exits fatally on listen or serve errors. `Stop` gracefully stops the server and runs endpoint cleanup; `ForceStop` stops immediately and also cleans up. Each unary RPC passes through `logGRPC`, then the handler, then JSON logging at verbosity 5.

## State, Persistence, And Dependencies
Server state is the active `grpc.Server` and endpoint cleanup callback. Unix socket files are created and removed by the endpoint package. Dependencies include gRPC, CSI generated registration functions, klog, JSON encoding, context, endpoint, and protosanitizer.

## Integration Points
`hostPath.Run` uses this to expose the driver socket consumed by sidecars, kubelet, socat, and tests. Optional snapshot metadata registration must align with identity capability advertisement.

## Risks
`Stop` assumes `s.server` and `s.cleanup` are initialized; calling it before `serve` has assigned them could panic. `serve` uses `klog.Fatalf`, terminating the process on listen/serve failures. Verbose logging can include sensitive request content except for the special NodePublish secrets sanitization path.

## Test Signals
Tests should start on a temp Unix socket, verify all configured CSI services are registered, call identity RPCs, stop and check socket cleanup, exercise ForceStop, and validate request logging avoids secret leakage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadata.go -->
# sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadata.go

## Purpose
This file implements block-difference scanning helpers for the optional CSI SnapshotMetadata service. It compares target snapshot files with either zero blocks or a base snapshot file and returns changed block metadata in fixed or merged variable-length form.

## Important APIs, Types, And Functions
`fileBlockReader` owns optional base file, target file, current offset, block size, metadata type, and maximum result count. `newFileBlockReader` opens files and constructs the reader. Methods `seekToStartingOffset`, `Close`, and `getChangedBlockMetadata` manage file positioning/lifetime and scanning. Helpers include `openFiles`, `readFileBlock`, `blockChanged`, `createBlockMetadata`, and `extendBlock`.

## Control Flow
The reader opens the target and optional base files, seeks both to the starting offset, then repeatedly reads `blockSize` chunks until it accumulates `maxResult` changed blocks, reaches EOF, or context is canceled. Without a base file, it compares target blocks to zero blocks and reports allocated/non-zero blocks. With a base file, it compares base and target bytes. For `VARIABLE_LENGTH`, adjacent changed blocks extend the previous metadata entry instead of appending a new one. The reader advances its offset as it scans so callers can request subsequent batches.

## State, Persistence, And Dependencies
State is held in open file descriptors and the mutable offset. The code reads snapshot files but does not write them. Dependencies are Go `bytes`, `io`, `os`, context cancellation, CSI block metadata types, and klog.

## Integration Points
The optional snapshot metadata gRPC server uses these helpers to implement allocated and delta metadata streaming when `EnableSnapshotMetadata` is configured. Snapshot files are those created by controller snapshot methods.

## Risks
The buffer size is `blockSize`; very large block sizes allocate large buffers. If `blockSize` or `maxResult` validation is missing in callers, zero/negative values could cause incorrect behavior. Partial final blocks are reported with full `blockSize` metadata, which may overstate changed size at EOF. Sequential file reads under long streams can be expensive.

## Test Signals
The companion snapshot metadata tests outside this work item cover changed and allocated block metadata scenarios. Additional tests should include cancellation, partial final blocks, invalid block sizes, seek offsets, fixed versus variable-length merging, and close error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadata.go -->
