<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix.go -->
# sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix.go

Purpose: Linux/BSD kernel backend using `uname`. Important APIs are `GetKernelVersion` and `CheckKernelVersion`. Control flow calls platform `uname`, converts the release byte array to a string, parses it, and compares current version against requested minimum while logging and allowing success if version lookup fails. State is host kernel snapshot only. Dependencies are x/sys/unix and containerd logging. Risks include permissive failure behavior in `CheckKernelVersion`, release parsing limitations, and platform build tags. Test signal is parser/comparator tests in `kernel_unix_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/kernel/kernel_unix.go -->
