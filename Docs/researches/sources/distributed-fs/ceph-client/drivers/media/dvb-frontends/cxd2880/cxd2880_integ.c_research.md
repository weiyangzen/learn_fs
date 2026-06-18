# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_integ.c

## Purpose
Provides integration-layer helpers that sequence low-level initialization and expose cancellation for long-running operations.

## Important APIs, Types, and Functions
`cxd2880_integ_init()` runs `cxd2880_tnrdmd_init1()`, polls `cxd2880_tnrdmd_check_internal_cpu_status()` until internal CPU tasks complete, then calls `cxd2880_tnrdmd_init2()`. `cxd2880_integ_cancel()` sets `tnr_dmd->cancel`. `cxd2880_integ_check_cancellation()` returns `-ECANCELED` if cancellation is set.

## Control Flow
Initialization polls every 10 ms with `usleep_range()` and times out after 500 ms using `ktime_get()`. Any low-level error aborts immediately.

## State and Persistence
Uses the atomic `cancel` field in `struct cxd2880_tnrdmd`; the flag persists until reset by initialization or caller behavior. Hardware init state is advanced by low-level functions.

## Dependencies and Integration Points
Depends on tuner-demod core and monitor CPU status APIs. Higher-level tune/scan code can call cancellation checks while waiting for locks.

## Risks and Edge Cases
Timeout tuning is hardware-sensitive; too low can reject slow startup, too high slows failure. Cancellation is not automatically checked inside `cxd2880_integ_init()` itself. The atomic flag must be reset before new operations.

## Test Signals
Successful init, delayed CPU completion near timeout, stuck CPU timeout, transport error propagation, and cancellation checks returning `-ECANCELED`.
