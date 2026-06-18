<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kclient.h -->
## sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kclient.h

Purpose: Declares the legacy KClient Kerberos API used by Windows OpenAFS/KfW integration code, with calling convention differences for Win32 and non-Win32 builds.

Important APIs, types, and functions: `KC_CALLTYPE` is `__stdcall` on Win32 and `WINAPI` otherwise; `KC_EXPORT` is empty on Win32 and `_export` otherwise. Ticket/session functions include `GetTicketForService`, `GetTicketGrantingTicket`, `DeleteAllSessions`, `SetUserName`, `KCGetUserName` or `GetUserName`, `ListTickets`, `SetTicketLifeTime`, `SetKrbdllMode`, `TgtExist`, optional `ChangePassword`, `KClientErrno`, `KClientKerberosErrno`, `SendTicketForService`, and `_KCGetNumInUse` on Win32.

Control flow and state: This is a header-only API contract; implementations manage Kerberos tickets, sessions, usernames, ticket lifetimes, and error state elsewhere. The Win32 export note says a `.def` file is used because the compiler could not combine `__stdcall` and `__declspec(dllexport)` as desired.

Persistence and dependencies: Ticket/session persistence is implementation-dependent, not in this header. Depends on `kcmacerr.h`, Windows `BOOL`, `LPSTR`, `LPDWORD`, `HWND`, `DWORD`, and `OSErr`.

Integration points: Used by OpenAFS Windows Kerberos compatibility and credential acquisition code.

Risks: This is a legacy ANSI API with global process/session state and non-thread-obvious error retrieval functions. `GetUserName` name conflicts with Win32 API, so Win32 uses `KCGetUserName`. Conditional `KLITE` changes exported surface. Calling convention/export mismatches can break binary compatibility.

Test signals: ABI/export tests against the DLL `.def`, calling-convention smoke tests from C/C++ clients, ticket acquisition/list/delete integration tests, and error-code propagation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/kclient/kclient.h -->
