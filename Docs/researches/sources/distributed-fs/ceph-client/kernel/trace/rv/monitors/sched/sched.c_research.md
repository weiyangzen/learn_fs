# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sched/sched.c

## Purpose

This module registers the top-level `sched` RV monitor container for scheduler behavior specifications.

## Important APIs, Types, and Functions

It defines exported `struct rv_monitor rv_sched` with no enable, disable, or reset callbacks, and module init/exit registration functions.

## Control Flow

`register_sched()` registers the container with no parent. `unregister_sched()` removes it. Child monitors pass `&rv_sched` as their parent.

## State and Persistence Behavior

The container tracks registration and enabled state in the RV core but has no own automaton state. Enabling a container in RV core enables children.

## Dependencies and Integration Points

It depends on `<linux/rv.h>` and is included through `sched.h` by scheduler child monitors.

## Risks and Edge Cases

RV core treats a monitor with children or missing enable callback as a container; this file relies on that behavior. Registration order matters for nested child display and parent linkage.

## Test Signals

Tracefs should show `sched` in available monitors and child monitors nested under `monitors/sched/`.
