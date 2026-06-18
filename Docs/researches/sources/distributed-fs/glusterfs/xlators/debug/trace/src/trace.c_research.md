<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.c -->
# sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.c

## Purpose
Debug translator that records GlusterFS FOP calls and callbacks before passing them to its single child. It can log to the process log, to an event-history ring, or both, and is intended for diagnosing call parameters, return values, GFIDs, paths, fd/inode lifetime, locks, xattrs, and stat buffers.

## APIs, Types, and Functions
Exports the translator `xlator_api` with `fops`, `cbks`, `dumpops`, init/fini/reconfigure, and memory accounting. The FOP wrappers cover lookup, stat/readlink, namespace mutations, fd operations, directory operations, locks, xattr ops, xattrop, rchecksum, setattr/fsetattr, and seek. Each wrapper logs request details, stores a GFID pointer in `frame->local` when callbacks need it, then `STACK_WIND`s to the first child. Callback functions format `op_ret`, `op_errno`, returned `iatt`, `statvfs`, lock data, fd pointers, and directory entries, then unwind with `TRACE_STACK_UNWIND`. Helpers include `trace_stat_to_str()`, `dump_history_trace()`, `enable_all_calls()`, `enable_call()`, `process_call_list()`, and `trace_dump_history()`.

## Control Flow, State, and Persistence
`init()` validates exactly one child, allocates `trace_conf_t`, initializes the global `trace_fop_names` table from `gf_fop_list`, applies `include-ops` or `exclude-ops`, creates `this->history` with `eh_new()`, sets `log-file`, `log-history`, `history-size`, and optional `force-log-level`, then stores private config. `reconfigure()` refreshes include/exclude state and toggles log destinations, but does not resize the existing history buffer. Runtime state is in `this->private`, `this->history`, per-frame `local` GFID pointers, and fd/inode ctx markers used so release/releasedir/forget can be logged. The translator does not persist data beyond logs and event-history dumps.

## Dependencies and Integration
Depends on GlusterFS xlator stack macros, event-history, logging, statedump, circ-buffer, time formatting, inode/fd ctx APIs, and FOP enum/name tables. It integrates as a pass-through debug xlator in a volume graph and exposes a dump operation for history.

## Risks and Test Signals
Risks include large fixed log buffers truncating complex data, global `trace_fop_names` shared by all instances, `frame->local` storing raw GFID array pointers from loc/fd/inode objects instead of an owned copy, possible null loc/inode assumptions in debug paths, and `init()` error exits that can leak the allocated config/history on some branches. Test signals are volume startup with valid/invalid child counts, include/exclude filtering, reconfigure toggles, statedump history output, representative FOP request/callback log pairs, and release/releasedir/forget logs after successful open/opendir/lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.c -->
