<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-220-stretch-pub-and-cluster.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-220-stretch-pub-and-cluster.sh

Purpose: positive stretch validation scenario with both public and cluster networks configured.

Important APIs and control flow: creates namespace/serviceaccount, rewrites `stretch.yaml` to use default NADs and the test namespace, runs the validation CLI, greps output for expected OSD and non-OSD client counts for arbiter, storage, and worker node types, checks total readiness of 13 clients, and asserts cleanup leaves no pods.

State, persistence, and integration: creates temporary namespace resources, generated config, and output log. Dependencies include labeled/tainted nodes, Multus/default NADs, and built `./rook`. Risks include expected-count and log-string coupling. Test signals are grep matches and empty pod list.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-220-stretch-pub-and-cluster.sh -->
