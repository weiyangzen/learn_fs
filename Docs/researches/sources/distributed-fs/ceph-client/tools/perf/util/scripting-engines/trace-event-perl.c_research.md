# sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-perl.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/scripting-engines/trace-event-perl.c` embeds a Perl interpreter for `perf script`, delivers perf events and tracepoint fields to Perl handlers, exposes callchain/context data, and generates starter Perl scripts for available tracepoints.

## Important APIs, Types, and Functions

The exported scripting engine descriptor is `perl_scripting_ops`. Interpreter bootstrap uses `xs_init`, `boot_Perf__Trace__Context`, `boot_DynaLoader`, and global `INTERP my_perl`. Event-symbol setup uses `define_symbolic_value`, `define_symbolic_values`, `define_symbolic_field`, `define_flag_value`, `define_flag_values`, `define_flag_field`, and `define_event_symbols`. Runtime delivery uses `perl_process_callchain`, `perl_process_tracepoint`, `perl_process_event_generic`, and `perl_process_event`. Lifecycle functions are `perl_start_script`, `perl_flush_script`, and `perl_stop_script`. Code generation is handled by `perl_generate_script`.

## Control Flow

Startup stores the current `perf_session` in `scripting_context`, builds a Perl command line from the script and arguments, allocates/constructs/parses/runs the interpreter, checks `ERRSV`, and calls optional `main::trace_begin`. Shutdown calls optional `main::trace_end`, destructs, and frees the interpreter.

For each event, `perl_process_event` updates the global scripting context, then attempts tracepoint-specific delivery and generic raw delivery. Tracepoint delivery only handles `PERF_TYPE_TRACEPOINT` evsels. It obtains the traceevent format, builds a handler name `system::event`, defines symbolic/flag metadata once for that invocation path, computes seconds/nanoseconds, pushes common arguments, callchain data, and all event fields onto the Perl stack, and calls the handler if it exists. If not, it calls `main::trace_unhandled` when available. Generic delivery calls `process_event` with packed bytes for `union perf_event`, `perf_event_attr`, `perf_sample`, and raw data.

Callchain processing resolves the sample callchain through the thread and evsel, then builds a Perl array of hashrefs with IP, optional symbol metadata, and optional DSO name. Script generation writes an output `.pl` file with imports, begin/end hooks, per-tracepoint handler skeletons, flag/symbol formatting helpers, backtrace printing, unhandled handler, and a generic packed `process_event` example.

## State and Persistence Behavior

The file owns the embedded Perl interpreter for the active script run and updates the global `scripting_context`. It uses static `cur_field_name` and `zero_flag_atom` while walking print formats. Generated scripts are written to `<outfile>.pl`. Runtime event handling writes only through Perl script side effects and stdout/stderr unless the script persists data.

## Dependencies and Integration Points

It depends on libperl, libtraceevent, perf callchain/thread/map/dso/symbol/event/evsel infrastructure, scripting context helpers, and generated Perl modules under `Perf-Trace-Util`. It registers itself as the Perl implementation of perf's scripting engine.

## Risks and Edge Cases

`events_defined` is declared inside `perl_process_tracepoint`, so symbolic definitions are not truly persisted across events despite the bitset check. Handler names are built with `sprintf` into a 256-byte static buffer. Field extraction assumes raw data matches traceevent format and performs direct unaligned casts for dynamic offsets. `cur_field_name` is static and overwritten during recursive format walking; allocation cleanup is limited. Error handling in Perl calls does not deeply inspect exceptions after each handler. Script generation uses `sprintf` for the output path and writes generated Perl source with field names from trace metadata.

## Test Signals

Tests should cover interpreter start/stop errors, optional begin/end hooks, tracepoint handler invocation with numeric/string/dynamic fields, unhandled fallback, generic `process_event`, callchain hash contents with/without symbols/maps, symbolic and flag metadata callbacks, generated script content for representative events, long event names/path handling, and Perl exception behavior.
