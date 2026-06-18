<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix_test.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix_test.go

Purpose: tests non-Windows kernel release parsing and version comparison. It covers typical kernel strings, missing patch versions, flavors, invalid releases, and compare outcomes for less/equal/greater numeric versions. State is pure value data. Dependencies are standard testing and fmt helper output. Risks covered include parser regressions and comparator ordering; runtime `uname` is not exercised. Test signal is strong for pure parser behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix_test.go -->
