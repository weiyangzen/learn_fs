<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin_test.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin_test.go

Purpose: tests Darwin `getRelease` parsing from representative `system_profiler` output. It asserts kernel release extraction and error behavior for malformed data. State is in-memory strings. Dependencies are gotest assertions. Risks covered are formatting assumptions around `Kernel Version`; real command execution is not tested. Test signal is focused parser coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_darwin_test.go -->
