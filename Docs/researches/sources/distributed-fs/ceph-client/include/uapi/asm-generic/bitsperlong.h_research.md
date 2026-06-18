# sources/distributed-fs/ceph-client/include/uapi/asm-generic/bitsperlong.h

Purpose: Defines generic user-space bit width macros for C `long` and `long long`.

Important APIs/types/functions: Provides `__BITS_PER_LONG`, derived from compiler `__CHAR_BIT__ * __SIZEOF_LONG__` when available or defaulting to 32, and `__BITS_PER_LONG_LONG` defaulting to 64.

Control flow: Preprocessor-only fallback logic lets architectures override `__BITS_PER_LONG` before inclusion.

State/persistence: No runtime state; establishes compile-time ABI assumptions.

Dependencies/integration: Included by many asm-generic UAPI headers that need layout decisions for 32-bit vs 64-bit user space.

Risks: Incorrect `__BITS_PER_LONG` breaks UAPI struct layout and ABI compatibility, especially for compat user space on 64-bit kernels.

Test signals: Build headers for 32-bit, 64-bit, and compat targets; validate IPC/time struct layout expectations.
