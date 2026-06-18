# sources/control-plane/ceph-csi/examples/cephfs/pod-clone.yaml

Purpose: example pod that consumes a CephFS PVC clone.

Important fields and flow: Pod `csi-cephfs-clone-demo-app` runs nginx and mounts PVC `cephfs-pvc-clone` at `/var/lib/www/html`.

State, dependencies, and integration: depends on `pvc-clone.yaml` creating a bound clone. E2E clone tests load this template and adjust names/labels.

Risks and test signals: clone PVC must exist and be publishable. Pod readiness and file checksum checks validate clone data access.
