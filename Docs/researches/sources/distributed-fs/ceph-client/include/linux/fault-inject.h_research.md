# sources/distributed-fs/ceph-client/include/linux/fault-inject.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fault-inject.h` declares the generic kernel fault injection policy structure and helper APIs. The source was read as a complete 134-line file for this report.

## Important APIs, Types, and Functions

Key exports are `enum fault_flags`, `struct fault_attr`, `FAULT_ATTR_INITIALIZER`, `DECLARE_FAULT_ATTR`, `setup_fault_attr`, `should_fail_ex`, `should_fail`, `fault_create_debugfs_attr`, `struct fault_config`, `fault_config_init`, `should_fail_alloc_page`, and `should_failslab`. Disabled configs provide empty structs and no-fail stubs.

## Control Flow

Consumers initialize a `fault_attr`, optionally expose it through debugfs/configfs, then call `should_fail()` or a specialized helper at allocation or operation points. The implementation evaluates probability, interval, count/times, stack/task filters, address ranges, size/space, verbosity, and rate limiting.

## State and Persistence Behavior

State is in `fault_attr`: counters, atomics, rate-limit state, filters, and debugfs dentries. There is no file-backed persistence beyond runtime debugfs/configfs settings.

## Dependencies and Integration Points

The enabled path depends on `atomic`, `configfs`, and `ratelimit`. Integration points include page allocation failure, slab allocation failure, usercopy failure, debugfs/configfs test controls, and subsystem-specific injected error paths.

## Risks and Edge Cases

Fault attributes are global or subsystem-owned mutable test state. Wrong default return semantics matter: the disabled `setup_fault_attr()` comment notes `0` means error for `__setup()` handlers. Tests must account for ratelimits, intervals, and task/stack filters.

## Test Signals

Fault-injection selftests, allocation failure paths, debugfs/configfs attribute creation tests, and disabled-config build coverage for all stubs.
