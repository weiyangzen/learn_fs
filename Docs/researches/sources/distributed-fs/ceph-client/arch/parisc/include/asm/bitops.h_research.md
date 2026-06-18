# sources/distributed-fs/ceph-client/arch/parisc/include/asm/bitops.h

Purpose: implements PA-RISC bit operations, including atomic bit set/clear/change/test and optimized find-first/last helpers.

Important APIs/types/functions: defines `set_bit`, `clear_bit`, `change_bit`, `test_and_set_bit`, `test_and_clear_bit`, `test_and_change_bit`, `__ffs`, `ffs`, `fls`, and imports generic non-atomic, little-endian, lock, scheduler, ext2, and hweight helpers.

Control flow: atomic operations are built on Linux atomic operations against the containing word; find operations use PA-RISC-friendly bit scanning sequences.

State and persistence: modifies caller-owned bitmaps, flags, page state, and filesystem bitmaps. Dependencies and integration: depends on compiler annotations, byte order, barriers, and generic bitops.

Risks and test signals: bit numbering and endian assumptions are high risk for filesystem and scheduler state. Test with bitmap selftests, ext2 bitops tests, and big-endian PA-RISC boot coverage.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
