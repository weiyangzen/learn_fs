# sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/config

## Purpose
This is the initial `.config` fragment for the `new_choice_with_dep` test.

## Important APIs, Types, and Functions
It sets `CONFIG_CHOICE_B=y`, leaves `CONFIG_CHOICE_D` unset, and sets `CONFIG_CHOICE_E=y`.

## Control Flow
The fixture represents a previous configuration before symbol `A` and dependency-related choice changes become visible.

## State and Persistence
It is copied to a temporary `.config` by `Conf.oldconfig()`.

## Dependencies and Integration Points
Used only by the paired pytest module.

## Risks and Edge Cases
The fragment intentionally lacks `CONFIG_A`, driving the new prompt path.

## Test Signals
Correct output depends on this starting state being preserved.
