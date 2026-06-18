# sources/distributed-fs/ceph-client/samples/trace_printk/trace-printk.c

## Purpose

This module exercises `trace_printk()` paths for static strings, dynamic strings, formatted strings, and IRQ context.

## Important APIs, Types, and Functions

It defines global non-static strings to force dynamic-string behavior, an `irq_work` item, `trace_printk_irq_work()`, `trace_printk_init()`, and `trace_printk_exit()`. It uses `trace_printk`, `init_irq_work`, `irq_work_queue`, and `irq_work_sync`.

## Control Flow

Module init initializes irq work, emits static and dynamic trace_printk calls in process context, queues and synchronously waits for IRQ work that emits similar calls in IRQ context, then emits formatted static and dynamic strings. Exit does nothing.

## State and Persistence Behavior

Global strings and `irqwork` are module state. Trace output persists in tracing buffers according to tracing configuration.

## Dependencies and Integration Points

It depends on trace_printk support and IRQ work. It is meant to test tracing internals, not as production logging guidance.

## Risks and Edge Cases

`trace_printk()` is expensive and inappropriate for production fast paths. Dynamic format strings exercise less optimized paths. IRQ context output tests context safety.

## Test Signals

Load the module and inspect `/sys/kernel/tracing/trace` or trace_pipe for expected process and IRQ messages.
