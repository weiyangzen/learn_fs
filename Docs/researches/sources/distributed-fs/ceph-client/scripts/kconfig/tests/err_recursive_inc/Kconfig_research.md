# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_inc/Kconfig

## Purpose
This fixture starts a recursive include chain by sourcing `Kconfig.inc1`.

## Important APIs, Types, and Functions
It contains only `source "Kconfig.inc1"`.

## Control Flow
The scanner/source stack should follow the include and detect recursion in the included files.

## State and Persistence
No persistent state.

## Dependencies and Integration Points
Targets scanner include handling rather than symbol calculation.

## Risks and Edge Cases
The real recursion pattern is in adjacent include fixtures not listed here; this top-level file is the entry point.

## Test Signals
The paired test expects nonzero exit and expected stderr.
