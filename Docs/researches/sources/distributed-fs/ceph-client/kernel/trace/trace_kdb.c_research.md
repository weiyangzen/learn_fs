# sources/distributed-fs/ceph-client/kernel/trace/trace_kdb.c

## Purpose
Adds a KDB command, `ftdump`, that dumps the ftrace ring buffer from the kernel debugger. It gives crash/debug sessions a safe way to inspect tracing data without relying on normal tracefs reads.

## APIs, Control Flow, and State
The file keeps a static `trace_iterator iter` and a per-CPU `buffer_iter[]` array. `kdb_ftrace_register()` installs `ftdump` through `kdb_register()` at `late_initcall`. The command accepts an optional skip count and optional CPU number; a negative skip means "show only the last N entries" after computing totals with `trace_total_entries()` or `trace_total_entries_cpu()`.

`kdb_ftdump()` initializes the global iterator, points it at `buffer_iter`, disables tracing for the target trace array, translates negative skips, calls `ftrace_dump_buf()`, then re-enables tracing. `ftrace_dump_buf()` temporarily clears `TRACE_ITER(SYM_USEROBJ)` to avoid user-memory lookups in panic/debugger context, starts ring-buffer iterators for all tracing CPUs or one CPU using `GFP_ATOMIC`, repeatedly calls `trace_find_next_entry_inc()`, formats each entry with `print_trace_line()`, emits with `trace_printk_seq()`, and cleans up each `ring_buffer_read_start()` with `ring_buffer_read_finish()`.

## Dependencies, Integration, Risks, and Tests
This file depends on KGDB/KDB, ftrace iterator internals, ring buffer iterators, trace output formatting, and `trace_output.h`. It integrates with the global top trace array via `trace_init_global_iter()` and uses KDB's `kdb_printf()` and interrupt flag handling.

Risks include debugger-context constraints: allocations must use atomic context, user-object symbolization is disabled deliberately, and the static iterator makes the command non-reentrant. CPU validation must reject offline or out-of-range CPUs, and tracing must be restored after early exits. Test signals include invoking `ftdump`, `ftdump <skip>`, `ftdump -N`, and `ftdump <skip> <cpu>` from KDB, validating empty-buffer output, interrupting a dump with KDB command interrupt, and confirming tracing resumes after command completion.
