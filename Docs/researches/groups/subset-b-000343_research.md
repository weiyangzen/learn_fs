# subset-b-000343 research

Grouped research report for the exact subset-b-000343 source list. Each file section preserves the source path in its title and is wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/vac-high-performance.yaml -->
## sources/control-plane/ceph-csi/examples/nvmeof/vac-high-performance.yaml

Purpose: Kubernetes `VolumeAttributesClass` example for the Ceph CSI NVMe-oF driver, named `high-performance`, showing how to apply high read/write IOPS and bandwidth limits through `storage.k8s.io/v1`.

Important API surface: `kind: VolumeAttributesClass`, `driverName: nvmeof.csi.ceph.com`, and string parameters `rwIosPerSecond` and `rwMbytesPerSecond`. The comment notes `v1beta1` for Kubernetes 1.33 compatibility, while the manifest uses `v1`.

Control flow and integration: The object is consumed by Kubernetes external-provisioner/controller modify flows and passed to the NVMe-oF Ceph CSI driver as mutable volume attributes. No local state is persisted by the manifest; persistence is the Kubernetes API object plus any driver-side QoS application to the NVMe-oF backend.

Dependencies and risks: Requires a cluster version exposing `VolumeAttributesClass` and a Ceph CSI NVMe-oF deployment that recognizes these keys. Values are strings and unit names are driver-specific, so typo or unit mismatch silently risks ineffective QoS. Test signal is example-level only: apply the manifest, bind it to a volume, then verify resulting NVMe-oF target limits.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/vac-high-performance.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/vac-unlimited.yaml -->
## sources/control-plane/ceph-csi/examples/nvmeof/vac-unlimited.yaml

Purpose: Kubernetes `VolumeAttributesClass` example for the NVMe-oF Ceph CSI driver that expresses unlimited QoS by setting multiple limit parameters to `"0"`.

Important API surface: `VolumeAttributesClass` named `unlimited`, `driverName: nvmeof.csi.ceph.com`, and parameters `rwIosPerSecond`, `rwMbytesPerSecond`, `rmBbytesPerSecond`, and `wmBbytesPerSecond`. The file documents the zero-as-unlimited convention.

Control flow and state: Kubernetes stores this as an API object and the CSI side interprets the class during volume attribute modification. There is no script or runtime loop in the file; it is declarative input to the driver and storage API.

Dependencies and risks: Depends on VAC support in Kubernetes and matching parameter parsing in the NVMe-oF driver. The `rmBbytesPerSecond`/`wmBbytesPerSecond` names look unusual compared with read/write abbreviations, so tests should verify the driver accepts them exactly. Test signal is practical: apply, attach to a volume, and inspect target-side throttling absence.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/nvmeof/vac-unlimited.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/block-pod-clone.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/block-pod-clone.yaml

Purpose: Example Pod consuming a cloned RBD block PVC as a raw block device.

Important API surface: A `v1/Pod` named `pod-with-block-volume-clone`, CentOS container, `volumeDevices` entry `devicePath: /dev/xvda`, and a `persistentVolumeClaim` reference to `block-pvc-clone`.

Control flow and integration: Kubernetes schedules the Pod, kubelet calls CSI node stage/publish for the PVC, and the RBD node plugin maps the cloned image as a block device instead of mounting a filesystem. State comes from the PVC/PV binding and mapped device on the node.

Dependencies, risks, tests: Requires `pvc-block-clone.yaml`, the original raw block source PVC, the RBD StorageClass, and node plugin privileges. Device path conflicts or missing `volumeMode: Block` in the PVC are primary risks. Test by creating the source PVC, clone PVC, then verifying `/dev/xvda` exists in the container.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/block-pod-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/exec-bash.sh -->
## sources/control-plane/ceph-csi/examples/rbd/exec-bash.sh

Purpose: Helper script to open an interactive shell in the first `csi-rbdplugin` Pod.

Important functions and flow: Sets `CONTAINER_NAME=csi-rbdplugin`, queries `kubectl get pods -l app=$CONTAINER_NAME -o=name | head -n 1`, polls `.status.phase` with `get_pod_status`, waits until `Running`, then runs `kubectl exec -it "${POD_NAME#*/}" -c "$CONTAINER_NAME" bash`.

State and dependencies: It persists no local state and depends entirely on current Kubernetes API state, the `kubectl` context, and the `app=csi-rbdplugin` label. It assumes at least one matching Pod exists and that the container includes `bash`.

Risks and test signals: If no Pod exists, the status polling can behave poorly because `POD_NAME` is empty. It does not handle `CrashLoopBackOff`, multiple namespaces, or shells without bash. Test by running after `plugin-deploy.sh` and confirming interactive access to the intended container.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/exec-bash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/groupsnapshot.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/groupsnapshot.yaml

Purpose: Example `VolumeGroupSnapshot` selecting RBD PVCs by label for group snapshot creation.

Important API surface: `apiVersion: groupsnapshot.storage.k8s.io/v1beta2`, `kind: VolumeGroupSnapshot`, metadata name `rbd-groupsnapshot`, selector `matchLabels.group: test`, and `volumeGroupSnapshotClassName: csi-rbdplugin-groupsnapclass`.

Control flow and state: The group snapshot controller resolves PVCs with the label, invokes the RBD CSI group snapshot capability, and persists snapshot state in Kubernetes `VolumeGroupSnapshot` and backend Ceph snapshot/group metadata. The selected PVC label is provided by `pvc.yaml`.

Dependencies and risks: Requires the group snapshot CRDs/controller, RBD group snapshot support, and `groupsnapshotclass.yaml`. Selector-based inclusion risks accidental snapshots of any PVC labeled `group=test`. Test by applying labeled PVCs and verifying the group snapshot reports ready and contains expected members.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/groupsnapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/groupsnapshotclass.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/groupsnapshotclass.yaml

Purpose: Example `VolumeGroupSnapshotClass` for the RBD CSI driver.

Important API surface: `apiVersion: groupsnapshot.storage.k8s.io/v1beta2`, `driver: rbd.csi.ceph.com`, required parameters `clusterID` and `pool`, optional `volumeGroupNamePrefix`, group snapshotter secret name/namespace, and `deletionPolicy: Delete`.

Control flow and state: The Kubernetes group snapshotter passes class parameters and secrets to the RBD CSI controller. Ceph CSI uses the cluster ID to resolve monitors/config and pool for backend group snapshot bookkeeping. Kubernetes stores class state; Ceph stores backend group/snapshot objects.

Dependencies and risks: Requires the `csi-rbd-secret`, valid `ceph-csi-config`, matching pool, and group snapshot sidecars/CRDs. Placeholder values must be replaced. `Delete` deletion policy can remove backend snapshots with the Kubernetes object. Test by creating a `VolumeGroupSnapshot` and checking backend cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/groupsnapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/logs.sh -->
## sources/control-plane/ceph-csi/examples/rbd/logs.sh

Purpose: Helper script to stream logs from the first running RBD node plugin Pod.

Important functions and flow: Uses the same `CONTAINER_NAME` and Pod label lookup as `exec-bash.sh`, defines `get_pod_status`, waits for `Running`, then executes `kubectl logs -f "$POD_NAME" -c "$CONTAINER_NAME"`.

State and integration: It reads Kubernetes Pod state and streams container logs; it persists nothing. It integrates with example deployments using the `app=csi-rbdplugin` label and the default `kubectl` namespace/context.

Risks and tests: Empty Pod matches, non-default namespaces, multiple daemonset Pods, or Pods stuck outside `Running` can make the script hang or target the wrong Pod. Test by deploying the plugin and confirming logs follow the intended node plugin container.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/logs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/plugin-deploy.sh -->
## sources/control-plane/ceph-csi/examples/rbd/plugin-deploy.sh

Purpose: Convenience deployment script for RBD Ceph CSI Kubernetes manifests and Vault KMS sample resources.

