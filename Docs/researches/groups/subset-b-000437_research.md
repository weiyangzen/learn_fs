# subset-b-000437 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshot.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshot.yaml

Purpose: example `VolumeGroupSnapshot` for selecting multiple CephFS PVCs into one CSI group snapshot.
Important APIs/types/functions: Kubernetes external snapshotter `groupsnapshot.storage.k8s.io/v1beta1`, `VolumeGroupSnapshot`, label selector `spec.source.selector.matchLabels`, and `volumeGroupSnapshotClassName`.
Control flow: after apply, the group snapshot controller selects PVCs labeled `group: snapshot-test` and asks the CephFS CSI driver through `csi-cephfsplugin-groupsnapclass` to create coordinated snapshots. State is persisted in Kubernetes API objects and in backend CephFS snapshots managed by CSI. Dependencies and integration points are the group snapshot CRDs/controller, matching PVC labels from `pvc.yaml`, and the CephFS group snapshot class. Risks: beta API availability, selector matching the wrong or no PVCs, and class/driver mismatch. Test signals: CRD installed, selected PVCs bound, snapshot class exists, and `VolumeGroupSnapshot.status` reaches ready.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshotclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshotclass.yaml

Purpose: declares the CephFS CSI group snapshot class used by the CephFS group snapshot example.
Important APIs/types/functions: `VolumeGroupSnapshotClass`, driver `rook-ceph.cephfs.csi.ceph.com`, `clusterID`, `fsName`, CSI group-snapshotter secret parameters, and `deletionPolicy: Delete`.
Control flow: the group snapshot controller resolves this class, passes cluster/filesystem identity and provisioner secret references to the CephFS CSI driver, and uses the deletion policy to remove backend group snapshot data when the API object is deleted. State lives in the cluster-scoped snapshot class plus Ceph snapshot metadata. Dependencies are CephFS CSI, Rook-generated `rook-csi-cephfs-provisioner` secret in `rook-ceph`, and filesystem `myfs`. Risks: stale `fsName`, wrong namespace in `clusterID`, missing beta group snapshot support, and destructive delete policy. Test signals: class is accepted, driver name matches installed CSIDriver, and a matching `VolumeGroupSnapshot` becomes ready.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/groupsnapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/kube-registry.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/kube-registry.yaml

Purpose: deploys a three-replica Docker registry backed by a shared CephFS PVC in `kube-system`.
Important APIs/types/functions: `PersistentVolumeClaim` named `cephfs-pvc`, `Deployment` `kube-registry`, `registry:2`, `REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY`, HTTP probes, and PVC volume mount `image-store`.
Control flow: Kubernetes binds the RWX PVC through `rook-cephfs`; registry pods mount it at `/var/lib/registry`, expose port 5000, and probes hit `/` on the registry port. State and persistence are container image blobs persisted on CephFS; Deployment replica state is Kubernetes-managed. Dependencies are the CephFS StorageClass, registry image, kube-system placement, and a CephFS volume that supports shared writes. Risks: sample HTTP secret is insecure, registry filesystem backend concurrency requires correct shared storage semantics, no Service is included, and namespace differs from other examples. Test signals: PVC bound, three pods ready, liveness/readiness pass, and pushing/pulling images works across pod restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/kube-registry.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pod-ephemeral.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pod-ephemeral.yaml

Purpose: demonstrates a generic ephemeral inline CephFS volume for a single nginx pod.
Important APIs/types/functions: `Pod`, `volumes[].ephemeral.volumeClaimTemplate`, `storageClassName: rook-cephfs`, RWX access mode, and `/myspace` mount.
Control flow: kubelet creates a PVC from the inline template for the pod lifetime; CSI dynamically provisions a CephFS subvolume, mounts it into nginx, and deletes it with the pod. State is intentionally pod-scoped and persisted only for the pod lifetime. Dependencies are Kubernetes generic ephemeral volumes, the CephFS CSI provisioner, and the `rook-cephfs` StorageClass. Risks: cluster version may not support ephemeral volume templates, RWX is unnecessary for one pod but exercises CephFS semantics, and data disappears on pod deletion. Test signals: generated PVC appears, pod reaches Ready, mount is writable, and PVC/backend subvolume are removed after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pod-ephemeral.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pod.yaml

Purpose: mounts the example CephFS PVC into an nginx pod to validate filesystem-backed workload access.
Important APIs/types/functions: `Pod` `csicephfs-demo-pod`, container `nginx`, `persistentVolumeClaim.claimName: cephfs-pvc`, and mount path `/var/lib/www/html`.
Control flow: the scheduler places the pod, kubelet asks CephFS CSI to stage/publish the already-bound PVC, and nginx sees the mounted directory. Persistent state is the referenced PVC/PV and CephFS subvolume; the pod itself is disposable. Dependencies are `pvc.yaml`, `storageclass.yaml`, CephFS CSI node plugin, and Rook secrets. Risks: pod fails if the PVC is not bound or access mode conflicts with the StorageClass, and the sample has no readiness probe. Test signals: pod Ready, `mount` shows CephFS/fuse or kernel client, writing under the mount survives pod recreation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-clone.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-clone.yaml

Purpose: demonstrates Kubernetes PVC cloning for a CephFS volume.
Important APIs/types/functions: `PersistentVolumeClaim`, `dataSource.kind: PersistentVolumeClaim`, source `cephfs-pvc`, `storageClassName: rook-cephfs`, and RWX access mode.
Control flow: the external provisioner detects `dataSource`, calls CSI clone support on the CephFS driver, and creates a new 1Gi PVC initialized from the source volume. State is stored as a new PVC/PV and CephFS subvolume clone. Dependencies are a bound source PVC in the same namespace, CSI clone feature support, and compatible StorageClass/access mode. Risks: source PVC must not be absent or in an incompatible namespace; clone behavior may be snapshot-backed and consume backend metadata. Test signals: clone PVC reaches Bound, contents match the source at clone time, and source/clone diverge independently after writes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-restore.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-restore.yaml

Purpose: restores a new CephFS PVC from a `VolumeSnapshot`.
Important APIs/types/functions: `PersistentVolumeClaim`, `dataSource.kind: VolumeSnapshot`, `apiGroup: snapshot.storage.k8s.io`, snapshot `cephfs-pvc-snapshot`, and StorageClass `rook-cephfs`.
Control flow: the external provisioner resolves the snapshot object, invokes CSI create-from-snapshot on the CephFS driver, and binds a new PVC with restored content. State lives in the new PVC/PV and backend CephFS subvolume; source snapshot state remains separate. Dependencies are snapshot CRDs/controller, a ready snapshot from `snapshot.yaml`, and matching CSI snapshot class. Risks: restore fails if snapshot is not ready, class or source volume size is incompatible, or snapshot deletion policy removed backend data. Test signals: restored PVC Bound, data matches snapshot point in time, and the PVC can mount through `pod.yaml`-style workload.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/pvc.yaml

Purpose: baseline CephFS PVC used by pod, snapshot, clone, and group snapshot examples.
Important APIs/types/functions: `PersistentVolumeClaim` `cephfs-pvc`, label `group: snapshot-test`, access mode `ReadWriteOnce`, request `1Gi`, and StorageClass `rook-cephfs`.
Control flow: Kubernetes asks the CephFS CSI provisioner to create a subvolume in the configured filesystem/pool and binds the resulting PV to this claim. State is persisted in Kubernetes PV/PVC objects and CephFS subvolume metadata. Dependencies are the `rook-cephfs` StorageClass and Rook CephFS secrets. Risks: CephFS commonly supports RWX, but this sample uses RWO, so it only validates single-writer semantics; the label controls inclusion in group snapshots. Test signals: PVC transitions to Bound, PV uses `rook-ceph.cephfs.csi.ceph.com`, and snapshot/clone examples can reference it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/snapshot.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/snapshot.yaml

