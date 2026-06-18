<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-240-stretch-cluster-only.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-240-stretch-cluster-only.sh

Purpose: positive stretch validation scenario with only a cluster network configured, where only OSD clients should run.

Important APIs and control flow: creates namespace/serviceaccount, rewrites `stretch.yaml` to blank public network and set cluster network, runs the validation CLI, greps OSD startup counts for each node type, checks that four clients become ready, and verifies cleanup.

State, persistence, and integration: creates temporary validation resources and generated config/log files. Dependencies include cluster NAD, node labels/taints, Multus, and built `./rook`. Risks include exact client count assumptions and not checking absence of non-OSD log lines. Test signals are grep matches for OSD counts, total ready clients, and empty pod list.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-240-stretch-cluster-only.sh -->
