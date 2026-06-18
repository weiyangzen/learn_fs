# sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-__ffs.h

Purpose: Provides a compiler-builtin implementation of `__ffs()` for architectures/toolchains that choose it over the manual generic version.

Important APIs, types, and functions: Defines `__ffs(unsigned long word)` as `__builtin_ctzl(word)`.

Control flow: Delegates entirely to the compiler builtin. Zero input remains undefined.

State and persistence: No state.

Dependencies and integration points: Depends on compiler support for `__builtin_ctzl`. Used by bitops configurations that prefer builtin codegen.

Risks and test signals: Risks include undefined zero behavior and compiler differences in builtin lowering. Test bitops selftests, zero guards, and generated code on GCC/Clang for 32-bit and 64-bit targets.
