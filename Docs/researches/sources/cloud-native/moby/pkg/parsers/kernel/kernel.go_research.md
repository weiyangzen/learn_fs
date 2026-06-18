<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel.go

Purpose: non-Windows kernel version model, parser, formatter, and comparator. Important APIs are `VersionInfo`, `String`, `CompareKernelVersion`, and `ParseRelease`. Control flow parses strings like `4.1.2-generic` or `3.12-1-amd64`, tolerates missing minor patch by treating flavor as suffix, and compares only numeric kernel/major/minor fields. State is pure value data. Dependencies are fmt and errors. Risks include ignoring flavor in comparisons, accepting unusual release formats, and parser behavior around vendor suffixes. Test signal is in `kernel_unix_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel.go -->
