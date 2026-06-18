# sources/distributed-fs/ceph-client/tools/include/linux/compiler_types.h

## Purpose

This header centralizes compiler type support used by the tools compiler abstraction.

## APIs, State, and Dependencies

It defines fallback `__has_builtin`, includes context-analysis stubs, includes GCC-specific definitions when `__GNUC__` is set, defines `asm_goto_output`, and provides `__unqual_scalar_typeof` using C11 `_Generic` to strip scalar qualifiers while leaving nonscalars unchanged. There is no runtime state.

## Risks and Test Signals

The `_Generic` type logic depends on compiler C dialect support. Tests should compile with GCC and Clang, including users of `__unqual_scalar_typeof` on signed, unsigned, char, and nonscalar expressions.
