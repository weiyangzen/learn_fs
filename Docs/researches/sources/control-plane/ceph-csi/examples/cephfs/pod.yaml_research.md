# sources/control-plane/ceph-csi/examples/cephfs/pod.yaml

Purpose: baseline CephFS example pod.

Important fields and flow: Pod `csi-cephfs-demo-pod` runs nginx and mounts PVC `csi-cephfs-pvc` at `/var/lib/www`.

State, dependencies, and integration: depends on `pvc.yaml` and `storageclass.yaml`. Many e2e helpers load and mutate this pod template for create, persistence, resize, snapshot, and upgrade tests.

Risks and test signals: uses external nginx image and assumes PVC name alignment. Pod readiness is the basic signal for CephFS NodeStage/NodePublish success.
