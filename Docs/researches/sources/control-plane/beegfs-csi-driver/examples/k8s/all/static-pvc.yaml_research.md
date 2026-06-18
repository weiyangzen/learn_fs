<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pvc.yaml

Purpose: claim that binds the combined example Pod to the static read/write BeeGFS PV.

Important APIs and flow: requests `ReadWriteMany` and `100Gi`, sets `storageClassName: ""` to avoid dynamic provisioning, and pins `volumeName: csi-beegfs-static-pv`.

State and persistence: PVC state binds to the named PV; storage lifecycle is controlled by the PV's `Retain` policy and external BeeGFS directory.

Dependencies and integration points: requires `static-pv.yaml` to exist and match capacity/access mode.

Risks and test signals: mismatched capacity/access modes or missing `storageClassName: ""` can prevent binding or trigger unwanted provisioning. Test PVC phase `Bound` and Pod mount.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/all/static-pvc.yaml -->
