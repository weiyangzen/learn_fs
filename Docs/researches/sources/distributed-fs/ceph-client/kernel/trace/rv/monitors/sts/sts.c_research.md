# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts.c

## Purpose

This module implements the `sts` per-CPU DA monitor for "schedule implies task switch" and related IRQ-disabled scheduling invariants.

## Important APIs, Types, and Functions

It uses generated `sts.h`, `rv/da_monitor.h`, IRQ flag handlers, IRQ entry handlers, scheduler switch/entry/exit handlers, and optional x86 local APIC vector IRQ handlers.

## Control Flow

On enable, it attaches IRQ disable/enable, generic IRQ entry, scheduler switch, scheduler entry, scheduler exit, and optional x86 vector tracepoints. Events drive the automaton through can-schedule, scheduling, disable-to-switch, switching, enable-to-exit, and IRQ states. Schedule exit uses a start event to resynchronize to the final can-schedule state after a scheduling sequence.

## State and Persistence Behavior

State is per CPU in DA storage. It is resettable through `da_monitor_reset_all` and destroyed on disable.

## Dependencies and Integration Points

It depends on `trace/events/irq.h`, `trace/events/preemptirq.h`, `trace/events/sched.h`, optional `asm/trace/irq_vectors.h`, and the scheduler container.

## Risks and Edge Cases

IRQ tracepoint coverage varies by architecture; x86 vector tracepoints are attached to cover local timer, irq work, reschedule, and call-function interrupts. The property can be affected by nested IRQs and precise ordering of IRQ enable/disable relative to scheduler tracepoints.

## Test Signals

Run scheduler and interrupt stress, inspect `event_sts` and `error_sts`, and compare x86/local-APIC builds with non-x86 builds.
