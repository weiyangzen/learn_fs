# sources/distributed-fs/ceph-client/include/asm-generic/bitops/ext2-atomic-setbit.h

Purpose: Provides ext2 little-endian atomic bitmap helpers using native atomic little-endian test-and-bit operations.

Important APIs, types, and functions: Defines `ext2_set_bit_atomic(l, nr, addr)` as `test_and_set_bit_le(nr, addr)` and `ext2_clear_bit_atomic(l, nr, addr)` as `test_and_clear_bit_le(nr, addr)`.

Control flow: Ignores the lock argument and relies on atomic little-endian bitops to return the previous bit value while updating the bitmap.

State and persistence: Mutates filesystem bitmaps, often persisted to disk by ext2-like filesystems after buffer writeback.

Dependencies and integration points: Depends on little-endian atomic bitops. Used by ext2 bitmap allocation/free paths on architectures with suitable atomic LE operations.

Risks and test signals: Risks are ignoring a lock on architectures where LE atomic ops are insufficient and confusing endian order. Test ext2 block/inode bitmap allocation under concurrency and compare on big-endian systems.
