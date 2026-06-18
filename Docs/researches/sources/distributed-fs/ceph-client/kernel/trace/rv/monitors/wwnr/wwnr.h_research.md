# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/wwnr.h

## Purpose

This generated header defines the intentionally broken `wwnr` sample automaton.

## Important APIs, Types, and Functions

States are `not_running` and `running`; events are `switch_in`, `switch_out`, and `wakeup`.

## Control Flow

The model starts/finalizes in `not_running`. Switch-in enters running, switch-out leaves running, wakeup is accepted in not-running, and wakeup while running is invalid.

## State and Persistence Behavior

Static model data only; runtime state is per task in DA storage.

## Dependencies and Integration Points

It is included by `wwnr.c` and DA monitor helpers.

## Risks and Edge Cases

The model's intentional mismatch with real scheduler wakeup behavior is used to test reactor paths, not to enforce production correctness.

## Test Signals

Trigger wakeup while running and verify `error_wwnr` plus selected reactor behavior.
