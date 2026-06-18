<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-config.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-config.yaml

Purpose: example BeeGFS CSI plugin configuration for Kustomize overlays, showing default, file-system-specific, node-specific, and node-plus-file-system-specific override shapes.

Important APIs and flow: this YAML maps to the driver's `PluginConfigFromFile` contract: top-level `config`, `fileSystemSpecificConfigs`, and `nodeSpecificConfigs`. `BeegfsConfig` fields include `grpcPort`, `connInterfaces`, `connNetFilter`, `connTcpOnlyFilter`, `connRDMAInterfaces`, and string-valued `beegfsClientConf` entries such as `connMgmtdPortTCP`, `connUseRDMA`, and `connTCPFallbackEnabled`. The runtime flow is precedence-driven: defaults apply broadly, file-system entries override by `sysMgmtdHost`, node entries override on matching nodes, and nested node file-system entries override both.

State and persistence: this file is consumed as configuration, typically rendered into a ConfigMap/Secret-backed deployment path by overlays or the operator. No Kubernetes object is declared directly.

Dependencies and integration points: depends on BeeGFS client config keys, BeeGFS 7.3+ for `connRDMAInterfaces`/TCP fallback, BeeGFS 8+ management gRPC port semantics, and deployment overlay wiring.

Risks and test signals: editing the example in place has no effect unless copied into an active overlay. Numeric and boolean BeeGFS client values must stay quoted strings. Test by deploying an overlay and checking node/controller driver logs for parsed config and successful mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-connauth.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-connauth.yaml

Purpose: example connAuth mapping file for BeeGFS file systems that require connection authentication.

Important APIs and flow: declares a YAML list of `sysMgmtdHost`, `connAuth`, and `encoding` entries, matching the driver's `ConnAuthConfig` shape. One example uses `encoding: raw`; the other uses a folded base64 secret. At runtime the deployment parser associates each secret value with a BeeGFS management host and merges it with plugin configuration outside the public CRD schema.

State and persistence: this is secret material intended to be transformed into Kubernetes Secret data or an equivalent mounted file, not persisted in the `BeegfsDriver` CR spec.

Dependencies and integration points: integrates with BeeGFS authentication, overlay secret generation, and the driver's redaction-aware `MarshalJSON` behavior for connAuth values.

Risks and test signals: raw values are sensitive, and base64 is encoding rather than encryption. Wrong `sysMgmtdHost` keys lead to unauthenticated mounts. Test with authenticated BeeGFS mounts and verify logs redact the value as `******`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-connauth.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-tlscerts.yaml

Purpose: example TLS certificate mapping for BeeGFS management endpoints that require certificate material.

Important APIs and flow: declares a list of `sysMgmtdHost` to PEM `tlsCert` entries, matching the driver's `TLSCertConfig` type. The examples cover a hostname and an IP address key. Runtime parsing associates the PEM certificate with a BeeGFS file system identity and injects it into the driver's connection configuration.

State and persistence: certificate data should be stored as a Secret or mounted config file. It is intentionally not exposed as a JSON field in `BeegfsConfig` and is redacted in log marshaling.

Dependencies and integration points: depends on BeeGFS TLS support, valid PEM formatting, overlay wiring, and exact host identity matching.

Risks and test signals: placeholder PEM blocks must be replaced; malformed certificates or host mismatches cause connection failures. Test by mounting a TLS-enabled file system and confirming logs redact certificate content.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/csi-beegfs-tlscerts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/container-resources.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/container-resources.yaml

Purpose: optional Kustomize strategic merge patch that sets CPU and memory requests/limits for BeeGFS CSI controller and node containers.

Important APIs and flow: patches the `csi-beegfs-controller` StatefulSet containers `beegfs` and `csi-provisioner`, and the `csi-beegfs-node` DaemonSet containers `beegfs`, `node-driver-registrar`, and `liveness-probe`. Values mirror documented defaults and are meant to be edited before enabling.

State and persistence: changes persist as Pod template resource fields, causing rollout on apply. No runtime state is stored by this file itself.

Dependencies and integration points: depends on Kustomize patch inclusion and exact workload/container names from the base manifests.

Risks and test signals: YAML indentation is fragile in the DaemonSet portion, and invalid resources can break scheduling or patch application. Test with `kustomize build`, Kubernetes server dry-run, and inspection of rendered Pod specs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/container-resources.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/image-pull-policy.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/image-pull-policy.yaml

Purpose: optional patch that forces the BeeGFS driver image to be pulled on every controller and node Pod start.

Important APIs and flow: strategic merge patch targets the `beegfs` container in the `csi-beegfs-controller` StatefulSet and the `csi-beegfs-node` DaemonSet, setting `imagePullPolicy: Always`.

State and persistence: persists in Pod templates and affects future image resolution behavior; existing Pods require rollout to pick up the change.

