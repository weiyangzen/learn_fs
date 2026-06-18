# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khremote.h

## Purpose

`khremote.h` defines the compatibility IPC contract used by external processes, especially older Leash-compatible callers, to request NetIDMgr credential dialogs. It names the request daemon window, shared-memory mapping format, request command, and fixed-layout dialog information structure.

## Important APIs, Types, and Functions

- `ID_OBTAIN_TGT_WITH_LPARAM` is the Leash-compatible command ID.
- `KHUI_REQDAEMONWND_CLASS` and `KHUI_REQDAEMONWND_NAME` identify the request daemon window.
- `KHUI_REQD_MAPPING_FORMAT` formats a per-request local file mapping name using a process or request ID.
- Fixed string sizes cover username, realm, title, and credential cache name.
- Dialog types are `NETID_DLGTYPE_TGT` and `NETID_DLGTYPE_CHPASSWD`.
- `NETID_DLGINFO` contains structure size, dialog type, input title/principal/realm/ccache/options/lifetimes/flags, and output username/realm/ccache.
- `NETID_DLGINFO_V1_SZ` records the version-1 structure size for compatibility.

## Control Flow

An external caller locates the NetIDMgr request daemon window, creates or opens a named mapping following `KHUI_REQD_MAPPING_FORMAT`, fills `NETID_DLGINFO`, then sends the Leash-compatible command with mapping information in `LPARAM`. NetIDMgr reads input fields, opens either an initial-ticket or password-change dialog, writes selected output fields, and signals completion according to the surrounding window-message protocol.

## State and Persistence Behavior

The structure is a shared-memory IPC record. Input fields are fixed-size wide-character buffers; output fields are written back into the same mapped region. Kerberos credential persistence happens in the selected credential cache, not in this structure. The `size` field supports compatibility with `NETID_DLGINFO_V1_SZ` and future extension.

## Dependencies and Integration Points

The header depends on Win32 `DWORD` and `WCHAR`. It duplicates a compatible shape also visible in `inc/leash/leashwin.h`, tying NetIDMgr to older Leash/KfW callers. It integrates with new-credentials UI in `khnewcred.h`, action IDs for obtaining tickets, and Kerberos cache settings.

## Risks and Edge Cases

- Fixed-size arrays must be explicitly null-terminated by readers and writers.
- Shared mappings named under `Local\\` are session-local; services or elevated processes may need different namespace handling.
- `NETID_DLGINFO_V1_SZ` is manually computed; adding fields requires careful version checks.
- The contract exposes credential options across process boundaries, so callers and the daemon must validate structure size and mapping ownership.

## Test Signals

- Exercise both TGT and password-change dialog requests through a mapped `NETID_DLGINFO`.
- Validate behavior with `size == NETID_DLGINFO_V1_SZ`, larger sizes, and too-small sizes.
- Test maximum-length username, realm, title, and cache fields for termination.
- Verify output username/realm/cache are written back after success and unchanged or cleared on cancel.
