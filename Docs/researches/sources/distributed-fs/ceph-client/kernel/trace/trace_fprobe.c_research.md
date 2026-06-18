# sources/distributed-fs/ceph-client/kernel/trace/trace_fprobe.c

## Purpose
Implements fprobe-backed dynamic tracing events. Users can create fentry probes, fexit probes, and tracepoint probes with fetch arguments; the resulting events can feed ftrace and perf and can be managed through the dynamic-event interface.

## Important APIs, Types, And Functions
The main object is `struct trace_fprobe`, containing a `dyn_event`, `struct fprobe`, target symbol name, tracepoint-probe flag, optional `tracepoint_user`, and embedded `struct trace_probe`. `struct tracepoint_user` tracks tracepoint names, loaded tracepoint pointers, and references so tracepoint probes can survive module load/unload transitions.

Dynamic-event operations are in `trace_fprobe_ops`: create, show, busy check, free, and match. Runtime handlers include `fentry_dispatcher()`, `fexit_dispatcher()`, `trace_fprobe_entry_handler()`, `fentry_trace_func()`, `fexit_trace_func()`, and perf equivalents. Registration helpers include `register_trace_fprobe_event()`, `append_trace_fprobe_event()`, `__register_trace_fprobe()`, `__unregister_trace_fprobe()`, `enable_trace_fprobe()`, `disable_trace_fprobe()`, and the trace event `.reg` callback `fprobe_register()`.

## Control Flow
Creation starts at `trace_fprobe_create()`, which tokenizes the raw command and calls `trace_fprobe_create_internal()`. Supported command forms are fentry (`f:`), fexit (`f... %return` or `$retval` fetch), and tracepoint (`t:`). Parsing derives group/event names, validates symbols or tracepoint names, expands BTF/meta/dentry arguments, parses fetch arguments into trace-probe instructions, configures return-probe entry data when needed, builds a print format, and registers or appends the probe event under `event_mutex`.

When an event is enabled by ftrace or perf, `fprobe_register()` calls `enable_trace_fprobe()`. The first enable of a trace-probe event registers each sibling fprobe. Normal function probes call `register_fprobe()`, while tracepoint probes find or create a `tracepoint_user`, register the tracepoint probestub if loaded, and then register an fprobe against the probestub address. Disable removes file links or perf flags; when no consumers remain, it unregisters fprobes and releases tracepoint users.

On hit, fentry and fexit dispatchers inspect trace-probe flags and send data to ftrace and/or perf. They compute dynamic data size, reserve the right buffer, store the entry IP or return IP/function pair, evaluate fetch instructions from `ftrace_regs` and optional entry data, and commit. The return path can capture selected entry arguments into fprobe entry data for later use by fexit fetch instructions.

## State And Persistence
Dynamic fprobe events persist in the dyn-event registry until explicitly removed and not busy. Sibling probes can share one trace event when group/event names and argument types match. `tracepoint_user_list` persists tracepoint-name users across modules; entries can have a null `tpoint` when the tracepoint is not currently loaded. Module notifiers re-register tracepoint users and fprobes when modules come and unregister fprobes before tracepoint memory disappears.

## Dependencies And Integration Points
This file depends on fprobe, trace probes, dyn events, trace event registration, tracepoint iteration, module notifiers, kallsyms, perf events, lockdown checks (`LOCKDOWN_KPROBES`), and fetch-argument helpers from `trace_probe`. It integrates with tracefs dynamic event commands, ftrace event enabling, perf event registration, and module load/unload notifications.

## Risks
Important risks are target lifetime and probe registration ordering. Function probes are verified before registration but module lifetime is not locked for ordinary symbols, so registration can still fail later. Tracepoint probes depend on notifier ordering: the tracepoint-user notifier must update `tpoint` before the fprobe notifier registers or unregisters the probestub fprobe. Return probes with entry data must enforce `MAX_FPROBE_DATA_SIZE`. Fetch instruction processing runs in probe context and must not fault unexpectedly. Busy checks must prevent removing events that ftrace/perf still reference.

## Test Signals
Tests should create fentry, fexit, and tracepoint probes through dynamic events; fetch `$argN`, `$retval`, `$stack`, symbol memory, and aliases; enable through ftrace and perf; and verify output formats and field definitions. Negative tests should cover bad event names, tracepoint names with illegal characters, `$retval` on tracepoint probes, too many args, oversized entry data, duplicate same probes, and locked-down environments. Module tests should load/unload a module with a tracepoint while a tracepoint probe exists and check for correct rebind and no stale fprobe.