Purpose: creates a point-in-time snapshot of the example CephFS PVC.
Important APIs/types/functions: `VolumeSnapshot`, `volumeSnapshotClassName: csi-cephfsplugin-snapclass`, and `source.persistentVolumeClaimName: cephfs-pvc`.
Control flow: the snapshot controller creates a `VolumeSnapshotContent`, calls the CephFS CSI snapshotter, and records readiness in `VolumeSnapshot.status`. Snapshot state is stored both in Kubernetes snapshot objects and backend CephFS snapshot/subvolume metadata. Dependencies are `snapshotclass.yaml`, snapshot CRDs/controller, a bound source PVC, and CephFS CSI snapshot support. Risks: snapshots are crash-consistent at the volume level, deletion policy is defined by the class, and source PVC writes may continue during snapshot creation. Test signals: `readyToUse: true`, non-empty restore size, and `pvc-restore.yaml` can create a usable volume from it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/snapshotclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/snapshotclass.yaml

Purpose: defines the standard CephFS CSI `VolumeSnapshotClass`.
Important APIs/types/functions: `VolumeSnapshotClass`, driver `rook-ceph.cephfs.csi.ceph.com`, `clusterID`, snapshotter secret name/namespace, and `deletionPolicy: Delete`.
Control flow: the snapshot controller maps `VolumeSnapshot` requests to this class, supplies secret parameters to the CephFS CSI driver, and deletes backend snapshots when snapshot content is removed. State is a cluster-scoped class plus generated `VolumeSnapshotContent`. Dependencies are CephFS CSI, Rook provisioner secret, and snapshot external controller. Risks: secret namespace must track the Rook namespace, delete policy can remove restore points, and driver name must match the installed CSIDriver. Test signals: class exists, `snapshot.yaml` reaches ready, and deletion cleans up content without orphan errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass-ec.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass-ec.yaml

Purpose: example CephFS StorageClass targeting an erasure-coded CephFS data pool.
Important APIs/types/functions: `StorageClass` `rook-cephfs`, provisioner `rook-ceph.cephfs.csi.ceph.com`, `clusterID`, `fsName: myfs-ec`, `pool: myfs-ec-erasurecoded`, CSI secret parameters, expansion, reclaim policy, and optional mount debug flag.
Control flow: dynamic provisioning creates CephFS subvolumes in the named filesystem and pool; expansion requests route through controller expand secrets. Persistent state is CephFS subvolumes and Kubernetes PV/PVC objects. Dependencies are a `CephFilesystem` like `filesystem-ec.yaml`, Rook-generated CephFS CSI secrets, and an EC data pool with a replicated default pool. Risks: EC pools need enough OSDs, filesystem name must match the deployed CR, and using the same `rook-cephfs` name as the replicated class means only one can be installed at a time. Test signals: PVC binds, writes succeed, expansion works, and Ceph reports subvolume data in the EC pool.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass-ec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass.yaml

Purpose: primary CephFS dynamic provisioning StorageClass for replicated filesystem examples.
Important APIs/types/functions: `StorageClass` `rook-cephfs`, `clusterID: rook-ceph`, `fsName: myfs`, `pool: myfs-replicated`, provisioner/controller-publish/node-stage secrets, optional encryption and mounter parameters, `allowVolumeExpansion`, and `mountOptions`.
Control flow: PVC creation calls the CephFS CSI provisioner to create a subvolume in `myfs`; node staging mounts it with kernel client or ceph-fuse; expansion uses controller expand credentials. State persists in Kubernetes PV/PVCs, CephFS subvolumes, and optional KMS if encryption is enabled. Dependencies are `filesystem.yaml`, Rook CSI secrets, CephFS CSI sidecars, and Kubernetes StorageClass support. Risks: secret namespace coupling, optional encrypted volumes require KMS config, mounter choice affects node prerequisites, and delete reclaim policy removes backend data. Test signals: sample PVC binds, pod can mount/write, expansion changes capacity, and CSI logs show expected filesystem/pool.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/driver.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/driver.yaml

Purpose: deploys the Rook-managed Ceph NFS CSI `Driver` custom resource.
Important APIs/types/functions: `csi.ceph.io/v1` `Driver`, name `rook-ceph.nfs.csi.ceph.com`, `fsGroupPolicy: File`, node plugin rolling update strategy, and controller plugin block.
Control flow: the Rook CSI operator reconciles this CR into controller and node plugin workloads for the NFS CSI driver. State is the driver CR and generated CSI Kubernetes resources. Dependencies are Rook CSI operator CRDs, namespace `rook-ceph`, and Ceph NFS support. Risks: the custom Driver API must be installed, driver name must match StorageClasses and snapshot classes, and empty controllerPlugin relies on defaults. Test signals: CSIDriver appears, controller/node pods become ready, and `storageclass.yaml` provisions an NFS PVC.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/pod.yaml

Purpose: validates an NFS CSI PVC by mounting it into an nginx pod.
Important APIs/types/functions: `Pod` `csinfs-demo-pod`, `persistentVolumeClaim.claimName: nfs-pvc`, and mount path `/var/lib/www/html`.
Control flow: kubelet stages/publishes the NFS CSI volume from the bound PVC into the container. Persistent state is in the referenced PVC/PV and backend CephFS export managed by the NFS CSI driver. Dependencies are `pvc.yaml`, `storageclass.yaml`, the NFS CSI node plugin, and an active CephNFS server. Risks: sample PVC requests RWO although NFS can support shared access, and no readiness probe verifies filesystem writes. Test signals: pod Ready, mount is NFS-backed, writes under the mount persist across pod recreation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc-clone.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/pvc-clone.yaml

Purpose: demonstrates cloning an NFS CSI PVC.
Important APIs/types/functions: `PersistentVolumeClaim` `nfs-pvc-clone`, `dataSource.kind: PersistentVolumeClaim`, source `nfs-pvc`, StorageClass `rook-nfs`, and RWX access mode.
Control flow: Kubernetes invokes CSI clone support through the NFS driver to create a new exported volume initialized from `nfs-pvc`. State persists as a new PV/PVC and underlying CephFS/NFS export resources. Dependencies are a bound source PVC, CSI clone support in the NFS driver path, and compatible requested size/access mode. Risks: clone support depends on backend CephFS behavior, source namespace must match, and access mode differs from the base example. Test signals: cloned PVC Bound, data copied from source, and source/clone mutations are independent.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc-restore.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/pvc-restore.yaml

Purpose: restores an NFS CSI PVC from a snapshot.
Important APIs/types/functions: `PersistentVolumeClaim`, `dataSource.kind: VolumeSnapshot`, `apiGroup: snapshot.storage.k8s.io`, source `nfs-pvc-snapshot`, and StorageClass `rook-nfs`.
Control flow: the provisioner resolves the ready snapshot and asks the NFS CSI driver to create a new 1Gi volume/export from it. State is a new PVC/PV and backend exported volume; the snapshot object remains separate. Dependencies are `snapshot.yaml`, `snapshotclass.yaml`, snapshot CRDs/controller, and NFS CSI restore support. Risks: snapshot may not be ready, restore size must be compatible, and deletion policies can remove backend snapshot content. Test signals: restored PVC Bound, pod mount succeeds, and data reflects the snapshot point.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/pvc.yaml

