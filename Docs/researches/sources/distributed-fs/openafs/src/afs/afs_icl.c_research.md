# sources/distributed-fs/openafs/src/afs/afs_icl.c

## Purpose
`afs_icl.c` implements the kernel in-core logging facility used by the AFS Cache Manager. It owns trace logs, trace sets, event append paths, privileged control operations, copyout to user space, log resizing, activation/deactivation, and shutdown cleanup. The default Cache Manager logs are created as `cmfx`, `cm`, and `cmlongterm`.

## Important APIs, types, and functions
Top-level globals include `afs_iclSetp`, `afs_iclLongTermSetp`, `afs_icl_allLogs`, `afs_icl_allSets`, `afs_icl_lock`, and `afs_icl_inited`. Initialization uses `afs_icl_InitLogs`, `afs_icl_CreateLog`, and `afs_icl_CreateSetWithFlags`; teardown uses `shutdown_icl`, `afs_icl_LogFree`, and `afs_icl_SetFree`.

Runtime tracing enters through `afs_icl_Event0` through `afs_icl_Event4`, which all funnel into `afs_icl_Event4` and then `afs_icl_AppendRecord`. Append helpers include `afs_icl_GetLogSpace`, `afs_icl_AppendString`, `ICL_APPENDINT32`, `ICL_APPENDLONG`, and `afs_icl_AppendOne`.

Privileged user control goes through `Afscall_icl` or Darwin's `Afscall64_icl`. Supported operations include copyout, copyout-and-clear, enumerate logs, enumerate logs by set, clear log, clear set, clear all, enumerate sets, set set status, set all set statuses, set log size, and query log/set state.

## Control flow
Trace emission first checks whether the set is active, holds the set, decodes the log mask from `lAndT`, checks per-event enable bits, and appends a record to each selected log. `afs_icl_AppendRecord` samples time, inserts a timestamp record when the low timestamp window rolls, computes record size from parameter types, evicts oldest records until enough ring-buffer space exists, and writes a compact record header, event id, thread id, timestamp, and encoded arguments.

Copyout starts from a caller-supplied cookie. `afs_icl_CopyOut` maps that cookie into the circular buffer, marks `ICL_COPYOUTF_MISSEDSOME` if the requested data has already been overwritten, copies at most the requested word count across one or two ring spans, optionally clears the log after reaching the end, and can wait for more data when requested.

Set activation with `ICL_OP_SS_ACTIVATE` reasserts log use if the set had been freed, while `ICL_OP_SS_FREE` is rejected for active sets and otherwise decrements log use counts so backing buffers can be freed.

## State and persistence behavior
All ICL data is in memory. Logs keep circular buffer fields `datap`, `logSize`, `firstUsed`, `firstFree`, `logElements`, `baseCookie`, `lastTS`, `setCount`, `refCount`, and state flags such as persistent/deleted/waiting. Sets keep their name, reference count, state flags, event enable bitmap, and up to `ICL_LOGSPERSET` log references. Log storage is allocated lazily on first real set use and can be freed while the log structure remains named. Persistent logs/sets are protected from bulk clear/status changes.

## Dependencies and integration points
The module depends on AFS locks, OSI allocation, optional kernel pinning, copyin/copyout wrappers from `afs_osi.h`, Rx lock wrappers for syscall paths, thread id/time helpers, and global AFS superuser checks. It is used by many Cache Manager files through `afs_Trace*` macros, including lock tracing, fetch/store tracing, memory cache tracing, DNLC tracing, NFS translator tracing, and cache initialization events.

## Risks and edge cases
The logging path is performance-sensitive and can run while holding the global AFS lock. Record size is capped at 255 words by the encoded high byte; oversized records are silently dropped. String arguments are copied by walking kernel memory, so callers must pass stable strings. Refcount and deleted-state handling is subtle because logs and sets can be found, held, freed, and zapped under different locks. The `ICL_COPYOUTF_WAITIO` path sleeps on the log lock address but append does not obviously wake waiters in this file, so wait semantics depend on surrounding ICL conventions.

## Test signals
Test by enabling and disabling trace sets, copying logs out with cookies across wrap boundaries, resizing logs while inactive and active, freeing and reactivating sets, validating persistent log behavior, exercising 32-bit and Darwin 64-bit syscall argument paths, and checking that lock tracing avoids recursive ICL locks.
