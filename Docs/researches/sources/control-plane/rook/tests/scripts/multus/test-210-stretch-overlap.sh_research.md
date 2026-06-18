<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-210-stretch-overlap.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-210-stretch-overlap.sh

Purpose: negative Multus validation test proving that overlapping node-type selections are detected.

Important APIs and control flow: creates namespace/serviceaccount, rewrites `stretch.yaml` into `stretch-overlap.yaml` with default namespace NADs, runs the validation command expecting failure, greps for the exact overlap error between worker and storage node types, and asserts pods remain for debugging.

State, persistence, and integration: creates namespace, serviceaccount, generated config, output log, and validation pods left intentionally after failure. Dependencies include labels without storage taints, built `./rook`, Multus, and default NADs. Risks include exact error-message coupling and intentional leftover resources requiring cleanup. Test signals are command failure, grep match, and non-empty pod list.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-210-stretch-overlap.sh -->
