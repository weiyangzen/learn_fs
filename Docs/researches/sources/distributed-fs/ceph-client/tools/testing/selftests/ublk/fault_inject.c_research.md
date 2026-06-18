# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/fault_inject.c

## Purpose
This target implements a synthetic ublk backend for fault-injection tests. It behaves like a large null device but can delay completions and intentionally kill the server during request fetch.

## Important APIs, Types, and Functions
`struct fi_opts` stores `delay_ns` and `die_during_fetch`. `ublk_fault_inject_tgt_init()` configures a 250 GiB device and integrity parameters. `ublk_fault_inject_pre_fetch_io()` can `SIGKILL` the server before fetching tag 1. `ublk_fault_inject_queue_io()` submits an io_uring timeout. `ublk_fault_inject_tgt_io_done()` completes the ublk I/O after `-ETIME`. Command parsing supports `--delay_us` and `--die_during_fetch`.

## Control Flow
Target initialization rejects auto zero-copy fallback, creates params, and stores options. Each queued I/O becomes a timeout SQE with duration derived from `delay_us`; completion expects `-ETIME` and returns the requested byte count. The pre-fetch hook can submit live commands and kill the process to simulate incomplete fetch teardown.

## State and Persistence
Runtime state is the heap `fi_opts` stored in `dev->private_data`. No backing storage exists.

## Dependencies and Integration Points
It depends on `kublk.h`, target callbacks, ublk params, io_uring timeout operations, and tests `test_generic_06.sh` and `test_generic_17.sh`.

## Risks
The target intentionally kills the process, so cleanup relies on kernel ublk teardown/recovery. Delay is nanosecond timeout based and scheduler-sensitive.

## Test Signals
Generic fault-injection tests expect fast I/O failure after daemon death and successful device deletion after incomplete recovery teardown.