Important flow: Accepts optional `deployment_base` then `kms_base`, defaults to `../../deploy/rbd/kubernetes` and `../kms/vault`, `pushd`s into each, and runs `kubectl create -f` for ordered object arrays. RBD objects include RBAC, config map, provisioner, node plugin, and CSIDriver; KMS objects include Vault, token review RBAC, and KMS config.

State and integration: It creates Kubernetes API resources and relies on manifest ordering for dependencies. It does not persist local state or use idempotent apply.

Risks and test signals: `kubectl create` fails on existing resources and no rollback is attempted after partial failure. `shift` is called even if no args are supplied, which is benign in bash without `set -e` but brittle. Test by running against a clean namespace and verifying pods, RBAC, config, and KMS objects become ready.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/plugin-deploy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/plugin-teardown.sh -->
## sources/control-plane/ceph-csi/examples/rbd/plugin-teardown.sh

Purpose: Convenience teardown script for the RBD Ceph CSI example deployment and Vault KMS sample resources.

Important flow: Mirrors `plugin-deploy.sh` with defaults for deployment and KMS directories, then runs `kubectl delete -f` over RBD objects in a deletion-oriented order and Vault/KMS objects afterward.

State and integration: It deletes Kubernetes API resources defined by the referenced YAML files. It does not remove Ceph backend volumes or snapshots created by separate PVC examples.

Risks and tests: Deleting RBAC/config before workloads fully terminate can produce noisy cleanup failures; missing resources cause `kubectl delete` errors. The script has no namespace override and no `--ignore-not-found`. Test by deploying first, running teardown, and verifying CSI pods, sidecars, CSIDriver, and KMS objects are gone while PV reclaim policy governs backend storage.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/plugin-teardown.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-block-restore.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pod-block-restore.yaml

Purpose: Example Pod consuming a restored RBD block PVC.

Important API surface: Pod `pod-block-volume-restore` with CentOS container, raw block `volumeDevices` mapping `data` to `/dev/xvda`, and PVC reference `rbd-block-pvc-restore`.

Control flow and state: Kubelet publishes the restored block PVC to the container as a device. The source restoration is defined by `pvc-block-restore.yaml` using a `VolumeSnapshot`; this Pod only validates node-side consumption.

Dependencies and risks: Requires a snapshot object and block restore PVC, RBD CSI block mode support, and privileged node plugin mapping. A filesystem-style PVC would not match `volumeDevices`. Test by writing/reading the block device from inside the container after restore.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-block-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-clone.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pod-clone.yaml

Purpose: Example nginx Pod mounting an RBD PVC cloned from another PVC.

Important API surface: Pod `csi-rbd-clone-demo-app`, container `web-server`, mount path `/var/lib/www/html`, PVC reference `rbd-pvc-clone`, and `readOnly: false`.

Control flow and state: Kubernetes binds the clone PVC, the RBD node plugin maps and mounts it as a filesystem volume, and nginx sees it as writable content storage. State lives in the cloned RBD image, PV/PVC binding, and node mount.

Dependencies and risks: Requires `pvc-clone.yaml`, source `rbd-pvc`, and a valid StorageClass. Source/target size and access mode compatibility are important. Test by provisioning source content before cloning and checking cloned data in the nginx mount.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-ephemeral.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pod-ephemeral.yaml

Purpose: Example Pod using a generic ephemeral RBD PVC template.

Important API surface: Pod `csi-rbd-demo-ephemeral-pod`, `volumes[].ephemeral.volumeClaimTemplate`, `storageClassName: csi-rbd-sc`, `ReadWriteOnce`, and requested size `1Gi`, mounted at `/myspace`.

Control flow and state: Kubernetes creates a lifecycle-bound PVC from the inline template, the RBD provisioner creates a backing image, and the PVC is garbage-collected with the Pod. No separate PVC manifest is needed.

Dependencies and risks: Requires Kubernetes generic ephemeral volume support, Ceph CSI dynamic provisioning, and a valid RBD StorageClass. The storage lifecycle is tied to Pod deletion; data should not be treated as durable beyond the Pod. Test by creating/deleting the Pod and observing PVC/PV/image lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-ephemeral.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-restore.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pod-restore.yaml

Purpose: Example nginx Pod mounting a filesystem PVC restored from an RBD `VolumeSnapshot`.

Important API surface: Pod `csi-rbd-restore-demo-pod`, mount path `/var/lib/www/html`, PVC reference `rbd-pvc-restore`, and `readOnly: false`.

Control flow and state: The restore is performed by `pvc-restore.yaml`; this Pod triggers node publish and exercises restored data as a mounted filesystem. State lives in the restored RBD image and Kubernetes volume objects.

Dependencies and risks: Requires snapshot CRDs/controller, snapshot object, snapshot class, and RBD CSI snapshot restore support. Restored PVC size must be valid for the snapshot. Test by creating a source PVC with data, snapshotting, restoring, then checking data from the nginx mount.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-rwop.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pod-rwop.yaml

Purpose: Example Pod consuming an RBD filesystem PVC with `ReadWriteOncePod` access mode.

Important API surface: Pod `csi-rbd-demo-fs-rwop-pod`, nginx container, mount path `/var/lib/www/html`, and PVC `rbd-rwop-pvc`.

Control flow and state: Kubernetes enforces single-Pod access semantics for the PVC while the RBD node plugin handles regular filesystem staging/publish. The manifest itself only wires the Pod to the PVC.

Dependencies and risks: Requires Kubernetes and sidecar versions supporting RWOP, plus `pvc-rwop.yaml`. Multiple Pods attempting the same PVC should be rejected or remain pending. Test by creating this Pod and a second competing Pod and checking scheduler/attach behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod-rwop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pod.yaml

Purpose: Baseline nginx Pod mounting the standard RBD filesystem PVC.

Important API surface: Pod `csi-rbd-demo-pod`, container `web-server`, PVC `rbd-pvc`, mount path `/var/lib/www/html`, and writable mount.

Control flow and state: The Pod causes kubelet to call the RBD CSI node path for a dynamically provisioned filesystem volume. Persistent state is in the RBD image and Kubernetes PV/PVC objects.

Dependencies and risks: Requires `pvc.yaml`, `storageclass.yaml`, secret/config map, and deployed RBD plugin. It is a basic smoke test and does not verify advanced features. Test by writing data through the mount, restarting the Pod, and confirming persistence.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-block-clone.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pvc-block-clone.yaml

Purpose: Example PVC cloning a raw block RBD PVC.

Important API surface: `PersistentVolumeClaim` named `block-pvc-clone`, `storageClassName: csi-rbd-sc`, `volumeMode: Block`, data source kind `PersistentVolumeClaim` named `raw-block-pvc`, `ReadWriteOnce`, and `1Gi` request.

Control flow and state: Kubernetes sends a CSI `CreateVolume` request with a volume content source. The RBD controller creates a clone from the source PVC's RBD image and binds a new PV to this claim.

Dependencies and risks: Requires source PVC to exist and be bound, clone support in the RBD driver, same namespace data source rules, and size not smaller than source. Test by writing to source block PVC, cloning, and verifying copied block contents.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-block-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-block-restore.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pvc-block-restore.yaml

Purpose: Example raw block PVC restored from an RBD `VolumeSnapshot`.

Important API surface: PVC `rbd-block-pvc-restore`, `dataSource` referencing `rbd-pvc-snapshot` in API group `snapshot.storage.k8s.io`, `volumeMode: Block`, `ReadWriteOnce`, and `1Gi` request.

Control flow and state: The external provisioner passes the snapshot source to RBD CSI, which creates a new block-mode RBD image from the snapshot and binds it to the PVC.

Dependencies and risks: Requires `snapshot.yaml`, `snapshotclass.yaml`, a snapshot controller, and a source snapshot compatible with block restore semantics. Requested size must be at least snapshot size. Test by publishing via `pod-block-restore.yaml` and validating block data.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-block-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-clone.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pvc-clone.yaml

Purpose: Example filesystem PVC cloned from another RBD PVC.

