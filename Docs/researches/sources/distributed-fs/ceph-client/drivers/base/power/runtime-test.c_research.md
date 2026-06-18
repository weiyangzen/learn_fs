# sources/distributed-fs/ceph-client/drivers/base/power/runtime-test.c

## Purpose
Provides KUnit tests for runtime PM core behavior on synthetic KUnit devices.

## Important APIs, Types, And Functions
Tests use `kunit_device_register()`, `pm_runtime_enable()`, `pm_runtime_get_sync()`, `pm_runtime_put_sync()`, `pm_runtime_suspend()`, `pm_runtime_autosuspend()`, request helpers, status helpers, `pm_runtime_set_active()`, `pm_runtime_set_suspended()`, `pm_runtime_barrier()`, and `pm_runtime_resume_and_get()`. Test cases cover depth handling, already-suspended operations, idle behavior, disabled runtime PM, runtime error recovery, and probe-active flow.

## Control Flow
Each test registers a fresh device named `pm_runtime_test_device`. The depth test exercises usage-count transitions from suspended to active and back. Already-suspended and idle tests verify return codes when no transition is needed or usage count blocks idle. Disabled tests confirm runtime PM disabled devices are treated as active and return `-EACCES` while keeping refcounts balanced. Error tests inject `dev->power.runtime_error`, verify operations fail with `-EINVAL`, clear the error via `pm_runtime_set_suspended()`, and retest normal behavior. The probe-active test models a probe that marks the device active before enabling runtime PM and then idles it.

## State And Persistence
State is isolated to KUnit-created devices and their embedded `dev->power` runtime PM fields: disable depth, runtime status, usage count, runtime error, and pending work. No external persistence is used.

## Dependencies And Integration
Depends on KUnit device helpers and runtime PM APIs from `runtime.c`. The Makefile builds it under `CONFIG_PM_RUNTIME_KUNIT_TEST`.

## Risks And Test Signals
The suite is a direct regression signal for runtime PM return-code semantics, usage-count balancing, disabled/error handling, barrier behavior, and probe sequencing. Gaps include real driver callbacks, autosuspend delay timing, parent/child runtime PM, and concurrent operations.