Dependencies and integration points: relies on Kustomize overlay inclusion, Kubernetes image pull semantics, and the base manifest's container names.

Risks and test signals: useful for mutable tags or development images but increases registry dependency and startup latency. Test by rendering the overlay and checking new Pods include `Always`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/image-pull-policy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/log-level.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/log-level.yaml

Purpose: optional patch that raises or changes container log verbosity through `LOG_LEVEL` environment variables.

Important APIs and flow: targets controller `beegfs`, controller `csi-provisioner`, node `beegfs`, and node `node-driver-registrar`, assigning `LOG_LEVEL` values as strings. It is meant to be referenced from an overlay when debugging.

State and persistence: persists as Pod template env settings; rollout is required to update running containers.

Dependencies and integration points: depends on the driver and sidecars honoring `LOG_LEVEL`, plus Kustomize patch matching by workload and container name.

Risks and test signals: high verbosity can expose request detail, increase log volume, and hide signal in noisy clusters. The patch is indentation-sensitive. Test with `kustomize build` and observe container logs after rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/log-level.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/versions/v1.21/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/versions/v1.21/kustomization.yaml

Purpose: version-specific Kustomize entry point for Kubernetes v1.21-compatible deployment manifests.

Important APIs and flow: declares `apiVersion: kustomize.config.k8s.io/v1beta1`, `kind: Kustomization`, and includes `../../bases` as its only base. It delegates all object content to the shared base tree.

State and persistence: no direct cluster state beyond the rendered base resources; this file selects a render path.

Dependencies and integration points: depends on Kustomize and the relative `deploy/k8s/bases` directory remaining compatible with v1.21.

Risks and test signals: the file warns not to modify because version overlays may be regenerated. Test with `kustomize build deploy/k8s/versions/v1.21` and Kubernetes v1.21 server dry-run.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/versions/v1.21/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-bc.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-bc.yaml

Purpose: OpenShift BuildConfig stack for producing a BeeGFS client image from the OpenShift `driver-toolkit`.

Important APIs and flow: creates an `ImageStream`, a `ConfigMap` containing `poststart.sh`, and a `BuildConfig`. The Dockerfile installs BeeGFS repository metadata, imports the BeeGFS GPG key, installs `beegfs-client`, `beegfs-utils`, and `beegfs-helperd`, clears `beegfs-mounts.conf`, disables helperd authentication, and adds the postStart script. The postStart script copies `beegfs-client.conf` and `beegfs-ctl` into `/plugin/client` and may install matching `kernel-devel`/`kernel-modules` before restarting the client.

State and persistence: produces the `beegfs-client:latest` ImageStreamTag and populates files later mounted through a hostPath by the DaemonSet.

Dependencies and integration points: requires OpenShift build APIs, `driver-toolkit:latest`, yum access/entitlements, BeeGFS release repos, and namespace `beegfs-csi`.

Risks and test signals: privileged system package installation and helperd auth changes are operationally sensitive. Test via OpenShift build logs, resulting image tag, and DaemonSet postStart behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-bc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-ds.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-ds.yaml

Purpose: experimental OpenShift DaemonSet deployment that runs a BeeGFS client service on nodes and exposes client utilities to the CSI driver.

Important APIs and flow: defines a `ServiceAccount`, Role/RoleBinding for the privileged SCC, and a `DaemonSet` using `image-registry.openshift-image-registry.svc:5000/beegfs-csi/beegfs-client:latest`. The container runs `/sbin/init`, executes `/usr/local/sbin/poststart.sh`, stops BeeGFS services on preStop, exposes host port 8006, and mounts `/var/lib/kubelet/plugins/beegfs.csi.netapp.com/client` into `/plugin/client`.

State and persistence: writes shared client config and binaries into the hostPath for CSI node components. Service processes run in a privileged, host-networked container.

Dependencies and integration points: depends on the BuildConfig image, OpenShift SCCs, systemd-capable image, host networking, and kubelet plugin path conventions.

Risks and test signals: privileged host networking and hostPath writes increase blast radius. Test DaemonSet readiness, postStart output, hostPath contents, and CSI mounts on RHCOS/RHEL nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-ds.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/all-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/all-app.yaml

Purpose: combined demo Pod that mounts dynamic, generic ephemeral, static read/write, and static read-only BeeGFS volumes at once.

Important APIs and flow: a single Alpine Pod mounts four volumes at `/mnt/dyn`, `/mnt/ge`, `/mnt/static`, and `/mnt/static-ro`. Its command creates UID-named marker files in writable mounts and sleeps for seven days. The generic ephemeral volume embeds a PVC template using `csi-beegfs-ge-sc`; the others reference named PVCs.

State and persistence: writes marker files into BeeGFS-backed volumes; read-only mount should reject writes. Pod state is ephemeral, storage state depends on backing PV/PVC reclaim behavior.

