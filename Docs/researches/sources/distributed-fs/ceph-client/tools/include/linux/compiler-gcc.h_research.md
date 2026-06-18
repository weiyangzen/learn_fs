# sources/distributed-fs/ceph-client/tools/include/linux/compiler-gcc.h

## Purpose

This header supplies GCC-specific compiler attributes and helpers for the tools compiler abstraction layer.

## APIs, State, and Dependencies

It is guarded so it must be included through `<linux/compiler.h>`. It defines `GCC_VERSION`, `fallthrough`, `__compiletime_error`, `__must_be_array`, `__pure`, `noinline`, `__packed`, `__noreturn`, `__aligned`, `__printf`, and `__scanf` as supported by the compiler. There is no state.

## Risks and Test Signals

Compiler feature detection must work for GCC and Clang-compatible frontends. Direct inclusion intentionally errors. Tests should compile attribute users with GCC and Clang and verify direct include failure is preserved.
