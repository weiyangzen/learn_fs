<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/instloop.c -->
## sources/distributed-fs/openafs/src/WINNT/install/loopback/instloop.c

Purpose: Command-line installer/uninstaller for the Microsoft Loopback Adapter configured for OpenAFS.

Important APIs, types, and functions: `ShowUsage` prints CLI syntax. `DisplayStartup` and `DisplayResult` print install/uninstall status. `_tmain` parses `-i [name [ip mask]]` and `-u`, applies defaults from `loopbackutils.h`, calls `IsLoopbackInstalled`, `InstallLoopBack`, or `UnInstallLoopBack`, and returns the resulting code.

Control flow and state: Install mode defaults to connection name `AFS`, IP `10.254.254.253`, and mask `255.255.255.252`. If a loopback adapter is already detected, it returns success without installing another. Optional compile-time output redirection appends to `instlog.txt`.

Persistence and dependencies: Persists network adapter installation, connection rename, IP/mask, binding changes, and hosts/lmhosts updates through `loopbackutils.cpp` and `wmi.cpp`. Depends on administrative privileges and SetupAPI/WMI support.

Integration points: Standalone wrapper around the loopback DLL/helper functions also used by MSI/rundll entry points.

Risks: Argument parsing requires both IP and mask if either is specified. Installation can take a long time and depends on hardware/driver enumeration. Existing adapter detection does not validate current name/IP/bindings.

Test signals: CLI usage, default install, custom name/IP/mask install, already-installed behavior, uninstall behavior, and return codes requiring reboot or failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/loopback/instloop.c -->
