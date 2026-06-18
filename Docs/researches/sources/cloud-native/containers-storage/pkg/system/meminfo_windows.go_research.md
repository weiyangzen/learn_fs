# sources/cloud-native/containers-storage/pkg/system/meminfo_windows.go

Purpose: Windows implementation of host memory probing for the `system` package. It backs the cross-platform `ReadMemInfo` API by calling `kernel32!GlobalMemoryStatusEx`.

Important APIs/types/functions: defines the local `memorystatusex` struct matching the Win32 `MEMORYSTATUSEX` layout, lazy DLL/proc handles for `kernel32.dll`, and `ReadMemInfo() (*MemInfo, error)`. `ReadMemInfo` fills `MemTotal`, `MemFree`, `SwapTotal`, and `SwapFree` from physical and pagefile counters.

Control flow: allocate a struct with `dwLength` set to 64, invoke the syscall through `procGlobalMemoryStatusEx.Call`, and return an empty `MemInfo` on failure rather than surfacing the Win32 error. On success it converts unsigned byte counts to signed `int64`.

State/persistence: no persistent state. Lazy procedure handles are package-level process state and memory values are a point-in-time host snapshot.

Dependencies/integration: depends on `golang.org/x/sys/windows` and `unsafe`. It integrates with generic storage resource reporting wherever `system.ReadMemInfo` is used on Windows.

Risks: the hard-coded `dwLength` must continue to match the struct layout; if the syscall fails, callers cannot distinguish zero-memory results from failure because nil error is returned with an empty struct. Large pagefile values are cast to `int64`.

Test signals: Windows tests should mock or run on real hosts to verify non-zero memory counters, syscall failure behavior, and ABI layout if the struct changes.
