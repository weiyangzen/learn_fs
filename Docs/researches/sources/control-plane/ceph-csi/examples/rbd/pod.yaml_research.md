## sources/control-plane/ceph-csi/examples/rbd/pod.yaml

Purpose: Baseline nginx Pod mounting the standard RBD filesystem PVC.

Important API surface: Pod `csi-rbd-demo-pod`, container `web-server`, PVC `rbd-pvc`, mount path `/var/lib/www/html`, and writable mount.

Control flow and state: The Pod causes kubelet to call the RBD CSI node path for a dynamically provisioned filesystem volume. Persistent state is in the RBD image and Kubernetes PV/PVC objects.

Dependencies and risks: Requires `pvc.yaml`, `storageclass.yaml`, secret/config map, and deployed RBD plugin. It is a basic smoke test and does not verify advanced features. Test by writing data through the mount, restarting the Pod, and confirming persistence.
