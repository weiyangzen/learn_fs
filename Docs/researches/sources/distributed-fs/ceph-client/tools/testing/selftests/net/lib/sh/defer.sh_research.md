# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/sh/defer.sh

## Purpose
This Bash helper implements scoped deferred cleanup for shell networking selftests, similar to stack-based `defer` semantics.

## Important APIs and Functions
Public functions are `defer_scope_push`, `defer_scope_pop`, `defer`, `defer_prio`, `defer_scopes_cleanup`, and `in_defer_scope`. Internal functions build associative-array keys, schedule quoted commands, run deferred commands, and wipe scope counters. Priority defers run before default defers, and both tracks run in LIFO order.

## Control Flow and State
State is held in associative arrays `__DEFER__JOBS` and `__DEFER__NJOBS`, keyed by scope id and track, plus `__DEFER__SCOPE_ID`. `in_defer_scope` pushes a scope, runs a command, pops and executes cleanup, then returns the command status. `DEFER_PAUSE_ON_FAIL=yes` optionally pauses after failed cleanup commands.

## Dependencies and Integration
It requires Bash associative arrays and `${@@Q}` quoting support. `lib.sh` sources it and uses it in `tests_run` and `adf_*` cleanup wrappers.

## Risks and Test Signals
Deferred commands are executed with `eval`, so callers must pass trusted command components. `defer_scopes_cleanup` loops down through scope `0`, so misuse of the global scope can trigger broad cleanup. Failed cleanup commands do not automatically fail the original scope unless callers inspect side effects; the optional pause aids debugging.
