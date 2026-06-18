## sources/control-plane/ceph-csi/examples/rbd/plugin-teardown.sh

Purpose: Convenience teardown script for the RBD Ceph CSI example deployment and Vault KMS sample resources.

Important flow: Mirrors `plugin-deploy.sh` with defaults for deployment and KMS directories, then runs `kubectl delete -f` over RBD objects in a deletion-oriented order and Vault/KMS objects afterward.

State and integration: It deletes Kubernetes API resources defined by the referenced YAML files. It does not remove Ceph backend volumes or snapshots created by separate PVC examples.

Risks and tests: Deleting RBAC/config before workloads fully terminate can produce noisy cleanup failures; missing resources cause `kubectl delete` errors. The script has no namespace override and no `--ignore-not-found`. Test by deploying first, running teardown, and verifying CSI pods, sidecars, CSIDriver, and KMS objects are gone while PV reclaim policy governs backend storage.