Important API surface: PVC `rbd-pvc-clone`, `storageClassName: csi-rbd-sc`, data source `PersistentVolumeClaim` named `rbd-pvc`, `ReadWriteOnce`, and `1Gi` size.

Control flow and state: Kubernetes translates the data source into a CSI volume clone request. The RBD controller creates a cloned RBD image and records normal PV/PVC binding state.

Dependencies and risks: Requires source `rbd-pvc` to exist, be compatible, and not exceed requested target size. Clone behavior depends on RBD image features such as layering. Test by mounting source, writing data, creating clone, and mounting `pod-clone.yaml`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-restore.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pvc-restore.yaml

Purpose: Example filesystem PVC restored from an RBD `VolumeSnapshot`.

Important API surface: PVC `rbd-pvc-restore`, `storageClassName: csi-rbd-sc`, data source `VolumeSnapshot` named `rbd-pvc-snapshot`, API group `snapshot.storage.k8s.io`, `ReadWriteOnce`, and `1Gi`.

Control flow and state: The snapshot controller/provisioner passes snapshot identity to the RBD CSI controller, which creates a new image initialized from the snapshot and binds a PV.

Dependencies and risks: Requires source snapshot, snapshot class, snapshot CRDs/controller, and a valid storage class. Size and volume mode must be compatible with the source. Test using `pod-restore.yaml` and data comparison against the source snapshot.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-rwop.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pvc-rwop.yaml

Purpose: Example RBD filesystem PVC using `ReadWriteOncePod`.

Important API surface: PVC `rbd-rwop-pvc`, access mode `ReadWriteOncePod`, `storageClassName: csi-rbd-sc`, and requested storage `1Gi`.

Control flow and state: Dynamic provisioning creates a normal RBD image, while Kubernetes access mode semantics restrict the claim to one Pod at a time. CSI sidecars must advertise/support RWOP semantics.

Dependencies and risks: Requires Kubernetes support for RWOP and compatible sidecars. Older clusters may reject the access mode or not enforce it fully. Test with `pod-rwop.yaml` plus a second consumer to confirm only one Pod can use the claim.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc-rwop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/pvc.yaml

Purpose: Baseline dynamically provisioned RBD filesystem PVC.

Important API surface: PVC `rbd-pvc`, label `group: test`, `ReadWriteOnce`, `storageClassName: csi-rbd-sc`, and `1Gi` request.

Control flow and state: The external provisioner creates an RBD-backed PV using `storageclass.yaml`. The label integrates with `groupsnapshot.yaml` as the selector for group snapshot membership.

Dependencies and risks: Requires storage class, secret, Ceph config map, and RBD controller deployment. The `group: test` label can include this PVC in group snapshots unintentionally if reused. Test by applying the PVC, observing binding, mounting with `pod.yaml`, and checking group snapshot selection.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/raw-block-pod-rwop.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/raw-block-pod-rwop.yaml

Purpose: Example Pod consuming an RBD raw block PVC with `ReadWriteOncePod`.

Important API surface: Pod `csi-rbd-demo-rwop-pod`, CentOS container, `volumeDevices` mapping `data` to `/dev/xvda`, and PVC `raw-block-rwop-pvc`.

Control flow and state: Kubelet requests CSI node publish as a block device; Kubernetes access mode limits the PVC to a single Pod. The raw device contains whatever block-level data the workload writes.

Dependencies and risks: Requires `raw-block-pvc-rwop.yaml`, RBD block mode support, and RWOP cluster support. Incorrect workload assumptions about filesystem presence are a risk because the device is raw. Test by checking device presence and competing Pod rejection.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/raw-block-pod-rwop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/raw-block-pod.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/raw-block-pod.yaml

Purpose: Example Pod consuming the standard RBD raw block PVC.

Important API surface: Pod `pod-with-raw-block-volume`, CentOS container, `volumeDevices` device path `/dev/xvda`, and PVC `raw-block-pvc`.

Control flow and state: The RBD node plugin maps the PVC's RBD image and exposes it as a block device. Kubernetes does not mount a filesystem because the PVC uses `volumeMode: Block`.

Dependencies and risks: Requires `raw-block-pvc.yaml` and CSI block mode support. Applications must format or use the block device directly. Test by running block-level commands inside the container and verifying persistence across Pod restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/raw-block-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/raw-block-pvc-rwop.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/raw-block-pvc-rwop.yaml

Purpose: Example raw block RBD PVC with `ReadWriteOncePod`.

Important API surface: PVC `raw-block-rwop-pvc`, `volumeMode: Block`, `accessModes: ReadWriteOncePod`, `storageClassName: csi-rbd-sc`, and `1Gi` request.

Control flow and state: Dynamic provisioning creates an RBD image and Kubernetes enforces one-Pod access. The PVC is consumed by a Pod through `volumeDevices`.

Dependencies and risks: Requires RWOP support and RBD CSI block support. Testing should confirm both block device publication and single-Pod enforcement; older sidecars may not fully support RWOP.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/raw-block-pvc-rwop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/raw-block-pvc.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/raw-block-pvc.yaml

Purpose: Baseline dynamically provisioned RBD raw block PVC.

Important API surface: PVC `raw-block-pvc`, `volumeMode: Block`, `ReadWriteOnce`, `storageClassName: csi-rbd-sc`, and requested size `1Gi`.

Control flow and state: External provisioning asks the RBD CSI controller for a block-mode image; kubelet later maps it into Pods as a device rather than a mounted filesystem.

Dependencies and risks: Requires valid RBD StorageClass and node plugin support for block devices. Workloads must handle raw device initialization. Test with `raw-block-pod.yaml`, write bytes or create a filesystem, and confirm persistence.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/raw-block-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/secret.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/secret.yaml

Purpose: Example Kubernetes Secret carrying Ceph credentials and an encryption passphrase for RBD CSI.

Important API surface: `v1/Secret` named `csi-rbd-secret` in `default`, `stringData.userID`, `stringData.userKey`, and `stringData.encryptionPassphrase`.

Control flow and state: CSI sidecars reference this secret from StorageClass and SnapshotClass parameters for provisioning, staging, publishing, expansion, modification, and snapshotting. Kubernetes stores secret data base64-encoded in etcd; the driver uses it to authenticate to Ceph and optionally unlock encryption.

Dependencies and risks: Placeholder credentials must be replaced and must not include `client.` prefix in `userID`. Example plaintext passphrase is unsuitable for production. RBAC should limit secret access. Test by provisioning a PVC and verifying authentication succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/secret.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/snapshot.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/snapshot.yaml

Purpose: Example `VolumeSnapshot` for the baseline RBD PVC.

Important API surface: `snapshot.storage.k8s.io/v1`, `VolumeSnapshot` named `rbd-pvc-snapshot`, `volumeSnapshotClassName: csi-rbdplugin-snapclass`, and source `persistentVolumeClaimName: rbd-pvc`.

Control flow and state: The snapshot controller invokes RBD CSI `CreateSnapshot`; Kubernetes stores snapshot CR state and Ceph stores the backend image snapshot. This snapshot is used by restore PVC examples.

Dependencies and risks: Requires snapshot CRDs/controller, `snapshotclass.yaml`, bound source PVC, and Ceph CSI snapshot capability. Deleting the object may delete backend snapshot because class policy is `Delete`. Test by applying and verifying `readyToUse` before restore.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/snapshotclass.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/snapshotclass.yaml

Purpose: Example `VolumeSnapshotClass` for RBD CSI snapshots.

Important API surface: `driver: rbd.csi.ceph.com`, required `clusterID`, optional `snapshotNamePrefix`, snapshotter secret name/namespace, and `deletionPolicy: Delete`.

Control flow and state: The external snapshotter passes class parameters and secret references to RBD CSI. The driver resolves the Ceph cluster from `clusterID` and creates/deletes backend snapshots according to Kubernetes snapshot lifecycle.