Purpose: baseline PVC for the Rook NFS CSI examples.
Important APIs/types/functions: `PersistentVolumeClaim` `nfs-pvc`, access mode `ReadWriteOnce`, size `1Gi`, and `storageClassName: rook-nfs`.
Control flow: the NFS CSI provisioner creates or references a Ceph-backed NFS export and binds a PV to this claim. State persists in Kubernetes PV/PVC objects, CephFS backing storage, and NFS export metadata. Dependencies are the `rook-nfs` StorageClass, NFS CSI driver CR, and CephNFS service. Risks: RWO does not exercise multi-writer NFS semantics, backend export server must be reachable by nodes, and delete reclaim removes data. Test signals: PVC Bound, PV provisioner is `rook-ceph.nfs.csi.ceph.com`, and the NFS pod can mount it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/snapshot.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/snapshot.yaml

Purpose: creates a snapshot of the NFS CSI example PVC.
Important APIs/types/functions: `VolumeSnapshot`, snapshot class `csi-nfsplugin-snapclass`, and source PVC `nfs-pvc`.
Control flow: the snapshot controller asks the NFS CSI driver to snapshot the backing volume/export and records readiness on the snapshot object. State spans Kubernetes snapshot resources and backend Ceph snapshot data. Dependencies are snapshot CRDs/controller, NFS snapshot class, a bound PVC, and driver snapshot support. Risks: snapshot consistency depends on active workload writes and backend implementation; delete policy comes from the class. Test signals: `readyToUse` true and `pvc-restore.yaml` can create a PVC from it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/snapshotclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/snapshotclass.yaml

Purpose: defines the NFS CSI `VolumeSnapshotClass`.
Important APIs/types/functions: `VolumeSnapshotClass`, driver `rook-ceph.nfs.csi.ceph.com`, `clusterID`, snapshotter secret parameters that reuse CephFS provisioner credentials, and `deletionPolicy: Delete`.
Control flow: the external snapshotter uses this class to route NFS snapshot operations and provide credentials to the driver. State is cluster-scoped class configuration plus generated snapshot content. Dependencies are NFS CSI driver, Rook CSI CephFS provisioner secret, and snapshot controller. Risks: secret reuse couples NFS snapshotting to CephFS secret names, driver name mismatch prevents binding, and deletion policy destroys backend snapshots. Test signals: class accepted, snapshot reaches ready, and deletion removes snapshot content cleanly.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/storageclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nfs/storageclass.yaml

Purpose: dynamic provisioning StorageClass for Rook Ceph NFS exports.
Important APIs/types/functions: `StorageClass` `rook-nfs`, provisioner `rook-ceph.nfs.csi.ceph.com`, `nfsCluster`, `server`, `clusterID`, `fsName`, `pool`, CSI secret parameters, expansion, and optional debug mount option.
Control flow: PVC provisioning creates CephFS-backed NFS export resources against the named NFS cluster/server, then node publish mounts the NFS export. State persists in PV/PVC objects, CephFS subvolumes, NFS export metadata, and Ceph credentials. Dependencies are a `CephNFS` named `my-nfs`, service `rook-ceph-nfs-my-nfs-a`, filesystem `myfs`, pool `myfs-replicated`, and CephFS CSI secrets. Risks: hard-coded service/name coupling, NFS server availability, and secret namespace drift. Test signals: PVC Bound, export exists on the NFS cluster, pod mount succeeds, and expansion is reflected in PVC capacity.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nfs/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/driver.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/driver.yaml

Purpose: declares the NVMe-oF CSI driver managed by the Rook CSI operator.
Important APIs/types/functions: `csi.ceph.io/v1` `Driver`, name `rook-ceph.nvmeof.csi.ceph.com`, namespace `rook-ceph`, and `controllerPlugin.hostNetwork: false`.
Control flow: the CSI operator reconciles this CR into NVMe-oF controller and node plugin resources. State is Kubernetes Driver CR plus generated CSI workloads. Dependencies are Rook CSI operator support for NVMe-oF and matching StorageClass provisioner name. Risks: NVMe-oF CSI is more environment-sensitive than filesystem examples, and host networking choice must match gateway reachability. Test signals: CSIDriver and pods are ready, sidecars register the provisioner, and `pvc.yaml` provisions via `storageclass.yaml`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/driver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/nvmeof-pool.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/nvmeof-pool.yaml

Purpose: creates the Ceph block pool backing NVMe-oF CSI volumes.
Important APIs/types/functions: `CephBlockPool` `nvmeof`, namespace `rook-ceph`, `failureDomain: host`, and replicated `size: 3`.
Control flow: Rook operator reconciles the pool CR into a Ceph RADOS pool; the NVMe-oF StorageClass references this pool for image allocation. State is persisted in the CephBlockPool CR and Ceph pool metadata/data. Dependencies are a healthy CephCluster with at least enough OSD failure domains for replica size 3. Risks: insufficient hosts/OSDs block or degrade pool creation, and pool name must match `storageclass.yaml`. Test signals: CephBlockPool Ready, Ceph reports pool `nvmeof`, and PVC provisioning allocates images there.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/nvmeof-pool.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/pod.yaml

Purpose: test pod for mounting an NVMe-oF CSI PVC and periodically reporting filesystem usage.
Important APIs/types/functions: `Pod` `nvmeof-test-pod`, `busybox`, shell loop, `df -h /mnt/nvmeof`, PVC `nvmeof-external-volume`, and `restartPolicy: Never`.
Control flow: kubelet stages the NVMe-oF volume, mounts it at `/mnt/nvmeof`, and the container loops every 45 seconds printing mount status. Persistent state is the referenced PVC/PV and RBD/NVMe-oF backend image; pod state is transient. Dependencies are a bound `nvmeof-external-volume`, NVMe-oF node connectivity, and the StorageClass gateway configuration. Risks: `restartPolicy: Never` does not self-heal, busybox command only checks mount visibility, and gateway/listener DNS must be reachable. Test signals: pod Running, `df` output includes the mounted volume, and pod logs continue without I/O errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/pvc.yaml

Purpose: baseline PVC for the NVMe-oF CSI StorageClass.
Important APIs/types/functions: `PersistentVolumeClaim` `nvmeof-external-volume`, namespace `default`, StorageClass `ceph-nvmeof`, RWO access mode, and `128Mi` request.
Control flow: the external provisioner allocates an RBD image in the configured pool and exposes it through the NVMe-oF gateway/subsystem. State persists in PVC/PV objects, Ceph RBD image metadata, and gateway namespace/subsystem configuration. Dependencies are `storageclass.yaml`, `nvmeof-pool.yaml`, Rook NVMe-oF gateway, and RBD CSI secrets. Risks: small test size may not cover production alignment, gateway provisioning must succeed, and namespace defaults differ from Rook namespace. Test signals: PVC Bound, PV references NVMe-oF CSI driver, and the test pod can mount it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/storageclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/nvmeof/storageclass.yaml

