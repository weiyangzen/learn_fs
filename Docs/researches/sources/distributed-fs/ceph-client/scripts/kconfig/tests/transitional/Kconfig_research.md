# sources/distributed-fs/ceph-client/scripts/kconfig/tests/transitional/Kconfig

## Purpose
This fixture validates transitional symbol migration for all Kconfig value types and precedence cases.

## Important APIs, Types, and Functions
It defines `MODULES`, new symbols defaulting to old transitional symbols for bool, tristate, string, hex, and int, precedence variants where new user values should win, `OLD_WITH_HELP`, disabled/default edge cases, a conditional default case, and `REGULAR_OPTION`.

## Control Flow
`olddefconfig` should read old transitional values from an initial config, transfer values to new symbols through defaults, omit old transitional symbols from output, avoid prompting when transitional defaults provide values, and still prompt when conditional defaults are not visible.

## State and Persistence
The paired test uses an `initial_config` fixture outside this requested list and compares generated `.config` with expected output.

## Dependencies and Integration Points
Targets parser transitional syntax, symbol calculation in `symbol.c`, config reading/writing, and oldconfig prompting.

## Risks and Edge Cases
Transitional defaults must not override explicit new values, must handle all value types, and must not be written back. Conditional default visibility is a subtle prompt path.

## Test Signals
The paired test checks olddefconfig output and oldconfig stdout for conditional prompting.
