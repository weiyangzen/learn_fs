# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize/Kconfig

## Purpose
This fixture tests randconfig across dependent choices where the second choice is visible only when member `B` of the first choice is selected.

## Important APIs, Types, and Functions
It defines a first choice between `A` and `B`, then a second choice between `X` and `Y` with `depends on B`.

## Control Flow
During randconfig, the first choice is randomized. If `B` is selected, the second choice becomes visible and must also be randomized consistently.

## State and Persistence
Only the generated `.config` from each seed persists during a test iteration.

## Dependencies and Integration Points
Targets `sym_calc_choice()`, visibility recalculation, and randconfig randomness.

## Risks and Edge Cases
The dependency of one choice on another choice member can expose stale visibility or insufficient recalculation.

## Test Signals
The paired test expects all three possible output patterns across 100 seeds.