Purpose: StorageClass for provisioning RBD-backed volumes exposed through Ceph NVMe-oF.
Important APIs/types/functions: `StorageClass` `ceph-nvmeof`, provisioner `rook-ceph.nvmeof.csi.ceph.com`, `clusterID`, pool `nvmeof`, `subsystemNQN`, management gateway address/port, JSON `listeners`, RBD CSI secret parameters, image format/features, `Immediate` binding, and expansion.
Control flow: PVC creation allocates an RBD image, configures NVMe-oF gateway namespace/subsystem via the management API, and node staging connects workers to listed gateway listeners. State persists in PV/PVCs, RBD images, and NVMe-oF gateway configuration. Dependencies are gateway service DNS, SPDK/NVMe-oF subsystem naming, RBD provisioner/node secrets, and the `nvmeof` pool. Risks: single listener is not HA despite comments, NQN/address are hard-coded, feature set must be kernel/client compatible, and gateway API port reachability is required. Test signals: PVC Bound, gateway reports namespace, node connects to listener, expansion works.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/nvmeof/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pod-ephemeral.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pod-ephemeral.yaml

Purpose: demonstrates a generic ephemeral inline RBD volume for an nginx pod.
Important APIs/types/functions: `Pod`, `ephemeral.volumeClaimTemplate`, StorageClass `rook-ceph-block`, RWO access mode, and mount path `/myspace`.
Control flow: kubelet creates a pod-scoped PVC from the template, the RBD CSI provisioner creates an image, and the node plugin maps/formats/mounts it into the container; deletion of the pod removes the generated claim and backend image. State is temporary and tied to pod lifetime. Dependencies are generic ephemeral volume support, RBD CSI provisioner/node plugin, and `rook-ceph-block` StorageClass. Risks: data is deleted with the pod, RBD is single-writer by default, and image mapping needs node kernel/nbd support. Test signals: generated PVC appears, pod Ready, mount writable, and generated PVC/image are cleaned up after pod deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pod-ephemeral.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pod.yaml

Purpose: validates the standard RBD PVC by mounting it into nginx.
Important APIs/types/functions: `Pod` `csirbd-demo-pod`, PVC `rbd-pvc`, and mount path `/var/lib/www/html`.
Control flow: kubelet stages/maps the RBD image, formats if needed, mounts it, and publishes it to the container path. State persists in the referenced PVC/PV and RBD image. Dependencies are `pvc.yaml`, `storageclass.yaml`, RBD CSI node plugin, and Ceph credentials. Risks: RBD RWO volumes cannot be mounted read-write by multiple nodes, sample lacks probes, and node kernel/nbd mapping failures surface as pod mount errors. Test signals: pod Ready, mount writable, data persists after pod recreation, and RBD image appears in the configured pool.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc-clone.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pvc-clone.yaml

Purpose: demonstrates RBD PVC cloning.
Important APIs/types/functions: `PersistentVolumeClaim` `rbd-pvc-clone`, `dataSource.kind: PersistentVolumeClaim`, source `rbd-pvc`, StorageClass `rook-ceph-block`, and RWO access mode.
Control flow: the CSI provisioner creates a new RBD image cloned from the source PVC image, usually through snapshot/clone mechanics provided by RBD. State persists as a new PVC/PV and RBD image. Dependencies are a bound source PVC, RBD CSI clone support, and image features such as `layering`. Risks: source and clone must be in the same namespace, clone support depends on StorageClass features, and clone chains may affect cleanup/performance. Test signals: clone PVC Bound, data equals source at clone time, and deleting source does not break clone.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc-clone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc-restore.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pvc-restore.yaml

Purpose: restores a new RBD PVC from an RBD volume snapshot.
Important APIs/types/functions: `PersistentVolumeClaim`, `dataSource.kind: VolumeSnapshot`, `apiGroup: snapshot.storage.k8s.io`, source `rbd-pvc-snapshot`, and StorageClass `rook-ceph-block`.
Control flow: the external provisioner resolves the snapshot and asks RBD CSI to create a new image from it, then binds the PVC. State persists in the new PV/PVC and cloned/restored RBD image. Dependencies are snapshot CRDs/controller, a ready snapshot from `snapshot.yaml`, `snapshotclass.yaml`, and compatible image features. Risks: restore requires snapshot content to exist, restored size cannot be smaller than source, and deletion policy may remove backend snapshots. Test signals: PVC Bound, pod mount succeeds, and data matches the snapshot point.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc-restore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/pvc.yaml

Purpose: baseline RBD block-backed filesystem PVC.
Important APIs/types/functions: `PersistentVolumeClaim` `rbd-pvc`, RWO access mode, `1Gi` request, and StorageClass `rook-ceph-block`.
Control flow: RBD CSI creates an image in the configured pool and binds it as a filesystem volume for pods. State persists in Kubernetes PV/PVC objects and Ceph RBD image metadata/data. Dependencies are the RBD StorageClass, Rook CSI secrets, and a healthy CephBlockPool. Risks: delete reclaim policy from the StorageClass removes image data, RWO limits scheduling, and missing image features can break clone/snapshot examples. Test signals: PVC Bound, PV provisioner `rook-ceph.rbd.csi.ceph.com`, and pod mount/write succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pod.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pod.yaml

Purpose: demonstrates consuming an RBD PVC as a raw block device.
Important APIs/types/functions: `Pod` `csirbd-block-demo-pod`, `volumeDevices`, device path `/dev/xvda`, CentOS sleep container, and PVC `raw-block-rbd-pvc`.
Control flow: kubelet stages/maps the RBD image but passes it as a block device rather than formatting/mounting it; the container sees `/dev/xvda`. State persists in the raw-block PVC and RBD image; filesystem state is left to the workload. Dependencies are `raw-block-pvc.yaml`, RBD CSI block volume support, and privileged-enough container/device handling by kubelet. Risks: the device path can be overwritten by workload commands, no filesystem is created, and data interpretation is application-defined. Test signals: pod Running, `/dev/xvda` exists, block reads/writes work, and no mount is created.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pvc.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pvc.yaml

Purpose: provisions an RBD volume in Kubernetes raw block mode.
Important APIs/types/functions: `PersistentVolumeClaim` `raw-block-rbd-pvc`, `volumeMode: Block`, RWO access mode, `1Gi` request, and StorageClass `rook-ceph-block`.
Control flow: RBD CSI creates an image and binds it as a block PV; node publish maps it directly into pods via `volumeDevices`. State persists in PV/PVC metadata and the RBD image. Dependencies are RBD CSI support for `volumeMode: Block` and the referenced StorageClass/pool. Risks: workloads must handle partitioning/filesystem/application data safely, and the example does not include a filesystem check. Test signals: PVC Bound with block volume mode, raw-block pod sees a device, and writes persist after pod restart.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/raw-block-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/snapshot.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/snapshot.yaml

Purpose: creates a CSI snapshot of the baseline RBD PVC.
Important APIs/types/functions: `VolumeSnapshot`, `volumeSnapshotClassName: csi-rbdplugin-snapclass`, and source PVC `rbd-pvc`.
Control flow: the snapshot controller asks RBD CSI to snapshot the backing image and records readiness/restore size in Kubernetes snapshot status. State is persisted in `VolumeSnapshot`, `VolumeSnapshotContent`, and RBD snapshot metadata. Dependencies are snapshot CRDs/controller, RBD snapshot class, and a bound source PVC. Risks: active filesystem writes may require application quiescing for application consistency, delete policy removes backend snapshot data, and image features must support snapshot/clone use. Test signals: snapshot `readyToUse` true, RBD lists a snapshot, and `pvc-restore.yaml` succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/snapshotclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/snapshotclass.yaml

