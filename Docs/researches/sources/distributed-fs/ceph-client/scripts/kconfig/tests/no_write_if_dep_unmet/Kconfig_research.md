# sources/distributed-fs/ceph-client/scripts/kconfig/tests/no_write_if_dep_unmet/Kconfig

## Purpose
This fixture verifies choice values are not written to `.config` when the enclosing choice dependency is unmet.

## Important APIs, Types, and Functions
It defines bool `A` and a choice depending on `A` with members `CHOICE_B` and `CHOICE_C`.

## Control Flow
Starting from `CONFIG_A=y`, oldaskconfig answers `n` to turn off `A`; the choice becomes invisible and its member unset lines should not be emitted.

## State and Persistence
The paired `config` file provides the initial state.

## Dependencies and Integration Points
Targets symbol write flags and choice-value calculation in `symbol.c`.

## Risks and Edge Cases
Choice values have special computation paths, making them prone to writing stale `# CONFIG_... is not set` entries.

## Test Signals
The paired test compares generated config to `expected_config`.