Dependencies and risks: Requires matching `ceph-csi-config`, `csi-rbd-secret`, snapshot CRDs, and the RBD controller. Placeholder cluster ID must be replaced. `Delete` can remove backend snapshots on object deletion. Test with `snapshot.yaml` and restore manifests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/storageclass.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/storageclass.yaml

Purpose: Comprehensive example `StorageClass` for dynamically provisioned RBD volumes.

Important API surface: `provisioner: rbd.csi.ceph.com`, required `clusterID` and `pool`, optional data pool, image features, mkfs options, mounter selection, map/unmap options, logging, encryption, topology constrained pools, striping parameters, `allowVolumeExpansion: true`, `reclaimPolicy: Delete`, mount option `discard`, and all relevant CSI secret references including provisioner, node stage, controller expand/publish/modify, and node publish.

Control flow and state: Kubernetes external-provisioner sends parameters to the RBD CSI controller to create images and PVs. Node-side calls use secret references and fstype/mount options to map and mount images. Expansion and VolumeAttributesClass modification are enabled by the secret references and `allowVolumeExpansion`.

Dependencies and integration: Requires `ceph-csi-config` with the cluster ID, `secret.yaml`, a real RBD pool, and deployed RBD controller/node plugin. Integrates with clone, snapshot, block, ephemeral, RWOP, encryption, topology, rbd-nbd, krbd QoS, and cgroup VAC examples.

Risks and test signals: Most values are placeholders or commented documentation; production use needs careful feature compatibility, especially RBD feature dependencies, mounter support, encryption KMS, topology JSON, and discard behavior. Test by provisioning filesystem and block PVCs, expansion, snapshot/restore, clone, and optional encryption/QoS flows.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-high.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-high.yaml

Purpose: High-tier cgroup v2 QoS `VolumeAttributesClass` for RBD.

Important API surface: `VolumeAttributesClass` named `cgroup-qos-high`, `driverName: rbd.csi.ceph.com`, and parameters `maxReadIops`, `maxWriteIops`, `maxReadBps`, `maxWriteBps` set to 2000 IOPS and 200 MiB/s.

Control flow and state: Kubernetes stores the VAC and the CSI modify-volume path passes attributes to RBD CSI. For krbd, limits are expected to apply at the cgroup v2 `io.max` layer for the container/device.

Dependencies and risks: Requires Kubernetes VAC support, controller-modify and node-publish secrets in the StorageClass, cgroup v2 nodes, and driver support for these keys. Test by applying the class to a volume and measuring throttled I/O.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-high.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-low.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-low.yaml

Purpose: Low-tier cgroup v2 QoS `VolumeAttributesClass` for RBD.

Important API surface: VAC `cgroup-qos-low`, RBD CSI driver name, 500 read/write IOPS, and 50 MiB/s read/write bandwidth in byte-per-second parameters.

Control flow and state: The class is declarative Kubernetes state that the RBD driver interprets during volume attribute modification, applying limits through cgroup v2 for krbd-mapped devices.

Dependencies and risks: Requires the same cgroup/VAC/driver prerequisites as the other cgroup examples. Incorrect node cgroup mode or mounter choice can make limits ineffective. Test with fio inside a Pod and compare measured throughput against limits.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-low.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-medium.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-medium.yaml

Purpose: Medium-tier cgroup v2 QoS `VolumeAttributesClass` for RBD.

Important API surface: VAC `cgroup-qos-medium`, `driverName: rbd.csi.ceph.com`, 1000 read/write IOPS, and 100 MiB/s read/write bandwidth.

Control flow and state: Kubernetes stores the class and passes attributes to the RBD CSI driver for cgroup-backed I/O throttling. The object itself has no controller loop.

Dependencies and risks: Needs cgroup v2, RBD CSI support, and compatible sidecars. Numeric values are strings; unit mistakes or unsupported keys can lead to unthrottled volumes. Test by switching a volume between low/medium/high classes and observing I/O changes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-medium.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup.yaml

Purpose: General cgroup v2 QoS `VolumeAttributesClass` example for krbd RBD volumes.

Important API surface: VAC `cgroup-qos-vac`, RBD driver name, and four `io.max`-style parameters: `maxReadIops`, `maxWriteIops`, `maxReadBps`, and `maxWriteBps`. Comments define positive-integer values and byte units.

Control flow and state: The class is applied through Kubernetes volume attribute modification; RBD CSI uses the values to set cgroup limits at node publish/modify time for krbd-mapped devices.

Dependencies and risks: Requires cgroup v2 and driver support for cgroup QoS, plus StorageClass secrets for modify/publish. Does not apply to all mounters equally. Test by inspecting cgroup `io.max` and running workload I/O benchmarks.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass.yaml -->
## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass.yaml

Purpose: RBD QoS `VolumeAttributesClass` example for volume-level read/write IOPS and bandwidth limits, primarily documented for `rbd-nbd`.

Important API surface: VAC `qos-vac`, `driverName: rbd.csi.ceph.com`, active `baseIops: "1000"`, and commented parameters for max/base read/write IOPS, bytes/sec, per-GiB scaling, and `baseVolSizeBytes`.

Control flow and state: Kubernetes persists this class and passes attributes to CSI modify-volume. The RBD driver computes limits from base values and optional size-scaling parameters, then applies QoS through the supported mounter/backend path.

Dependencies and risks: Currently noted as supporting `rbd-nbd`; krbd may require cgroup VAC instead. Missing max values or per-GiB parameters change scaling behavior. Test by applying to different-sized PVCs and checking effective rbd-nbd QoS limits.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/controllerserver.go -->
## sources/control-plane/ceph-csi/internal/cephfs/controllerserver.go

Purpose: Implements CephFS CSI controller RPCs for volume create/delete, expand, snapshot create/delete, controller publish/unpublish, and backing-snapshot/fencing metadata coordination.

Important types and functions: `ControllerServer` embeds `DefaultControllerServer` and owns `VolumeLocks`, `SnapshotLocks`, `OperationLocks`, `VolumeGroupLocks`, and `ClusterName`. Key functions include `CreateVolume`, `DeleteVolume`, `ControllerExpandVolume`, `CreateSnapshot`, `DeleteSnapshot`, `ControllerPublishVolume`, `ControllerUnpublishVolume`, `createBackingVolume*`, `checkContentSource`, `cleanUpBackingVolume`, `doSnapshot`, `getSubvolumeMetadataHandler`, `removeUserIdMapping`, and `fenceNode`.

Control flow: `CreateVolume` validates, builds admin credentials and `VolumeOptions`, checks content source, validates clone/restore/backing-snapshot rules, checks OMAP reservation state, reserves a name, creates a subvolume or clone/snapshot-backed reference, retrieves root path, sets Kubernetes metadata, and returns CSI volume context. Delete reverses backend subvolume or reftracked backing snapshot state, then undoes the journal reservation. Snapshot create reserves a snapshot, creates a CephFS subvolume snapshot, records metadata, and copies encryption config for restore.

State and persistence: Persistent state spans CephFS subvolumes/snapshots, RADOS OMAP journals via `store`, KMS/fscrypt DEKs, snapshot-backed reftracker objects, subvolume/snapshot metadata keys, and Kubernetes secrets. Locks provide in-process idempotency and collision control but do not replace backend journal consistency.

Dependencies and integrations: Uses CSI protobufs, gRPC status codes, go-ceph FSAdmin/OSD admin via core/store, Kubernetes metadata/secret helpers, reftracker errors, KMS, and Ceph OSD blocklist for fencing. Controller publish returns service-account restrictions from CephFS metadata; unpublish removes node user mapping and optionally blocklists a stale client address.

Risks and tests: Complex error rollback can leave stale OMAPs or subvolumes if backend cleanup fails. Clone pending/in-progress is mapped to `Aborted`; EAGAIN is mapped to `ResourceExhausted`. Snapshot-backed volumes have read-only and expansion restrictions. Test coverage in this subset is indirect; high-value tests are idempotent create/delete, clone retry, snapshot-backed reftracker races, fencing metadata, and metadata unsupported clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/clone.go -->
## sources/control-plane/ceph-csi/internal/cephfs/core/clone.go