Purpose: defines the RBD CSI `VolumeSnapshotClass`.
Important APIs/types/functions: `VolumeSnapshotClass`, driver `rook-ceph.rbd.csi.ceph.com`, `clusterID`, RBD snapshotter secret parameters, and `deletionPolicy: Delete`.
Control flow: snapshot requests referencing this class are routed to the RBD CSI driver with Rook provisioner credentials; deletion of snapshot content removes backend RBD snapshots. State is cluster-scoped class configuration and generated snapshot content. Dependencies are RBD CSI sidecars, Rook provisioner secret in `rook-ceph`, and snapshot CRDs/controller. Risks: wrong secret namespace or driver name breaks snapshots; delete policy is destructive. Test signals: class exists, `snapshot.yaml` reaches ready, and deleting the snapshot removes content without stuck finalizers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-ec.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-ec.yaml

Purpose: production-style RBD StorageClass using an erasure-coded data pool with a replicated metadata pool.
Important APIs/types/functions: `CephBlockPool` `replicated-metadata-pool`, `CephBlockPool` `ec-data-pool`, `StorageClass` `rook-ceph-block`, RBD provisioner, `dataPool`, `pool`, image format/features, CSI secret parameters, filesystem type, expansion, and delete reclaim.
Control flow: Rook creates the pools; PVC provisioning creates RBD images whose metadata resides in the replicated pool and data in the EC pool. State persists in Ceph pools, RBD image metadata/data, and PV/PVC objects. Dependencies are at least three OSD failure domains, RBD CSI, and Rook secrets. Risks: EC pool requirements, metadata pool replica size 2 may be less durable than default production patterns, image features are conservative `layering`, and same StorageClass name conflicts with non-EC examples. Test signals: pools Ready, PVC Bound, data objects land in EC pool, snapshots/clones still work.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-ec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-test.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-test.yaml

Purpose: low-redundancy RBD StorageClass for test clusters with a single OSD.
Important APIs/types/functions: `CephBlockPool` `replicapool`, `failureDomain: osd`, `replicated.size: 1`, `requireSafeReplicaSize: false`, StorageClass `rook-ceph-block`, RBD CSI secret parameters, `imageFeatures: layering`, and expansion.
Control flow: Rook creates a single-replica pool; RBD CSI provisions images there for PVCs. State persists in a deliberately unsafe Ceph pool and Kubernetes PV/PVCs. Dependencies are Rook CephCluster, RBD CSI, and `rook-ceph` secrets. Risks: explicit data-loss risk with replica 1, not production-safe, and same StorageClass name as production examples can overwrite intent. Test signals: pool Ready on one OSD, PVC binds, pod mounts, and tests avoid using it for durable data.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass.yaml -->
# sources/control-plane/rook/deploy/examples/csi/rbd/storageclass.yaml

Purpose: primary replicated RBD pool and StorageClass example.
Important APIs/types/functions: `CephBlockPool` `replicapool`, `failureDomain: host`, `replicated.size: 3`, `requireSafeReplicaSize: true`, StorageClass `rook-ceph-block`, RBD provisioner, image format/features, optional map/unmap/encryption/KMS/mounter settings, CSI secrets, `fstype: ext4`, expansion, and delete reclaim.
Control flow: Rook creates the replicated pool; PVC provisioning creates RBD images in `replicapool`; node publish maps and formats images for pods. State persists in Ceph pool/image data and Kubernetes PV/PVCs. Dependencies are a healthy multi-host Ceph cluster, RBD CSI sidecars/node plugin, and Rook-generated secrets. Risks: hard-coded namespace/secret names, older kernels require conservative image features, optional `rbd-nbd` is not recommended for production in comments, and delete reclaim removes images. Test signals: pool Ready, PVC Bound, pod mount works, expansion succeeds, and snapshot/clone examples pass.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/rbd/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-external-http.yaml -->
# sources/control-plane/rook/deploy/examples/dashboard-external-http.yaml

Purpose: exposes the active Ceph manager dashboard HTTP port through a Kubernetes `NodePort` Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-external-http`, namespace `rook-ceph`, port/targetPort `7000`, selector labels `app: rook-ceph-mgr`, `mgr_role: active`, and `rook_cluster`.
Control flow: Kubernetes routes NodePort traffic to the active mgr pod matching the selector. State is only the Service object and endpoint slices derived from pod labels. Dependencies are a Ceph manager dashboard listening on HTTP port 7000 and Rook labels. Risks: HTTP exposure is unauthenticated transport unless dashboard itself enforces auth, active mgr label changes must update endpoints, and NodePort opens cluster nodes. Test signals: Service endpoints point to one active mgr, NodePort responds, and failover updates endpoints.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-external-http.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-external-https.yaml -->
# sources/control-plane/rook/deploy/examples/dashboard-external-https.yaml

Purpose: exposes the Ceph manager dashboard HTTPS port with a `NodePort` Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-external-https`, port/targetPort `8443`, selector `app: rook-ceph-mgr`, `mgr_role: active`, `rook_cluster`, and `type: NodePort`.
Control flow: Kubernetes creates external node-level access to the active mgr dashboard HTTPS endpoint. State is Service/endpoints only; dashboard sessions remain in Ceph mgr. Dependencies are dashboard enabled on port 8443 and Rook active mgr labels. Risks: NodePort surface area, self-signed cert handling by clients, and endpoint loss during mgr failover. Test signals: endpoint exists, HTTPS request reaches dashboard, certificate/auth behavior is expected, and endpoints update after mgr failover.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-external-https.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-ingress-https.yaml -->
# sources/control-plane/rook/deploy/examples/dashboard-ingress-https.yaml

Purpose: ingress example for routing HTTPS traffic to the Ceph dashboard through nginx ingress and ACME TLS.
Important APIs/types/functions: `networking.k8s.io/v1` `Ingress`, `ingressClassName: nginx`, TLS host `rook-ceph.example.com`, service backend `rook-ceph-mgr-dashboard` port `https-dashboard`, and nginx annotations for HTTPS backend and disabled upstream cert verification.
Control flow: the ingress controller terminates external TLS for the configured host, then proxies to the dashboard Service over HTTPS while skipping backend certificate verification. State persists in the Ingress and TLS Secret; routing state is maintained by the ingress controller. Dependencies are the internal dashboard Service, nginx ingress, DNS, and ACME/cert-manager if used. Risks: `proxy_ssl_verify off` trusts the backend blindly, placeholder host/secret must be replaced, and ingress only works if the dashboard Service exists. Test signals: ingress admitted, TLS secret issued, host resolves, and browser reaches the dashboard.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-ingress-https.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-loadbalancer.yaml -->
# sources/control-plane/rook/deploy/examples/dashboard-loadbalancer.yaml

