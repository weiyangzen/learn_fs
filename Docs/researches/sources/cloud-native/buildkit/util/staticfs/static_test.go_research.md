<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/static_test.go -->
# sources/cloud-native/buildkit/util/staticfs/static_test.go

Purpose: unit tests for the in-memory static filesystem.

Important APIs and types: `TestStatic`.

Control flow: test adds files with modes/data, opens and reads content, verifies not-found behavior, walks all files checking size/mode/order, then adds a third file and verifies all open/read paths.

State and persistence: in-memory only.

Dependencies and integration: uses `context`, `io`, `os`, `io/fs`, `testify/require`, and `fsutil/types`.

Risks: no tests for target-prefixed walks, leading slash normalization, or directory-like paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/staticfs/static_test.go -->
