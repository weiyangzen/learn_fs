# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw.h

## Purpose

This generated header defines the `sssw` per-task automaton.

## Important APIs, Types, and Functions

States are `runnable`, `signal_wakeup`, `sleepable`, and `sleeping`. Events cover runnable/sleepable set-state, blocking/suspend/preempt/yield switch variants, switch-in, wakeup, and signal delivery.

## Control Flow

The model starts/finalizes in `runnable`. Sleepable state can transition to sleeping on suspend/blocking and back to runnable on wakeup or runnable set-state. Sleeping accepts wakeup only. Signal wakeup is an intermediate state resolved by signal delivery or execution/wakeup paths.

## State and Persistence Behavior

Static model data only; per-task state is external.

## Dependencies and Integration Points

It is consumed by `sssw.c` and the DA monitor framework.

## Risks and Edge Cases

The transition table encodes nuanced scheduler semantics; implementation event classification must stay synchronized with the model.

## Test Signals

Transition tests should cover every switch subtype and invalid wake/sleep combinations.
