# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/const_hweight.h

## Purpose

This header implements compile-time and runtime population-count macros for 8-, 16-, 32-, and 64-bit values.

## APIs, State, and Dependencies

`__const_hweight*` count set bits in constant expressions. `hweight*` choose constant versions with `__builtin_constant_p` or runtime `__arch_hweight*`. `HWEIGHT*` force constant arguments with `BUILD_BUG_ON_ZERO`. It depends on build-bug macros, `u64`, and arch hweight hooks. There is no runtime state.

## Risks and Test Signals

Macro arguments can be evaluated in compile-time contexts, so type width and constant-ness matter. Tests should compile constant and non-constant hweight users, intentionally reject nonconstant `HWEIGHT*` inputs, and compare runtime counts.
