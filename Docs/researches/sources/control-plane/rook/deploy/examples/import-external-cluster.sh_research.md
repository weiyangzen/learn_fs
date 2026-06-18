<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/import-external-cluster.sh -->
# sources/control-plane/rook/deploy/examples/import-external-cluster.sh

Purpose: top-level copy of the external-cluster import script; it is byte-identical to `external/import-external-cluster.sh`.
Important APIs/types/functions: same environment contract and functions as the external copy: validates generated env vars, creates namespace, imports mon/CSI/RGW secrets, creates monitor endpoint ConfigMap and command ConfigMap, optionally creates RADOS namespace/subvolume group CRs, and creates RBD/CephFS/topology StorageClasses.
Control flow: sequential bash execution under `set -e` applies external cluster resources using `kubectl`, with optional `$KUBECONTEXT`; existing objects are skipped or patched selectively. State persists in Kubernetes secrets, configmaps, CRs, and StorageClasses. Dependencies are `kubectl`, `jq`, Rook CRDs, and exports from `create-external-cluster-resources.py`. Risks mirror the external copy: secret-bearing environment, fixed readiness timeouts, partial patch behavior, and one function using plain `kubectl`. Test signals: same as the external path, with an additional checksum/`cmp` check to ensure copies stay synchronized.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/import-external-cluster.sh -->
