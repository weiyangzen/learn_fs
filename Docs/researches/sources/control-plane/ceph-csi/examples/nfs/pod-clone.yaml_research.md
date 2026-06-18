# sources/control-plane/ceph-csi/examples/nfs/pod-clone.yaml

Purpose: example pod that consumes an NFS PVC clone.

Important fields and flow: Pod `csi-nfs-clone-demo-app` runs nginx and mounts PVC `nfs-pvc-clone` at `/var/lib/www`.

State, dependencies, and integration: depends on clone PVC creation from `pvc-clone.yaml`. Used by e2e clone flows for NFS.

Risks and test signals: clone PVC must bind and export must be mountable. Pod readiness and checksum checks validate clone access.
