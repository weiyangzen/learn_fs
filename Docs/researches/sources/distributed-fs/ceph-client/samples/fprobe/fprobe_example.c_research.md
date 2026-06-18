# sources/distributed-fs/ceph-client/samples/fprobe/fprobe_example.c

Purpose: kernel module demonstrating fprobe entry/exit handlers on one or more kernel symbols, defaulting to `kernel_clone`.

Important APIs/functions: `struct fprobe`, `register_fprobe`, `register_fprobe_syms`, `unregister_fprobe`, `stack_trace_save`, `stack_trace_print`, and module params `symbol`, `nosymbol`, `stackdump`, `use_trace`.

Control flow: init configures entry and exit handlers. If `symbol` contains `*`, it registers a filter-based probe with optional `nosymbol`; if a single symbol, it registers directly; otherwise it splits comma-separated symbols and registers all. Handlers log entry/return and optionally dump a stack. Exit unregisters and logs hit/miss counts.

State and persistence: global `sample_probe`, `nhit`, and module parameters. No persistent storage.

Dependencies and integration: depends on fprobe/ftrace instrumentation and kallsyms visibility for requested symbols.

Risks: tracing hot or recursive paths can flood logs and affect performance. `trace_printk` is intentionally debug-only. Symbol filters must avoid probing unsafe paths.

Test signals: insert with `symbol=kernel_clone`, fork processes, inspect logs and `nmissed`; repeat with wildcard and `nosymbol` filters.
