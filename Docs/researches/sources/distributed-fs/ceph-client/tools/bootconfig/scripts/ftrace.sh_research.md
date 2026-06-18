<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace.sh

Purpose: this file provides shell helper functions for resetting and toggling ftrace state inside a tracefs directory. It is intended to be sourced and run from `$TRACEFS` or an instance directory, not executed as a standalone command.

Important APIs/functions: simple controls include `clear_trace()`, `disable_tracing()`, `enable_tracing()`, and `reset_tracer()`. Cleanup helpers include `reset_trigger_file()`, `reset_trigger()`, `reset_events_filter()`, `reset_ftrace_filter()`, `disable_events()`, and `clear_synthetic_events()`. `initialize_ftrace()` orchestrates a full reset to nop tracer, disabled events, no filters/triggers/probes, cleared PID filters, optional snapshot reset, empty trace buffer, and tracing re-enabled.

Control flow: `initialize_ftrace()` stops tracing, resets current tracer, removes triggers before filters/events, clears function filters and PID filters when files exist, clears kprobe/uprobe/synthetic event definitions, resets snapshot, clears trace, and enables tracing again. Trigger reset removes action triggers first because ftrace requires action triggers to be deleted before their associated hist/trigger commands in some cases.

State and persistence: all state is live tracefs state. There is no durable file written by the script itself. The operations write to tracing control files and can destroy existing user tracing setup in the current tracefs scope.

Dependencies and integration points: it assumes current working directory contains tracefs files such as `trace`, `tracing_on`, `current_tracer`, `events/*/*/trigger`, `events/*/*/filter`, `set_ftrace_filter`, and dynamic event files. `bconf2ftrace.sh --init` sources this file and calls `initialize_ftrace`.

Risks: glob expansion over `events/*/*` can fail or act unexpectedly on kernels without matching files or with special event layouts. Several commands parse trigger/filter lines using `grep`, `cut`, and shell word splitting, which can mishandle unusual trigger syntax. `reset_ftrace_filter()` clears `set_ftrace_filter` before trying to read back entries, so the later loop is effectively operating on already-cleared state on some shells/kernels. This script is destructive by design.

Test signals: integration tests should verify that synthetic events, kprobes, uprobes, normal triggers, hist action triggers, event filters, ftrace filters, tracers, snapshots, and trace output are cleared on representative kernels. Idempotency tests should run initialization twice and on kernels lacking optional files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/ftrace.sh -->
