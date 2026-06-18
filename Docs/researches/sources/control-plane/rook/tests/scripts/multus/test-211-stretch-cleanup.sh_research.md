<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-211-stretch-cleanup.sh -->
# sources/control-plane/rook/tests/scripts/multus/test-211-stretch-cleanup.sh

Purpose: cleanup test for resources left by the negative Multus overlap validation.

Important APIs and control flow: runs `./rook --log-level DEBUG multus validation cleanup --namespace stretch-overlap` and asserts no non-terminating pods remain in that namespace.

State, persistence, and integration: deletes validation resources in the overlap namespace. Dependencies include the built Rook CLI and resources from `test-210-stretch-overlap.sh`. Risks include namespace/resource leakage if cleanup misses kinds beyond pods. Test signals are an empty pod list after cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/test-211-stretch-cleanup.sh -->
