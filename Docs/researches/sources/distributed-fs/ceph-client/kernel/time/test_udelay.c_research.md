# sources/distributed-fs/ceph-client/kernel/time/test_udelay.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/time/test_udelay.c` is a debugfs kernel module for measuring whether `udelay()` delays at least as long as requested within a small allowed fast-error margin. Tests are configured by writing microseconds and optional iteration count to `/sys/kernel/debug/udelay_test`, then run by reading the same file. The complete 160-line source was read.

## Important APIs, Types, and Functions

Important functions are `udelay_test_single`, `udelay_test_show`, `udelay_test_open`, `udelay_test_write`, `udelay_test_init`, and `udelay_test_exit`. The file defines `DEFAULT_ITERATIONS`, `DEBUGFS_FILENAME`, module metadata, a mutex, and two configuration variables: `udelay_test_usecs` and `udelay_test_iterations`. It exposes `udelay_test_debugfs_ops` using `single_open`, `seq_read`, and a write handler.

## Control Flow

Module init creates the debugfs file. A write copies a short user buffer, parses `USECS [ITERS]`, defaults iterations when omitted, and updates configuration under `udelay_test_lock`. A read snapshots the configuration under the same mutex. Positive usec/iteration values run `udelay_test_single`, which loops, samples `ktime_get_ns` before and after `udelay`, tracks min/max/average, counts cases that are more than 0.5 percent fast, warns on negative deltas, and prints one summary line. A zero usec value prints usage and current `loops_per_jiffy`/ktime. Module exit removes the debugfs file.

## State and Persistence Behavior

State is limited to module globals protected by a mutex. Configuration persists only while the module is loaded. Test results are generated on demand and are not stored.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, user copy, `udelay`, `ktime_get_ns`, `loops_per_jiffy`, mutexes, and kernel module infrastructure. It integrates with manual debug workflows rather than automated syscalls.

## Risks and Edge Cases

`sscanf` accepts negative usec/iteration values; negative or zero usec values avoid running a test and may show usage instead. Very large iteration counts can monopolize CPU because `udelay` busy-waits. The allowed error calculation uses integer arithmetic (`usecs * 5` ns) and only detects fast delays, not excessive slow delays except via printed max/avg. Debugfs creation failure is not checked.

## Test Signals

Signals include loading/unloading the module, writing valid and invalid debugfs input, checking output for expected min/avg/max and FAIL count, running with several `udelay` values across HZ/CPU-frequency configurations, and validating that debugfs removal leaves no stale file.
