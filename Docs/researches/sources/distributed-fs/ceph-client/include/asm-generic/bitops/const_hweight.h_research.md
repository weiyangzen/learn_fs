# sources/distributed-fs/ceph-client/include/asm-generic/bitops/const_hweight.h

Purpose: Provides compile-time and runtime population-count macros that choose constant folding when possible and architecture/software hweight otherwise.

Important APIs, types, and functions: Defines `__const_hweight8/16/32/64`, generic `hweight8/16/32/64`, constant-required `HWEIGHT8/16/32/64`, and type-invariant `HWEIGHT()`.

Control flow: `__builtin_constant_p()` selects compile-time bit counting; constant-required forms use `BUILD_BUG_ON_ZERO` to reject nonconstant arguments.

State and persistence: No state.

Dependencies and integration points: Depends on arch hweight hooks, `BUILD_BUG_ON_ZERO`, and compiler constant detection. Used by bitmask validation, static sizing, and runtime bitmap metrics.

Risks and test signals: Risks include multiple evaluation surprises for macro arguments, nonconstant misuse of `HWEIGHT*`, and width truncation. Test compile-time constant enforcement, runtime hweight equivalence, and side-effect-free usage expectations.
