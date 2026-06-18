<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/storageclass.yaml -->
# sources/control-plane/longhorn/examples/storageclass.yaml

Purpose: sample Longhorn StorageClass showing common and optional parameters.

Important APIs/types/functions: StorageClass `longhorn-test`, provisioner `driver.longhorn.io`, expansion enabled, reclaim Delete, Immediate binding, replica/timeout/fromBackup/fsType parameters, and commented examples for mkfs, backing images, selectors, recurring jobs, unmap, and NFS options.

Control flow: PVCs using this class are dynamically provisioned by Longhorn CSI with supplied parameters.

State and persistence: controls volume spec defaults; created volumes persist through PVC/PV lifecycle.

Dependencies/integration points: depends on Longhorn CSI parameter support and optional backing image/recurring job features when uncommented.

Risks/test signals: Immediate binding can provision before pod scheduling constraints are known; optional JSON/string parameters are easy to mistype. Test signals are StorageClass admission, PVC provisioning, parameter reflection in Longhorn Volume spec, and expansion/reclaim behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/storageclass.yaml -->
