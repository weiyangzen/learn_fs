## sources/control-plane/rook/deploy/charts/ceph-csi-drivers/values.yaml

Purpose: provides Rook-compatible defaults for installing the upstream `ceph-csi-drivers` chart alongside the Rook operator chart.

Important configuration: `operatorConfig.namespace` defaults to `rook-ceph`; `driverSpecDefaults.imageSet.name` points at `rook-csi-operator-image-set-configmap`; node and controller CSI plugins get critical priority classes. Driver blocks enable RBD and CephFS by default and disable NFS and NVMe-oF, with provisioner names matching Rook naming conventions such as `rook-ceph.rbd.csi.ceph.com`.

Control flow: values-only file consumed by Helm and the ceph-csi-operator dependency. No templating logic in this file, but comments explain that driver names must match Rook provisioner names in StorageClasses and VolumeSnapshotClasses.

State and persistence: influences Kubernetes CSI driver resources rendered by the ceph-csi-drivers chart, not directly by Rook templates. Misconfiguration persists as mismatched driver names and broken dynamic provisioning.

Dependencies and integration points: tightly coupled to `rook-ceph/templates/configmap.yaml`, which renders the image set ConfigMap, and to cluster chart StorageClasses that use RBD/CephFS provisioner names. Risks: changing the Rook operator namespace requires changing driver names; enabling disabled drivers requires matching Rook/operator support and RBAC. Test signal should come from Helm render tests and CSI provisioning e2e.
