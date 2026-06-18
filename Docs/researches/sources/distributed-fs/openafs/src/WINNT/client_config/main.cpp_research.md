# sources/distributed-fs/openafs/src/WINNT/client_config/main.cpp

## Purpose
`main.cpp` is the Win32 entry point and property-sheet bootstrap for the AFS Client Configuration utility and Control Center variant.

## Important APIs, Types, and Functions
It defines the global `GLOBALS g`, `WinMain`, `Main_ShowMountTab`, `Main_OnInitDialog`, `Main_RefreshAllTabs`, `Quit`, `GetCautionTitle`, and `GetErrorTitle`.

## Control Flow
`WinMain` loads localized resources, starts Winsock, registers custom controls, initializes mount-root utilities, clears `g`, detects platform/admin state, parses `/c` for Control Center mode, selects the help file, creates a property sheet, and adds tabs based on mode, OS, and `ShowMountTab` registry policy. The modal property sheet owns the app lifetime.

## State and Persistence Behavior
`g` holds all process-global app state. `Main_ShowMountTab` reads `ShowMountTab` from HKCU first and HKLM second, using 64-bit registry view on WOW64. `Main_OnInitDialog` centers the property sheet and strips context-help styles. Title helpers cache localized strings.

## Dependencies and Integration Points
The entry point wires together general, drives, prefs, hosts, and advanced tabs. It depends on `isadmin`, custom UI control registration, `fs_utils_InitMountRoot`, registry constants, and the property-sheet helper library.

## Risks and Edge Cases
The command-line parser only recognizes leading slash/dash options and appears to advance only over spaces after each option, so combined or valued options are not robust. There is no `WSACleanup`. Tab inclusion depends on registry policy and OS/admin flags, so missing registry values can hide drive UI.

## Test Signals
Smoke tests should verify startup in NT, Win9x-compatible, and Control Center modes; `ShowMountTab` policy from HKCU/HKLM including WOW64; correct tab set; help-file selection; and `Main_RefreshAllTabs` delivery of `IDC_REFRESH`.
