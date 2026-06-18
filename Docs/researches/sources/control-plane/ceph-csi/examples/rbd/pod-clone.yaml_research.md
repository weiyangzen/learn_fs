## sources/control-plane/ceph-csi/examples/rbd/pod-clone.yaml

Purpose: Example nginx Pod mounting an RBD PVC cloned from another PVC.

Important API surface: Pod `csi-rbd-clone-demo-app`, container `web-server`, mount path `/var/lib/www/html`, PVC reference `rbd-pvc-clone`, and `readOnly: false`.

Control flow and state: Kubernetes binds the clone PVC, the RBD node plugin maps and mounts it as a filesystem volume, and nginx sees it as writable content storage. State lives in the cloned RBD image, PV/PVC binding, and node mount.

Dependencies and risks: Requires `pvc-clone.yaml`, source `rbd-pvc`, and a valid StorageClass. Source/target size and access mode compatibility are important. Test by provisioning source content before cloning and checking cloned data in the nginx mount.
