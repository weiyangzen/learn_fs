# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice_randomize2/Kconfig

## Purpose
This fixture tests randconfig choice recalculation when invisible choices and dependencies can affect later visible choices.

## Important APIs, Types, and Functions
It defines an always-invisible choice (`depends on n`), a visible `A`/`B` choice, `FOO` depending on `A`, and a final choice containing `X` depending on `FOO`.

## Control Flow
Randconfig must ignore the invisible dummy choice, randomize the visible choice, recalculate `FOO`, and only make the final choice visible when dependencies are met.

## State and Persistence
Generated configs vary by seed but remain local to the test temp directory.

## Dependencies and Integration Points
Targets choice shuffling and dependency recalculation after choice decisions.

## Risks and Edge Cases
If choice randomization changes symbol order without recalculating values, the final choice can be emitted inconsistently.

## Test Signals
The paired test accepts exactly three expected valid configurations for 20 seeds.
