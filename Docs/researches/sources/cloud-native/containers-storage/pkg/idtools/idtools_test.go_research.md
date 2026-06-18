## sources/cloud-native/containers-storage/pkg/idtools/idtools_test.go

Purpose: unit tests for core ID mapping and override-xattr formatting/parsing.

Important APIs/types/functions: `TestToHost`, `TestToHostOverflow`, `TestGetRootUIDGID`, `TestIsContiguous`, `TestParseOverrideXattr`, `TestFormatContainersOverrideXattrDevice`, and `TestParseDevice`.

Control flow: constructs in-memory maps, verifies translation and overflow IDs, tests root ID extraction error cases, checks contiguous and non-contiguous maps, parses xattr strings into `Stat`, formats many mode/type/device combinations, and validates device parser error handling.

State and persistence: mostly pure; overflow tests may read cached `/proc/sys/kernel/overflow*` through code under test.

Dependencies and integration points: covers behavior used by archive/chunked force-mask and namespace remapping.

Risks: no tests for `SafeChown`, xattr system calls, `NewIDMappings`, or malformed subid files here. `IsContiguous` mutation of input order is not asserted.

Test signals: strong pure-function coverage; local execution unavailable because `go` is missing.
