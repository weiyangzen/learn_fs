# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep.h

## Purpose

This generated header contains the Buchi automaton for the `sleep` LTL property.

## Important APIs, Types, and Functions

It defines nineteen atoms covering sleep/wake, RT status, syscall sleep forms, futex/RT mutex blocking, kernel-thread exceptions, and wake source/priority. It defines eight Buchi states `S0` through `S7`, `ltl_atom_str()`, `ltl_start()`, and `ltl_possible_next_states()`.

## Control Flow

The generated boolean logic allows safe cases such as non-RT/no-sleep, accepted blocking mechanisms, wake by equal-or-higher priority, hardirq/NMI wake, abort sleep, kthread stop, migration/RCU tasks, and selected absolute nanosleep/epoll/futex waits. Missing a next state indicates property violation.

## State and Persistence Behavior

Per-task atom and state bitsets are managed by the LTL framework. This file is static generated logic and stores no mutable data.

## Dependencies and Integration Points

It includes `<linux/rv.h>` and expects the implementation file to update atoms consistently with tracepoints.

## Risks and Edge Cases

The generated boolean variables are opaque, so maintaining correctness requires tracing back to the original LTL spec. Atom update omissions can invalidate the property more easily than the generated code itself.

## Test Signals

Property tests should target every named atom category and verify both accepted and violating next-state sets.
