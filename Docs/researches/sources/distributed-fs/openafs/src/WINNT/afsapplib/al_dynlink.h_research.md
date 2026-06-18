## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_dynlink.h

Purpose: Declares the dynamic-loading interface for optional OpenAFS admin DLLs and exposes macro names that make function-pointer calls look like normal API calls.

Important APIs and types: Declares `OpenUtilLibrary`, `OpenKasLibrary`, `OpenClientLibrary` and close counterparts. Defines function pointer typedefs for utility error translation, KAS principal enumeration/get, token get/new/close/query, cell open/close, and local cell lookup. Declares extern variables such as `afsclient_TokenGetExistingP` and maps `afsclient_TokenGetExisting` to `(*afsclient_TokenGetExistingP)`.

Control flow: This header has no runtime logic; it creates the contract that callers must obey: call `Open*Library` before using the macro-expanded function pointers and `Close*Library` afterward.

State and persistence: State is external global process state implemented in `al_dynlink.cpp`. There is no persistence.

Dependencies and integration points: Pulls in `afs_Admin.h`, `afs_utilAdmin.h`, `afs_kasAdmin.h`, and `afs_clientAdmin.h`. It is included by credential, misc/error translation, and KAS-related code.

Risks: Macro aliases hide pointer dereferences and will crash if callers forget to open the library or ignore `Open*Library` failure. The header exposes mutable globals across compilation units, making ownership and thread-safety unclear.

Test signals: Compile tests should verify typedef compatibility with shipped DLL exports. Runtime tests should call every macro only after a successful open and confirm failure paths never dereference null pointers.
