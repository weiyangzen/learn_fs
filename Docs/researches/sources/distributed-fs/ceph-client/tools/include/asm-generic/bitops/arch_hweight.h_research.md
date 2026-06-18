# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/arch_hweight.h

## Purpose

This header defines architecture hweight hooks for tools builds that do not provide optimized population-count operations.

## APIs, State, and Dependencies

`__arch_hweight8`, `__arch_hweight16`, `__arch_hweight32`, and `__arch_hweight64` forward to software implementations `__sw_hweight*`. It depends on asm integer types and on the software hweight functions being linked elsewhere. There is no state.

## Risks and Test Signals

Missing `__sw_hweight*` definitions cause link failures. Performance may be lower than architecture popcount, but correctness should match. Tests should compile and link bitmap users and compare hweight results against known bit counts.
