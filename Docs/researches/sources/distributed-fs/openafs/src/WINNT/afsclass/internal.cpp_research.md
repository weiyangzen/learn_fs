# sources/distributed-fs/openafs/src/WINNT/afsclass/internal.cpp

## Purpose
`internal.cpp` provides shared process-local support for the Win32 `afsclass` library: a lazy global critical section, time and restart-time conversions, recurring schedule parsing/formatting, path splitting, address conversion, refresh-domain state, worker initialization, and Kerberos-style user name construction.

## Important APIs, types, and functions
The synchronization surface is `AfsClass_InitCriticalSection`, `AfsClass_GetCriticalSection`, `AfsClass_Enter`, `AfsClass_Leave`, and `AfsClass_GetEnterCount`. With `LOCAL_CRITSEC_COUNT` enabled it tracks recursion count and owning thread separately in `cs_EnterCount` and `cs_ThreadID`.

Time helpers include `AfsClass_UnixTimeToSystemTime`, `AfsClass_SystemTimeToUnixTime`, `AfsClass_ElapsedTimeToSeconds`, `AfsClass_FileTimeToDouble`, `AfsClass_ParseRecurringTime`, `AfsClass_FormatRecurringTime`, `AfsClass_SystemTimeToRestartTime`, and `AfsClass_RestartTimeToSystemTime`.

Utility APIs include `AfsClass_SplitFilename`, `AfsClass_IntToAddress`, `AfsClass_AddressToInt`, `AfsClass_SpecifyRefreshDomain`, `AfsClass_Initialize`, `AfsClass_RequestLongServerNames`, and `AfsClass_GenFullUserName`.

## Control flow
Initialization is lazy. Any caller entering or retrieving the class lock calls `AfsClass_InitCriticalSection`, which allocates and initializes `pcs` once. `AfsClass_Enter` increments the local recursion counter after entering the Win32 critical section; `AfsClass_Leave` validates the local owner/count with `ASSERT` before leaving.

Unix time conversion builds a Windows `FILETIME`-compatible 100 ns interval count by multiplying seconds and adding the 1601-to-1970 epoch offset, then converts to `SYSTEMTIME`. The reverse path calls `SystemTimeToFileTime`, subtracts the same offset, divides by 10,000,000, and returns a 32-bit `ULONG`.

Recurring-time parsing recognizes `never`, optional leading `at`, optional three-letter weekday, first numeric hour, second numeric minute, and an `a`/`p` marker anywhere later in the string. Formatting emits either `never`, `H:MM am/pm`, or `day H:MM am/pm`. BOS restart conversions map these `SYSTEMTIME` fields to `bos_RestartTime_t` masks.

## State and persistence behavior
All state is process-local and in-memory. `pcs`, `cs_EnterCount`, `cs_ThreadID`, `cRefreshAllReq`, `fLongServerNames`, and `dwWant` are globals used by the wider `afsclass` code. No file or registry state is persisted here. Restart-time and recurring-time helpers transform caller-provided structures but do not store schedules themselves.

## Dependencies and integration points
The file depends on WinSock/Win32 types, `afsclass.h`, `internal.h`, BOS restart types, and `worker.h` through `internal.h`. `AfsClass_Initialize` delegates runtime admin-library setup to `Worker_Initialize`. Address helpers translate between AFS integer server addresses and `SOCKADDR_IN`. Restart helpers integrate UI schedule text with BOS admin restart APIs.

## Risks and edge cases
The global critical section is never deleted and lazy initialization is not protected against two racing first callers. The local recursion tracker only stores one owning thread ID, so it is diagnostic rather than a general ownership model. Several string operations (`lstrcpy`, `wsprintf`, copying parsed components into fixed buffers) assume sufficiently sized caller buffers and trusted input. `AfsClass_SystemTimeToUnixTime` returns a 32-bit value and treats year 1970 as zero, which conflates the epoch with failure or "unset" semantics. `AfsClass_ParseRecurringTime` is permissive and can parse malformed strings into zero hour/minute values.

## Test signals
Useful tests include lock enter/leave recursion on one thread and failed leave from a non-owner in debug builds; Unix/SYSTEMTIME round trips for zero, current time, and post-2038 boundaries; recurring-time parse/format cases for `never`, daily, weekly, AM/PM noon/midnight, and malformed text; BOS restart mask conversions for disabled, daily, and weekly schedules; path splitting for no separator, slash, backslash, and root-like paths; and address int/socket round trips.
