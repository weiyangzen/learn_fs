## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/volumesnapshotclass.yaml

Purpose: renders optional CephFS and RBD `VolumeSnapshotClass` resources.

Important template behavior: reads `.Values.cephFileSystemVolumeSnapshotClass` and `.Values.cephBlockPoolsVolumeSnapshotClass`. For each enabled class it creates `snapshot.storage.k8s.io/v1` VolumeSnapshotClass with labels, default-class annotation, driver from `csiDriverNamePrefix` or `operatorNamespace`, clusterID, standard snapshotter secret references, user parameters, and deletionPolicy defaulting to Delete.

Control flow: independent conditionals for filesystem and block-pool snapshot classes.

State and persistence: creates cluster-scoped snapshot class resources used by CSI external snapshotter. Default-class annotations can affect snapshot behavior cluster-wide.

Dependencies and integration points: requires snapshot CRDs/controller, Ceph CSI drivers, and Rook CSI secret naming. Risks: enabling defaults can conflict with other snapshot classes; driver name mismatch breaks snapshotting; deletionPolicy has data retention implications. Tests should render both enabled classes and prefix/operator namespace variants.
