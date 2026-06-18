<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-200-stretch-label-nodes.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-200-stretch-label-nodes.sh

Purpose: prepares KinD nodes with topology and storage labels for Multus stretch validation tests.

Important APIs and control flow: labels `kind-control-plane` as zone `arbiter`, `kind-worker` as zone `dc1` and storage node, `kind-worker2` as zone `dc2` and storage node, and `kind-worker3` as zone `dc2`.

State, persistence, and integration: mutates Kubernetes Node labels consumed by `stretch.yaml` placement rules. Dependencies include exact KinD node names. Risks include failing on non-KinD clusters or reruns where labels need overwrite. Test signals are subsequent validation selecting correct node groups.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-200-stretch-label-nodes.sh -->
