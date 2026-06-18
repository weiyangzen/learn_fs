# sources/cloud-native/containers-storage/pkg/system/syscall_windows.go

Purpose: Windows syscall helpers for OS/SKU detection, command-line parsing, win32k support, and cross-platform stubs.

Important APIs/types/functions: `OSVersion`, `GetOSVersion`, `IsWindowsClient`, `IsIoTCore`, `Unmount`, `CommandLineToArgv`, `HasWin32KSupport`, and `IsEBUSY`.

Control flow: version/SKU functions call `GetVersion`, `GetVersionExW`, and `GetProductInfo`, logging warnings and returning conservative false values on failures. `CommandLineToArgv` converts a UTF-16 command line through the Windows API and frees the returned buffer. `HasWin32KSupport` probes a lazy DLL load.

State/persistence: no persistent storage; lazy DLL handles are process state. `Unmount` is a no-op on Windows.

Dependencies/integration: used by Windows container platform checks, licensing/SKU gates, LCOW/path logic, and tests.

Risks: Windows version APIs can be manifest-sensitive. `IsWindowsClient` and `IsIoTCore` are marked as licensing-sensitive and should not be casually changed. `IsEBUSY` always false, so removal retry behavior differs from Unix.

Test signals: `syscall_windows_test.go` verifies `HasWin32KSupport` does not panic; broader Windows CI should cover command-line parsing and SKU helper behavior.
