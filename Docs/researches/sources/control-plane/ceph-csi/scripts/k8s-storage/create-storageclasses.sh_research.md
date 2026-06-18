<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-storageclasses.sh -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/create-storageclasses.sh

Purpose: materializes StorageClass templates for k8s storage e2e tests.

Control flow: finds Rook toolbox pod, reads Ceph fsid, loops over `sc-*.yaml.in`, substitutes `@@CLUSTER_ID@@`, and pipes each manifest to `kubectl create -f -`.

State and persistence: creates Kubernetes StorageClasses.

Dependencies: kubectl, Rook toolbox, template files.

Integration points: paired with driver YAMLs that reference existing storage class names.

Risks: repeated runs fail if StorageClasses already exist. Substitution only handles cluster ID and assumes templates contain all other correct values.

Test signals: no tests; e2e provisioning is validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-storageclasses.sh -->
