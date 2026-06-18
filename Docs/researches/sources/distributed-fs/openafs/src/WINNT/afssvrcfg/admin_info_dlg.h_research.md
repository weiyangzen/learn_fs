# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/admin_info_dlg.h

## Purpose
Declares the administrator-information dialog entry point and option enum for the OpenAFS server configuration UI.

## Important APIs, Types, And Functions
`GET_ADMIN_INFO_OPTIONS` has `GAIO_LOGIN_ONLY` and `GAIO_GET_SCS`, where the latter includes the former plus system-control-server collection. `GetAdminInfo(HWND hParent, GET_ADMIN_INFO_OPTIONS eOptions)` opens the modal dialog and returns success/failure.

## Control Flow
Callers select the mode, call `GetAdminInfo`, and on `TRUE` read updated global configuration data managed by the dialog implementation.

## State And Persistence
The header itself has no state. The option controls which UI fields are shown and which global config fields are saved by `admin_info_dlg.cpp`.

## Dependencies And Integration Points
It depends on Win32 `HWND`/`BOOL` types from surrounding includes and is consumed by the server configuration application where administrator credentials are needed.

## Risks And Test Signals
The enum ordering is documented as cumulative, so future options should preserve that assumption. Compile coverage and dialog smoke tests in both modes are sufficient signals.
