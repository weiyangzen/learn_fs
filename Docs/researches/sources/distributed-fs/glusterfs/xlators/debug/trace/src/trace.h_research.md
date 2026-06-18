<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.h -->
# sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.h

## Purpose
Private header for the trace translator. It defines trace configuration, per-FOP enable metadata, default history sizing, and logging/unwind helpers used by `trace.c`.

## APIs, Types, and Functions
Defines `TRACE_DEFAULT_HISTORY_SIZE`, `trace_fop_name_t`, global `trace_fop_names[GF_FOP_MAXVALUE]`, and `trace_conf_t` with `log_file`, `log_history`, `history_size`, and `trace_log_level`. `TRACE_STACK_UNWIND()` clears `frame->local` before strict unwind. `LOG_ELEMENT()` sends a formatted record to event history via `gf_log_eh()` and/or the normal log via `gf_log()`.

## Control Flow, State, and Persistence
The header has no standalone control flow, but its macros control callback cleanup and dual-destination logging. State is process memory: the global FOP enable table and each xlator instance's `trace_conf_t`. History persistence is indirect through `this->history` in `trace.c`.

## Dependencies and Integration
Assumes GlusterFS types and symbols such as `gf_boolean_t`, `GF_FOP_MAXVALUE`, `STACK_UNWIND_STRICT`, `THIS`, and logging APIs are already visible through including source files.

## Risks and Test Signals
Because it defines, not declares, `trace_fop_names`, including this header from multiple objects would create duplicate definitions. `LOG_ELEMENT()` relies on `THIS->name`, so thread-local xlator context must be correct. Build coverage of trace and runtime logging with both destinations enabled are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/debug/trace/src/trace.h -->