Purpose: exposes the Ceph manager dashboard HTTPS endpoint through a cloud/load-balancer Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-loadbalancer`, port/targetPort `8443`, active mgr selector labels, and `type: LoadBalancer`.
Control flow: Kubernetes/cloud controller allocates an external load balancer and routes it to the active mgr dashboard endpoint. State includes Service status load-balancer ingress and endpoint slices. Dependencies are cloud/load balancer support, dashboard HTTPS, and Rook mgr labels. Risks: public exposure of an administrative dashboard, cloud firewall defaults, self-signed certificates, and endpoint churn on mgr failover. Test signals: external IP assigned, endpoints point at active mgr, HTTPS dashboard reachable, and failover maintains routing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/dashboard-loadbalancer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/direct-mount.yaml -->
# sources/control-plane/rook/deploy/examples/direct-mount.yaml

Purpose: privileged toolbox-style Deployment for directly mounting Ceph devices/filesystems from a pod using host kernel facilities.
Important APIs/types/functions: `Deployment` `rook-direct-mount`, image `docker.io/rook/ceph:master`, command `/usr/local/bin/toolbox.sh`, `serviceAccountName: rook-ceph-default`, `hostNetwork: true`, privileged root security context, hostPath mounts `/dev`, `/sys/bus`, `/lib/modules`, Rook mon secret, and mon endpoints ConfigMap.
Control flow: Kubernetes starts a privileged pod with host device and module access; the Rook toolbox entrypoint can run Ceph commands and direct mount/map operations using injected mon endpoints and secrets. State is operational and host-level; persistent data remains in Ceph, while pod state is ephemeral. Dependencies are Rook mon secret/configmap and host kernel modules. Risks: broad host/device privilege, `master` image tag drift, hostNetwork requirement, and secret exposure. Test signals: pod Running, Ceph CLI authenticates, `rbd map` or CephFS mount works, and cleanup unmaps devices.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/direct-mount.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/cluster-external.yaml -->
# sources/control-plane/rook/deploy/examples/external/cluster-external.yaml

Purpose: minimal `CephCluster` CR for a Kubernetes consumer cluster that connects to an external Ceph cluster.
Important APIs/types/functions: `CephCluster` `rook-ceph-external`, `spec.external.enable: true`, disabled crash collector, daemon health check for mons, and optional external mgr monitoring endpoints.
Control flow: Rook reconciles this CR without provisioning local Ceph daemons, instead using imported external cluster secrets/configmaps to represent and monitor the external cluster. State is the CephCluster CR status plus imported credentials/endpoints. Dependencies are `common-external.yaml`, external-cluster import resources, Rook operator, and external Ceph availability. Risks: missing imported secrets prevents readiness, monitoring endpoints are optional/commented, and crash collection is disabled. Test signals: CephCluster becomes Connected/Ready, operator logs external mode, and storage classes using imported credentials provision volumes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/cluster-external.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/common-external.yaml -->
# sources/control-plane/rook/deploy/examples/external/common-external.yaml

Purpose: common namespace, service accounts, roles, and role bindings required for external Ceph cluster mode.
Important APIs/types/functions: `Namespace` `rook-ceph`, `RoleBinding` `rook-ceph-cluster-mgmt`, `RoleBinding` and `Role` `rook-ceph-cmd-reporter`, service accounts `rook-ceph-cmd-reporter` and `rook-ceph-default`, and permissions over pods/configmaps.
Control flow: applying the manifest prepares RBAC and service accounts that Rook uses to manage external-cluster resources and command reporting in the consumer namespace. State persists in Kubernetes RBAC objects. Dependencies are existing ClusterRole `rook-ceph-cluster-mgmt`, operator service account namespace alignment, and Rook CRDs/operator install order. Risks: namespace comments must be substituted consistently, duplicate instructions in the header can confuse apply order, and RBAC over pods/configmaps is intentionally broad for command reporting. Test signals: rolebindings resolve valid subjects/roles, service accounts exist, and external CephCluster reconciliation does not fail RBAC checks.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/common-external.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/create-external-cluster-resources-tests.py -->
# sources/control-plane/rook/deploy/examples/external/create-external-cluster-resources-tests.py

Purpose: unit tests for the external cluster resource generation script using `DummyRados`.
Important APIs/types/functions: `unittest.TestCase` `TestRadosJSON`, dynamic import of `create-external-cluster-resources`, setup with `RadosJSON` arguments, DummyRados substitution, and tests for JSON/bash output, CephFS keyring permissions, command failures, multi-filesystem/data-pool handling, RGW endpoint validation, permission upgrade, monitoring endpoint validation, skip-monitoring behavior, and v2 monitor port.
Control flow: each test constructs or mutates a `RadosJSON` instance, adjusts dummy command output maps or parser flags, calls target methods, and asserts exceptions or output state. State is in-memory test object fields and dummy command fixtures; no real Ceph/Kubernetes resources are mutated. Dependencies are Python stdlib, sibling script import path, and DummyRados coverage. Risks: tests print heavily and use broad try/except patterns instead of precise assertions; real rados paths are bypassed. Test signals: `python3 -m unittest --verbose create-external-cluster-resources-tests` passes and covers error branches.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/create-external-cluster-resources-tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/create-external-cluster-resources.py -->
# sources/control-plane/rook/deploy/examples/external/create-external-cluster-resources.py

Purpose: generates JSON or shell exports needed to import an existing Ceph cluster into a Rook consumer Kubernetes cluster.
Important APIs/types/functions: `ExecutionFailureException`, `DummyRados`, `S3Auth`, and `RadosJSON`. Major methods parse CLI/config flags, run Ceph monitor commands through `rados`, validate pools/namespaces/topology/RGW/monitoring endpoints, create or upgrade CephX users, generate CSI and health-checker caps, initialize RBD pools, create/pin CephFS subvolume groups, create RGW admin-ops users, and emit ConfigMap/Secret/StorageClass-shaped JSON or bash exports.
Control flow: `main()` resolves key generation for rotate/revert, supports upgrade mode, otherwise calls `gen_json_out()` or `gen_shell_out()`. `_gen_output_map()` is the central orchestration: validates RBD and CephFS inputs, collects fsid/mon/mgr/RGW data, creates keyrings, records output variables, and conditionally adds monitoring, topology, RADOS namespace, CephFS, RBD, and RGW resources. State is mostly `self.out_map`, parser fields mutated by discovery, CephX users and RGW users created in the external Ceph cluster, and optional output files. Dependencies are `rados`, `rbd`, `requests`, `subprocess` calls to `ceph`/`radosgw-admin`, Python config/URL/IP libraries, and the import shell script consuming the bash exports. Risks: it performs real credential and user mutations, broad `except` blocks hide detail in places, output includes secrets, config-file precedence uses `sys.argv` string search, and endpoint validation depends on live network/manager modules. Test signals: sibling unit tests with DummyRados, dry-run output, successful JSON parse, and import script applying generated resources.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/create-external-cluster-resources.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/dashboard-external-http.yaml -->
# sources/control-plane/rook/deploy/examples/external/dashboard-external-http.yaml

Purpose: external-cluster variant of the Ceph dashboard HTTP NodePort Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-external-http`, namespace `rook-ceph`, port `7000`, selector labels for active mgr, and `type: NodePort`.
Control flow: Kubernetes exposes the active mgr dashboard HTTP endpoint discovered/imported for the external cluster. State is Service/endpoints only. Dependencies are external cluster mgr dashboard service/pods represented by Rook labels and namespace consistency. Risks: HTTP administrative dashboard exposure, active mgr endpoint availability in external mode, and hard-coded namespace/cluster labels. Test signals: endpoints resolve, NodePort responds on port 7000, and active mgr failover updates endpoints.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/dashboard-external-http.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/dashboard-external-https.yaml -->
# sources/control-plane/rook/deploy/examples/external/dashboard-external-https.yaml

Purpose: external-cluster variant of the Ceph dashboard HTTPS NodePort Service.
Important APIs/types/functions: `Service` `rook-ceph-mgr-dashboard-external-https`, port/targetPort `8443`, active mgr selector labels, and `type: NodePort`.
Control flow: Kubernetes routes node-level HTTPS traffic to the active mgr dashboard endpoint for the external cluster representation. State is Service/endpoints. Dependencies are dashboard HTTPS availability and Rook external mgr service labeling. Risks: administrative exposure, self-signed certificates, and endpoint mismatch if external cluster labels differ. Test signals: endpoint exists, NodePort answers HTTPS, and dashboard login works through the imported cluster credentials.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/dashboard-external-https.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/import-external-cluster.sh -->
# sources/control-plane/rook/deploy/examples/external/import-external-cluster.sh

