# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/snapshotclass.yaml

Purpose: v4.10.0 optional VolumeSnapshotClass.

Important APIs/types/functions: `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass`; values `.Values.volumeSnapshotClass.create`, `.name`, `.deletionPolicy`, and `.Values.driver.name`.

Control flow: Renders only when create is true. Emits name, driver, and deletion policy without labels or annotations in this version.

State and persistence: Cluster-scoped snapshot class used by VolumeSnapshots.

Dependencies and integration points: Snapshot CRDs, snapshot-controller, and NFS CSI snapshotter.

Risks: No annotation support limits default class declaration. Wrong deletion policy affects snapshot content retention. Test signals: render true/false and create/delete VolumeSnapshot using the class.
