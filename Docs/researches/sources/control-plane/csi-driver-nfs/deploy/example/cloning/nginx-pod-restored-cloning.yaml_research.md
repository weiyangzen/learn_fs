# sources/control-plane/csi-driver-nfs/deploy/example/cloning/nginx-pod-restored-cloning.yaml

Purpose: example Kubernetes manifest demonstrating PVC clone restore smoke test after `pvc-nfs-cloning` binds for the NFS CSI driver.

Important APIs/types/functions: defines Pod resource(s) named `nginx-nfs-restored-cloning`. It mounts PVC `pvc-nfs-cloning` at `/mnt/nfs` and appends timestamps through an nginx container. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
