# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_common.h

## Purpose

`scoped_common.h` provides the common helper for creating a Landlock scoped domain in scope-specific selftests. It avoids duplicating the ruleset creation and enforcement sequence for signal and abstract UNIX socket scopes.

## Important APIs, Types, and Functions

The single helper `create_scoped_domain(struct __test_metadata *, __u16 scope)` initializes `struct landlock_ruleset_attr` with `.scoped = scope`, calls `landlock_create_ruleset()`, enforces it through `enforce_ruleset()`, and closes the ruleset FD with kselftest assertions.

## Control Flow and State

The helper has straight-line control flow: create ruleset, fail the current kselftest on error, restrict the calling thread/process, and close. The persistent effect is the new Landlock domain layer attached to the caller; no file state is written.

## Dependencies and Integration Points

It depends on `common.h` for `enforce_ruleset()` and kselftest metadata, `<linux/landlock.h>` via including tests, and Landlock kernels that support `.scoped`.

## Risks and Test Signals

Risks are failing to close ruleset FDs, using the wrong scope bit, or calling it in a process after synchronization expectations have changed. Signals are downstream tests seeing `EPERM` only after this helper is called and `_metadata` capturing setup failures cleanly.
