# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/atomic.h

## Purpose

This header maps generic atomic bit set/clear names onto test-and-modify operations for tools builds.

## APIs, State, and Dependencies

It defines `set_bit` as `test_and_set_bit` and `clear_bit` as `test_and_clear_bit`. The actual atomic behavior comes from the included atomic implementation such as `atomic-gcc.h`. No state is stored in the header.

## Risks and Test Signals

The aliases discard the old-bit return value when used through `set_bit` or `clear_bit`, but the underlying functions still perform fetch-style atomics. Tests should compile users expecting kernel names and run simple concurrent bit set/clear operations where supported.
