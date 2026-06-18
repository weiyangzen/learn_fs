<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSDefines.h -->
# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSDefines.h

## Purpose
`AFSDefines.h` centralizes compile-time switches, compatibility shims, constants, flags, request codes, timing values, extent geometry, network-provider constants, GUIDs, and small flag macros for the OpenAFS Windows redirector kernel library.

## Important APIs, Types, And Constants
The file provides an older-Windows compatibility definition for `FsRtlSetupAdvancedHeader`, function-pointer typedefs for security-descriptor routines, worker pool sizes (`AFS_WORKER_COUNT`, `AFS_IO_WORKER_COUNT`), worker state flags, worker request codes, synchronous request flags, FCB/object/volume reference flags, object lifetime and extent request timing, stack I/O run threshold, `FlagOn`/`BooleanFlagOn`/`SetFlag`/`ClearFlag`, write-to-EOF checking, CCB and directory-entry flags, network-provider status/resource constants, control/redirector instance flags, extent list geometry, dirty chunk threshold, redirector control and OpenAFS DFS reparse GUIDs, enumeration index constants, and library state flags such as `AFS_REDIR_LIB_FLAGS_NONPERSISTENT_CACHE`.

## Control Flow And Integration
There is no runtime control flow, but these definitions drive control flow across worker dispatch, write/read dispatch, object cleanup, name parsing, directory enumeration, extent mapping, invalidation, and network-provider operations. For example, `AFS_WORK_DEFERRED_WRITE` and `AFS_WORK_START_IOS` are consumed by `AFSWorker.cpp`; `AFS_MAX_STACK_IO_RUNS`, `AFS_DIRTY_CHUNK_THRESHOLD`, and `IS_BYTE_OFFSET_WRITE_TO_EOF` are consumed by I/O paths; object/volume reference reason indexes size reference accounting arrays in `AFSStructs.h`.

## State And Persistence
No state is stored here. The constants shape in-memory state layout and persistence behavior elsewhere: object lifetime determines garbage-collection eligibility, extent sizes and skip-list geometry determine cache mapping granularity, server flush/purge delays influence dirty-data retention, and flag values are persisted in memory fields such as FCB, object-info, directory-entry, connection, and process-control structures.

## Dependencies And Integration Points
The header depends on Windows kernel primitive names, interlocked operations, security descriptor types, file-offset sentinel values, and GUID macros. It is included by `AFSCommon.h` before structures and prototypes, making it foundational for `AFSStructs.h`, `AFSWorker.cpp`, `AFSWrite.cpp`, extent support, name support, and provider-support code.

## Risks And Edge Cases
Many constants are ABI-like within the driver. Changing worker request codes, reference-reason counts, flag bits, extent geometry, or special enumeration indexes can silently corrupt queues, arrays, trees, or service/kernel protocol assumptions. `SetFlag` and `ClearFlag` wrap interlocked operations and expect compatible integral lvalues. `QuadAlign` casts pointers through `ULONG`, which is risky on 64-bit if used with full pointer values. The misspelled `AFS_DIR_ENTRY_CASE_INSENSTIVE_LIST_HEAD` is part of the existing API surface. `GEN_MD5` is only defined under `DBG`, so non-debug conditional code relying on it must be guarded carefully.

## Test Signals
Compile-time tests should cover 32-bit and 64-bit builds, old-WDK compatibility, and all code paths using conditional constants. Runtime signals include worker request dispatch matching expected codes, object/volume reference reason array bounds, write-to-EOF recognition, extent mapping across list-size boundaries, directory enumeration indexes for dot/dot-dot/PIOCtl entries, nonpersistent-cache mode, DFS reparse tag behavior, and flag set/clear operations under contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/Include/AFSDefines.h -->
