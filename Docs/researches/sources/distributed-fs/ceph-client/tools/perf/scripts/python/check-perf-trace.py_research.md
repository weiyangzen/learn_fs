<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/check-perf-trace.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/check-perf-trace.py
Purpose: Python perf-script self-test handler analogous to the Perl version. It verifies generated event handlers, common context access, flag/symbol formatting, and unhandled-event reporting.

Important APIs/types/functions: Defines `trace_begin`, `trace_end`, handlers `irq__softirq_entry` and `kmem__kmalloc`, `trace_unhandled`, `print_header`, `print_uncommon`, and `print_unhandled`. Imports `Core` helpers and all symbols from `perf_trace_context`.

Control flow: On matching trace events, handlers print common event header fields, extra context fields from the C extension, and decoded symbolic/flag values. Unhandled events increment an `autodict` counter and are printed at trace end.

State and persistence: `unhandled` is the only accumulator. Output is stdout.

Dependencies and integration points: Requires `PERF_EXEC_PATH` to locate Python trace utilities and the compiled `perf_trace_context` extension. Paired with record scripts capturing kmem and irq tracepoints.

Risks: Broad imports and generated definitions can hide missing names until runtime. Missing tracepoint format definitions reduce symbol/flag formatting quality.

Test signals: Running with matching perf.data should print `trace_begin`, decoded softirq/kmalloc fields, common context values, and a final unhandled summary if applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/check-perf-trace.py -->
