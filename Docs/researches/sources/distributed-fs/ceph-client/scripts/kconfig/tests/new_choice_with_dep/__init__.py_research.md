# sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/__init__.py

## Purpose
This pytest module verifies oldconfig asks about new choice values after dependencies make them visible.

## Important APIs, Types, and Functions
The test calls `conf.oldconfig('config', 'y')` and checks `stdout_contains('expected_stdout')`.

## Control Flow
The input `y` answers the prompt for new symbol `A`, after which choice prompt behavior is validated.

## State and Persistence
Initial config state is read from the local `config` file and copied to the temp directory.

## Dependencies and Integration Points
Depends on oldconfig prompting and expected stdout fixture.

## Risks and Edge Cases
Output is interaction-order sensitive.

## Test Signals
Pass means newly visible choices are prompted rather than silently defaulted.
