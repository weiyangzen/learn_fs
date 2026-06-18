<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/merge_test.go -->
# sources/cloud-native/buildkit/util/staticfs/merge_test.go

Purpose: validates overlay semantics of `MergeFS`.

Important APIs and types: `TestMerge`.

Control flow: the test builds lower and upper `FS` instances, verifies `Open` chooses upper content for duplicate path `foo` and lower for `bar`, walks merged output and asserts sizes/modes/order, then layers an additional filesystem and checks fallback/open/not-found behavior.

State and persistence: in-memory filesystems only.

Dependencies and integration: uses `context`, `io`, `os`, `io/fs`, `testify/require`, and `fsutil/types`.

Risks: tests assume deterministic path ordering from static FS and merge logic. They do not simulate walk callback errors or context cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/merge_test.go -->
