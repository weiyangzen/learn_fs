<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.c

Purpose: Implements a Win32 GUI application for browsing OSI remote-debug collections exposed by the `dbrpc` RPC server. It connects to a host/object id, lists available collection types, retrieves entries, formats them with server-provided labels, and optionally saves displayed results to a file.

Important APIs, types, and functions: `WinMain`, `InitApplication`, and `InitInstance` set up the window class and child controls. `main_Layout` computes button, name, type list, result list, and status rectangles. `main_GetBinding` composes an `ncacn_ip_tcp` RPC binding, sets a short communication timeout, and attaches an object UUID. `main_GetFormatCache` caches positive and negative format descriptors from `dbrpc_GetFormat`. `main_RetrieveType` opens a remote fd, repeatedly calls `dbrpc_GetInfo`, formats string and integer data by region/index metadata, and closes the fd. `MainWndProc` handles command buttons, list selection, resize, paint, save-to-file, and quit. `FileProc` and `About` are modal dialog procedures; `main_SetStatus` updates the status control.

Control flow and state: The user enters a value like `host:instance`, clicks "Debug Server", and the code parses the suffix as a long converted to a UUID with `osi_LongToUID`. It obtains a remote binding, fetches the `"type"` collection into the types list, and later fetches a selected collection into the results list. Format metadata is cached globally in `main_allFormatsp`, so repeated fields avoid extra RPC calls. Save-to-file enumerates listbox strings and writes newline-terminated records with `WriteFile`.

Persistence and dependencies: Persistent writes are limited to a user-selected output file. Runtime state is mostly global HWNDs, rectangles, format cache entries, a binding handle, and `main_fileName`. Dependencies include Win32 GUI APIs, Microsoft RPC APIs, generated `dbrpc` client stubs, `osiutils.c` UUID conversion, `osidebug.h` resource IDs, and remote server format contracts.

Integration points: This is the manual diagnostic client for `osidb.c`, `osifd.c`, `osilog.c`, `osisleep.c`, and `osistatl.c`. It expects fd type names and format descriptors registered by those packages.

Risks: Several functions use implicit `int` return style and old Win32 casts. String handling uses fixed buffers, `strcpy`, `strcat`, and `wsprintf`, so long host names, file names, or server-returned values can overflow. `main_RetrieveType` treats `code == 1` as negative-cache format absence, coupling to numeric RPC constants. The condition `if (index != LB_ERR || main_remoteHandle == NULL)` appears inverted for null-handle protection and could call RPC with no binding. The GUI assumes ANSI APIs and old help/dialog resources.

Test signals: Manual or UI automation should verify binding success/failure messages, type listing, selecting each built-in fd type, formatting hex/signed/unsigned fields, EOF handling, repeated retrieval with format cache, save-to-file content, and behavior for unreachable hosts or malformed `host:id` strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osidebug.c -->
