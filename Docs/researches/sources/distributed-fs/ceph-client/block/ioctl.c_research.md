<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/ioctl.c -->
# sources/distributed-fs/ceph-client/block/ioctl.c

## Purpose
`ioctl.c` implements generic block-device ioctl handling, compat ioctl handling, persistent reservation commands, geometry/size/read-only/block-size controls, discard/secure erase/zeroout operations, crypto/zone delegation, and an io_uring command path for discard.

## Important APIs, Types, and Functions
- Entry points: `blkdev_ioctl()`, `compat_blkdev_ioctl()`, `blkdev_compat_ptr_ioctl()`, and `blkdev_uring_cmd()`.
- Partition mutation: `blkpg_ioctl()`, `compat_blkpg_ioctl()`, `blkpg_do_ioctl()`.
- Data modification: `blk_ioctl_discard()`, `blk_ioctl_secure_erase()`, `blk_ioctl_zeroout()`, `blkdev_cmd_discard()`.
- Persistent reservation helpers wrap `struct pr_ops`: register, reserve, release, preempt, clear, read keys, and read reservation.
- Common dispatch is centralized in `blkdev_common_ioctl()`.

## Control Flow
Native and compat ioctl entry points handle structurally incompatible commands first, then call `blkdev_common_ioctl()`. Unknown commands fall back to driver `fops->ioctl` or `fops->compat_ioctl` when present. `BLKPG` requires `CAP_SYS_ADMIN`, whole-disk access, positive partition numbers, aligned byte ranges, overflow checks, and capacity checks before delegating to add/delete/resize partition helpers.

Discard and zeroing ioctls copy a two-u64 byte range from userspace, validate write access, read-only state, alignment, nonzero length, and end-of-device bounds. They lock the block inode and invalidate mapping pages before issuing discard/secure erase/zeroout bios. Secure erase checks secure-erase queue support and uses `blkdev_issue_secure_erase()`. Zeroout uses `BLKDEV_ZERO_NOUNMAP | BLKDEV_ZERO_KILLABLE`.

Persistent reservation commands gate partition use, capability/open-mode permissions, user copy, flag validity, and driver `pr_ops` presence. Read-key output allocates a variable-size kernel buffer, copies only the requested/available key count, and returns generation/count metadata.

The io_uring path currently supports `BLOCK_URING_CMD_DISCARD`: it validates SQE padding, persists start/len in the command private data across reissue, supports nonblocking invalidation/allocation with `-EAGAIN`, chains discard bios, and completes through task work.

## State and Persistence Behavior
The file can persistently alter media via discard, secure erase, zeroout, partition table mutation, read-only flags, block-size changes, persistent reservations, crypto key preparation/import/generation, and zone management. It mutates page cache and bdev metadata to keep kernel state coherent with destructive media operations. It also updates BDI readahead pages and returns diskseq for user-space event correlation.

## Dependencies and Integration Points
It integrates with VFS file mode conversion from `file_to_blk_mode()`, partition core helpers, zone management, blktrace, blk-crypto, persistent reservation driver callbacks, block queue limits, page cache invalidation, io_uring command infrastructure, and compat userspace ABI translation.

## Risks and Edge Cases
The ioctl ABI is broad and compatibility-sensitive. Misaligned or overflowing ranges must be rejected before destructive operations. `BLKFLSBUF` has holder sync behavior under `bd_holder_lock`; incorrect locking could deadlock or skip stacked-device sync. Compat command numbers differ for selected commands. io_uring discard cannot safely report partial multi-bio failures in NOWAIT mode, so it forces retry. `blkdev_bszset()` must reopen exclusively when the original file is not exclusive.

## Test Signals
Run block ioctl ABI tests for native and compat userspace, BLKPG add/delete/resize races, discard/zeroout/secure erase boundary tests, read-only permission tests, persistent reservation passthrough tests with capable and unprivileged callers, blk-crypto ioctl tests, zone ioctl tests, io_uring discard NOWAIT/blocking tests, and syzkaller-style user pointer/fuzz tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/ioctl.c -->
