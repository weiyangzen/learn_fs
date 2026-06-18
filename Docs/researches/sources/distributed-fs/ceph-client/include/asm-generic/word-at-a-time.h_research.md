# sources/distributed-fs/ceph-client/include/asm-generic/word-at-a-time.h

Purpose: endian-aware word scanning helpers used by string routines to detect zero bytes efficiently.

Important APIs/types/functions: `struct word_at_a_time`, `WORD_AT_A_TIME_CONSTANTS`, `has_zero`, `prep_zero_mask`, `create_zero_mask`, `find_zero`, `zero_bytemask`, and little-endian `count_masked_bytes`.

Control flow: callers load a machine word, call `has_zero()` to produce a mask/bits value, normalize it with `prep_zero_mask()`/`create_zero_mask()`, then use `find_zero()` to locate the first zero byte. Big-endian and little-endian implementations use different arithmetic and mask conventions.

State and persistence: stateless; constants are passed by caller and no data persists outside the computed masks.

Dependencies and integration points: depends on `linux/bitops.h`, `linux/wordpart.h`, and byteorder definitions. Used by optimized `strlen`, `strnlen`, and related word-at-a-time string scans.

Risks: correctness is highly endian- and word-size-sensitive. Off-by-one byte indexes or mask convention mismatches can cause string functions to overrun buffers or misreport lengths.

Test signals: string selftests over aligned/unaligned buffers, big-endian and little-endian build/runtime tests, 32-bit and 64-bit coverage, and KASAN/UBSAN overread detection.
