# sources/distributed-fs/openafs/src/WINNT/client_creds/afscreds.h

Purpose: central shared header for `afscreds.exe`; it collects Windows/OpenAFS includes, resource IDs, shared constants, global data structures, macros, and cross-module prototypes.

Important types: `CREDS` stores cell, user, expiration time, and reminder flag. `GLOBALS` stores the main window, dynamic credential array, retest timestamp, message-display count, wizard pointer, startup/OS flags, two OSI mutexes, and SMB share name.

Control flow: no direct flow, but it defines timing constants for reminder, renewal, service polling, and mouse-over retests. The `REALLOC` macro routes dynamic array growth through `AfsCredsReallocFunction`.

State/persistence: declares external `GLOBALS g`, which is the primary in-process state shared by main window, tabs, tray icon, token operations, and wizard code. Registry value names and shortcut options document persistent configuration surfaces.

Dependencies/integration: pulls in `TaLocale`, Win32 common controls, registry constants, OSI locks, RXKAD, wizard/dialog helpers, all local tab headers, drive mapping, and help IDs.

Risks: very broad include surface couples most modules to Windows, OpenAFS, and UI details. Global mutable state demands correct locking around `g.aCreds` and expiration checks. Macro redefinition of `REALLOC` can collide with other headers.

Test signals: full application build, thread-safety tests around `g.credsLock`, and registry setting compatibility across 32/64-bit registry views.
