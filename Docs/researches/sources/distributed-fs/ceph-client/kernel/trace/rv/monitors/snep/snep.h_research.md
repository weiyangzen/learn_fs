# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep.h

## Purpose

This generated header defines the `snep` DA model.

## Important APIs, Types, and Functions

States are `non_scheduling_context` and `scheduling_contex`; events are `preempt_disable`, `preempt_enable`, `schedule_entry`, and `schedule_exit`.

## Control Flow

The model starts/finalizes outside scheduling context. Schedule entry enters scheduling context; schedule exit leaves it. Preempt enable inside scheduling context is invalid.

## State and Persistence Behavior

It defines static model data; runtime state is per CPU in DA storage.

## Dependencies and Integration Points

It is consumed by `snep.c` and DA helpers.

## Risks and Edge Cases

The typo in `scheduling_contex` appears in enum and trace names and should be treated as ABI-like once exposed.

## Test Signals

Transition tests should verify preempt enable during scheduling produces an error.
