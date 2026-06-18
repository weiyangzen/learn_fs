<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_windows.go -->
# sources/cloud-native/moby/daemon/internal/platform/platform_windows.go

Purpose: implements Windows host architecture and processor count detection.

Important APIs and types: `systeminfo`, Windows architecture constants, `runtimeArchitecture`, `NumProcs`, and `possibleCPUs`.

Control flow: calls `GetSystemInfo` through `syscall.SyscallN`, maps processor architecture codes to strings, returns processor count, and leaves possible CPU discovery unimplemented.

State and persistence: lazy DLL/proc handles are package globals; no other state.

Dependencies and integration: used by `platform.go` on Windows.

Risks: TODO notes `GetNativeSystemInfo` would be more accurate for WOW64 processes. Unknown architecture returns an error. `possibleCPUs` nil forces generic fallback.

Test signals: no direct Windows tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_windows.go -->
