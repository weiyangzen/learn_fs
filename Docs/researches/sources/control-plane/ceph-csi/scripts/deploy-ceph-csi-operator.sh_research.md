<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/deploy-ceph-csi-operator.sh -->
## sources/control-plane/ceph-csi/scripts/deploy-ceph-csi-operator.sh

Purpose: deploys or cleans up the external Ceph-CSI Operator plus driver custom resources for tests.

Control flow: sources `utils.sh` and `build.env`, normalizes operator version `latest` to `main`, fetches operator install YAML from GitHub, rewrites namespace, generates image set and encryption config maps, creates an `OperatorConfig`, and creates RBD/CephFS/NFS `Driver` resources. Cleanup regenerates matching resources and deletes them before deleting operator install YAML.

State and persistence: creates Kubernetes resources in `OPERATOR_NAMESPACE` and temp YAML files under a trap-cleaned directory.

Dependencies: `curl`, `kubectl_retry`, raw GitHub manifests, build.env sidecar image versions, Kubernetes cluster with operator CRDs.

Integration points: e2e/operator test deployment path.

Risks: remote `main` manifests make `latest` non-reproducible. `kubectl create` rather than apply means existing resources rely on retry wrapper's AlreadyExists behavior. Secrets/encryption config is empty by default.

Test signals: no direct tests; operational validation is pod/operator readiness in e2e.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/deploy-ceph-csi-operator.sh -->
