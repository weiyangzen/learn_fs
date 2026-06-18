# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/permassert.h

## Purpose
`permassert.h` defines VDO assertion macros that log permanent assertion failures and return error codes instead of crashing the kernel.

## Important APIs, Types, and Functions
`vdo_must_use()` applies `__must_check` to expressions. `VDO_ASSERT(expr, ...)` returns `VDO_SUCCESS` or an assertion error and must be checked. `VDO_ASSERT_LOG_ONLY(expr, ...)` logs only. `__VDO_ASSERT` performs the conditional dispatch. The header declares `vdo_assertion_failed()`.

## Control Flow
Macros evaluate the expression with `likely()`. On false, they stringify the expression, pass file and line metadata plus the caller format to `vdo_assertion_failed()`, and either require the result be used or allow log-only behavior.

## State and Persistence Behavior
No state is stored. Effects are log messages and returned error codes.

## Dependencies and Integration Points
It includes Linux compiler attributes and VDO error definitions. It is included by most VDO/UDS files for invariant checks.

## Risks and Edge Cases
`VDO_ASSERT_LOG_ONLY()` should not be used where continued execution is unsafe. The format arguments must match because failures call a varargs logger. Ignoring `VDO_ASSERT()` results should trigger compiler warnings through `vdo_must_use()`.

## Test Signals
Compile checks for ignored return values, successful and failed assertions, log-only behavior, and format attribute warnings are useful.
