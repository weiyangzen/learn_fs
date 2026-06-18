<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-110-cli.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-110-cli.sh

Purpose: smoke test for direct `rook multus validation run` CLI arguments without a config file.

Important APIs and control flow: creates namespace `cli-test`, creates the expected `rook-ceph-system` service account, runs `./rook --log-level DEBUG multus validation run` with namespace, public and cluster networks in `default`, and two daemons per node, then greps output for expected client startup and readiness lines. It asserts no non-terminating pods remain.

State, persistence, and integration: creates namespace/serviceaccount and temporary validation resources that should be cleaned by the CLI. Dependencies include built `./rook`, default NADs, and Multus. Risks include fixed expected client count of six and log-string coupling. Test signals are grep matches and empty namespace pod list after success.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-110-cli.sh -->
