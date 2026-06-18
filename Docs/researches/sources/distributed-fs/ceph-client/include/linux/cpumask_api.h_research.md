<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask_api.h -->
# sources/distributed-fs/ceph-client/include/linux/cpumask_api.h

## Purpose

`cpumask_api.h` is a one-line compatibility/include shim that includes `linux/cpumask.h`. The source was read as a complete 1-line file.

## Important APIs, Types, and Functions

It introduces no new APIs, types, macros, or functions. Consumers receive the complete `cpumask.h` API by including this file.

## Control Flow

There is no runtime control flow. Preprocessor inclusion forwards to `cpumask.h`.

## State and Persistence Behavior

No state is owned by this header. All state behavior is inherited from `cpumask.h`.

## Dependencies and Integration Points

It depends solely on `linux/cpumask.h`. Its integration role is source compatibility for code that includes `cpumask_api.h`.

## Risks and Edge Cases

The only risk is include-order or stale-include confusion. Any semantic behavior or ABI risk belongs to `cpumask.h`.

## Test Signals

Signals include compile coverage for users including `cpumask_api.h` directly and include-what-you-use checks ensuring no hidden APIs beyond `cpumask.h` are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask_api.h -->
