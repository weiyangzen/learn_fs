# sources/distributed-fs/ceph-client/arch/x86/include/asm/word-at-a-time.h

Purpose: Provides optimized x86 word-at-a-time zero-byte detection and safe unaligned word loading used by string/usercopy-style helpers.

Important APIs/types/functions: `struct word_at_a_time` stores `one_bits` and `high_bits`; `WORD_AT_A_TIME_CONSTANTS` initializes them to repeated `0x01` and `0x80`. `has_zero()` detects zero bytes with the classic `(a - one_bits) & ~a & high_bits` expression. `prep_zero_mask()`, `create_zero_mask()`, `zero_bytemask()`, and `find_zero()` transform detection masks differently on 64-bit and 32-bit. `load_unaligned_zeropad()` loads an unaligned word and uses an exception-table entry with `EX_TYPE_ZEROPAD` to zero-fill missing bytes on a page-crossing fault.

Control flow: Callers load a word, call `has_zero()`, derive a mask, then find the first zero byte or byte mask. `load_unaligned_zeropad()` executes one `mov`; if the access faults on an unmapped next page, exception-table fixup resumes after the load with zero padding semantics.

State and persistence: No persistent state. It reads memory and may take a handled exception.

Dependencies and integration points: Depends on bitops, wordpart helpers, x86 asm exception-table macros, and string routines in the kernel.

Risks: Bit tricks are width-specific. Exception-table correctness is critical; an incorrect fixup can turn a safe string load into a kernel fault. Unaligned access assumptions are x86-specific.

Test signals: String/memchr/strlen style tests, KASAN/KCSAN builds, page-boundary fault tests for zeropad behavior, and 32-bit/64-bit build coverage.
