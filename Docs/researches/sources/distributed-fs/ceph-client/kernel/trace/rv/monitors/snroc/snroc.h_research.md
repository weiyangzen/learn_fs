# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc.h

## Purpose

This generated header defines the `snroc` per-task automaton.

## Important APIs, Types, and Functions

States are `other_context` and `own_context`; events are `sched_set_state`, `sched_switch_in`, and `sched_switch_out`.

## Control Flow

The model starts/finalizes in `other_context`. Switch-in moves to own context, switch-out returns to other context, and `sched_set_state` is valid only in own context.

## State and Persistence Behavior

Static transition data only; per-task state is stored by DA helpers.

## Dependencies and Integration Points

It is included by `snroc.c`.

## Risks and Edge Cases

Final state marks only `other_context`, so a currently running task is non-final but expected.

## Test Signals

Test all event transitions and invalid set-state from other context.
