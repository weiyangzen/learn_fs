# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_transitional/Kconfig

## Purpose
This fixture validates that transitional symbols may only have type and help, and no other properties.

## Important APIs, Types, and Functions
It defines invalid transitional symbols with default, prompt, select, imply, depends, range, and missing type cases, plus `OTHER_SYMBOL`.

## Control Flow
`parser.y` accepts the syntax, then post-parse `transitional_check_sanity()` should reject each invalid property/condition.

## State and Persistence
No persistent state; the run should fail before producing a valid config.

## Dependencies and Integration Points
Targets parser transitional-property validation and diagnostics.

## Risks and Edge Cases
Only the first or a subset of errors may be emitted depending on validation flow; expected stderr must match implementation order.

## Test Signals
The paired test expects `olddefconfig()` exit code 1 and expected transitional-symbol stderr.
