# sources/distributed-fs/ceph-client/kernel/trace/Kconfig

## Purpose

`kernel/trace/Kconfig` defines the configuration surface for the kernel tracing subsystem. It declares architecture capability symbols, core tracing dependencies, user-visible tracer options, dynamic probe/event features, test modules, startup selftests, and the runtime verification tracing submenu.

## Important APIs, types, and functions

This is Kconfig metadata rather than C code. Important symbols include:

- Architecture capability symbols: `HAVE_FUNCTION_TRACER`, `HAVE_FUNCTION_GRAPH_TRACER`, `HAVE_DYNAMIC_FTRACE`, `HAVE_SYSCALL_TRACEPOINTS`, `HAVE_RETHOOK`, `HAVE_FENTRY`, object-tool mcount capabilities, and related dynamic ftrace feature gates.
- Core internal symbols: `TRACING`, `GENERIC_TRACER`, `RING_BUFFER`, `EVENT_TRACING`, `CONTEXT_SWITCH_TRACER`, `TRACE_CLOCK`, `TRACER_MAX_TRACE`, and `TRACING_SUPPORT`.
- User-facing tracer menu: `menuconfig FTRACE`, `FUNCTION_TRACER`, `FUNCTION_GRAPH_TRACER`, `DYNAMIC_FTRACE`, `FUNCTION_PROFILER`, `STACK_TRACER`, `IRQSOFF_TRACER`, `PREEMPT_TRACER`, `SCHED_TRACER`, `HWLAT_TRACER`, `OSNOISE_TRACER`, `TIMERLAT_TRACER`, `MMIOTRACE`, `FTRACE_SYSCALLS`, `TRACER_SNAPSHOT`, branch profiling options, and `BLK_DEV_IO_TRACE`.
- Dynamic events and probe features: `FPROBE`, `FPROBE_EVENTS`, `KPROBE_EVENTS`, `UPROBE_EVENTS`, `EPROBE_EVENTS`, `BPF_EVENTS`, `PROBE_EVENTS_BTF_ARGS`, `DYNAMIC_EVENTS`, and `PROBE_EVENTS`.
- Build tooling choices: `FTRACE_MCOUNT_USE_CC`, `FTRACE_MCOUNT_USE_OBJTOOL`, `FTRACE_MCOUNT_USE_RECORDMCOUNT`, and `BUILDTIME_MCOUNT_SORT`.
- Test/debug options: tracepoint/ring-buffer benchmarks, eval map retention, recursion recording, startup tests, ring buffer delta validation, mmiotrace/preemptirq/synthetic/kprobe test modules, histogram trigger debug, and remote tracing test.
- It sources `kernel/trace/rv/Kconfig` for runtime verification monitors.

## Control flow

The dependency flow starts with architecture symbols selecting capabilities. `TRACING_SUPPORT` requires IRQ flags and stacktrace support, then `FTRACE` opens the tracer menu. Most user-visible tracers select either `GENERIC_TRACER` or `TRACING`, which in turn selects ring buffer, tracepoints, event tracing, trace clock, binary printf, and RCU task support.

Feature-specific options layer on top of those bases. Function tracing requires architecture support and enables kallsyms/context-switch/glob/tasks-RCU dependencies. Dynamic ftrace depends on function tracing and architecture patching support. Function graph tracing depends on function tracing and graph support. Probe events select generic `PROBE_EVENTS` and `DYNAMIC_EVENTS` so common tracing infrastructure is built when any probe provider is enabled.

The file ends with test and debug options and remote tracing symbols inside the `if FTRACE` block, meaning those options disappear unless the tracing menu is enabled.

## State and persistence behavior

Kconfig symbols persist in the generated kernel configuration and shape both build output and runtime behavior. `select` relationships force hidden prerequisites on when a feature is enabled; `depends on` prevents invalid combinations from being offered. Defaults such as `FTRACE=y if DEBUG_KERNEL`, `DYNAMIC_FTRACE=y`, and several probe events defaulting to `y` under their prerequisites affect typical debug kernels.

## Dependencies and integration points

This file integrates with architecture Kconfig files that select `HAVE_*` symbols, with `kernel/trace/Makefile` object selection, with tracefs/debugfs runtime interfaces documented under `Documentation/trace/`, with block tracing (`BLK_DEV_IO_TRACE` selects `RELAY`, `DEBUG_FS`, `TRACEPOINTS`, `GENERIC_TRACER`, and `STACKTRACE`), with BPF/perf/kprobes/uprobes, and with runtime verification through the sourced RV Kconfig.

## Risks and edge cases

- Heavy use of `select` can silently enable substantial tracing infrastructure. Misplaced selects may create circular dependencies or unexpected build/runtime overhead.
- Several options are explicitly dangerous or high overhead (`PROFILE_ALL_BRANCHES`, ring buffer validation, hwlat/osnoise/timerlat on production systems, KPROBE_EVENTS_ON_NOTRACE, `MMIOTRACE_TEST`).
- Build-tool path selection for mcount is mutually constrained by compiler, objtool, and patchable function entry support; architecture capability mistakes can break ftrace patching.
- `BLK_DEV_IO_TRACE` pulls in debugfs and relay and depends on block/sysfs, so enabling it changes both ABI surface and runtime tracepoint registration.
- Startup tests intentionally add boot time and can trigger broad event enable/disable cycles.

## Test signals

Signals include successful `olddefconfig`/`allmodconfig` coverage across architectures, absence of Kconfig dependency warnings, object inclusion matching `Makefile` expectations, tracefs files appearing for enabled tracers, ftrace startup selftest output when configured, ring buffer benchmark/test logs, and probe/tracer runtime smoke tests under `/sys/kernel/tracing`.