Purpose: CephFS core clone implementation wrapping go-ceph subvolume snapshot clone APIs and mapping Ceph clone states to internal CSI errors.

Important types/functions: `cephFSCloneState`, `CephFSCloneError`, `ToError`, `GetProgressReport`, `CreateCloneFromSubvolume`, `CleanupSnapshotFromSubvolume`, `CreateCloneFromSnapshot`, and `GetCloneState`.

Control flow: PVC-to-PVC clone creates an intermediate snapshot named after the target clone, clones it to the target subvolume, checks clone state, expands the clone if needed, and deletes the intermediate snapshot. Snapshot restore clones the existing snapshot to the target and expands. Deferred cleanup purges the target and/or snapshot on non-retry errors.

State and persistence: Uses CephFS subvolume snapshots and clone state maintained by the Ceph manager. No local persistence; callers coordinate RADOS journal reservations. Clone progress fields are exposed for `ErrCloneInProgress`.

Dependencies and risks: Depends on `go-ceph/cephfs/admin`, CephFS clone support, internal errors, and logging. Retry errors intentionally avoid destructive cleanup because clone may still progress. A failed delete of the intermediate snapshot can leave cleanup work. `CephFSCloneError` is a sentinel with default state, so state mapping relies on matching enum zero behavior. Unit test covers `ToError` mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/clone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/clone_test.go -->
## sources/control-plane/ceph-csi/internal/cephfs/core/clone_test.go

Purpose: Unit test for clone-state-to-error translation.

Important APIs: `TestCloneStateToError` constructs a map from `cephFSCloneState` values to expected internal errors using go-ceph clone states `CloneComplete`, `CloneInProgress`, `ClonePending`, and `CloneFailed`, plus `CephFSCloneError`.

Control flow and state: The test iterates table entries and asserts `require.ErrorIs(t, state.ToError(), err)`. It is parallelized with `t.Parallel()` and does not touch Ceph or persistent state.

Dependencies and risks: Depends on `testify/require`, go-ceph admin enums, and internal CephFS errors. It verifies error wrapping compatibility but not clone cleanup, progress reporting, or actual FSAdmin interactions. Risk is map iteration obscuring case order in failure output, but coverage is focused and cheap.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/clone_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/filesystem.go -->
## sources/control-plane/ceph-csi/internal/cephfs/core/filesystem.go

Purpose: Small abstraction over CephFS filesystem discovery APIs used by volume and group snapshot option construction.

Important types/functions: `FileSystem` interface, `fileSystem` implementation, `NewFileSystem`, `GetFscID`, `GetMetadataPool`, and `GetFsName`.

Control flow: Each method obtains `FSAdmin` from the cluster connection, enumerates volumes or file systems, scans for the requested name or ID, and returns the matching filesystem ID, metadata pool, or name. Missing entries map to Ceph CSI `ErrVolumeNotFound` or `util.ErrPoolNotFound` wrapping.

State and persistence: Reads Ceph cluster filesystem metadata only; no writes or local state. Callers use returned FscID and metadata pool to generate CSI IDs and journal locations.

Dependencies and risks: Depends on go-ceph FSAdmin and internal logging/errors. Linear scans are simple but assume filesystem names/IDs are available and stable. Tests in this subset do not cover this file directly; integration tests should validate behavior with missing filesystem, missing metadata pool, and multiple filesystems.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/metadata.go -->
## sources/control-plane/ceph-csi/internal/cephfs/core/metadata.go

Purpose: Provides CephFS subvolume metadata helpers for Kubernetes metadata, cluster name, node client address, user ID mapping, and service-account restrictions.

Important constants/functions: `clusterNameKey`, `clientAddressKey`, `userIdMappingKey`, exported `ServiceAccountKey`, `ErrSubVolMetadataNotSupported`, `GetClientAddressKey`, `GetUserIDMappingKey`, `SetAllMetadata`, `UnsetAllMetadata`, and `ListMetadata`.

Control flow: Per-cluster metadata support is cached in `clusterAdditionalInfo`. `setMetadata`, `removeMetadata`, and `listMetadata` call FSAdmin metadata APIs and convert `NotImplementedError` into a soft unsupported state. Bulk set/unset/list methods ignore unsupported clusters but wrap other errors with key/value context.

State and persistence: Metadata is stored on CephFS subvolumes. Keys starting with `.` are intended to avoid copying to mirrored subvolumes. Global in-memory support cache influences later calls per cluster ID.

Dependencies and risks: Depends on go-ceph cephfs/admin metadata APIs and libcephfs not-exist errors. The global cache is protected during initialization but subsequent state mutation is not separately locked, so concurrent unsupported detection may race. Tests are not present here; integration should cover unsupported Ceph versions and metadata cleanup on unpublish/delete.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/quiesce.go -->
## sources/control-plane/ceph-csi/internal/cephfs/core/quiesce.go

Purpose: Wraps CephFS filesystem quiesce operations used to take crash-consistent group snapshots across subvolumes.

Important types/functions: `QuiesceState` constants `Released`, `Quiescing`, `Quiesced`; `GetQuiesceState`; `FSQuiesceClient` interface; `FSQuiesceClientMap`; `Volume`; `fsQuiesce`; `NewFSQuiesce`; `FSQuiesce`, `FSQuiesceWithExpireTimeout`, `ResetFSQuiesce`, `ReleaseFSQuiesce`, and `getMembers`.

Control flow: `NewFSQuiesce` binds FSAdmin and a map from subvolume groups to subvolume names. Quiesce calls build `admin.FSQuiesceOptions` with timeout/expiration/reset/release flags and call `FSQuiesce` on go-ceph with a reservation name. `getMembers` formats members as `group/subvolume`.

State and persistence: Quiesce state is maintained by the CephFS manager under the reservation name. The client holds a cluster connection and must destroy it after use.

Dependencies and risks: Depends on go-ceph admin quiesce APIs and Ceph versions that support them. Hard-coded 180-second timeouts/expirations may be too short for large sets. Map iteration order is nondeterministic but should not matter to Ceph. Tests are indirect through group snapshot request validation only; integration should cover quiesce in-progress, reset, release, and multi-filesystem grouping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/quiesce.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/snapshot.go -->
## sources/control-plane/ceph-csi/internal/cephfs/core/snapshot.go

Purpose: CephFS subvolume snapshot client abstraction for create, delete, inspect, clone, and metadata operations.

Important types/functions: `SnapshotClient`, `snapshotClient`, `Snapshot`, `SnapshotInfo`, `NewSnapshot`, `CreateSnapshot`, `DeleteSnapshot`, `GetSnapshotInfo`, and `CloneSnapshot`.

Control flow: Methods obtain FSAdmin from the cluster connection and call go-ceph subvolume snapshot APIs. `GetSnapshotInfo` maps missing snapshots to `ErrSnapNotFound` and extracts creation time and pending-clone status. `CloneSnapshot` builds `admin.CloneOptions`, including target group and optional pool layout, then invokes `CloneSubVolumeSnapshot`.

State and persistence: Writes CephFS subvolume snapshots and clone jobs; snapshot metadata methods are defined in `snapshot_metadata.go`. CSI journals are handled by callers.

Dependencies and risks: Depends on go-ceph admin and rados errors. Force deletion is used for snapshots. `CreationTime` field in `SnapshotInfo` is present but populated by higher-level controller after converting `CreatedAt`. Tests are indirect; integration should cover pending clones, missing parent, pool layout, and delete failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/snapshot_metadata.go -->
## sources/control-plane/ceph-csi/internal/cephfs/core/snapshot_metadata.go

Purpose: Adds metadata support for CephFS subvolume snapshots, mirroring subvolume metadata behavior.

Important APIs: `ErrSubVolSnapMetadataNotSupported`, support detection helpers, `setSnapshotMetadata`, `removeSnapshotMetadata`, `listSnapshotMetadata`, `SetAllSnapshotMetadata`, `UnsetAllSnapshotMetadata`, and `ListSnapshotMetadata`.

