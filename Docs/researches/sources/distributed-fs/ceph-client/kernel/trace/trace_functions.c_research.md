# sources/distributed-fs/ceph-client/kernel/trace/trace_functions.c

## Purpose
Implements the ring-buffer based `function` tracer and dynamic ftrace function commands. It records function-entry events, optionally records arguments, stack traces, or repeat compression, and lets users attach per-function commands such as `traceon`, `traceoff`, `stacktrace`, `dump`, and `cpudump` through ftrace filters.

## Important APIs, Types, And Functions
Tracer setup uses `ftrace_allocate_ftrace_ops()`, `ftrace_create_function_files()`, `function_trace_init()`, `function_trace_reset()`, `function_trace_start()`, `func_set_flag()`, and `init_function_trace()`. Runtime callbacks include `function_trace_call()`, `function_args_trace_call()`, `function_stack_trace_call()`, `function_no_repeats_trace_call()`, and `function_stack_no_repeats_trace_call()`.

Options are stored in `func_flags` with bits for stack traces, no repeats, and argument capture. Per-instance ftrace operations live in `trace_array->ops`; repeat compression uses per-CPU `trace_func_repeats`. Dynamic command callbacks are represented by `struct ftrace_func_command` and `struct ftrace_probe_ops`.

## Control Flow
Initialization selects the callback matching current tracer options, allocates repeat state if required, initializes ftrace array ops, records the current CPU, starts command-line recording, and registers the ftrace function. On callback, the tracer checks `function_enabled`, applies recursion protection or per-CPU disabled counters for stack cases, resolves true parent IP when the function graph return trampoline is involved, builds trace context, and calls `trace_function()`.

The no-repeat callbacks compare current IP/parent IP against per-CPU last state. Repeated calls update timestamps and counts instead of emitting every event; the next different function flushes the repeat summary through `trace_last_func_repeats()`. Stack variants emit `__trace_stack()` after function tracing. Option changes while the function tracer is active unregister the old ftrace function, swap `ops->func`, and re-register.

Dynamic ftrace commands are registered when `CONFIG_DYNAMIC_FTRACE` is enabled. Writing commands through ftrace filter infrastructure invokes callbacks that parse optional counts, register or unregister per-function probes, and use mapper-backed counters when counts are requested. Probe callbacks toggle tracing, dump all or current CPU buffers, or emit stack traces.

## State And Persistence
Function tracer state is attached to each `trace_array`: ftrace ops, current flags, `function_enabled`, repeat buffers, and filter files. Dynamic command state persists in ftrace function probe registrations and optional `ftrace_func_mapper` count storage. `tracing_on` changes are global or trace-array scoped through tracer helpers; command counters are mutable and decrement on hits.

## Dependencies And Integration Points
This file integrates with the ftrace core, trace arrays and instances, function graph support for parent IP correction and graph ops allocation, stack tracing, command-line recording, ring-buffer trace functions, dynamic ftrace command registration, and ftrace filter files. It also participates in ftrace selftests when configured.

## Risks
Callback context is hot and recursion-prone, so recursion guards, IRQ state handling, and per-CPU disabled counters are critical. Switching callbacks while tracing must unregister/register in the right order. Repeat compression intentionally has weak synchronization around interrupts and can lose exact counts, as noted in the source comment. Counted function commands use pointer-cast counts and mapper state, so registration/free paths must stay balanced. Stack tracing from ftrace callbacks is especially sensitive to skip counts and unwinder configuration.

## Test Signals
Signals include enabling the `function` tracer, toggling `func_stack_trace`, `func-no-repeats`, and `func-args`, validating output and repeat summaries, and using instance-specific filters. Dynamic command tests should write `traceon`, `traceoff`, `stacktrace`, `dump`, and `cpudump` commands with and without counts to `set_ftrace_filter`, then remove them with `!`. Stress signals include concurrent option changes, ftrace filter updates, and lockdep/recursion warnings under high function-call load.