Dependencies and integration points: integrates all example StorageClasses, PVCs, and PVs; depends on the CSI provisioner, node plugin, and BeeGFS management host replacement.

Risks and test signals: `localhost` and `name` placeholders must be replaced. Test with `kubectl exec` listing/touching each mount and verifying read-only failure.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/all-app.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-pvc.yaml

Purpose: demo PersistentVolumeClaim for dynamically provisioned BeeGFS storage in the combined example.

Important APIs and flow: requests `ReadWriteMany` access and `100Gi` storage from `storageClassName: csi-beegfs-dyn-sc`. Kubernetes binds it through the BeeGFS CSI provisioner.

State and persistence: persists as a PVC and, after provisioning, a dynamically created PV and BeeGFS directory under the StorageClass base path.

Dependencies and integration points: depends on `dyn-sc.yaml`, the CSI external provisioner, and BeeGFS management connectivity.

Risks and test signals: requested capacity is mostly a Kubernetes binding signal for BeeGFS and not an enforced quota in this manifest. Test PVC binding, PV creation, and successful Pod mount.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-sc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-sc.yaml

Purpose: StorageClass for dynamically provisioning BeeGFS volumes in the combined examples.

Important APIs and flow: `provisioner: beegfs.csi.netapp.com` passes `sysMgmtdHost` and `volDirBasePath` parameters to the CSI driver. Optional stripe pattern and permissions parameters are documented as string values. `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and `allowVolumeExpansion: true` control Kubernetes lifecycle.

State and persistence: creates/deletes BeeGFS directories through dynamic provisioning and supports expansion operations through the CSI driver.

Dependencies and integration points: depends on an actual BeeGFS management host, unique cluster-specific base path, and CSI provisioner sidecar.

Risks and test signals: leaving `localhost` or `k8s/name/dyn` unchanged can collide or fail. Test by PVC bind, directory creation, deletion cleanup, and expansion.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/dyn-sc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/ge-sc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/ge-sc.yaml

Purpose: StorageClass for Kubernetes generic ephemeral BeeGFS volumes in the combined examples.

Important APIs and flow: mirrors the dynamic StorageClass but uses `volDirBasePath: k8s/name/ge` and `allowVolumeExpansion: false`, appropriate for ephemeral claim templates. The provisioner is `beegfs.csi.netapp.com`.

State and persistence: creates BeeGFS-backed volumes for Pod-scoped PVCs and deletes them with the owning Pod/PVC lifecycle under `reclaimPolicy: Delete`.

Dependencies and integration points: used by `all-app.yaml` embedded `volumeClaimTemplate`, CSI provisioner, and BeeGFS management service.

Risks and test signals: generic ephemeral support depends on the Kubernetes version and feature availability. Unique base paths avoid cross-cluster collisions. Test Pod creation and cleanup of generated PVC/PV/volume directory.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/ge-sc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pv.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pv.yaml

Purpose: statically provisioned read/write BeeGFS PersistentVolume for the combined examples.

Important APIs and flow: declares a `PersistentVolume` with `ReadWriteMany`, `100Gi`, `Retain`, and a CSI source using driver `beegfs.csi.netapp.com`. The `volumeHandle` encodes BeeGFS management host and path as `beegfs://localhost/k8s/all/static`.

State and persistence: Kubernetes retains the PV and BeeGFS directory after PVC deletion. The driver does not create the target directory for static volumes.

Dependencies and integration points: binds to `static-pvc.yaml` by `volumeName`; depends on pre-existing BeeGFS directory and a valid management host.

Risks and test signals: stale or missing directories cause mount failure. Test PV/PVC binding and Pod write/read of marker files.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pvc.yaml

Purpose: claim that binds the combined example Pod to the static read/write BeeGFS PV.

Important APIs and flow: requests `ReadWriteMany` and `100Gi`, sets `storageClassName: ""` to avoid dynamic provisioning, and pins `volumeName: csi-beegfs-static-pv`.

State and persistence: PVC state binds to the named PV; storage lifecycle is controlled by the PV's `Retain` policy and external BeeGFS directory.

Dependencies and integration points: requires `static-pv.yaml` to exist and match capacity/access mode.

Risks and test signals: mismatched capacity/access modes or missing `storageClassName: ""` can prevent binding or trigger unwanted provisioning. Test PVC phase `Bound` and Pod mount.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pv.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pv.yaml

Purpose: statically provisioned read-only BeeGFS PersistentVolume for the combined example.

Important APIs and flow: declares `ReadOnlyMany`, placeholder capacity `5Gi`, `Retain`, and CSI `volumeHandle: beegfs://localhost/k8s/all/static-ro`. Comments clarify capacity is required for binding but not meaningful for read-only static usage.

State and persistence: does not create or delete the BeeGFS directory; Kubernetes retains the PV.

