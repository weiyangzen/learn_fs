## sources/control-plane/ceph-csi/examples/rbd/plugin-deploy.sh

Purpose: Convenience deployment script for RBD Ceph CSI Kubernetes manifests and Vault KMS sample resources.

Important flow: Accepts optional `deployment_base` then `kms_base`, defaults to `../../deploy/rbd/kubernetes` and `../kms/vault`, `pushd`s into each, and runs `kubectl create -f` for ordered object arrays. RBD objects include RBAC, config map, provisioner, node plugin, and CSIDriver; KMS objects include Vault, token review RBAC, and KMS config.

State and integration: It creates Kubernetes API resources and relies on manifest ordering for dependencies. It does not persist local state or use idempotent apply.

Risks and test signals: `kubectl create` fails on existing resources and no rollback is attempted after partial failure. `shift` is called even if no args are supplied, which is benign in bash without `set -e` but brittle. Test by running against a clean namespace and verifying pods, RBAC, config, and KMS objects become ready.
