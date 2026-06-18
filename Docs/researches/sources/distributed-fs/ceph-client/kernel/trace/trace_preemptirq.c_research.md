# sources/distributed-fs/ceph-client/kernel/trace/trace_preemptirq.c

## Purpose
Provides the low-level tracepoint glue for hard IRQ enable/disable and preempt enable/disable transitions. It emits `preemptirq` trace events and forwards transitions to latency tracers such as `irqsoff` and `preemptoff`.

## APIs, Control Flow, and State
The file defines tracepoints from `trace/events/preemptirq.h` via `CREATE_TRACE_POINTS`. With `CONFIG_TRACE_IRQFLAGS`, it exports `trace_hardirqs_on_prepare()`, `trace_hardirqs_on()`, `trace_hardirqs_off_finish()`, and `trace_hardirqs_off()`. A per-CPU `tracing_irq_cpu` flag suppresses redundant hardirq-off/on transitions. The "prepare" and "finish" variants omit lockdep calls for low-level entry code ordering; the full variants also call `lockdep_hardirqs_on_prepare()`, `lockdep_hardirqs_on()`, or `lockdep_hardirqs_off()`.

With `CONFIG_TRACE_PREEMPT_TOGGLE`, `trace_preempt_on()` and `trace_preempt_off()` emit `preempt_enable` / `preempt_disable` tracepoints and call `tracer_preempt_on/off()`. The local `trace(point, args)` wrapper is configuration-sensitive: noinstr-capable architectures use regular tracepoint calls, while older architectures avoid NMI context and temporarily enter/exit RCU watching for idle tasks so tracepoint execution is legal.

## Dependencies, Integration, Risks, and Tests
Dependencies include hardirq/lockdep state tracking, context tracking RCU helpers, NMI checks, preemptirq trace events, kprobe `NOKPROBE_SYMBOL`, and the tracer hooks implemented in `trace_irqsoff.c`. Integration points are architecture entry/exit code, lockdep, tracepoints visible to ftrace/perf/BPF, and latency tracers.

Risks are ordering-sensitive: tracing must not run when RCU is not watching unless it explicitly enters context tracking, NMI contexts are excluded on older paths, lockdep ordering differs between prepare/finish and full APIs, and missing per-CPU state transitions can duplicate or drop IRQ state events. Test signals include IRQ flag tracepoint enablement, lockdep IRQ state validation, idle-path IRQ tracing, preempt toggle tracepoints, `irqsoff`/`preemptoff` latency tracer interaction, and architecture builds with and without `CONFIG_ARCH_WANTS_NO_INSTR`.
