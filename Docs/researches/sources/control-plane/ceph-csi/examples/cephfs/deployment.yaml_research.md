# sources/control-plane/ceph-csi/examples/cephfs/deployment.yaml

Purpose: example nginx Deployment that consumes the standard CephFS PVC.

Important fields and flow: Deployment `csi-cephfs-demo-depl` runs one `web-server` replica and mounts PVC `csi-cephfs-pvc` at `/var/lib/www/html`.

State, dependencies, and integration: creates an apps/v1 Deployment relying on `pvc.yaml` and `storageclass.yaml`. E2E helpers load it for PVC+Deployment binding checks.

Risks and test signals: depends on the PVC being bound and nginx image availability. Readiness validates that a CephFS filesystem volume can be published into a Deployment workload.
