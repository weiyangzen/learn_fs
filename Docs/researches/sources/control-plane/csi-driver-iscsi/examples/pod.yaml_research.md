## sources/control-plane/csi-driver-iscsi/examples/pod.yaml

Purpose: example workload consuming the iSCSI CSI PersistentVolumeClaim.

Control flow is declarative: a Linux-selected `nginx` Pod mounts PVC `iscsiplugin-pvc` at `/var/www`. State is Kubernetes pod lifecycle and the mounted filesystem inside the container.

Dependencies are the PVC/PV example pair, a running CSI node plugin, an accessible iSCSI target, and Linux nodes. Risks include no readiness/cleanup guidance, fixed PVC name, and generic nginx image not validating writes. Test signal is manual pod readiness and mount inspection; `verify-yamllint.sh` may lint the file.
