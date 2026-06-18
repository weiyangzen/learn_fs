# sources/control-plane/ceph-csi/examples/cephfs/plugin-teardown.sh

Purpose: simple teardown script for CephFS CSI Kubernetes manifests.

Important APIs and flow: accepts an optional deployment base path, defaults to `../../deploy/cephfs/kubernetes`, changes there, and deletes provisioner, nodeplugin, config map, RBAC, and CSIDriver manifests in an order that removes workloads before shared support objects.

State, dependencies, and integration: deletes resources created by `plugin-deploy.sh` from the current kubectl context.

Risks and test signals: no `--ignore-not-found`, so missing resources can fail the script. It does not wait for pod termination or check final cluster state.
