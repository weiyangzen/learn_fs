## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_dynlink.cpp

Purpose: Lazily loads OpenAFS admin DLLs and resolves the client, KAS, and utility admin entry points needed by the app library when no remote admin server client is in use.

Important APIs and functions: `OpenUtilLibrary`/`CloseUtilLibrary`, `OpenKasLibrary`/`CloseKasLibrary`, and `OpenClientLibrary`/`CloseClientLibrary` maintain module handles and exported function pointer variables declared in `al_dynlink.h`. Loaded DLLs are `AfsAdminUtil.dll`, `AfsKasAdmin.dll`, and `AfsClientAdmin.dll`.

Control flow: Each `Open*Library` increments a request counter, loads the DLL only on the first request, resolves all required exports with `GetProcAddress`, and rolls back by calling the corresponding close function if any step fails. `OpenClientLibrary` additionally resolves `afsclient_Init` and calls it before reporting success. Each `Close*Library` decrements the request count and frees the library when it reaches zero.

State and persistence: Global static counters (`g_cReq*Library`), module handles, and global function pointers hold process-local library state. There is no on-disk persistence and no explicit synchronization around counters or function pointer mutation.

Dependencies and integration points: Includes AFS admin headers for function signatures and Win32 `LoadLibrary`/`FreeLibrary`. Used by credential, error translation, and misc routines to call AFS client/admin APIs through macro aliases.

Risks: The reference counters are unsigned `size_t`; calling a close routine without a matching open underflows and prevents cleanup. The code is not thread-safe, so concurrent opens/closes can race. Partial failure leaves some function pointers stale until next successful load. DLL names are unqualified, so Windows DLL search-order behavior matters.

Test signals: Test successful and missing-DLL cases, missing export cases, repeated nested opens/closes, client init failure, and concurrent access from credential/background worker paths. Confirm `pStatus` receives useful `GetLastError` or AFS status values.
