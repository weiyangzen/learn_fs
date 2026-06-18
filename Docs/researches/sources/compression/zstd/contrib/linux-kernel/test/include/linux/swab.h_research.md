# sources/compression/zstd/contrib/linux-kernel/test/include/linux/swab.h

Purpose: byte-swap shim for user-space kernel-zstd tests.

Important behavior: defines `swab32(x)` and `swab64(x)` using compiler builtins `__builtin_bswap32` and `__builtin_bswap64`.

State, dependencies, and integration: no state or includes. It supports `contrib/linux-kernel/mem.h` byte-swap helpers.

Risks and test signals: requires GCC/Clang-compatible builtins. Any need for 16-bit or other swap helpers will fail at compile time until added.
