<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/hourglass.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/hourglass.h

Purpose: Defines a tiny RAII cursor helper that switches to a wait cursor while an object is in scope.

Important APIs/types: `HOURGLASS` constructor stores the current cursor and calls `SetCursor(LoadCursor(NULL, idCursor))`; destructor restores the previous cursor. `PHOURGLASS` is an alias pointer typedef.

Control flow: Stack allocation around slow UI operations temporarily changes the cursor.

State and persistence: Object-local previous cursor handle only. No persistence.

Dependencies and integration points: Uses Win32 cursor APIs. Included from `afscfg.h` and used by pages such as partition setup.

Risks: Cursor changes are thread/window-message sensitive; restoring a cursor saved before nested cursor changes can produce unexpected UI state. No error handling for `LoadCursor`.

Test signals: Test nested hourglass objects, exceptions/early returns, and use from UI thread only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/hourglass.h -->
