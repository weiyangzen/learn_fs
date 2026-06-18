# sources/distributed-fs/ceph-client/arch/sparc/lib/strlen.S

Purpose: optimized SPARC assembly implementation of `strlen`, adapted from GNU libc and exported as the kernel string helper.

Important APIs/functions: `ENTRY(strlen)` returns the number of bytes before the first NUL. It uses magic constants `LO_MAGIC` and `HI_MAGIC`, linkage macros, and `EXPORT_SYMBOL(strlen)`.

Control flow: the routine saves the starting pointer, peels up to three bytes to align on a 4-byte boundary, then scans words with the subtract/high-bit zero-detection trick. On possible zero, it checks each byte in word order and subtracts the original pointer. Labels `11`, `12`, and `13` return immediate lengths for early unaligned hits.

State and persistence: no persistent state and no writes. It reads memory until a NUL terminator and uses only registers.

Dependencies/integration: includes `linux/export.h`, `linux/linkage.h`, and `asm/asm.h` for branch macros that abstract 32/64-bit conditional forms. Used throughout kernel and module code wherever `strlen` is referenced.

Risks: optimized word scanning assumes accessible bytes up to the terminator; like most strlen implementations, invalid unterminated strings can fault. Endianness and byte-order checks must match SPARC layout. Alignment peel labels are easy sources of off-by-one return errors.

Test signals: string tests for every alignment modulo 4, empty strings, terminator in each byte lane, long strings crossing cache lines/pages, and comparison against generic C `strlen`.
