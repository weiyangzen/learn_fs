<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.cpp

Purpose: Implements loopback adapter installation/uninstallation, installed detection, rundll/MSI entry points, argument parsing, and MSI/printf reporting for OpenAFS loopback configuration.

Important APIs, types, and functions: `UnInstallLoopBack` enumerates present network devices, finds hardware id `*msloop`, selects and removes it. `IsLoopbackInstalled` scans present devices for the same hardware id. `InstallLoopBack` creates a net-class device info set, finds the Microsoft loopback class driver, registers/installs the phantom device, reads `NetCfgInstanceId`, renames the connection, sets IP/mask, adjusts bindings, and updates hosts/lmhosts. `process_args` parses rundll/MSI command-line tokens with defaults. `doLoopBackEntryW` and `uninstallLoopBackEntryW` are RunDll32 entry points. `installLoopbackMSI` and `uninstallLoopbackMSI` consume `CustomActionData`, call install/uninstall, and schedule reboot for return code 2. `ReportMessage` and `SetMsiReporter` report through stdout or MSI action data.

Control flow and state: Install creates and registers the adapter first, then configures it. On error after registration, cleanup removes the device. The code sets `registered` and `destroyList` flags to decide cleanup operations. MSI mode sets global `dwReporterType` and `hMsiHandle`; reporting is otherwise printf-based. Argument parsing allocates wide strings and frees them in `Args` destructor.

Persistence and dependencies: Persists device installation, registry/device state, network connection name, static IP configuration, binding order/enabled protocols, and `hosts`/`lmhosts` edits. Dependencies include SetupAPI, COM/WMI helpers from `wmi.cpp`, shell rename helper, MSI APIs, and admin rights.

Integration points: Used by `instloop.c`, RunDll32 custom entries, and WiX/MSI custom actions. Calls exported functions declared in `loopbackutils.h`: `RenameConnection`, `SetIpAddress`, `LoopbackBindings`, and `UpdateHostsFile`.

Risks: Device enumeration and driver detail parsing use fixed buffers and pointer bounds that must match MULTI_SZ layout. `InstallLoopBack` calls `SetupDiDeleteDeviceInfo` even after successful install, relying on behavior of the setup API. MSI property buffer allocation loops must handle `ERROR_MORE_DATA` carefully. Global MSI reporter state is not thread-safe. `process_args` treats any substring containing `help` as help. `ReportMessage` creates MSI records but sets only four fields in a five-field record.

Test signals: Install/uninstall in clean VM, already-installed detection, failure cleanup after driver registration, MSI custom action `CustomActionData` parsing, RunDll32 invocation, scheduled reboot paths, and host/lmhost/binding/IP postconditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/loopbackutils.cpp -->