Dependencies and integration points: binds to `static-ro-pvc.yaml` and is mounted read-only by the Pod claim reference.

Risks and test signals: accessModes alone do not enforce read-only at mount time; the Pod volume reference must set `readOnly: true`. Test by attempting a write and expecting failure.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pvc.yaml

Purpose: PVC that binds to the combined example's static read-only BeeGFS PV.

Important APIs and flow: requests `ReadOnlyMany`, `5Gi`, disables dynamic provisioning with `storageClassName: ""`, and pins `volumeName: csi-beegfs-static-ro-pv`.

State and persistence: binding state is stored in Kubernetes; underlying BeeGFS content is externally managed and retained.

Dependencies and integration points: requires the named static read-only PV and a Pod volume reference with `readOnly: true` for enforcement.

Risks and test signals: the manifest comment highlights that capacity is required by Kubernetes even though semantically arbitrary. Test PVC binding and read-only Pod behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-ro-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-app.yaml

Purpose: standalone demo Pod for a dynamically provisioned BeeGFS volume.

Important APIs and flow: Alpine Pod mounts PVC `csi-beegfs-dyn-pvc` at `/mnt/dyn`, writes a marker file named with `metadata.uid`, and sleeps for seven days. Optional OpenShift nodeSelector comments guide scheduling onto RHEL nodes when the driver is not installed on RHCOS.

State and persistence: marker file persists in the dynamically provisioned BeeGFS directory until reclaim cleanup. Pod runtime is transient.

Dependencies and integration points: depends on `dyn-pvc.yaml`, `dyn-sc.yaml`, the CSI node plugin, and BeeGFS client availability on the selected node.

Risks and test signals: placeholder StorageClass parameters must be fixed. Test with `kubectl exec csi-beegfs-dyn-app -- ls /mnt/dyn` and PVC/PV events.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-app.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-pvc.yaml

Purpose: standalone dynamic BeeGFS PVC.

Important APIs and flow: requests `ReadWriteMany`, `100Gi`, and `storageClassName: csi-beegfs-dyn-sc`, causing the external CSI provisioner to call `CreateVolume`.

State and persistence: Kubernetes stores PVC/PV state; BeeGFS stores the provisioned directory under the StorageClass base path.

Dependencies and integration points: requires the dynamic StorageClass and a running BeeGFS CSI controller.

Risks and test signals: capacity is a Kubernetes request and may not reflect real BeeGFS quota. Test `Bound` phase, PV CSI volume handle, and Pod write.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-sc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-sc.yaml

Purpose: standalone dynamic BeeGFS StorageClass.

Important APIs and flow: declares BeeGFS CSI provisioner with `sysMgmtdHost`, `volDirBasePath`, optional stripe/permission keys, `Delete` reclaim policy, immediate binding, and volume expansion enabled.

State and persistence: controls dynamic directory lifecycle and expansion requests for PVCs using the class.

Dependencies and integration points: integrates with Kubernetes storage APIs, BeeGFS management daemon, and driver parameter parsing.

Risks and test signals: all StorageClass parameters are strings; unquoted numeric optional values can be rejected or misparsed. Test provision/delete/expand flows and controller logs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-sc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-app.yaml

Purpose: standalone demo Pod for Kubernetes generic ephemeral BeeGFS volumes.

Important APIs and flow: Alpine Pod defines an `ephemeral.volumeClaimTemplate` requesting `ReadWriteMany`, `100Gi`, and `storageClassName: csi-beegfs-ge-sc`. The container writes a UID marker under `/mnt/ge` and sleeps.

State and persistence: Kubernetes creates an owner-linked PVC/PV for the Pod; BeeGFS backing storage should be deleted with the ephemeral volume lifecycle.

Dependencies and integration points: depends on generic ephemeral volume support, the `ge-sc.yaml` StorageClass, CSI provisioner, and node driver.

Risks and test signals: cleanup correctness is the key behavior. Test by creating/deleting the Pod and confirming generated PVC/PV and BeeGFS directory lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-app.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-sc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-sc.yaml

Purpose: StorageClass for standalone generic ephemeral BeeGFS demo volumes.

Important APIs and flow: uses `beegfs.csi.netapp.com`, `sysMgmtdHost`, `volDirBasePath: k8s/name/ge`, optional string-valued stripe/permission parameters, `Delete` reclaim policy, immediate binding, and expansion disabled.

State and persistence: creates Pod-scoped storage through generated PVCs and deletes it with reclaim lifecycle.

Dependencies and integration points: consumed by `ge-app.yaml`; depends on CSI provisioner and BeeGFS management path uniqueness.

Risks and test signals: generic ephemeral volumes can leave storage behind if finalizers or deletion fail. Test cleanup after Pod removal and watch provisioner logs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-sc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-app.yaml

