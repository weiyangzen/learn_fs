# sources/compression/zstd/contrib/linux-kernel/test/include/linux/unaligned.h

Purpose: user-space implementation of Linux unaligned access helpers for the kernel-zstd test harness.

Important APIs and control flow: detects little endian from compiler macros and asserts runtime agreement. Implements little-endian and big-endian unaligned get/put helpers for 16/32/64-bit values using `__builtin_memcpy` and byte swaps. Generic macros `__get_unaligned_le/be` and `__put_unaligned_le/be` dispatch by pointed-to type size using `__builtin_choose_expr` or switch, calling `__bad_unaligned_access_size()` for unsupported sizes. `get_unaligned`/`put_unaligned` map to little- or big-endian variants based on host endian.

State, dependencies, and integration: no persistent state. It depends on `assert.h`, `linux/types.h`, GCC extensions, and compiler bswap/memcpy builtins. `mem.h` uses these helpers for zstd memory I/O.

Risks and test signals: `_swap16()` appears to mask nibbles rather than bytes, which would be wrong on big-endian paths for 16-bit conversions. Most CI hosts are little-endian, so big-endian coverage matters. Linux-kernel tests and QEMU big-endian jobs are useful signals.
