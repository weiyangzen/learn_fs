# sources/distributed-fs/openafs/src/WINNT/afsapplib/subclass.cpp

## Purpose
Implements a small global manager for stacking multiple window-procedure hooks on the same HWND without requiring strict reverse-order uninstallation by independent callers.

## Important APIs and Control Flow
`Subclass_AddHook` finds or creates a `SubclassWindow` entry for the target, finds or creates a hook slot for the requested procedure, increments the request count, and installs `Subclass_WndProc` as the real Win32 window procedure when the first active hook is added. `Subclass_RemoveHook` decrements the hook's request count, clears the slot at zero, decrements active-hook count, and restores the original window procedure when no hooks remain. `Subclass_FindNextHook` returns the next registered hook after the caller's procedure, or the original proc if the caller is last. `Subclass_WndProc` dispatches each message to the first active hook; hook code is expected to call `Subclass_FindNextHook` and forward manually.

## State, Dependencies, and Integration
State is a process-global dynamic `aTargets` array, each target containing original procedure, hook array, capacity, and active count. Allocation uses `GlobalAlloc` through a local `REALLOC`. It depends on Win32 `GetWindowLongPtr`, `SetWindowLongPtr`, and `CallWindowProc`, plus afsapplib's public `subclass.h` contract.

## Risks and Test Signals
There is no synchronization around global arrays, so cross-thread subclass changes can race. Underflow is possible if `Subclass_RemoveHook` is called for an unregistered hook because `nHooksActive` is decremented once a target is found regardless of whether a hook was removed. `SetWindowLongPtr` receives `PtrToLong(Subclass_WndProc)`, which can truncate on 64-bit builds. Hook ordering is slot order, not necessarily reverse install order, and duplicate add calls only increment `nReq`, so the procedure appears once in dispatch. Tests should cover duplicate add/remove counts, removing unknown hooks, multiple hooks on one window, multiple windows, forwarding chain correctness, and 64-bit pointer safety.
