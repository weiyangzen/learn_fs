# sources/distributed-fs/ceph-client/lib/fault-inject.c

## Purpose
Implements the generic kernel fault-injection decision engine and its debugfs/configfs configuration surfaces. Subsystems embed `struct fault_attr` and call `should_fail()` or `should_fail_ex()` to probabilistically or deterministically force failures for testing.

## Important APIs, Types, and Functions
Exported APIs include `setup_fault_attr()`, `should_fail()`, `fault_create_debugfs_attr()` under debugfs, and `fault_config_init()` under configfs. Core helpers are `fault_prandom_u32_below_100()`, `fail_dump()`, `fail_task()`, optional `fail_stacktrace()`, and the main `should_fail_ex()`. Configfs support defines `struct fault_config` item attributes via generated show/store functions.

## Control Flow
`setup_fault_attr()` parses boot strings as `<interval>,<probability>,<space>,<times>`, initializes per-CPU pseudo-random state, and seeds the attribute. `should_fail_ex()` first handles per-task `current->fail_nth`, then rejects if probability is zero, task filtering fails, times is zero, stacktrace filters fail, space budget remains, interval has not reached a trigger point, or the random percentage test misses. On failure it optionally logs/dumps, decrements `times` unless infinite, and returns true.

Debugfs creation builds one directory per fault attribute with files for probability, interval, times, space, verbosity, rate limit, task filter, and optional stacktrace bounds. Configfs exposes equivalent attributes for dynamically created fault configurations.

## State and Persistence
State is stored in caller-owned `struct fault_attr` fields plus a static per-CPU `rnd_state` array. `times`, `space`, `count`, rate-limit state, stacktrace ranges, and task-filter flags mutate over time. Configuration persists only in memory and in configfs/debugfs live objects.

## Dependencies and Integration Points
Depends on debugfs, configfs, per-CPU pseudo-random state, scheduler task fields (`make_it_fail`, `fail_nth`), stacktrace capture when configured, atomics, and rate limiting. Integrated subsystems pass size values to `should_fail()` and may add their own boot parameters or configfs groups.

## Risks
`attr->count` is not atomic, so concurrent callers can race interval accounting. Debugfs/configfs stores update fields directly, and invalid operational combinations can create aggressive system-wide failures. Stacktrace filtering depends on reliable saved stacks and address bounds. The non-cryptographic PRNG is intentional but unsuitable for security decisions. `setup_fault_attr()` returns `0` on parse error because of `__setup` conventions, which can be surprising to non-boot-parameter callers.

## Test Signals
Verify probability extremes, intervals, finite/infinite `times`, space accounting, task filtering, `fail_nth`, `FAULT_NOWARN`, verbose rate limits, stacktrace require/reject ranges, debugfs/configfs show/store parsing, and concurrent callers. Subsystem tests should assert that injected failures are observable and recoverable.
