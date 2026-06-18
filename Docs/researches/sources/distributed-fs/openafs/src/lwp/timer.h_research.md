# sources/distributed-fs/openafs/src/lwp/timer.h

Purpose: public timer-list data structure and API declarations for LWP timers.

Important APIs/types/functions: `struct TM_Elem` contains circular list links, caller-provided `TotalTime`, package-filled `TimeLeft`, and caller-owned `BackPointer`. Declares `TM_Init`, `TM_Final`, `TM_Rescan`, `TM_Insert`, `TM_GetExpired`, `TM_GetEarliest`, `TM_eql`, `openafs_insque`, and `openafs_remque`. Defines `FOR_ALL_ELTS` circular-list scanner.

Control flow: no runtime logic beyond macros. `TM_Remove` maps to `openafs_remque`; `Tm_Insert` appears to be a compatibility macro using raw insertion when `_TIMER_IMPL_` is not defined.

State and persistence: no header-owned state.

Dependencies/integration: requires `struct timeval` to be visible from includers. Used by `timer.c` and LWP/IOMGR timeout handling.

Risks and test signals: macro names are historically inconsistent (`Tm_Insert` vs `TM_Insert`), and intrusive list use requires callers not to remove unlinked elements. Compile coverage and timer behavior tests validate it.
