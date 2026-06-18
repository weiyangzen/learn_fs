# sources/distributed-fs/ceph-client/kernel/trace/trace_output.h

## Purpose
Declares the trace output helper APIs shared by trace output producers and printers.

## APIs, Control Flow, and State
The header exports prototypes for printk-message-only printers, symbol/IP printing, context printing, latency context printing, event-field printing, trace event registry locking and lookup, no-op printing, latency flag formatting, and module unregister support. It exposes `trace_event_sem` for module-side unregister paths. It also defines `SEQ_PUT_FIELD()` and `SEQ_PUT_HEX_FIELD()` helpers for binary/hex output, plus the `print_function_args()` declaration or a stub that prints `()` when function-argument tracing is disabled.

The inline helpers `seq_print_ip_sym_offset()` and `seq_print_ip_sym_no_offset()` wrap `seq_print_ip_sym()` while forcing or clearing `TRACE_ITER(SYM_OFFSET)`. There is no persistent state owned by the header; state is owned by `trace_output.c` and caller trace iterators.

## Dependencies, Integration, Risks, and Tests
The header depends on `trace_seq.h` and local `trace.h`. It integrates standard output helpers into kprobe, mmiotrace, KDB ftrace dump, event printers, and modules unregistering trace events. Risks are declaration drift with `trace_output.c`, misuse of `trace_event_sem`, and differing behavior of `print_function_args()` across configurations. Test signals are compile coverage across configurations with and without `CONFIG_FUNCTION_TRACE_ARGS`, module event unregister paths, and output users that include this header.
