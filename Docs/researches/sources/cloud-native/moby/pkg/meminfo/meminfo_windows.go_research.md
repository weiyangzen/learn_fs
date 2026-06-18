<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_windows.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo_windows.go

Purpose: Windows memory information backend. It defines a `MEMORYSTATUSEX`-compatible struct and calls `GlobalMemoryStatusEx` to populate physical and pagefile memory totals/free values. State is a host memory snapshot. Dependencies are `golang.org/x/sys/windows` and unsafe syscall struct layout. Risks include struct-size/layout correctness, API failure handling, and semantic differences between Windows pagefile and Unix swap. Test signal is platform integration rather than unit coverage in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo_windows.go -->