Purpose: standalone Pod that verifies read-only mounting of a static BeeGFS volume.

Important APIs and flow: Alpine Pod mounts `csi-beegfs-static-ro-pvc` at `/mnt/static-ro` with `readOnly: true` and sleeps. Comments describe using `touch` to verify write failure.

State and persistence: Pod has no write path by design; underlying BeeGFS data is external and retained.

Dependencies and integration points: depends on static read-only PV/PVC manifests and the CSI node driver enforcing read-only mount semantics.

Risks and test signals: PV/PVC `ReadOnlyMany` does not itself enforce read-only access; the Pod claim's `readOnly: true` is essential. Test with a failed write attempt.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-app.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pv.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pv.yaml

Purpose: standalone static read-only BeeGFS PV.

Important APIs and flow: declares `ReadOnlyMany`, required capacity `5Gi`, `Retain`, driver `beegfs.csi.netapp.com`, and `volumeHandle: beegfs://localhost/k8s/all/static-ro`.

State and persistence: uses an existing BeeGFS directory and does not delete it through Kubernetes.

Dependencies and integration points: binds to `static-ro-pvc.yaml`; mount semantics are completed by the Pod's `readOnly: true`.

Risks and test signals: wrong management host/path or missing directory prevents staging. Test bind, mount, read, and write rejection.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pvc.yaml

Purpose: standalone PVC for the static read-only BeeGFS example.

Important APIs and flow: requests `ReadOnlyMany`, `5Gi`, sets `storageClassName: ""`, and binds to `csi-beegfs-static-ro-pv`.

State and persistence: stores only binding intent; BeeGFS content remains externally managed.

Dependencies and integration points: requires the matching PV and a consuming Pod that mounts read-only.

Risks and test signals: Kubernetes requires the storage request even though the comment notes it is otherwise meaningless for read-only static volumes. Test `Bound` status and read-only mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-app.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-app.yaml

Purpose: standalone Pod demonstrating read/write access to a statically provisioned BeeGFS directory.

Important APIs and flow: Alpine Pod mounts `csi-beegfs-static-pvc` at `/mnt/static`, writes a marker file including the Pod UID and a cluster name placeholder, then sleeps. Optional OpenShift nodeSelector comments address RHEL/RHCOS placement.

State and persistence: marker file persists in the pre-existing BeeGFS directory after Pod deletion. Kubernetes does not create/delete the static target path.

Dependencies and integration points: depends on `static-pv.yaml`, `static-pvc.yaml`, node plugin mount support, and pre-created BeeGFS path.

Risks and test signals: cluster-name placeholder should be customized to avoid collisions. Test by exec listing `/mnt/static` and checking PV/PVC events.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-app.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pv.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pv.yaml

Purpose: standalone static read/write BeeGFS PV.

Important APIs and flow: declares `ReadWriteMany`, `100Gi`, `Retain`, driver `beegfs.csi.netapp.com`, and `volumeHandle: beegfs://localhost/k8s/all/static`.

State and persistence: points at an existing BeeGFS directory; Kubernetes retains the PV and does not create the directory.

Dependencies and integration points: binds to `static-pvc.yaml`; depends on management host replacement and BeeGFS path existence.

Risks and test signals: static path mismatch causes mount failures, while `Retain` can leave stale claims/data for later runs. Test bind and Pod write/read.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pvc.yaml

Purpose: standalone PVC binding to the static read/write BeeGFS PV.

Important APIs and flow: requests `ReadWriteMany`, `100Gi`, disables dynamic provisioning with an empty StorageClass, and pins `volumeName: csi-beegfs-static-pv`.

State and persistence: holds Kubernetes binding state; underlying BeeGFS storage remains external and retained.

Dependencies and integration points: requires the named PV to exist with compatible access modes and capacity.

Risks and test signals: missing empty `storageClassName` could select a default StorageClass unexpectedly. Test PVC `Bound` phase and Pod mount.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static/static-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/dynamic-demo-alias.sh -->
# sources/control-plane/beegfs-csi-driver/hack/dynamic-demo-alias.sh

Purpose: sourced shell helper defining `csc` aliases for manual CSI RPC testing against a locally running BeeGFS CSI driver.

Important APIs and flow: initializes `SYS_MGMTD_HOST`, creates fake kubelet staging/publish directories under `/tmp`, and aliases controller/node calls such as `createvolume`, `nodestagevolume`, `nodepublishvolume`, `nodeunpublishvolume`, `nodeunstagevolume`, `deletevolume`, and capability validation. It exercises volume parameters for stripe patterns and permissions.

State and persistence: creates local `/tmp/kubelet` and `/tmp/csdatadir` paths and may create/delete BeeGFS directories through CSI calls.

Dependencies and integration points: requires `csc`, sudo access, a driver socket at `/tmp/csi.sock`, a running driver, and a BeeGFS management host.

