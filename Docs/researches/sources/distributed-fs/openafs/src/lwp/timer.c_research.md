# sources/distributed-fs/openafs/src/lwp/timer.c

Purpose: timer-list implementation used by LWP/IOMGR code for scheduling timeout events.

Important APIs/types/functions: exports `TM_Init`, `TM_Final`, `TM_Insert`, `TM_Rescan`, `TM_GetExpired`, `TM_GetEarliest`, `TM_eql`, `openafs_insque`, and `openafs_remque`. Internal helpers `subtract`, `add`, and `blocking` manage `timeval` arithmetic and infinite timeout detection.

Control flow: `TM_Init` initializes fasttime once and creates a circular sentinel. `TM_Insert` sets `TimeLeft`, treats negative times as blocking/infinite, computes absolute expiration for finite timers, and inserts by remaining time order. `TM_Rescan` refreshes each finite timer's `TimeLeft` from current time and counts expired entries. `TM_GetExpired` returns the first expired finite timer; `TM_GetEarliest` returns the head's first element.

State and persistence: timer lists are caller-owned circular in-memory lists. `globalInitDone` prevents repeated fasttime init. No persistence.

Dependencies/integration: depends on `FT_Init` and `FT_AGetTimeOfDay` from fasttime, `timer.h`, and `lwp.h`. IOMGR is the likely consumer.

Risks and test signals: list ordering compares original `TimeLeft` values while storing absolute expiration, so callers must rescan before relying on current state. Negative `timeval` fields mean blocking. Tests should cover insertion, rescan, expiration, infinite timers, and list removal.
