<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/word-at-a-time.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/word-at-a-time.h

Purpose: Implements PowerPC optimized word-at-a-time zero-byte detection and safe unaligned zero-padded loads used by string routines.

Important APIs/types/functions: Endian-specific `struct word_at_a_time`, `WORD_AT_A_TIME_CONSTANTS`, `has_zero()`, `prep_zero_mask()`, `create_zero_mask()`, `find_zero()`, `zero_bytemask()`, and `load_unaligned_zeropad()`.

Control flow: String scanning loads machine words, computes masks for zero bytes using big-endian arithmetic, little-endian `cmpb` on 64-bit, or generic 32-bit LE arithmetic, then converts masks to byte offsets. Faulting unaligned loads branch through an exception-table fixup that reloads an aligned word and shifts away bytes before the address.

State and persistence: No persistent state. The exception table metadata persists in the object file so fault handling can redirect load faults.

Dependencies and integration points: Depends on bit operations, wordpart helpers, asm compatibility macros, exception-table macros, and PowerPC load/shift instructions. Used by optimized `strlen`, `strnlen`, and related routines/selftests.

Risks: Endian and word-size branches are easy to regress. `load_unaligned_zeropad()` is exception-table-sensitive and must preserve fault safety near page boundaries.

Test signals: lib/string and word-at-a-time selftests, fault-near-page-boundary tests, big/little-endian PPC32/PPC64 builds, and objtool/exception-table inspection.

Source read size: 206 lines, 4905 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/word-at-a-time.h -->
