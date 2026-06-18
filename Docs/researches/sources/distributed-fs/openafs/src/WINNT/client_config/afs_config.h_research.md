# sources/distributed-fs/openafs/src/WINNT/client_config/afs_config.h

## Purpose
`afs_config.h` is the central include and global-state contract for the AFS client configuration applet. It pulls in the Win32 UI controls, OpenAFS configuration headers, local tab headers, CellServDB support, drive-map support, resources, and configuration APIs.

## Important APIs, Types, and Functions
The primary type is `GLOBALS`, exported as `extern GLOBALS g`. It stores the main property sheet, platform/admin flags, help-file path, restart-required flag, and an embedded `Configuration` struct containing gateway, cell, sysname, cache, daemon/thread, login, diagnostic, server preference, CellServDB, and drive-map state.

## Control Flow
This header has no executable flow, but it defines the shared state that `main.cpp` initializes and every tab reads or mutates. It also declares application helpers such as `Quit`, `AfsConfigReallocFunction`, `Main_OnInitDialog`, `Main_RefreshAllTabs`, `GetCautionTitle`, and `GetErrorTitle`.

## State and Persistence Behavior
`g.Configuration` is the in-memory staging area for values read from registry, CellServDB, service state, and pioctl calls. Dialogs compare their local values against `g.Configuration` before calling `Config_Set*` functions. `g.fNeedRestart` is the cross-tab signal that a service restart should be offered after applying changes.

## Dependencies and Integration Points
The header couples all client-config modules to `TaLocale`, custom controls (`fastlist`, `spinner`, `sockaddr`, `dialog`), `cellservdb.h`, `drivemap.h`, `resource.h`, `config.h`, `help.hid`, and OpenAFS registry constants.

## Risks and Edge Cases
Because `GLOBALS` is a process-wide mutable singleton, tabs can observe stale values if one dialog updates registry or service state without updating `g.Configuration`. The broad include surface also means build-order and macro conflicts are likely. The `REALLOC` macro hides pointer/count mutation, so misuse can silently corrupt shared arrays.

## Test Signals
Compile-time coverage should ensure every tab sees the same structure layout. Runtime smoke tests should open all tabs, apply changes in different orders, and verify `g.fNeedRestart` and `g.Configuration` remain consistent after commits and cancellations.
