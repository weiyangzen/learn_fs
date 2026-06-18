# sources/distributed-fs/openafs/src/WINNT/client_creds/shortcut.h

Purpose: declares shortcut lifecycle and creation helpers for `afscreds.exe`.

Important APIs: `Shortcut_Init`, `Shortcut_Exit`, `Shortcut_Create`, and `Shortcut_FixStartup`. `Shortcut_Create` has default `NULL` description and argument parameters for C++ callers.

Control flow: no implementation. Main startup/shutdown calls COM lifecycle wrappers, while settings and install paths call `Shortcut_FixStartup`.

State/persistence: declared functions may create or delete filesystem `.lnk` files and read registry settings.

Dependencies/integration: requires C++ default arguments and Win32 string types; used from `main.cpp` and `advtab.cpp`.

Risks: header is C++-oriented despite the broader project using C linkage in places. Callers must ensure COM lifecycle is initialized before shell-link operations if bypassing `Shortcut_FixStartup`.

Test signals: compile references and startup shortcut behavior from install/uninstall and Advanced tab toggles.
