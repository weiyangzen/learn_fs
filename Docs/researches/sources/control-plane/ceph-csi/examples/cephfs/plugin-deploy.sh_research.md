# sources/control-plane/ceph-csi/examples/cephfs/plugin-deploy.sh

Purpose: simple deployment script for CephFS CSI Kubernetes manifests.

Important APIs and flow: accepts an optional deployment base path, defaults to `../../deploy/cephfs/kubernetes`, changes into that directory, and runs `kubectl create -f` for RBAC, config map, provisioner, nodeplugin, and CSIDriver objects.

State, dependencies, and integration: creates cluster and namespace resources from the deploy manifests. Used for examples and local e2e-style deployment.

Risks and test signals: fails if the directory is wrong or resources already exist. It relies on current kubectl context and lacks rollback. Successful completion means all manifests were accepted, not necessarily that pods are ready.
