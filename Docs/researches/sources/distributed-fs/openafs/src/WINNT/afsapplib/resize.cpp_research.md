# sources/distributed-fs/openafs/src/WINNT/afsapplib/resize.cpp

## Purpose
Implements generic Win32 dialog resizing and splitter support. A caller supplies `rwWindowData` rules for each child control, then `ResizeWindow` applies movement and sizing deltas when the parent changes size or its client area changes.

## Important APIs and Control Flow
`ResizeWindow` records the previous parent rectangle in a global `WindowList`, optionally moves the parent for `rwaMoveToHere`, computes deltas for normal resize or `rwaNewClientArea`, and uses `BeginDeferWindowPos`/`DeferWindowPos` to update child windows according to `raMove*`, `raSize*`, and center-half flags. It handles repaint and resize notification flags after all positions are deferred.

`rwFindOrAddWnd` registers a tracked window and installs `Resize_DialogProc` through the subclass helper. `Resize_DialogProc` handles `WM_GETMINMAXINFO` by calling `FindResizeLimits` and removes tracking on `WM_DESTROY`. `CreateSplitter` determines a splitter rectangle between two controls, registers horizontal and vertical splitter window classes, allocates `SplitterData`, and creates a child splitter. `SplitterWndProc` tracks mouse capture and calls `ResizeSplitter`, which clamps movement with `FindSplitterMinMax` and applies child deltas. `GetRectInParent` converts screen coordinates to parent client coordinates.

## State, Dependencies, and Integration
State is global and in-process: tracked windows in `awl`, per-window saved rectangles and half-pixel remainder accumulators, static splitter class registration, and per-splitter `SplitterData`. Dependencies include Win32 windowing APIs, `al_resource.h` cursor IDs, afsapplib allocation helpers, `subclass.h`, and `TaLocale.h`.

## Risks and Test Signals
The global tracking list and splitter registration are unsynchronized. `rwFindAndRemoveWnd` calls `Subclass_RemoveHook(awl[ii].hWnd, hWnd)` even though the hook installed was `Resize_DialogProc`, which looks like a removal bug. In `SplitterWndProc`, `WM_DESTROY` frees `SplitterData` only inside `if (psd->fDragging)`, so non-dragging splitters may leak. The code uses `SetWindowLong`/`GetWindowLong` and a `GWL_USER` fallback, which is fragile for pointer-sized data. Tests should exercise resize deltas, odd-pixel center accumulation, min/max tracking, destroy cleanup, splitter drag clamping, hook removal, and both horizontal and vertical layouts.
