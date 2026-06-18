# sources/distributed-fs/openafs/src/WINNT/client_creds/main.cpp

Purpose: process entry and application initialization for `afscreds.exe`.

Important APIs/functions: `WinMain`, `InitApp`, `ExitApp`, `PumpMessage`, `Quit`, and `IsServerInstalled`. Command-line switches control auto token init, map renewal, network monitor, show/quiet/exit/install/uninstall, share mapping, unmapping, and map testing.

Control flow: startup initializes shortcuts, locale resources, tracing, and mount root; parses command-line flags; handles install/uninstall shortcut and registry writes; enforces single instance by class-name scan; loads tray startup preference; initializes Winsock/common controls/OSI locks/KFW; optionally starts the AFS service; creates the main modeless dialog; shows setup wizard or token prompts as needed; optionally starts the IP change monitor; then runs the message loop.

State/persistence: initializes global `g`, including startup flag, OS flag, mutexes, main window, and SMB share. Reads/writes `ShowTrayIcon` under HKCU/HKLM OpenAFS keys and manipulates the Startup shortcut.

Dependencies/integration: ties together shortcut, locale, tracing, mount-root, service control, KFW, drive-map, credentials UI, startup wizard, and network-change monitor.

Risks: single-instance detection scans top-level windows by class name and can race. Some command-line paths return before full initialization/cleanup. Service start requires privileges and logs mostly to debugger. Registry precedence logic is important for policy/user overrides.

Test signals: each command-line switch, install/uninstall behavior with existing instance, first-start with service stopped/configured/unconfigured, auto-init token prompt, drive-map renewal, and message loop shutdown.