Purpose: imports generated external Ceph cluster values into Kubernetes by creating namespaces, secrets, configmaps, optional CRs, and StorageClasses.
Important APIs/types/functions: environment variables from `create-external-cluster-resources.py`, `checkEnvVars`, `createClusterNamespace`, `importClusterID`, `importSecret`, `importConfigMap`, `createInputCommadConfigMap`, CSI secret import functions, `createRBDStorageClass`, `createECRBDStorageClass`, `createCephFSStorageClass`, topology helpers, and optional RADOS namespace/subvolume group CR creation.
Control flow: the script validates required env vars and kubectl context, ensures the namespace, optionally creates RADOS namespace/subvolume group CRs and derives cluster IDs, creates or patches mon and CSI secrets/configmaps, optionally creates RGW admin secret, then emits StorageClasses for RBD, EC RBD, CephFS, and topology-constrained RBD based on available variables. State persists in Kubernetes secrets, configmaps, CRs, and StorageClasses. Dependencies are `kubectl`, `jq`, Rook CRDs, generated secret values, and the external Ceph cluster already prepared. Risks: secrets appear in environment/process context, existing objects are patched only partially, waits use fixed 20 second timeouts, and `kubectl` is used directly in one topology function instead of `$KUBECTL`. Test signals: script exits zero, required resources exist, StorageClasses reference imported secret names, and PVC provisioning succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/import-external-cluster.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/object-bucket-claim-delete.yaml -->
# sources/control-plane/rook/deploy/examples/external/object-bucket-claim-delete.yaml

Purpose: example ObjectBucketClaim that creates a bucket through an external object store StorageClass with delete reclaim semantics.
Important APIs/types/functions: `objectbucket.io/v1alpha1` `ObjectBucketClaim`, `generateBucketName: ceph-bkt`, `storageClassName: rook-ceph-delete-bucket`, and optional quota fields in `additionalConfig`.
Control flow: the bucket provisioner creates a bucket or grants access according to the referenced StorageClass, then writes Secret/ConfigMap connection details for the claim. State persists in OBC/OB resources, bucket credentials, and the external RGW bucket. Dependencies are object bucket CRDs/provisioner, `storageclass-bucket-delete.yaml`, and external object store configuration. Risks: delete reclaim can delete bucket data when the claim is removed, generated names are non-deterministic, and quotas are commented out. Test signals: OBC Bound, connection Secret exists, bucket is reachable via S3, and deleting the OBC removes the bucket when expected.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/object-bucket-claim-delete.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/object-external.yaml -->
# sources/control-plane/rook/deploy/examples/external/object-external.yaml

Purpose: defines a Rook `CephObjectStore` that points at an external RGW endpoint.
Important APIs/types/functions: `CephObjectStore` `external-store`, namespace `rook-ceph`, `spec.gateway.port: 80`, and `externalRgwEndpoints` with IP/optional hostname.
Control flow: Rook represents an external RGW service without deploying local gateways; bucket provisioning and object clients use the configured endpoint. State is the object store CR and external RGW service/bucket state. Dependencies are an accessible RGW endpoint, imported RGW admin credentials when bucket provisioning is used, and object bucket provisioner. Risks: placeholder IP must be replaced, only one endpoint is shown, TLS/hostname are omitted, and endpoint must belong to the intended Ceph cluster. Test signals: CephObjectStore ready, bucket StorageClass can create OBCs, and S3 operations reach the external endpoint.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/object-external.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/storageclass-bucket-delete.yaml -->
# sources/control-plane/rook/deploy/examples/external/storageclass-bucket-delete.yaml

Purpose: object bucket StorageClass that deletes externally provisioned buckets when claims are deleted.
Important APIs/types/functions: `StorageClass` `rook-ceph-delete-bucket`, provisioner `rook-ceph.ceph.rook.io/bucket`, `reclaimPolicy: Delete`, `objectStoreName`, `objectStoreNamespace`, and optional existing `bucketName`.
Control flow: OBC creation calls the Rook bucket provisioner, which creates or binds a bucket in the named object store and returns credentials. Deletion follows the StorageClass reclaim policy and removes bucket data. State lives in OBC/OB resources, generated Secrets/ConfigMaps, and RGW buckets/users. Dependencies are `object-external.yaml`, object bucket CRDs, and RGW admin credentials. Risks: file references `objectStoreName: my-store` while the object store example is named `external-store`, so users must align names; delete policy is destructive. Test signals: OBC binds, bucket exists in RGW, credentials work, and deletion behavior matches policy.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/external/storageclass-bucket-delete.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-ec.yaml -->
# sources/control-plane/rook/deploy/examples/filesystem-ec.yaml

Purpose: creates a CephFS filesystem with replicated metadata/default data and an erasure-coded secondary data pool.
Important APIs/types/functions: `CephFilesystem` `myfs-ec`, metadata pool replication, `dataPools` with replicated and `erasurecoded` pools, `preserveFilesystemOnDelete`, MDS `activeCount`, `activeStandby`, placement anti-affinity, and `CephFilesystemSubVolumeGroup` `myfs-csi` with distributed pinning.
Control flow: Rook reconciles pools and MDS deployments, then creates the CSI subvolume group for dynamic provisioning. State persists in CephFS pools/MDS metadata and Kubernetes CR status. Dependencies are enough OSDs/hosts for EC chunks and replica size, Rook CephFilesystem CRD, and CSI StorageClass using `myfs-ec`. Risks: EC data pool needs bluestore/OSD capacity, `preserveFilesystemOnDelete: true` leaves backend data after CR deletion, and subvolume group references `filesystemName: myfs` while the filesystem CR is `myfs-ec`, which may require user correction. Test signals: CephFilesystem Ready, MDS active/standby pods run, subvolume group ready, and EC StorageClass PVCs bind.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-ec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-mirror.yaml -->
# sources/control-plane/rook/deploy/examples/filesystem-mirror.yaml

Purpose: deploys a CephFS mirror daemon managed by Rook.
Important APIs/types/functions: `CephFilesystemMirror` `my-fs-mirror`, placement hooks, annotations, resource requests/limits, and optional priority class.
Control flow: Rook reconciles the mirror CR into cephfs-mirror daemon pods used for filesystem mirroring between clusters when peers/schedules are configured on filesystems. State is the mirror CR and daemon deployment status; mirrored data state is in Ceph. Dependencies are CephFS mirroring support, Rook operator, and any filesystem mirroring configuration elsewhere. Risks: this file alone does not configure peers or schedules, resource limits may need tuning, and placement is mostly commented. Test signals: mirror pod Running, Ceph reports mirror daemon, and configured mirrored filesystems show healthy replay/sync.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-mirror.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-test.yaml -->
# sources/control-plane/rook/deploy/examples/filesystem-test.yaml

Purpose: single-OSD CephFS example for non-production testing.
Important APIs/types/functions: `CephFilesystem` `myfs`, metadata/data pools with replica size 1 and `requireSafeReplicaSize: false`, `preserveFilesystemOnDelete: false`, MDS `activeStandby: false`, and `CephFilesystemSubVolumeGroup` `myfs-csi`.
Control flow: Rook creates a low-redundancy filesystem and default CSI subvolume group suitable for small test clusters. State persists in CephFS pools and Kubernetes CRs, but filesystem deletion does not preserve data. Dependencies are Rook CephFilesystem CRD and at least one OSD. Risks: explicit data-loss exposure with replica 1, no standby MDS, and delete removes filesystem data. Test signals: CephFilesystem Ready on a single OSD, subvolume group ready, and `rook-cephfs` PVCs bind in test clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem.yaml -->
# sources/control-plane/rook/deploy/examples/filesystem.yaml

