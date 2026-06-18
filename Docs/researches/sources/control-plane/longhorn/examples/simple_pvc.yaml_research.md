<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/simple_pvc.yaml -->
# sources/control-plane/longhorn/examples/simple_pvc.yaml

Purpose: minimal Longhorn PVC example.

Important APIs/types/functions: `PersistentVolumeClaim` `longhorn-simple-pvc` in `default`, RWO access mode, StorageClass `longhorn`, and 1Gi request.

Control flow: applying the manifest triggers dynamic provisioning through Longhorn CSI.

State and persistence: creates a persistent Longhorn volume governed by the StorageClass reclaim policy.

Dependencies/integration points: depends on installed Longhorn CSI provisioner and StorageClass `longhorn`.

Risks/test signals: default reclaim behavior may delete data with PVC deletion. Test signals are PVC Bound, PV creation, Longhorn volume creation, and successful pod consumption.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/simple_pvc.yaml -->
