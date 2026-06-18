# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp.c

## Purpose

This module implements the `nrp` per-task deterministic automaton monitor for "need resched preempts." It observes IRQ entry, need-resched setting, and scheduler entry to verify preemption is preceded by reschedule intent.

## Important APIs, Types, and Functions

The monitor uses `RV_MON_PER_TASK`, generated `nrp.h`, and `rv/da_monitor.h`. Handlers are `handle_irq_entry()`, `handle_vector_irq_entry()` on x86 APIC builds, `handle_sched_need_resched()`, and `handle_schedule_entry()`. Lifecycle functions are `enable_nrp()`, `disable_nrp()`, and module registration under `rv_sched`.

## Control Flow

On enable, it initializes DA storage and attaches generic IRQ handler, scheduler need-resched, scheduler entry, and optional x86 vector IRQ tracepoints. `TIF_NEED_RESCHED` starts the task monitor on `sched_need_resched`; IRQ entry drives the current task into IRQ/preempt context; scheduler entry emits either `schedule_entry_preempt` or normal `schedule_entry` based on the tracepoint's `preempt` flag.

## State and Persistence Behavior

State is per task and held by the DA framework. It is reset/destroyed when the monitor is disabled and has no persistence beyond the enabled session.

## Dependencies and Integration Points

The file depends on `trace/events/irq.h`, `trace/events/sched.h`, optional `asm/trace/irq_vectors.h`, `rv_trace.h`, and the scheduler container `rv_sched`. It uses `rv_attach_trace_probe()` and `rv_detach_trace_probe()` for instrumentation.

## Risks and Edge Cases

The handler intentionally starts at a simpler state for `need_resched`, which may not mirror all live system state but reduces false complexity. Architecture-specific IRQ tracepoint coverage can differ; x86 vector IRQs are added because generic IRQ entry is insufficient there. ARM64 instability is reflected in Kconfig.

## Test Signals

Signals include preemptive scheduling workloads, IRQ-heavy workloads, checking x86 vector event attachment, forcing need-resched paths, and observing `event_nrp`/`error_nrp` tracepoints.
