<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_windows.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_windows.go

Purpose: Windows-specific kernel version backend and model. `GetKernelVersion` reads `BuildLabEx` from the registry and uses `windows.GetVersion` to fill major, minor, and build numbers; `String` formats those values. State is a snapshot of registry and OS version APIs. Dependencies are Windows registry and x/sys/windows. Risks include dockerd manifest requirements for correct `GetVersion`, registry access failure, and private lowercase fields limiting cross-platform API symmetry. Test signal is platform integration only.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_windows.go -->
