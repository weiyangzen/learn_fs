# sources/distributed-fs/ceph-client/scripts/kconfig/tests/err_repeated_inc/__init__.py

## Purpose
This pytest module verifies repeated Kconfig inclusion errors.

## Important APIs, Types, and Functions
It runs `conf.oldaskconfig()` and checks stderr against `expected_stderr`.

## Control Flow
The Kconfig run should fail during include processing.

## State and Persistence
No persistent state besides captured stderr.

## Dependencies and Integration Points
Depends on scanner repeated-include detection.

## Risks and Edge Cases
Expected output is sensitive to path and line diagnostics.

## Test Signals
Pass means repeated includes are rejected as designed.
