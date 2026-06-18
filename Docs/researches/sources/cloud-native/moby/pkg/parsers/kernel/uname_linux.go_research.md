<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/uname_linux.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/uname_linux.go

Purpose: Linux implementation of the package-local `uname` helper. It calls `unix.Uname` and returns the populated `unix.Utsname`. State is host kernel uname data. Dependencies are x/sys/unix. Risks are low; errors propagate to `GetKernelVersion`. Test signal is indirect through runtime kernel-version calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/uname_linux.go -->
