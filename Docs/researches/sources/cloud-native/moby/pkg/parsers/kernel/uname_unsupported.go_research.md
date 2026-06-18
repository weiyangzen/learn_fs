<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/uname_unsupported.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/uname_unsupported.go

Purpose: unsupported-platform fallback for `uname`. It defines a compatible `utsName` shape and returns an unsupported error. State is absent. Dependencies are errors. Risks are low; callers must handle kernel version unavailability. Test signal is compile-time portability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/uname_unsupported.go -->