Control flow: Support is cached per cluster in `clusterAdditionalInfo`. Set/remove call FSAdmin snapshot metadata APIs and convert `NotImplementedError` into unsupported. Bulk functions add caller parameters plus `clusterNameKey`, and ignore missing keys on unset.

State and persistence: Metadata is stored on CephFS subvolume snapshots. This is used for snapshot-backed volumes where node user/client metadata must live on the backing snapshot rather than a real subvolume.

Dependencies and risks: Depends on go-ceph snapshot metadata APIs. `listSnapshotMetadata` calls `fsa.ListMetadata` for the subvolume rather than an obvious snapshot-specific list API, which is a risk worth verifying against go-ceph behavior. Unlike subvolume metadata, unsupported snapshot metadata errors are not swallowed in `SetAllSnapshotMetadata`, so older clusters may fail snapshot metadata updates. Tests are absent.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/snapshot_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/volume.go -->
## sources/control-plane/ceph-csi/internal/cephfs/core/volume.go

Purpose: Core CephFS subvolume client and data model used by controller and node paths.

Important types/functions: `Subvolume`, `SubVolumeClient`, `subVolumeClient`, `SubVolume`, `NewSubVolume`, `GetVolumeRootPathCephDeprecated`, `GetVolumeRootPathCeph`, `GetSubVolumeInfo`, `CreateVolume`, `ExpandVolume`, `ResizeVolume`, `PurgeVolume`, and `checkSubvolumeHasFeature`. It also defines cluster-level support cache types shared with metadata.

Control flow: Create uses FSAdmin `CreateSubVolume` with size and optional pool layout. Info reads subvolume details and normalizes quota/features. Expand compares requested/current quota and calls resize. Purge removes the subvolume with force and optionally retains snapshots if the subvolume supports `snapshot-retention`.

State and persistence: Directly creates, resizes, queries, and removes CephFS subvolumes. `clusterAdditionalInfo` is in-memory feature support state. Callers handle journals and CSI ID generation.

Dependencies and risks: Depends on go-ceph FSAdmin, rados error mapping, and internal util/log packages. `ExpandVolume` compares `s.Size` against current quota but logs `bytesQuota`, so caller consistency matters. Infinite or nil quotas are tolerated only in specific states. Tests in this subset do not directly cover create/resize/purge; integration should exercise not-found, invalid-command, snapshot-retained, and volume-has-snapshots cases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/core/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/driver.go -->
## sources/control-plane/ceph-csi/internal/cephfs/driver.go

Purpose: Initializes and runs the CephFS CSI driver, including identity, controller, node, group controller, journals, mounters, topology, read affinity, and CSI-Addons server.

Important types/functions: `cephfsDriver`, `NewDriver`, `NewIdentityServer`, `NewControllerServer`, `NewNodeServer`, `Run`, and `setupCSIAddonsServer`.

Control flow: `Run` loads available mounters, sets the CephFS RADOS namespace, reads node labels/topology/read-affinity inputs, initializes volume/snapshot/group journals, constructs the CSI driver and capabilities, creates requested servers based on config, starts CSI-Addons, then starts the nonblocking gRPC server. Controller capabilities include create/delete volume/snapshot, expand, clone, single-node multi-writer, publish/unpublish, and group snapshots.

State and persistence: Initializes global journal configs in `store` and process-local server state/locks. Persistent cluster state is created later by request handlers.

Dependencies and risks: Depends on mounter probing, Kubernetes helpers, CSI common server, health checker, journal package, CSI-Addons CephFS services, and config feature gates. Fatal logging is used for startup failures. Test coverage verifies CSI-Addons socket creation but not full driver startup. Risks include mounter availability, topology config errors, and global journal state coupling.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/driver_test.go -->
## sources/control-plane/ceph-csi/internal/cephfs/driver_test.go

Purpose: Unit/integration-style test for CSI-Addons server setup.

Important flow: `TestSetupCSIAddonsServer` creates a temporary Unix socket endpoint, builds a minimal `util.Config`, invokes `drv.setupCSIAddonsServer`, asserts no error and non-nil server, checks the socket path exists, then stops the server.

State and dependencies: Uses a temp directory and creates a local Unix socket. Depends on the CSI-Addons server implementation and filesystem socket support; it does not contact Ceph.

Risks and signal: Provides a concrete signal that addon server initialization and service registration are viable with minimal config. It does not validate full `Run`, controller/node setup, or error cases for invalid endpoints. Parallel execution is safe because each test owns a temp socket.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/driver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/errors/errors.go -->
## sources/control-plane/ceph-csi/internal/cephfs/errors/errors.go

Purpose: Centralizes CephFS-specific sentinel errors and string constants used across core, store, controller, and node code.

Important APIs: `VolumeNotEmpty` string for CLI error matching; sentinels `ErrCloneInProgress`, `ErrClonePending`, `ErrInvalidClone`, `ErrCloneFailed`, `ErrInvalidVolID`, `ErrNonStaticVolume`, `ErrSnapNotFound`, `ErrVolumeNotFound`, `ErrInvalidCommand`, `ErrVolumeHasSnapshots`, `ErrQuiesceInProgress`, `ErrGroupNotFound`; and `IsCloneRetryError`.

Control flow and state: This file has no runtime state. It enables `errors.Is` matching across wrapped errors and maps backend conditions to CSI gRPC codes in higher layers.

Dependencies and risks: Only depends on Go `errors`. String matching for `VolumeNotEmpty` is brittle because it depends on backend/CLI wording. Adding new clone retry states requires updating `IsCloneRetryError`. Test signal comes from `clone_test.go` for clone errors; other sentinels are exercised indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/fuserecovery.go -->
## sources/control-plane/ceph-csi/internal/cephfs/fuserecovery.go

Purpose: Implements recovery for corrupted or missing Ceph-FUSE stage/publish mounts after node plugin restarts or mount failures.

Important types/functions: `mountState` enum (`msUnknown`, `msNotMounted`, `msMounted`, `msCorrupted`), `String`, `getMountState`, `tryRestoreFuseMountsInNodePublish`, and `tryRestoreFuseMountInNodeStage`.

Control flow: Recovery first classifies stage and target paths using `IsMountPoint` and corrupted mount detection. NodePublish recovery requires a stored `NodeStageMountinfo` record; it rebuilds `VolumeOptions`, selects mounter, remounts staging if needed, and unmounts the publish target so normal publish can continue. NodeStage recovery simply unmounts a corrupted staging target and lets staging proceed.

State and persistence: Reads `NodeStageMountinfo` persisted by `fsutil` during successful FUSE staging. Uses current mount table state and may mutate mounts by unmounting/remounting.

Dependencies and risks: Depends on node server volume option resolution, mounter selection, and saved secrets/capability. If mountinfo is missing, recovery logs and returns nil, leaving normal flow to handle the state. Tests are absent; important scenarios are corrupted stage path, corrupted bind target, missing mountinfo, and non-FUSE volumes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/fuserecovery.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/groupcontrollerserver.go -->
## sources/control-plane/ceph-csi/internal/cephfs/groupcontrollerserver.go

Purpose: Implements CSI group controller RPCs for CephFS volume group snapshots using filesystem quiesce plus per-volume snapshots and a group journal.

Important functions: `validateCreateVolumeGroupSnapshotRequest`, `CreateVolumeGroupSnapshot`, `queisceFileSystems`, `releaseQuiesceAndGetVolumeGroupSnapshotResponse`, `createSnapshotAddToVolumeGroupJournal`, `formatCreateSnapshotRequest`, `releaseFSQuiesce`, `fsQuiesceWithExpireTimeout`, `createSnapshotAndAddMapping`, `checkIfFSNeedQuiesceRelease`, `getClusterIDForVolumeID`, `getFsNamesAndSubVolumeFromVolumeIDs`, `destroyFSConnections`, `matchesSourceVolumeIDs`, `deleteSnapshotsAndUndoReservation`, `validateVolumeGroupSnapshotDeleteRequest`, `DeleteVolumeGroupSnapshot`, and `extractDeleteVolumeGroupError`.

