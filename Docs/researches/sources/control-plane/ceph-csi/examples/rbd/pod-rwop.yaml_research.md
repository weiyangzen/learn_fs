## sources/control-plane/ceph-csi/examples/rbd/pod-rwop.yaml

Purpose: Example Pod consuming an RBD filesystem PVC with `ReadWriteOncePod` access mode.

Important API surface: Pod `csi-rbd-demo-fs-rwop-pod`, nginx container, mount path `/var/lib/www/html`, and PVC `rbd-rwop-pvc`.

Control flow and state: Kubernetes enforces single-Pod access semantics for the PVC while the RBD node plugin handles regular filesystem staging/publish. The manifest itself only wires the Pod to the PVC.

Dependencies and risks: Requires Kubernetes and sidecar versions supporting RWOP, plus `pvc-rwop.yaml`. Multiple Pods attempting the same PVC should be rejected or remain pending. Test by creating this Pod and a second competing Pod and checking scheduler/attach behavior.
