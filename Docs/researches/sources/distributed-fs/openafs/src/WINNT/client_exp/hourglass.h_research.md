## sources/distributed-fs/openafs/src/WINNT/client_exp/hourglass.h

Purpose: Provides an RAII helper that switches the cursor to a wait cursor for the lifetime of a stack object.

Important APIs/types: `HOURGLASS` stores the previous `HCURSOR` in its constructor and restores it in its destructor. The default cursor resource is `IDC_WAIT`.

Control flow/state: Used by long-running UI operations around cache-manager ioctls, registry updates, token work, and network lookups. State is only the saved cursor handle.

Dependencies/integration: Depends on `<windows.h>` and Win32 `GetCursor`, `SetCursor`, and `LoadCursor`. Integrated broadly across dialogs and `gui2fs.cpp`.

Risks/tests: Cursor state is thread/UI-message sensitive; nested instances should restore in LIFO order. Test exceptions/early returns, nested hourglasses, and calls from non-UI worker contexts.