Risks and test signals: aliases capture `SYS_MGMTD_HOST` at source time and use sudo/local mounts. Test by running the command sequence and inspecting CSI responses and mount paths.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/dynamic-demo-alias.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/many-volumes.sh -->
# sources/control-plane/beegfs-csi-driver/hack/many-volumes.sh

Purpose: manual stress-manifest generator for flooding Kubernetes and the BeeGFS CSI controller with many dynamic PVCs.

Important APIs and flow: defines `NUM_PVCS=100` and `SYS_MGMTD_HOST`, writes `many-volumes.yaml` with one StorageClass and a loop-generated series of PVCs named `many-volumes-pvc-N`. The StorageClass uses `permissions/mode: "1644"` to force a mount and slow the driver.

State and persistence: writes a local generated YAML file and, when applied, creates many PVC/PV objects and BeeGFS directories under `k8s/many-volumes`.

Dependencies and integration points: depends on kubectl apply/delete by the operator, BeeGFS CSI dynamic provisioning, and a reachable management host.

Risks and test signals: no cleanup trap and hard-coded output name can overwrite prior manifests. Test by applying/deleting the manifest and watching controller logs for concurrency behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/many-volumes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/orphan-mounts-stress.sh -->
# sources/control-plane/beegfs-csi-driver/hack/orphan-mounts-stress.sh

Purpose: repeated e2e stress runner for detecting orphaned BeeGFS mounts after Kubernetes volume lifecycle churn.

Important APIs and flow: creates a temp output directory, logs all script output, cleans old test namespaces, then runs 20 iterations of nondisruptive and disruptive Ginkgo e2e suites. On failure, `fail()` captures controller and node logs since script start and exits. On success, it greps controller logs for orphan-mount-related messages and removes the temp directory.

State and persistence: creates/deletes test namespaces and temporary logs under `/tmp/e2e.*`; may leave the output directory on failure for inspection.

Dependencies and integration points: requires `KUBECONFIG`, deployed driver, `ginkgo`, `kubectl`, root SSH user env, and e2e tests.

Risks and test signals: destructive namespace cleanup uses name patterns; parallel/disruptive tests can affect clusters. Test signal is either captured failure logs or clean 20-iteration completion.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/orphan-mounts-stress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/Dockerfile -->
# sources/control-plane/beegfs-csi-driver/operator/Dockerfile

Purpose: packages the prebuilt BeeGFS CSI operator manager binary into a minimal distroless container.

Important APIs and flow: starts from `gcr.io/distroless/static:nonroot`, sets OCI labels, accepts `TARGETARCH`, copies `bin/manager$TARGETARCH` to `/manager`, runs as UID/GID 65532, and uses `/manager` as entrypoint. Build comments explain that binaries are built externally because the operator is inside the larger project module.

State and persistence: image contains only the manager binary and metadata; no writable state is declared.

Dependencies and integration points: depends on `make build` producing architecture-suffixed binaries and on buildx passing `TARGETARCH` for multi-arch builds.

Risks and test signals: missing `bin/manager$TARGETARCH` breaks image build; distroless limits debugging. Test with `make build`, `docker build`, and running manager health probes in cluster.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/Makefile -->
# sources/control-plane/beegfs-csi-driver/operator/Makefile

Purpose: development, build, deployment, bundle, and catalog automation for the BeeGFS CSI operator.

Important APIs and flow: key targets include `manifests`, `generate`, `fmt`, `vet`, `test`, `build`, `run`, `docker-build`, `install`, `deploy`, `bundle`, `bundle-build`, `catalog-build`, and `docker-buildx`. The build loop compiles `main.go` for tuples in `BUILD_PLATFORMS`; `test` uses envtest assets; `bundle` regenerates OLM manifests and applies a custom OpenShift minimum version script; `docker-buildx` is intentionally disabled.

State and persistence: writes binaries and tools under `bin`, CRD/bundle manifests under config/bundle paths, local cover profiles, and may mutate Kustomize image references.

Dependencies and integration points: uses Go, controller-gen, kustomize, setup-envtest, operator-sdk, opm, Docker, kubectl, and GitHub-hosted tool downloads.

Risks and test signals: network/tool version drift affects reproducibility; `docker-buildx` exits intentionally. Test with `make test`, `make bundle`, and operator-sdk bundle validation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/beegfsdriver_types.go -->
# sources/control-plane/beegfs-csi-driver/operator/api/v1/beegfsdriver_types.go

Purpose: source of truth for the `beegfs.csi.netapp.com/v1` operator API, CRD schema annotations, status conditions, plugin config structures, and secret redaction behavior.

