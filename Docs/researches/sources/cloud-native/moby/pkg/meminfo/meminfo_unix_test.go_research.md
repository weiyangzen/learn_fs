<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_unix_test.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo_unix_test.go

Purpose: tests Linux meminfo parser behavior using synthetic `/proc/meminfo` content. It verifies recognized fields are parsed from kB to bytes and malformed lines are ignored. State is in-memory string readers. Dependencies are testing and strings. Risks covered include bad tokens and non-kB units; actual host `/proc/meminfo` read errors are not exercised. Test signal is strong for parser resilience.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_unix_test.go -->