Control flow: Create validates parameters, locks by group name, builds credentials/options, checks or reserves a group, resolves source volume IDs into filesystem quiesce clients, quiesces filesystems, creates snapshots one by one while refreshing quiesce expiration, writes volume-to-snapshot mappings to the group journal, releases quiesce, and returns a group snapshot response. Existing partial groups can trigger a release-and-complete path when all source mappings exist. Delete resolves the group ID, deletes member snapshots, removes journal mappings, and undoes the reservation.

State and persistence: Persists group reservations and volume snapshot maps in RADOS OMAP through `VolumeGroupJournal`, creates normal CephFS snapshots through `CreateSnapshot`, and uses CephFS quiesce reservation state. It opens additional cluster connections grouped by monitor set and filesystem.

Dependencies and risks: Depends on CephFS quiesce support, store volume lookups, controller snapshot methods, RADOS journals, and CSI group snapshot APIs. The function name `queisceFileSystems` is misspelled but internal. Source-volume matching sorts slices in place, mutating caller-provided slices. Cleanup inside `deleteSnapshotsAndUndoReservation` undoes reservation inside the loop, which deserves integration scrutiny for multi-snapshot groups. Tests cover request validation only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/groupcontrollerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/groupcontrollerserver_test.go -->
## sources/control-plane/ceph-csi/internal/cephfs/groupcontrollerserver_test.go

Purpose: Unit tests for group snapshot create request validation.

Important APIs: `TestControllerServer_validateCreateVolumeGroupSnapshotRequest` constructs a `ControllerServer` with a default CSI driver and table-tests `validateCreateVolumeGroupSnapshotRequest`.

Control flow and state: Cases cover a valid request, empty name, empty source volume IDs, missing clusterID, and missing fsName. The test asserts expected gRPC status codes for invalid cases and runs subtests in parallel. No Ceph or Kubernetes state is used.

Dependencies and risks: Depends on CSI protobufs, `status.Code`, and csi-common default driver validation. It validates request shape but not quiesce, journaling, cleanup, delete, or multi-volume behavior. Test signal is useful for API-level parameter enforcement but leaves most group snapshot behavior to integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/groupcontrollerserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/identityserver.go -->
## sources/control-plane/ceph-csi/internal/cephfs/identityserver.go

Purpose: CephFS CSI identity server implementation for plugin capability discovery.

Important API: `IdentityServer` embeds `DefaultIdentityServer`; `GetPluginCapabilities` returns controller service, online volume expansion, and group controller service plugin capabilities.

Control flow and state: The method is a pure response builder with no external calls or persistent state. Kubernetes sidecars use these advertised capabilities to decide which controller and expansion operations are available.

Dependencies and risks: Depends on CSI protobuf types and csi-common default identity behavior. Capability mismatch with actual controller registration would confuse sidecars; here it aligns with `driver.go` adding controller/group capabilities. Tests are not present for this file specifically.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/mounter/fuse.go -->
## sources/control-plane/ceph-csi/internal/cephfs/mounter/fuse.go

Purpose: Implements Ceph-FUSE mounting and unmount tracking for CephFS volumes.

Important APIs: `FuseMounter`, `mountFuse`, `(*FuseMounter).Mount`, `Name`, `UnmountVolume`, `UnmountAll`, constants `volumeMounterFuse` and `cephEntityClientPrefix`, global `fusePidMap`, mutex, and `fusePidRx`.

Control flow: `mountFuse` builds `ceph-fuse` args with monitor list, config path, client identity/keyfile, root path, optional FUSE mount options and filesystem namespace, optionally runs through `nsenter`, parses stderr for the FUSE daemon PID, and records it by mountpoint. Unmount runs `umount`, tolerates not-mounted/not-found messages, removes PID tracking, and waits for the daemon process if it is known.

State and persistence: Maintains process-local map from mountpoint to FUSE daemon PID; actual mount state lives in the node mount table. No durable state is written here.

Dependencies and risks: Depends on `ceph-fuse` output format containing `starting fuse`, shell command execution helpers, and optional network namespace support. PID tracking is lost on plugin restart, which is why `fuserecovery.go` exists. Tests are absent; integration should cover stderr parsing, nsenter path, option construction, and unmount idempotency.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/mounter/fuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/mounter/kernel.go -->
## sources/control-plane/ceph-csi/internal/cephfs/mounter/kernel.go

Purpose: Implements CephFS kernel-client mounting for the node server.

Important APIs: `KernelMounter` interface, `kernelMounter`, `NewKernelMounter`, `Mount`, `Name`, `mountKernel`, and `filesystemSupported`.

Control flow: `NewKernelMounter` checks `/proc/filesystems` for Ceph support and records whether `modprobe ceph` is needed. `mountKernel` creates the mountpoint, loads the kernel module if needed, resolves FSID from volume options, builds `mount -t ceph <user>@<fsid>.<fsName>=<rootPath> <mountPoint> -o mon_addr=...,secretfile=...,...,_netdev`, and optionally executes inside a network namespace.

State and persistence: Mutates the node mount table and may load a kernel module. `needsModprobe` is process-local state.

Dependencies and risks: Depends on Linux kernel CephFS support, `mount.ceph`/kernel mount behavior, keyfiles, monitor address formatting, and network namespace helper. `filesystemSupported` reads `/proc/filesystems`; test coverage verifies positive `proc` and negative fake filesystem, but not Ceph mounting. Integration should cover FSID lookup and mount option propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/mounter/kernel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/mounter/kernel_test.go -->
## sources/control-plane/ceph-csi/internal/cephfs/mounter/kernel_test.go

Purpose: Unit test for filesystem support detection used by kernel mounter initialization.

Important flow: `TestFilesystemSupported` installs a test error logger, asserts `filesystemSupported("proc")` is true because proc is expected in `/proc/filesystems`, and asserts a made-up filesystem name is false.

State and dependencies: Reads the host `/proc/filesystems`; no Ceph state or mounts are involved. Uses `testify/require`.

Risks and signal: The test covers parser basics and failure reporting but does not validate Ceph module availability, modprobe, or mount command construction. It assumes procfs is present, which is valid for normal Linux CI but not for exotic environments.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/mounter/kernel_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/mounter/volumemounter.go -->
## sources/control-plane/ceph-csi/internal/cephfs/mounter/volumemounter.go

Purpose: Common mounter selection, probing, and bind-mount helpers for CephFS node operations.

Important APIs: Global `availableMounters`, `quotaSupport`, `LoadAvailableMounters`, `VolumeMounter`, `New`, `BindMount`, and helper `execCommandErr`.

Control flow: Startup probes `mount.ceph` and `ceph-fuse --version`. Kernel mounter is loaded only if forced or kernel version supports CephFS quota; FUSE is loaded if available. `New` chooses the requested mounter if loaded, otherwise falls back to the first available. `BindMount` runs `mount -o <options> from to` and remounts read-only when requested.

State and persistence: `availableMounters` is process-global startup state. Bind mounts mutate the node mount table. No durable files are created here.

Dependencies and risks: Depends on external binaries, kernel version detection, and mount commands. Fallback to the first available mounter can hide unsupported requested mounters unless logs are reviewed. `availableMounters` is global and not reset by this file, so tests would need cleanup. Integration should verify mounter ordering, forced kernel behavior, and read-only remount.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/mounter/volumemounter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/nodeserver.go -->
## sources/control-plane/ceph-csi/internal/cephfs/nodeserver.go

Purpose: Implements CephFS CSI node RPCs for staging, publishing, unpublishing, unstaging, volume stats, mount option construction, encryption unlock, fencing metadata, and health checking.

