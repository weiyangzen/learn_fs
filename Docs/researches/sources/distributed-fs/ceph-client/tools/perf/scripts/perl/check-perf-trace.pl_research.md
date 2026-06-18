<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/check-perf-trace.pl -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/perl/check-perf-trace.pl
Purpose: Perl perf-script self-test handler that validates generated event handlers, common context access, symbolic/flag formatting, begin/end callbacks, and unhandled-event accounting.

Important APIs/types/functions: Defines `trace_begin`, `trace_end`, handlers `irq::softirq_entry` and `kmem::kmalloc`, helper `print_uncommon`, `print_unhandled`, `trace_unhandled`, and `print_header`. It imports `Perf::Trace::Core`, `Context`, and `Util`.

Control flow: When perf script replays matching events, handler functions print a common header, context fields from XS, and decoded symbolic/flag fields. Unmatched events increment `%unhandled`; `trace_end` prints a final summary.

State and persistence: `%unhandled` accumulates counts during the run. Output is stdout only.

Dependencies and integration points: Designed to pair with `bin/check-perf-trace-record`, which records kmem and irq tracepoints. It validates the Perl trace utility stack.

Risks: It assumes generated definitions exist for `irq::softirq_entry` symbols and `kmem::kmalloc` flags. Missing tracepoints or permissions prevent meaningful output.

Test signals: If this script runs and displays expected decoded values and end output, Perl perf scripting support is operational.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/perl/check-perf-trace.pl -->
