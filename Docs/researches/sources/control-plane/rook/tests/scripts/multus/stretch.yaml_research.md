<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/stretch.yaml -->
# sources/control-plane/rook/tests/scripts/multus/stretch.yaml

Purpose: configuration file for `rook multus validation run` stretch-cluster scenarios. It models arbiter, storage, and worker node types with different daemon counts and placements.

Important structure: sets namespace `stretch-test`, public/cluster network names, timeouts, nginx image, and three node types. Arbiter nodes have no OSDs and one other daemon on zone `arbiter` with control-plane toleration. Storage nodes have two OSD clients and three other clients on `storage-node=true` with matching toleration. Worker nodes default to zero OSDs and two other clients with no placement.

State, persistence, and integration: consumed by the Rook CLI validation tool to create test resources and clients. Dependencies include labeled/tainted KinD nodes and NADs. Risks include overlap unless nodes are tainted/labeled correctly, fixed image, and namespace mutation by test scripts. Test signals are expected client-count log lines and cleanup assertions in the Multus scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/stretch.yaml -->