Important APIs and flow: defines `BeegfsDriverSpec`, `BeegfsDriverStatus`, `BeegfsDriver`, `BeegfsDriverList`, image/resource override types, `BeegfsConfig`, `PluginConfig`, `PluginConfigFromFile`, `ConnAuthConfig`, and `TLSCertConfig`. `init()` registers CR types. `NewBeegfsConfig` initializes the client-conf map. Custom `MarshalJSON` methods redact `ConnAuth` and `TLSCert` when logs encode config structs.

State and persistence: CR spec persists image/resource overrides, `logLevel`, node affinities, and non-secret plugin config. Status persists Kubernetes conditions for controller/node readiness. ConnAuth and TLS cert fields are deliberately not unmarshaled from CR JSON.

Dependencies and integration points: imports Kubernetes core/v1 and metav1 types, controller-gen/operator-sdk annotations, and JSON encoding.

Risks and test signals: schema comments feed CSV/GUI output, so wording changes are user visible. Test with `make generate`, `make manifests`, API serialization tests, and log redaction checks.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/beegfsdriver_types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/groupversion_info.go -->
# sources/control-plane/beegfs-csi-driver/operator/api/v1/groupversion_info.go

Purpose: registers the BeeGFS operator API group/version for Kubernetes runtime schemes.

Important APIs and flow: declares kubebuilder package annotations, `GroupVersion = schema.GroupVersion{Group: "beegfs.csi.netapp.com", Version: "v1"}`, `SchemeBuilder`, and `AddToScheme`.

State and persistence: no runtime state beyond scheme registration data compiled into the manager binary.

Dependencies and integration points: imports `k8s.io/apimachinery/pkg/runtime/schema` and controller-runtime `scheme`. Used by managers, clients, tests, and generated code to recognize `BeegfsDriver` objects.

Risks and test signals: changing group or version is a breaking API/storage change and must match CRDs, CSVs, RBAC, and manifests. Test by compiling, running envtest, and verifying CRD group/version alignment.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/groupversion_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/zz_generated.deepcopy.go -->
# sources/control-plane/beegfs-csi-driver/operator/api/v1/zz_generated.deepcopy.go

Purpose: controller-gen generated deep-copy implementations required for Kubernetes API machinery.

Important APIs and flow: implements `DeepCopyInto`, `DeepCopy`, and `DeepCopyObject` for CR root/list types, plus deep copies for nested config, image override, resource override, connAuth, and TLS structs. It allocates fresh slices/maps for connection filters, `beegfsClientConf`, node lists, file-system config arrays, conditions, and plugin config arrays, and delegates to Kubernetes deep-copy methods for `ObjectMeta`, `ResourceRequirements`, `NodeAffinity`, and `metav1.Condition`.

State and persistence: prevents shared mutable state when cached objects are copied by controllers or clients; does not persist data itself.

Dependencies and integration points: depends on controller-gen output and Kubernetes runtime interfaces.

Risks and test signals: manual edits will be overwritten and can introduce cache mutation bugs. Test with `make generate` producing no diff and `go test` controller/API paths.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/api/v1/zz_generated.deepcopy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-controller-manager-metrics-service_v1_service.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-controller-manager-metrics-service_v1_service.yaml

Purpose: OLM bundle Service exposing the operator controller manager metrics endpoint.

Important APIs and flow: creates a v1 `Service` named `beegfs-csi-driver-operator-controller-manager-metrics-service`, selects Pods with `control-plane: controller-manager`, and forwards TCP port 8443 to targetPort 8443.

State and persistence: persists a cluster Service object; no application state is stored.

Dependencies and integration points: integrates with the CSV deployment that runs manager with `--metrics-bind-address=0.0.0.0:8443`, and with metrics RBAC/auth manifests.

Risks and test signals: selector or port mismatch breaks metrics scraping. Test by checking endpoints and authenticated metrics access after OLM install.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-controller-manager-metrics-service_v1_service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-manager-config_v1_configmap.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-manager-config_v1_configmap.yaml

Purpose: bundled controller-runtime manager configuration for the BeeGFS CSI operator.

Important APIs and flow: ConfigMap `beegfs-csi-driver-operator-manager-config` stores `controller_manager_config.yaml` with health probe bind address `:8081`, metrics bind address `127.0.0.1:8080`, webhook port `9443`, and leader election resource name `0d697945.csi.netapp.com`.

State and persistence: persists static manager configuration in Kubernetes. In this bundle, the CSV deployment also supplies explicit manager args, so consumers must confirm whether the binary reads this ConfigMap in their install path.

Dependencies and integration points: generated by kubebuilder/operator-sdk config; aligns with controller-runtime config API.

Risks and test signals: mismatch between ConfigMap and deployment args can confuse operators. Test by inspecting manager args/logs and health/metrics listeners.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-manager-config_v1_configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-metrics-reader_rbac.authorization.k8s.io_v1_clusterrole.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-metrics-reader_rbac.authorization.k8s.io_v1_clusterrole.yaml

Purpose: RBAC role permitting read access to the operator metrics endpoint.

