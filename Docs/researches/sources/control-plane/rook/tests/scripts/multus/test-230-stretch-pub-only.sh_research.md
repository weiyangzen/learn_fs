<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-230-stretch-pub-only.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-230-stretch-pub-only.sh

Purpose: positive stretch validation scenario with only a public network configured.

Important APIs and control flow: creates namespace/serviceaccount, rewrites `stretch.yaml` to set public network and blank cluster network, runs the validation CLI, greps expected client counts for all node types, checks 13 ready clients, and verifies pod cleanup.

State, persistence, and integration: creates temporary validation resources and a generated config/log. Dependencies include public NAD, node labels/taints, Multus, and the Rook CLI. Risks include log-string coupling and fixed client counts. Test signals are expected grep lines and no remaining pods.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-230-stretch-pub-only.sh -->
