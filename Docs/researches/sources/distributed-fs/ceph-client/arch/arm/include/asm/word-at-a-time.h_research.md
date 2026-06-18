# sources/distributed-fs/ceph-client/arch/arm/include/asm/word-at-a-time.h

## Purpose
Implements ARM word-at-a-time zero-byte detection and optional unaligned zeropadded kernel loads for optimized string routines.

## Important APIs, Types, And Functions
Key declarations include struct word_at_a_time {; static inline unsigned long has_zero(unsigned long a, unsigned long *bits,; unsigned long mask = ((a - c->one_bits) & ~a) & c->high_bits;; static inline unsigned long create_zero_mask(unsigned long bits); static inline unsigned long find_zero(unsigned long mask); unsigned long ret;. Important macros/constants include __ASM_ARM_WORD_AT_A_TIME_H, WORD_AT_A_TIME_CONSTANTS, prep_zero_mask(a,, zero_bytemask(mask). It depends directly on #include <linux/bitops.h>, #include <linux/wordpart.h>, #include <asm-generic/word-at-a-time.h>.

## Control Flow
Little-endian builds use x86-style one/high-bit arithmetic and CLZ or fallback math to locate zero bytes; DCACHE_WORD_ACCESS builds use exception-table fixups for page-crossing unaligned loads.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/bitops.h>, #include <linux/wordpart.h>, #include <asm-generic/word-at-a-time.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
