# sources/distributed-fs/openafs/src/WINNT/afsapplib/resize.h

## Purpose
Declares the public dialog-resizing contract for afsapplib. The comments provide the expected integration pattern: call `ResizeWindow` during dialog initialization, on `WM_SIZE`, and after adding UI elements that alter the client area.

## Important APIs and Types
`rwAction` selects the operation: move parent then resize guts, fix child controls against a new parent size, resync without moving children, or account for a changed client area. `ra*` flags describe each child rule: leave alone, move or size in positive or negative X/Y, move or size by half the delta, repaint, and notify. `rwWindowData` binds a child control ID to flags and optional packed minimum/maximum sizes. `idDEFAULT` supplies default behavior and `idENDLIST` terminates rule arrays.

Exports are `CreateSplitter`, `DeleteSplitter`, `ResizeWindow`, and `GetRectInParent`.

## State, Dependencies, and Integration
The header includes `windows.h` and uses HWND, RECT, LONG, and DWORD. Rule arrays are caller-owned and must remain valid while the window is tracked because the implementation caches the last `rwWindowData *`. Splitter creation also needs a caller-owned delta variable and rule table.

## Risks and Test Signals
The API encodes min/max dimensions in low/high words of DWORD fields, which limits range and requires callers to pack values correctly. The behavior of `rwaNewClientArea` depends on `RECT` being interpreted as a delta, not a literal rectangle. Test signals should validate documented sample layouts, default-rule fallback, min/max packing, repaint/notify flags, and splitter cleanup through `DeleteSplitter`.
