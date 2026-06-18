<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/utils_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/utils_test.go

Purpose: shared test helpers for archive breakout/security tests.

Important APIs/types/functions: `testUntarFns` and `testBreakout`.

Control flow: `testBreakout` creates sibling `dest` and `victim` directories, writes a unique `victim/hello`, streams supplied tar headers into `Untar` or `ApplyLayer`, allows `breakoutError` as a successful detection, then verifies the victim directory and file were not removed, modified, replaced, or read into destination output.

State/persistence: temporary test directories only.

Dependencies/integration: supports `diff_test.go` and related untar tests by abstracting both extraction APIs behind `testUntarFns`.

Risks/test signal: this is a high-value security oracle for path traversal through names, hardlinks, and symlinks. It cannot prove all breakouts are impossible, but it checks concrete read/write/remove scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/utils_test.go -->
