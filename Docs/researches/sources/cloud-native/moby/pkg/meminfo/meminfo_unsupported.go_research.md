<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_unsupported.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo_unsupported.go

Purpose: unsupported-platform implementation of memory info. `readMemInfo` returns an error indicating the platform cannot provide data. State is absent. Dependencies are minimal error creation. Risks are low; callers must handle unsupported errors. Test signal is compile-time portability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_unsupported.go -->
