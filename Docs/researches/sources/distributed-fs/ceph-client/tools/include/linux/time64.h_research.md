<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/time64.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/time64.h

## Purpose
This tools header defines common time-unit conversion constants without importing the full kernel time64 API.

## APIs And Flow
It exports `MSEC_PER_SEC`, `USEC_PER_MSEC`, `NSEC_PER_USEC`, `NSEC_PER_MSEC`, `USEC_PER_SEC`, `NSEC_PER_SEC`, and `FSEC_PER_SEC`. There are no time structures, normalization helpers, or conversion functions.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration points are duration conversions in perf and other tools. Risks include callers expecting kernel `timespec64` APIs, signed overflow in large conversions, and unit mistakes because all constants are untyped long or long long. Tests should compile users, static-assert constant values, and check arithmetic at millisecond, microsecond, nanosecond, and femtosecond scales.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/time64.h -->
