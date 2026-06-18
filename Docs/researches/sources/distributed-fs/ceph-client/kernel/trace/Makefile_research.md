# sources/distributed-fs/ceph-client/kernel/trace/Makefile

## Purpose

`kernel/trace/Makefile` maps tracing Kconfig symbols to object files, controls instrumentation policy for the tracing subsystem itself, and adds a build-time undefined-symbol check for `simple_ring_buffer` users such as pKVM.

## Important APIs, types, and functions

This is kbuild metadata. Important constructs include:

- `ccflags-remove-$(CONFIG_FUNCTION_TRACER) += $(CC_FLAGS_FTRACE)` prevents tracing code from being function-instrumented by default.
- `KCSAN_SANITIZE := n` under function tracing avoids recursion/noise from KCSAN instrumentation in tracing code.
- Special cases re-enable ftrace instrumentation for selftests and `CONFIG_FUNCTION_SELF_TRACING`.
- `KBUILD_CFLAGS += -DDISABLE_BRANCH_PROFILING` disables branch profiling of tracing code when branch tracing is enabled.
- `GCOV_PROFILE := y` under `CONFIG_GCOV_PROFILE_FTRACE`.
- Per-object controls such as `KCOV_INSTRUMENT_trace_preemptirq.o := n`, include paths for `bpf_trace.o`, `trace_benchmark.o`, and `trace_events_filter.o`, and KASAN enabling for `undefsyms_base.o`.
- `obj-$(CONFIG_...)` lines select trace core, tracers, event/probe providers, tests, runtime verification, remote tracing, and block tracing objects.
- `UNDEFINED_ALLOWLIST` and `cmd_check_undefined` implement the `%.o.checked` target used by `always-$(CONFIG_SIMPLE_RING_BUFFER)`.

## Control flow

Kbuild evaluates configuration symbols and adds objects to the trace directory build. Core objects such as `trace.o`, `trace_output.o`, `trace_seq.o`, and `trace_stat.o` are built when `CONFIG_TRACING` is enabled. Function, graph, branch, latency, osnoise, block, event, syscall, BPF, kprobe, uprobe, boot-time, fprobe, and test objects are included according to their symbols.

For `CONFIG_BLOCK=y`, `blktrace.o` is also built when `CONFIG_EVENT_TRACING` is enabled, even if `CONFIG_BLK_DEV_IO_TRACE` is off, because `blktrace.c` contains the generic `blk_fill_rwbs()` helper under `CONFIG_EVENT_TRACING`. Runtime verification descends into `rv/`. `simple_ring_buffer.o` receives an extra `.checked` target that runs `nm -u` and fails the build on unexpected unresolved symbols.

## State and persistence behavior

The Makefile does not maintain runtime state, but it controls the persistent build artifact composition and instrumentation attributes. Build flags persist for the compilation of all objects in this directory unless overridden by per-object variables. The undefined-symbol allowlist is recomputed during the build and influences whether `simple_ring_buffer.o.checked` succeeds.

## Dependencies and integration points

The file integrates directly with `kernel/trace/Kconfig` symbols, kbuild variables (`obj-y`, `obj-m`, `always-*`, `targets`, `if_changed`), compiler instrumentation flags, sanitizer knobs, `nm`, `awk`, and optional subsystems including BPF, perf events, block layer, kgdb/kdb, PM tracepoints, runtime verification, remote tracing, and pKVM hypervisor symbol restrictions.

## Risks and edge cases

- Accidentally instrumenting tracing internals can cause recursion or misleading trace data. The file carefully removes ftrace flags globally and re-adds them only for selftest/debug cases.
- `blktrace.o` is selected by two independent conditions; changes must preserve the reason event tracing needs it even without full blktrace support.
- The undefined-symbol check depends on tool output and the allowlist. Too broad an allowlist can hide hypervisor-incompatible symbols; too narrow can break valid builds.
- Sanitizer/profiling overrides affect diagnostics. Disabling KCSAN/KCOV in some tracing objects is intentional but reduces coverage.
- Object list changes must stay synchronized with Kconfig dependency/select relationships.

## Test signals

Build tests should cover tracing disabled, core tracing, function tracing, self tracing, event tracing with `CONFIG_BLOCK`, full `BLK_DEV_IO_TRACE`, runtime verification, simple ring buffer, and GCOV/KCOV/KCSAN combinations. Useful signals are absence of recursive tracing warnings, successful `.o.checked` generation, expected tracefs features in built kernels, and no missing object or undefined-symbol link failures.
