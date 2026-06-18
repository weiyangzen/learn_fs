# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_recursive_inc/__init__.py

## Purpose
This pytest module verifies recursive Kconfig inclusion is detected.

## Important APIs, Types, and Functions
`test(conf)` runs `conf.oldaskconfig()` and checks nonzero return plus expected stderr.

## Control Flow
The parser should fail while traversing `source` statements.

## State and Persistence
Only return code and stderr are asserted.

## Dependencies and Integration Points
Depends on scanner include-stack diagnostics.

## Risks and Edge Cases
Include path resolution must be stable relative to the test `srctree`.

## Test Signals
Pass indicates recursive includes cannot hang or overflow.
