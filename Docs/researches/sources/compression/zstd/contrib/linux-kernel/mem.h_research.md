# sources/compression/zstd/contrib/linux-kernel/mem.h

Purpose: Linux-kernel replacement for zstd's `mem.h`, mapping zstd memory I/O helpers onto kernel unaligned access, byte-swap, and type facilities.

Important APIs and control flow: defines zstd basic integer aliases (`BYTE`, `U8`...`S64`) and static inline helpers for 32/64-bit detection, endian detection via `__LITTLE_ENDIAN`, native unaligned reads/writes, little-endian and big-endian reads/writes for 16/24/32/64/size_t, and byte swaps. Implementations call kernel-style `get_unaligned*`, `put_unaligned*`, `swab32`, and `swab64`; size_t helpers branch on `MEM_32bits()`.

State, dependencies, and integration: no state. It depends on `linux/unaligned.h`, `linux/compiler.h`, `linux/swab.h`, `linux/types.h`, and zstd `debug.h`. `freestanding.py` copies it into generated `common/mem.h`.

Risks and test signals: endian macro assumptions and test shim correctness are important. The 24-bit helpers manually compose bytes. Kernel import tests validate compilation and basic behavior through zstd round trips.
