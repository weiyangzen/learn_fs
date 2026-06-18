# sources/distributed-fs/ceph-client/fs/ext4/truncate.h

## Purpose
`truncate.h` contains small inline helpers shared by ext4 truncate/write failure paths. It centralizes the cleanup sequence for failed extending writes and computes bounded journal credit estimates for truncate transactions.

## Important APIs, Types, And Functions
`ext4_truncate_failed_write(struct inode *inode)` invalidates page cache beyond the current inode size and calls `ext4_truncate()` after a write path allocated blocks that were not successfully exposed. `ext4_blocks_for_truncate(struct inode *inode)` estimates the transaction credit budget for the next truncate chunk from `inode->i_blocks`, clamps corrupt-small values up to a safe minimum, caps large values at `EXT4_MAX_TRANS_DATA`, and adds `EXT4_DATA_TRANS_BLOCKS()`.

## Control Flow
The failed-write helper takes the inode mapping's invalidate lock, truncates cached pages to `inode->i_size`, runs ext4 block truncation, then releases the lock. It explicitly skips `ext4_break_layouts()` because the blocks being removed were never visible to userspace. The credit helper converts `i_blocks` from 512-byte sectors to filesystem blocks, applies lower and upper bounds, and returns a journal-credit count for callers that break truncate work into manageable transactions.

## State And Persistence Behavior
`ext4_truncate_failed_write()` removes page-cache state and persistent block mappings past the final visible file size. The helper assumes file size already reflects the correct exposed size. `ext4_blocks_for_truncate()` does not mutate state; it protects journal sizing from corrupt `i_blocks` values and from transactions too large for the journal.

## Dependencies And Integration Points
The helpers integrate with VFS page-cache invalidation, ext4's truncate implementation, ext4 journal credit macros, `struct inode`, `struct address_space`, and ext4 block accounting. They are intended for inclusion by write/truncate code rather than compiled as a separate translation unit.

## Risks And Edge Cases
The failed-write cleanup must hold invalidate locking so buffers are unmapped consistently with page-cache truncation. If callers pass an inode whose `i_size` was not restored correctly, valid blocks could be removed or stale blocks retained. The credit estimate intentionally tolerates corrupt `i_blocks`, but severe corruption can still make truncate behavior expensive or require multiple transactions.

## Test Signals
Useful tests include failed buffered writes after delayed allocation, ENOSPC/error injection during extending writes, mmap/page-cache coherency after failed writes, truncates of sparse and heavily fragmented files, corrupt or fuzzed inode block counts, and journal credit exhaustion boundaries around `EXT4_MAX_TRANS_DATA`.
