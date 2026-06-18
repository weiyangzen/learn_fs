# sources/distributed-fs/ceph-client/tools/include/asm/alternative.h

## Purpose

This tools header stubs architecture alternative-instruction support enough for userspace tools assembly to build.

## APIs, State, and Dependencies

For s390x assembly it defines an `ALTERNATIVE` macro that emits the old instruction. For other architectures it defines `ALTERNATIVE` as `#`, effectively disabling alternative patching for tools builds. There is no runtime state.

## Risks and Test Signals

This intentionally does not implement kernel runtime patching semantics. It is only safe for tools code that needs assembly to assemble, such as perf benchmarks. Tests should assemble relevant architecture files and ensure no runtime path expects alternative replacement.
