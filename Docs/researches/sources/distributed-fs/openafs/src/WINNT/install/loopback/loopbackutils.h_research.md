<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.h -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.h

Purpose: Declares the C ABI for loopback adapter installation/configuration helpers and shared defaults/reporting constants.

Important APIs, types, and functions: Exports include `InstallLoopBack`, `IsLoopbackInstalled`, `UnInstallLoopBack`, `RenameConnection`, `SetIpAddress`, `LoopbackBindings`, `UpdateHostsFile`, `ReportMessage`, and `SetMsiReporter`. Defaults are `DRIVER_DESC`, `DRIVER`, `DRIVERHWID`, `MANUFACTURE`, `DEFAULT_NAME`, `DEFAULT_IP`, and `DEFAULT_MASK`. Reporting modes are `REPORT_PRINTF`, `REPORT_MSI`, and `REPORT_IGNORE`; globals are `dwReporterType` and `hMsiHandle`.

Control flow and state: Consumers call install/uninstall/detect and lower-level configuration helpers. Reporting behavior is controlled by global mode and handle.

Persistence and dependencies: Implementations persist network and file changes. Header depends on Windows TCHAR/DWORD types and is C/C++ compatible via `extern "C"`.

Integration points: Shared by command-line installer, RunDll32/MSI DLL entry points, WMI helpers, and rename helper.

Risks: Default IP/mask and connection name are hard-coded. Reporter globals are process-wide. The ABI exposes lower-level helpers that can be called out of sequence.

Test signals: ABI export checks, C and C++ include tests, default value verification, and integration tests that call each exported helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.h -->
