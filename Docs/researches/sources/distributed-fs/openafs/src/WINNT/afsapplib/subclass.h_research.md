# sources/distributed-fs/openafs/src/WINNT/afsapplib/subclass.h

## Purpose
Declares the afsapplib subclass-chain helper. The header explains why direct `SetWindowLong(GWL_WNDPROC)` chaining is brittle when multiple components subclass the same child window and provides a cooperative alternative.

## Important APIs and Types
`Subclass_AddHook(HWND, PVOID)` registers a window procedure hook. `Subclass_RemoveHook(HWND, PVOID)` unregisters one request for that hook. `Subclass_FindNextHook(HWND, PVOID)` lets a hook discover the next hook or original procedure to forward to. The header intentionally exposes procedures as `PVOID`, leaving casts to caller code.

## State, Dependencies, and Integration
Consumers are expected to call add on creation, find-next and `CallWindowProc` inside the hook, and remove on destruction. Repeated add calls with the same target/proc require the same number of remove calls. This integrates with `resize.cpp`, which installs `Resize_DialogProc` on tracked dialogs.

## Risks and Test Signals
The API is cooperative: if a hook does not forward, later hooks and the original window proc do not see the message. Because the header uses `PVOID`, type safety is weak, especially across ANSI/Unicode and pointer-size builds. Tests should verify forwarding examples, duplicate-count behavior, and removal that is not reverse install order.
