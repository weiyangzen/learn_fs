<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin.go

Purpose: Darwin kernel version backend using `system_profiler SPSoftwareDataType`. Important APIs are `GetKernelVersion`, `getRelease`, and `getSPSoftwareDataType`. Control flow executes `system_profiler`, finds the `Kernel Version:` line, extracts the Darwin release after the OS name, and parses it with `ParseRelease`. State is command output only. Dependencies include external `system_profiler` and string parsing. Risks include localized or changed profiler output, empty release returning parse errors later, and command execution cost. Test signal is `kernel_darwin_test.go` for release extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin.go -->
