# sources/distributed-fs/ceph-client/arch/xtensa/lib/usercopy.S

Purpose: Implements low-level `__xtensa_copy_user()` for copying between kernel and user address spaces with exception fixups.

Important APIs, types, and functions: `__xtensa_copy_user`, aligned/unaligned destination paths, unaligned-source merge path, byte-copy fallback, exception fixup label `10`, and `EXPORT_SYMBOL`.

Control flow: Saves original length, aligns destination if profitable, uses fast 16-byte loops for aligned source/destination, uses `SRC` merge after aligning unaligned source, handles 8/4/2/1 byte tails, and returns zero on success. On fault, fixup computes `bytes_not_copied = original_len - (current_dst - original_dst)`.

State and persistence: Writes destination memory partially or completely; returns residual byte count. It intentionally remains separate from HAL `memcopy.S` so user fault behavior is not lost during HAL replacement.

Dependencies and integration: Used by Xtensa `copy_{to,from}_user` wrappers, exception tables, ABI macros, loop feature macros, and user access fault handling.

Risks: Partial copies must report precise residual bytes; unaligned-source path adjusts pointers for simulator warnings; CALL0/no-loop path uses a small stack slot for saved offset; combining with normal memcpy would break fault semantics.

Test signals: Usercopy tests over all alignments/lengths, fault at each segment, residual byte correctness, hardened usercopy, and no-loop/CALL0 builds.
