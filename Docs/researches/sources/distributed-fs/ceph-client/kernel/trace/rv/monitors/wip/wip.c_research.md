# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip.c

## Purpose

This module implements the standalone `wip` per-CPU DA sample monitor for wakeups while in a preemptive context.

## Important APIs, Types, and Functions

It uses generated `wip.h`, `rv/da_monitor.h`, handlers for `preempt_disable`, `preempt_enable`, and `sched_waking`, plus normal RV module registration.

## Control Flow

On enable, it initializes DA storage and attaches preempt enable, scheduler waking, and preempt disable tracepoints. Preempt disable moves to non-preemptive; preempt enable restarts to preemptive; waking is valid only from non-preemptive according to the model.

## State and Persistence Behavior

State is per CPU and transient. The monitor registers without a parent and exposes `da_monitor_reset_all`.

## Dependencies and Integration Points

It depends on preemptirq and scheduler tracepoints, `rv_trace.h`, and RV core registration.

## Risks and Edge Cases

As documented, preempt toggle events can miss nested or initial preemption state details, so the sample can be sensitive to enable-time state. The tracepoint attach order differs from detach order but all are removed before destroy.

## Test Signals

Run wakeup-heavy workloads with preemption toggles, inspect `event_wip`/`error_wip`, and test monitor enable during both preemptive and non-preemptive contexts.
