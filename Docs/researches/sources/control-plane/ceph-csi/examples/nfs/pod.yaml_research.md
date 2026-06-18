# sources/control-plane/ceph-csi/examples/nfs/pod.yaml

Purpose: baseline NFS CSI example pod.

Important fields and flow: Pod `cephcsi-nfs-demo-pod` runs nginx and mounts PVC `cephcsi-nfs-pvc` at `/var/lib/www`.

State, dependencies, and integration: depends on `pvc.yaml`, `storageclass.yaml`, and a reachable Ceph-managed NFS server/export.

Risks and test signals: external nginx image and export availability affect startup. Pod readiness is the primary NodePublish signal.
