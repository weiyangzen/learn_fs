# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/winlist.cpp

Purpose: tracks open modeless property windows so the UI can prevent duplicate user/group/cell property sheets and focus existing windows.

Important APIs and control flow: `WindowList_Add` ignores duplicate HWNDs, reuses empty slots, grows the static array with `REALLOC`, stores window type and object ASID, and registers the modeless dialog with the app library. `WindowList_Search` returns the first live entry matching type and, unless `ASID_ANY`, object ID. `WindowList_Remove` nulls the HWND slot without compacting.

State and dependencies: file-static `aWindowList` and `cWindowList` hold process-local window registry state. It depends on `TaAfsUsrMgr.h`, modeless dialog registration, and allocation macros.

Risks and test signals: stale slots are tolerated but never compacted; leaks are small but long-lived. Search by object ID `0` is used for multi-object property windows, so tests should cover exact object lookup, `ASID_ANY`, duplicate add, remove, and reusing empty slots.
