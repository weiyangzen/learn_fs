## sources/control-plane/ceph-csi/examples/rbd/raw-block-pod-rwop.yaml

Purpose: Example Pod consuming an RBD raw block PVC with `ReadWriteOncePod`.

Important API surface: Pod `csi-rbd-demo-rwop-pod`, CentOS container, `volumeDevices` mapping `data` to `/dev/xvda`, and PVC `raw-block-rwop-pvc`.

Control flow and state: Kubelet requests CSI node publish as a block device; Kubernetes access mode limits the PVC to a single Pod. The raw device contains whatever block-level data the workload writes.

Dependencies and risks: Requires `raw-block-pvc-rwop.yaml`, RBD block mode support, and RWOP cluster support. Incorrect workload assumptions about filesystem presence are a risk because the device is raw. Test by checking device presence and competing Pod rejection.
