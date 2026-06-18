## sources/control-plane/ceph-csi/examples/rbd/pvc.yaml

Purpose: Baseline dynamically provisioned RBD filesystem PVC.

Important API surface: PVC `rbd-pvc`, label `group: test`, `ReadWriteOnce`, `storageClassName: csi-rbd-sc`, and `1Gi` request.

Control flow and state: The external provisioner creates an RBD-backed PV using `storageclass.yaml`. The label integrates with `groupsnapshot.yaml` as the selector for group snapshot membership.

Dependencies and risks: Requires storage class, secret, Ceph config map, and RBD controller deployment. The `group: test` label can include this PVC in group snapshots unintentionally if reused. Test by applying the PVC, observing binding, mounting with `pod.yaml`, and checking group snapshot selection.