Important APIs and flow: defines ClusterRole `beegfs-csi-driver-operator-metrics-reader` with non-resource URL `/metrics` and verb `get`.

State and persistence: persists RBAC policy only; does not bind subjects by itself.

Dependencies and integration points: integrates with metrics Service and auth proxy/metrics access conventions generated by operator-sdk.

Risks and test signals: without a binding, no subject gains this permission; over-broad bindings could expose metrics. Test with Kubernetes auth checks and scorecard/OLM validation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-metrics-reader_rbac.authorization.k8s.io_v1_clusterrole.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator.clusterserviceversion.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator.clusterserviceversion.yaml

Purpose: OLM ClusterServiceVersion for installing and describing BeeGFS CSI driver operator v1.8.0.

Important APIs and flow: declares alm example `BeegfsDriver` named `csi-beegfs-cr`, owned CRD descriptors, long-form user documentation, install strategy, RBAC, deployment, install modes, links, maintainers, minimum Kubernetes version, and image `ghcr.io/thinkparq/beegfs-csi-driver-operator:v1.8.0`. The manager runs `/manager --leader-elect --metrics-bind-address=0.0.0.0:8443`, receives `BEEGFS_CSI_DRIVER_NAMESPACE` from its namespace, and exposes health/readiness probes on 8081.

State and persistence: OLM persists the CSV and creates operator Deployment, ServiceAccount, permissions, and watches the owned CRD. The operator then creates driver resources such as ConfigMaps, Secrets, StatefulSets, DaemonSets, PVs, and CSI objects.

Dependencies and integration points: depends on OLM, own-namespace install mode, privileged SCC use, Kubernetes storage APIs, and CRD schema alignment.

Risks and test signals: RBAC is broad because the operator manages CSI storage resources; OpenShift RHCOS caveats are documented. Test with operator-sdk bundle validation, scorecard, CSV phase `Succeeded`, and a sample `BeegfsDriver`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator.clusterserviceversion.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs.csi.netapp.com_beegfsdrivers.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs.csi.netapp.com_beegfsdrivers.yaml

Purpose: generated CustomResourceDefinition for namespaced `BeegfsDriver` objects.

Important APIs and flow: defines group `beegfs.csi.netapp.com`, version `v1`, kind/list/plural names, served/storage status, and status subresource. The OpenAPI schema exposes image overrides, resource overrides, `logLevel` with min 0/max 5, controller/node `NodeAffinity`, plugin config hierarchy, string-only `beegfsClientConf`, required `sysMgmtdHost` in file-system configs, required `nodeList` in node configs, and `status.conditions`. Metadata name is constrained to `^csi-beegfs-cr$`, enforcing a singleton resource name.

State and persistence: stores desired operator state in CR specs and observed readiness in status conditions. Secret auth/cert values are absent from the public CRD schema.

Dependencies and integration points: generated from Go API types by controller-gen v0.16.5 and consumed by the CSV/operator manager.

Risks and test signals: schema drift from Go types breaks OLM/API behavior. Test with `make manifests`, CRD apply, schema validation failures for invalid logLevel/name, and status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs.csi.netapp.com_beegfsdrivers.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/metadata/annotations.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/metadata/annotations.yaml

Purpose: bundle metadata annotations consumed by OLM/catalog tooling.

Important APIs and flow: declares bundle media type, manifests and metadata directories, package name `beegfs-csi-driver-operator`, channel/default channel `stable`, operator-sdk metrics metadata, scorecard test metadata, and minimum OpenShift version `v4.11`.

State and persistence: packaged into bundle image metadata; no cluster object by itself.

Dependencies and integration points: read by operator registry, bundle validation, scorecard discovery, and Red Hat/OpenShift catalog tooling.

Risks and test signals: incorrect package/channel annotations make upgrades or catalog indexing fail. Test with `operator-sdk bundle validate` and `opm index add`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/metadata/annotations.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/tests/scorecard/config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/tests/scorecard/config.yaml

Purpose: Operator SDK scorecard configuration for validating the BeeGFS CSI operator bundle.

Important APIs and flow: defines scorecard v1alpha3 `Configuration` with one parallel stage running `basic-check-spec`, `olm-bundle-validation`, `olm-crds-have-validation`, `olm-crds-have-resources`, `olm-spec-descriptors`, and `olm-status-descriptors` using `quay.io/operator-framework/scorecard-test:v1.19.1`.

State and persistence: no runtime state beyond test execution artifacts produced by scorecard.

Dependencies and integration points: referenced by bundle annotations under `tests/scorecard/` and run by operator-sdk scorecard tooling.

Risks and test signals: image/tool version is old relative to current generated manifests and may diverge from installed operator-sdk. Test by running scorecard and checking all basic/OLM suites pass.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/tests/scorecard/config.yaml -->
