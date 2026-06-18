# sources/distributed-fs/openafs/src/venus/fstrace.c

## Purpose
`fstrace.c` implements the `fstrace` command for inspecting and controlling OpenAFS kernel ICL trace logs and event sets. It can dump logs, follow a log like tail, list logs and sets, clear logs or sets, activate/deactivate/free event sets, and resize kernel log buffers.

## Important APIs, Types, And Functions
Trace decoding centers on `icl_GetSize`, `CheckTypes`, `DisplayRecord`, and `dce1_error_inq_text`. Kernel interaction wrappers include `icl_DumpKernel`, `icl_TailKernel`, `icl_ClearLog`, `icl_ClearSet`, `icl_ClearAll`, `icl_ListSets`, `icl_ListLogs`, `icl_ListLogsBySet`, `icl_ChangeSetState`, `icl_ChangeAllSetState`, `icl_ChangeLogSize`, `icl_GetLogsize`, and `icl_GetSetState`. The platform syscall adapter is `afs_syscall`, with Linux, Darwin, SGI, AIX, and generic syscall paths. Command handlers are `DoDump`, `DoShowLog`, `DoShowSet`, `DoClear`, `DoSet`, and `DoResize`, registered by the `SetUp*` helpers.

## Control Flow
`main` sets locale, detects SGI kernel pointer size when relevant, registers six subcommands (`dump`, `lslog`, `lsset`, `clear`, `setset`, `setlog`), and dispatches. Every command requires effective UID zero. Dump mode writes a header, then either dumps all logs, dumps logs attached to selected event sets, or follows one log with periodic sleep. Listing modes enumerate logs/sets through ICL syscalls. Clear and set modes send kernel operations for selected names or all names. Resize converts kilobytes to words/bytes according to `BUFFER_MULTIPLIER`, defaulting to the ICL default log size when zero.

## State And Persistence
Runtime state includes `allInfo`, a linked list of log names to dump, `dumpDebugFlag`, and kernel word-size flags. Persistent effects are in kernel memory: clearing logs, allocating/freeing dormant set state, toggling event set activity, and resizing log buffers. Dump output may be written to stdout or to a user-specified file. Message decoding reads installed NLS catalog files under the OpenAFS client data directory.

## Dependencies And Integration Points
The file depends on OpenAFS ICL constants, AFS syscall/proc syscall support, RX headers, OpenAFS command parsing, platform syscall ABI details, and NLS message catalogs for opcode text. It is tightly coupled to kernel ICL record layout and the installed message catalog naming scheme derived from facility/component/status fields.

## Risks And Test Signals
Risks include raw `fprintf` with decoded catalog strings after type checking, architecture-sensitive long/pointer decoding, global `allInfo` not freed, root-only commands exiting from handlers, platform syscall fallbacks that may silently become `-1` without `AFS_SYSCALL`, and a likely bug in `DoClear` where the `-log` branch iterates `as->parms[0].items` instead of the `-log` list. Test signals include dumping with known trace records, `-debug` raw output, following a log across buffer resizes, listing logs by set with missing slots, clearing by set/log/all, set active/inactive/dormant transitions, resizing `cmfx` and named logs, and running on 32-bit and 64-bit kernel/user ABI combinations.
