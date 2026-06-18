<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/sysinfo/sysinfo.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/sysinfo/sysinfo.go

Purpose: exposes cached system memory information from the Linux `sysinfo` syscall.

Important APIs/state: `GetSysinfo`, `GetTotalMemoryBytes`, and package globals `sysinfo`, `sysinfoOnce`, `sysinfoErr`. `GetTotalMemoryBytes` initializes once and returns `int(sysinfo.Totalram)`.

Control flow and state: the first `GetTotalMemoryBytes` call populates the global cache. Subsequent calls return the same value/error for process lifetime.

Dependencies/integration: uses standard `syscall.Sysinfo_t`; useful for config parsers that accept memory percentages.

Risks and test signals: `Sysinfo_t.Totalram` should be multiplied by `Unit` on some platforms/architectures, but this code returns `Totalram` directly. Conversion to `int` can overflow on 32-bit architectures. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/sysinfo/sysinfo.go -->