Important types/functions: `NodeServer`, `getCredentialsForVolume`, `getVolumeOptions`, `validateSnapshotBackedVolCapability`, `maybeUnlockFileEncryption`, `generateLockCookie`, `maybeInitializeFileEncryption`, `NodeStageVolume`, `setUserIdMapping`, `setClientAddress`, `startSharedHealthChecker`, `mount`, `getBackingSnapshotRoot`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeUnstageVolume`, `NodeGetCapabilities`, `NodeGetVolumeStats`, and `setMountOptions`.

Control flow: Stage validates, locks by volume ID, resolves dynamic/static/monitor-list volume options, sets net namespace, validates snapshot-backed read-only capability, creates a mounter, initializes fscrypt if needed, recovers FUSE mounts, sets user/client metadata for fencing, mounts if not already mounted, bind-mounts snapshot root for snapshot-backed volumes, unlocks file encryption, stores FUSE mountinfo, and starts a health checker. Publish validates service-account restrictions, restores FUSE if needed, checks staging mount, handles read-only/encrypted subdirectory paths, and bind mounts to the target. Unpublish/unstage stop health checks and unmount/remove paths. Stats use health checks before filesystem stats.

State and persistence: Mutates node mount table, writes/removes FUSE `NodeStageMountinfo`, stores CephFS subvolume or snapshot metadata for user ID and client address, uses RADOS object locks during fscrypt unlock, and starts health checker state in memory.

Dependencies and integrations: Uses CSI protobufs, csi-common validators/stats, core metadata, store volume parsing, mounter package, fscrypt, KMS settings embedded in volume options, Kubernetes service-account validation context, health checker manager, and Ceph cluster connections.

Risks and tests: FUSE mounter does not support encryption; snapshot-backed volumes are read-only only. Metadata operations may be unsupported by older clusters. Client address parsing and blocklisting depend on fencing being enabled and later controller unpublish. `NodeUnstageVolume` returns error if mountinfo removal fails, which can affect non-FUSE paths depending on helper behavior. Tests cover mount option precedence only; integration should cover stage/publish idempotency, encryption lock contention, FUSE recovery, service-account denial, corrupted mounts, and stats health conditions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/nodeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/nodeserver_test.go -->
## sources/control-plane/ceph-csi/internal/cephfs/nodeserver_test.go

Purpose: Unit tests for CephFS node mount option resolution.

Important flow: `Test_setMountOptions` writes a temporary JSON CSI config containing cluster-specific kernel/fuse mount options, constructs test cases for config vs CLI precedence across kernel and FUSE mounters, initializes a default node server, calls `setMountOptions`, and checks expected options are present.

State and dependencies: Uses a temp config file and in-memory `VolumeOptions`; no real mounts or Ceph connections. Depends on Kubernetes deploy API types, mounter constructors, csi-common server defaults, and JSON config parsing helpers.

Risks and signal: Confirms cluster config overrides CLI options and CLI options are used when config is empty. It does not test read-affinity options, read-only access mode injection, invalid config, or full stage/publish behavior. One test name appears mismatched to cluster setup, but the assertions check resulting option content.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/nodeserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/backingsnapshot.go -->
## sources/control-plane/ceph-csi/internal/cephfs/store/backingsnapshot.go

Purpose: Manages RADOS reftracker state for snapshot-backed CephFS volumes so backing snapshots are retained while referenced and removed when safe.

Important functions: `fmtBackingSnapshotReftrackerName`, `AddSnapshotBackedVolumeRef`, `UnrefSnapshotBackedVolume`, and `UnrefSelfInSnapshotBackedVolumes`.

Control flow: Add opens an ioctx in the metadata pool/namespace, adds refs for the backing snapshot ID and new volume ID, registers cleanup to remove them on failure, then re-fetches the backing snapshot to detect delete races. Unref for a volume removes the volume ref and returns whether the reftracker object is deleted. Unref self masks/removes the snapshot's own ref during snapshot deletion and returns whether no dependent snapshot-backed volumes remain.

State and persistence: Persists reftracker objects named `rt-backingsnapshot-<snapshotID>` in RADOS. Uses normal and mask ref types to distinguish dependent volumes from the snapshot self reference.

Dependencies and risks: Depends on RADOS ioctx, reftracker wrappers, store snapshot lookup, and cluster credentials. Races are partially handled with revalidation and `ErrObjectOutOfDate` handling in callers. Cleanup logging warns about orphaned reftracker objects if removal fails. Integration tests should simulate concurrent snapshot delete and volume create/delete.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/backingsnapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/fsjournal.go -->
## sources/control-plane/ceph-csi/internal/cephfs/store/fsjournal.go

Purpose: Implements CephFS volume and snapshot journal operations that provide idempotent CSI name-to-backend-object mapping.

Important types/functions: Global `VolJournal`, `SnapJournal`, `VolumeGroupJournal`; `VolumeIdentifier`; `SnapshotIdentifier`; `CheckVolExists`; `UndoVolReservation`; `updateTopologyConstraints`; `getEncryptionConfig`; `ReserveVol`; `ReserveSnap`; `UndoSnapReservation`; `CheckSnapExists`; and `SetSubVolCSIMetadata`.

Control flow: `CheckVolExists` connects to the volume journal, checks request-name reservation, validates existing backend subvolume or clone state, handles clone pending/in-progress/failed cleanup, retrieves root path, cleans stale reservations, and generates CSI volume ID. `ReserveVol` applies topology constraints, reserves a UUID/name in OMAP, sets `volOptions.VolID`, and generates CSI volume ID. Snapshot functions mirror this for snapshot reservations and existing snapshot validation. `SetSubVolCSIMetadata` decomposes a CSI ID, resolves monitors/subvolume group, connects, and writes Kubernetes PV/PVC metadata to the subvolume.

State and persistence: Uses RADOS OMAP journal objects in the CephFS metadata pool and namespace to persist CSI request names, UUIDs, image/subvolume names, parent relationships, encryption IDs, owners, and backing snapshot IDs. It also reads/writes CephFS subvolumes/snapshots and metadata via core clients.

Dependencies and integrations: Depends on internal journal package, core volume/snapshot APIs, util CSI ID generation/decomposition, topology selection, KMS encryption type, Kubernetes metadata preparation, and Ceph cluster connections.

Risks and tests: Correct locking by controller request name is required; comments explicitly warn that journal operations must be called under locks. Rollback paths are complex, especially clone failure cleanup and stale OMAP removal. `CheckVolExists` cleans intermediate clone snapshots when appropriate. Test coverage in this subset is absent; integration should cover stale reservation repair, clone retry progress, topology pool selection, encrypted volumes, and snapshot reservation cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/fsjournal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/volumegroup.go -->
## sources/control-plane/ceph-csi/internal/cephfs/store/volumegroup.go

Purpose: Provides store-layer option parsing and journal operations for CephFS volume group snapshots.

Important types/functions: `VolumeGroupOptions`, `NewVolumeGroupOptions`, `VolumeGroupSnapshotIdentifier`, `GetVolumeIDs`, `NewVolumeGroupOptionsFromID`, `CheckVolumeGroupSnapExists`, `ReserveVolumeGroup`, and `UndoVolumeGroupReservation`.

Control flow: Create path parses request parameters into volume options, extracts optional `volumeGroupNamePrefix`, connects to Ceph, resolves filesystem ID and metadata pool, and reserves/checks group snapshot names through `VolumeGroupJournal`. ID lookup decomposes the CSI group snapshot ID, resolves monitors/RADOS namespace from config, connects, resolves filesystem name and metadata pool, loads group attributes from the journal, and returns the volume-to-snapshot map.

State and persistence: Persists group snapshot reservation and `VolumeSnapshotMap` in RADOS OMAP via `VolumeGroupJournal`. Generated CSI IDs encode cluster ID, filesystem location ID, and group UUID.

Dependencies and risks: Depends on CSI group snapshot request types, `VolumeOptions` parsing, core filesystem lookup, util CSI ID/config helpers, and group journal implementation. Missing journal group name maps to `ErrGroupNotFound`. Tests in this subset do not exercise this store code directly; integration should validate ID decode failures, missing config, group map retrieval, reservation idempotency, and undo behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/volumegroup.go -->
