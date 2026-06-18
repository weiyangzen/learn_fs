<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/kind-config.yaml -->
# sources/control-plane/rook/tests/scripts/multus/kind-config.yaml

Purpose: KinD cluster topology for Multus validation tests.

Important structure: defines one control-plane node and three worker nodes using `kind.x-k8s.io/v1alpha4`.

State, persistence, and integration: consumed by `kind create cluster` to provision a four-node test cluster. Dependencies include KinD and Docker. Risks include fixed node names assumed by label/taint scripts and local resource demand. Test signals are successful node creation and subsequent label/taint operations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/kind-config.yaml -->
