# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_busy.c

## Purpose

`test_klp_callbacks_busy.c` is a target module that can keep execution inside a function livepatch wants to replace, forcing a livepatch transition to stall.

## Important APIs, Types, and Functions

It defines bool module parameter `block_transition`, work item `busymod_work_func`, completion `busymod_work_started`, and init/exit functions using `schedule_work()`, `wait_for_completion()`, `flush_work()`, `msleep()`, `READ_ONCE()`, and `WRITE_ONCE()`.

## Control Flow and State

On load, it schedules work and waits until the work function logs entry. If `block_transition` is false, init flushes the work so logs are serialized. If true, the worker sleeps in a loop until exit clears the flag, leaving a task inside a patch target.

## Dependencies and Integration Points

It is targeted by `test_klp_callbacks_demo` and driven by `test-callbacks.sh`.

## Risks and Test Signals

Risks are deadlock if `block_transition` is never cleared or failure to stall long enough. Signals are ordered `busymod_work_func enter/exit` logs and livepatch transition staying at 1 while blocked.
