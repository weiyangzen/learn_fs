<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/v2/storageclass.yaml -->
# sources/control-plane/longhorn/examples/v2/storageclass.yaml

Purpose: StorageClass for Longhorn v2 data engine volumes.

Important APIs/types/functions: StorageClass `longhorn-v2-data-engine`, provisioner `driver.longhorn.io`, expansion enabled, Delete reclaim, Immediate binding, replica/timeout/fsType, and `dataEngine: "v2"`; comments show optional selectors, recurring jobs, backup, backing image, unmap, and NFS options.

Control flow: PVCs using this class request Longhorn v2 data engine provisioning through CSI.

State and persistence: StorageClass policy influences Longhorn Volume specs and created volume data persists in Longhorn.

Dependencies/integration points: depends on Longhorn v2 engine support, compatible nodes, and CSI parameter handling.

Risks/test signals: applying this class where v2 is disabled or prerequisites are missing causes provisioning/attach failures. Test signals are PVC provisioning, Volume CR dataEngine, instance manager/v2 frontend health, and IO/expansion tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/v2/storageclass.yaml -->
