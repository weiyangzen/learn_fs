# sources/distributed-fs/ceph-client/include/asm-generic/bitops/arch_hweight.h

Purpose: Provides architecture hweight hooks that delegate to software population-count implementations.

Important APIs, types, and functions: Defines `__arch_hweight32()`, `__arch_hweight16()`, `__arch_hweight8()`, and `__arch_hweight64()` as wrappers around `__sw_hweight*`.

Control flow: Straight-line delegation.

State and persistence: No state.

Dependencies and integration points: Depends on asm types and software hweight helpers. Used by generic hweight macros and bitmap/counting code.

Risks and test signals: Risks are performance on architectures with hardware popcount but no override, and type-width mismatches. Test hweight selftests for all widths and performance-sensitive bitmap paths.