Purpose: production-oriented replicated CephFS filesystem example with default CSI subvolume group.
Important APIs/types/functions: `CephFilesystem` `myfs`, replicated metadata/data pools size 3, pool compression parameters, `preserveFilesystemOnDelete: true`, MDS active/standby settings, anti-affinity, priority class, liveness/startup probes, commented mirroring configuration, and `CephFilesystemSubVolumeGroup` `myfs-csi` with distributed pinning.
Control flow: Rook creates pools, deploys MDS pods, manages health/probes, and creates the CSI subvolume group used by CephFS StorageClasses. State persists in CephFS metadata/data pools and CR status. Dependencies are at least three OSD hosts for safe replica size, Rook operator, and CSI StorageClass `storageclass.yaml`. Risks: `preserveFilesystemOnDelete` leaves data after CR deletion, anti-affinity can block scheduling in small clusters, and commented mirroring requires additional peer secrets to activate. Test signals: CephFilesystem Ready, MDS active/standby healthy, subvolume group ready, PVC provisioning works, and pod anti-affinity behaves as intended.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/filesystem.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/headless-mon-service.yaml -->
# sources/control-plane/rook/deploy/examples/headless-mon-service.yaml

Purpose: exposes Rook Ceph monitor pods through a headless Kubernetes Service.
Important APIs/types/functions: `Service` `rook-ceph-mon`, namespace `rook-ceph`, `clusterIP: None`, selector `app: rook-ceph-mon`, and port `6789`.
Control flow: Kubernetes creates DNS records/endpoints for individual monitor pods instead of load-balancing through a cluster IP. State is Service and endpoint slice data. Dependencies are monitor pods with matching labels and clients that need stable DNS-based monitor discovery. Risks: monitor protocols may also require msgr2 port 3300 in modern deployments, and selector must match Rook labels. Test signals: endpoints list mons, DNS resolves per endpoint, and Ceph clients can connect through the service.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/headless-mon-service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/import-external-cluster.sh -->
# sources/control-plane/rook/deploy/examples/import-external-cluster.sh

Purpose: top-level copy of the external-cluster import script; it is byte-identical to `external/import-external-cluster.sh`.
Important APIs/types/functions: same environment contract and functions as the external copy: validates generated env vars, creates namespace, imports mon/CSI/RGW secrets, creates monitor endpoint ConfigMap and command ConfigMap, optionally creates RADOS namespace/subvolume group CRs, and creates RBD/CephFS/topology StorageClasses.
Control flow: sequential bash execution under `set -e` applies external cluster resources using `kubectl`, with optional `$KUBECONTEXT`; existing objects are skipped or patched selectively. State persists in Kubernetes secrets, configmaps, CRs, and StorageClasses. Dependencies are `kubectl`, `jq`, Rook CRDs, and exports from `create-external-cluster-resources.py`. Risks mirror the external copy: secret-bearing environment, fixed readiness timeouts, partial patch behavior, and one function using plain `kubectl`. Test signals: same as the external path, with an additional checksum/`cmp` check to ensure copies stay synchronized.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/import-external-cluster.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/kustomization.yaml -->
# sources/control-plane/rook/deploy/examples/kustomization.yaml

Purpose: Kustomize entry point that composes Rook example manifests.
Important APIs/types/functions: `apiVersion: kustomize.config.k8s.io/v1beta1`, `kind: Kustomization`, and `resources` pointing at `crds.yaml`, `common.yaml`, `operator.yaml`, and `cluster.yaml`.
Control flow: `kubectl apply -k` or `kustomize build` expands the listed resources in order into a deployable Rook example stack. State is not held by this file; it controls apply composition. Dependencies are the referenced files in the examples directory and Kustomize support in the client. Risks: only the base cluster path is included, not CSI examples in this research item; referenced files must exist relative to this file. Test signals: `kubectl kustomize` renders successfully and applying the output creates CRDs, common RBAC, operator, and cluster resources.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/csi-metrics-service-monitor.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/csi-metrics-service-monitor.yaml

Purpose: Prometheus Operator `ServiceMonitor` for scraping CSI sidecar/node metrics.
Important APIs/types/functions: `monitoring.coreos.com/v1` `ServiceMonitor` `csi-metrics`, namespace `rook-ceph`, label `team: rook`, namespace selector `rook-ceph`, selector `app: csi-metrics`, endpoint port `csi-http-metrics`, path `/metrics`, and interval `5s`.
Control flow: Prometheus Operator converts this CR into scrape config for matching CSI metrics Services. State is Prometheus scrape configuration and time-series data outside this manifest. Dependencies are Prometheus Operator CRDs, CSI metrics Services with matching labels/port names, and Prometheus selection of this ServiceMonitor. Risks: high 5s scrape interval can increase load, label/port mismatch yields no targets, and namespace must match Rook deployment. Test signals: ServiceMonitor accepted, Prometheus target appears Up, and CSI metrics are queryable.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/csi-metrics-service-monitor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/exporter-service-monitor.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/exporter-service-monitor.yaml

Purpose: Prometheus Operator `ServiceMonitor` for the Rook Ceph exporter.
Important APIs/types/functions: `ServiceMonitor` `rook-ceph-exporter`, selector labels `app: rook-ceph-exporter` and `rook_cluster: rook-ceph`, endpoint port `ceph-exporter-http-metrics`, path `/metrics`, and interval `10s`.
Control flow: Prometheus Operator discovers matching exporter Services in `rook-ceph` and scrapes metrics into Prometheus. State is monitoring configuration and Prometheus time-series data. Dependencies are exporter deployment/service enabled by Rook and Prometheus Operator CRDs. Risks: no targets if exporter disabled or labels differ, namespace comment substitutions must align, and scrape interval may need tuning. Test signals: Prometheus target Up, exporter metrics present, and labels include expected cluster identity.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/exporter-service-monitor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/externalrules.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/externalrules.yaml

Purpose: Prometheus alert rules for Ceph-backed persistent volume capacity usage in external monitoring setups.
Important APIs/types/functions: `PrometheusRule` `prometheus-ceph-rules`, group `persistent-volume-alert.rules`, alerts `PersistentVolumeUsageNearFull` and `PersistentVolumeUsageCritical`, PromQL joining kubelet volume stats, PVC info, and StorageClass provisioner labels for RBD/CephFS CSI, thresholds `> 0.75` and `> 0.85`, and warning/critical labels.
Control flow: Prometheus Operator loads the rules; Prometheus evaluates usage/capacity ratios for PVCs provisioned by Ceph CSI drivers and fires alerts after `5s`. State is alert evaluation state in Prometheus/Alertmanager. Dependencies are kubelet volume stats, kube-state-metrics `kube_persistentvolumeclaim_info` and `kube_storageclass_info`, Prometheus Operator, and provisioner label patterns. Risks: short `for: 5s` can be noisy, missing `cluster` labels break joins, non-RBD/CephFS provisioners are excluded, and high-cardinality joins may be expensive. Test signals: `promtool` validates rules, synthetic full PVC triggers alerts, and normal PVCs remain inactive.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/externalrules.yaml -->
