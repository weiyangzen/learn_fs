<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-200-stretch-taint-nodes.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-200-stretch-taint-nodes.sh

Purpose: adds NoSchedule taints to storage worker nodes so worker and storage node-type placements do not overlap in stretch validation tests.

Important APIs and control flow: taints `kind-worker` and `kind-worker2` with `storage-node=true:NoSchedule`.

State, persistence, and integration: mutates Kubernetes Node taints and relies on matching tolerations in `stretch.yaml` for storage-node clients. Dependencies include exact KinD node names. Risks include rerun/idempotency issues without `--overwrite` or taint removal handling. Test signals are the overlap test failing before this setup and success tests passing after it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-200-stretch-taint-nodes.sh -->
